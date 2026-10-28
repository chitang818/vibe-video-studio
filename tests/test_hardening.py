"""Regressions for the concrete cross-agent bypasses. Keys/approvals are TEST fixtures only."""
import copy
import json
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
import test_quality_gate as quality_fixtures
fixture=quality_fixtures.fixture
from scripts.quality_gate import static_checks,run_gate,REVIEW_CHECKS,read_json,validate_review
from scripts.text_contract import clean,strict_loads,validate_rows
from scripts.build_fast_project import editorial_subtitles,digest
from scripts.preview_template import canonical_html
from scripts.release import sign_approval,verify_approval,publish


class BypassTests(unittest.TestCase):
    def setUp(self): self.m,self.s,self.rows,self.p=fixture()
    def rules(self): return {e['rule'] for e in static_checks(self.m,self.s,self.rows,self.p)}
    def test_decimal_identity_is_preserved(self):
        self.assertNotEqual(clean('1.5倍'),clean('15倍'))
        self.assertEqual(clean('增长1.5倍。'),'增长1.5倍')
        self.assertNotEqual(clean('.5倍'),clean('5倍'))
        self.assertEqual(clean('1 .5倍'),'1.5倍')
        from scripts.text_contract import number_tokens
        self.assertNotEqual(number_tokens('15'),number_tokens('1，5'))
        self.assertNotEqual(number_tokens('-15°C'),number_tokens('15°C'))
    def test_timeline_keeps_decimals_and_numeric_token_boundaries(self):
        from scripts.extract_timeline import build_timeline_index,find_keyword
        text='先看15倍，再看1.5倍和20%，最后是0%。'
        rows=[dict(Char=c,StartSeconds=i*.1,EndSeconds=(i+1)*.1) for i,c in enumerate(text)]
        index=build_timeline_index(rows)
        self.assertEqual(find_keyword(index,'1.5倍')['start_idx'],text.index('1.5'))
        self.assertEqual(find_keyword(index,'0%')['start_idx'],text.index('0%',text.index('最后')))
        self.assertIsNone(find_keyword(index,'5倍'))
    def test_timeline_preserves_microseconds_and_rejects_partial_output(self):
        from scripts.extract_timeline import process_keywords
        import tempfile
        with tempfile.TemporaryDirectory() as work:
            root=Path(work);rows=[dict(Char=c,StartSeconds=.123456+i*.2,EndSeconds=.323456+i*.2) for i,c in enumerate('甲乙丙丁')]
            (root/'rows.json').write_text(json.dumps(rows),encoding='utf-8')
            (root/'keys.txt').write_text('甲乙丙丁|步骤',encoding='utf-8')
            process_keywords(str(root/'rows.json'),str(root/'keys.txt'),str(root/'timeline.txt'),str(root/'sfx.json'))
            self.assertEqual(read_json(root/'sfx.json')['click'],[.123456])
            original=(root/'sfx.json').read_bytes();(root/'keys.txt').write_text('不存在|步骤',encoding='utf-8')
            with self.assertRaises(ValueError):process_keywords(str(root/'rows.json'),str(root/'keys.txt'),str(root/'other.txt'),str(root/'sfx.json'))
            self.assertFalse((root/'other.txt').exists());self.assertEqual((root/'sfx.json').read_bytes(),original)
    def test_decimal_caption_uses_original_dot_row(self):
        text='增长1.5倍。下一段讲解。'
        rows=[dict(Char=c,StartSeconds=i*.1,EndSeconds=(i+1)*.1) for i,c in enumerate(text)]
        u=editorial_subtitles(rows,['增长1.5倍','下一段讲解'],2000000)
        self.assertEqual(''.join(c['text'] for c in u[0]['chars']),'增长1.5倍。')
        with self.assertRaises(ValueError):editorial_subtitles(rows,['增长15倍','下一段讲解'],2000000)
        text='增长.5倍。下一段讲解。'
        rows=[dict(Char=c,StartSeconds=i*.1,EndSeconds=(i+1)*.1) for i,c in enumerate(text)]
        u=editorial_subtitles(rows,['增长.5倍','下一段讲解'],2000000)
        self.assertEqual(''.join(c['text'] for c in u[0]['chars']),'增长.5倍。')
    def test_invalid_original_end_time_rejected(self):
        self.rows[-1]['EndSeconds']=99
        with self.assertRaises(ValueError):validate_rows(self.rows,self.m['durationUs'])
    def test_caption_cannot_cut_off_a_spoken_character(self):
        self.s['subtitles'][0]['endUs']=self.s['subtitles'][0]['chars'][-1]['startUs']+1
        self.assertIn('CAPTION',self.rules())
    def test_punctuation_is_not_a_beat_quote(self):
        self.p['scenes'][0]['beats'][0]['quote']='。'
        self.assertIn('BEAT',self.rules())
    def test_duplicate_and_nonfinite_json_rejected(self):
        for text in ['{"a":1,"a":2}','{"a":NaN}']:
            with self.assertRaises(ValueError):strict_loads(text)
    def test_dependency_drift_is_reported(self):
        from scripts.doctor import check_dependencies
        with patch('scripts.doctor.importlib.metadata.version',return_value='unexpected'):
            self.assertFalse(check_dependencies()[0])
    def test_square_profile_rejected(self):
        self.m['width']=1920;self.assertIn('PROFILE',self.rules())
    def test_unreadable_subtitle_rejected(self):
        self.s['subtitleSize']=8;self.assertIn('TYPE',self.rules())
    def test_invisible_beat_rejected(self):
        self.s['scenes'][0]['nodes'][2]['color']='rgba(0,0,0,0)';self.assertIn('VISIBILITY',self.rules())
    def test_unknown_role_rejected(self):
        self.p['scenes'][0]['roles']['arbitrary']=[self.p['scenes'][0]['roles']['content'].pop()]
        self.assertIn('SCHEMA',self.rules())
    def test_empty_beat_plan_is_rejected_by_schema(self):
        self.p['scenes'][0]['beats']=[];self.assertIn('SCHEMA',self.rules())
    def test_path_identifier_cannot_escape_evidence_directory(self):
        self.s['scenes'][0]['id']='../../escape';self.assertIn('SCHEMA',self.rules())
    def test_panel_cannot_hide_text_from_layout(self):
        self.p['scenes'][0]['roles']['panel']=[self.p['scenes'][0]['roles']['content'].pop()]
        self.assertIn('PLAN',self.rules())
    def test_node_variants_reject_unused_resource_fields(self):
        self.s['scenes'][0]['nodes'][0]['source']='../outside.png'
        self.assertIn('SCHEMA',self.rules())
    def test_changed_family_name_does_not_hide_duplicate_graphics(self):
        scenes=[];plans=[];rows=[];units=[]
        for i in range(4):
            shot=copy.deepcopy(self.s['scenes'][0]);shot.update(id=f'shot-{i}',startUs=i*6000000,endUs=(i+1)*6000000);scenes.append(shot)
            plan=copy.deepcopy(self.p['scenes'][0]);plan.update(sceneId=shot['id'],visualFamily=f'claimed-{i}')
            for b in plan['beats']:b['timeUs']+=i*6000000
            plans.append(plan)
            for r in self.rows:
                r=copy.deepcopy(r);r['StartSeconds']+=i*6;r['EndSeconds']+=i*6;rows.append(r)
            for u in self.s['subtitles']:
                u=copy.deepcopy(u);u['startUs']+=i*6000000;u['endUs']+=i*6000000
                for c in u['chars']:c['startUs']+=i*6000000
                units.append(u)
        self.s.update(scenes=scenes,subtitles=units);self.p['scenes']=plans;self.rows=rows;self.m['durationUs']=24000000
        self.assertIn('VARIETY',self.rules())
    def test_unreferenced_display_number_rejected(self):
        self.s['scenes'][0]['nodes'][2]['text']='提升99%';self.assertIn('FACT',self.rules())
    def test_standard_component_compiles_with_real_anchors(self):
        from scripts.components import compile_story
        story=dict(version=1,title='知识动画测试',authorId='fixture-author',scenes=[dict(id='test-scene',kind='process',heading='讲解机制流程',
            stages=[dict(text='第一阶段',anchor=dict(quote='戊')),dict(text='第二阶段',anchor=dict(quote='寅'))])])
        s,p=compile_story(story,self.rows,self.m['durationUs']);s['subtitles']=self.s['subtitles']
        self.assertEqual(static_checks(self.m,s,self.rows,p),[])
        story['scenes'][0]['javascript']='bad'
        with self.assertRaises(ValueError):compile_story(story,self.rows,self.m['durationUs'])
    def test_all_components_compile_and_data_values_are_source_bound(self):
        from scripts.components import compile_story,KINDS
        from scripts.contracts import validate_document
        for kind in KINDS:
            with self.subTest(kind=kind):
                rows=self.rows;duration=self.m['durationUs'];units=self.s['subtitles']
                stages=[dict(text='第一阶段',anchor=dict(quote='戊')),dict(text='第二阶段',anchor=dict(quote='寅'))]
                if kind=='data':
                    groups=['先来观察0%的变化','随后对比20%的结果','最后展示30%的数据']
                    text='，'.join(groups)+'。';rows=[dict(Char=c,StartSeconds=i*.2,EndSeconds=(i+1)*.2) for i,c in enumerate(text)];duration=round(len(rows)*.2*1e6)
                    stages=[dict(text=f'当前{n}%',value=n,unit='%',anchor=dict(quote=f'{n}%')) for n in (0,20,30)]
                    units=editorial_subtitles(rows,groups,duration)
                story=dict(version=1,title='知识动画测试',authorId='fixture-author',scenes=[dict(id='component-test',kind=kind,heading='解释机制过程',stages=stages)])
                scene,plan=compile_story(story,rows,duration);scene['subtitles']=units
                validate_document('scene',scene);validate_document('quality-plan',plan)
                self.assertEqual(static_checks(dict(self.m,durationUs=duration),scene,rows,plan),[])
    def test_legacy_pack_never_advertises_ready(self):
        import tempfile
        with tempfile.TemporaryDirectory() as work:
            (Path(work)/'index.html').write_text('<p>ordinary HTML</p>',encoding='utf-8')
            r=subprocess.run([sys.executable,'scripts/pack.py',work],capture_output=True,text=True,encoding='utf-8')
            self.assertNotEqual(r.returncode,0);self.assertNotIn('【就绪',r.stdout)
    def test_template_is_deterministic_across_hash_seeds(self):
        import tempfile
        with tempfile.TemporaryDirectory() as work:
            root=Path(work)
            for name in ('a.wav','b.wav','c.wav'):(root/name).write_bytes(b'test-fixture')
            code="""from pathlib import Path
from scripts.preview_template import render_html
from scripts.build_fast_project import runtime_root
import sys,hashlib
root=Path(sys.argv[1]);track={'version':1,'events':[dict(timeUs=i,source=n,gain=1) for i,n in enumerate(['a.wav','b.wav','c.wav'])]}
print(hashlib.sha256(render_html(root,{'scenes':[]},1080,1920,6000000,None,track,runtime_root()).encode()).hexdigest())
"""
            outputs=[]
            for seed in ('1','2','17'):
                env=dict(os.environ,PYTHONHASHSEED=seed)
                r=subprocess.run([sys.executable,'-c',code,work],capture_output=True,text=True,env=env)
                self.assertEqual(r.returncode,0,r.stderr);outputs.append(r.stdout)
            self.assertEqual(len(set(outputs)),1)


class TrustedReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Reuse the real browser fixture without treating it as a publishable creative work.
        quality_fixtures.BrowserReleaseTests.setUpClass();cls.fixture=quality_fixtures.BrowserReleaseTests;cls.root=cls.fixture.project;cls.report=cls.fixture.report
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        key=rsa.generate_private_key(public_exponent=65537,key_size=3072)
        cls.private=key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption())
        public=key.public_key().public_bytes(serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo).decode()
        cls.review=dict(version=1,status='passed',reviewer='external-test-reviewer',inputFingerprint=cls.report['inputFingerprint'],evidenceDigest=cls.report['evidenceDigest'],
            checks={k:dict(status='passed',observations='TEST FIXTURE ONLY: schema and signature verification, no creative signoff') for k in REVIEW_CHECKS},
            scenes=[dict(sceneId='test-scene',status='passed',observations='TEST FIXTURE ONLY: recorded scene review for contract validation',evidence=[cls.report['screenshots'][0]['file']])])
        (cls.root/'quality-review.json').write_text(json.dumps(cls.review),encoding='utf-8')
        cls.envelope=sign_approval(cls.root,cls.report,cls.private,'external-test-reviewer')
        cls.trust=cls.fixture.base/'trusted-reviewers.json'
        cls.trust.write_text(json.dumps(dict(version=1,keys={cls.envelope['keyId']:dict(publicKeyPem=public,reviewerId='external-test-reviewer')})),encoding='utf-8')
        (cls.root/'release.attestation.json').write_text(json.dumps(cls.envelope),encoding='utf-8')
    @classmethod
    def tearDownClass(cls):cls.fixture.tearDownClass()
    def test_plain_passed_json_without_trust_cannot_release(self):
        with patch.dict(os.environ,{},clear=True):
            with self.assertRaises(ValueError):verify_approval(self.root,self.report)
    def test_full_gate_rejects_self_report_without_attestation(self):
        path=self.root/'release.attestation.json';original=path.read_bytes();path.unlink()
        try:
            with patch.dict(os.environ,{'VIBE_TRUST_STORE':str(self.trust)}):
                result=run_gate(self.root,release=True)
            self.assertEqual(result['status'],'blocked')
            self.assertTrue(any(e['rule']=='APPROVAL' for e in result['errors']))
        finally:path.write_bytes(original)
    def test_valid_external_signature_is_accepted(self):
        self.assertEqual(verify_approval(self.root,self.report,self.trust)['status'],'approved')
    def test_changed_observations_invalidate_signature(self):
        path=self.root/'quality-review.json';original=path.read_bytes()
        try:
            value=read_json(path);value['checks']['soundMix']['observations']='changed test review observations'
            path.write_text(json.dumps(value),encoding='utf-8')
            with self.assertRaises(ValueError):verify_approval(self.root,self.report,self.trust)
        finally:path.write_bytes(original)
    def test_unknown_key_and_changed_payload_are_rejected(self):
        path=self.root/'release.attestation.json';original=path.read_bytes()
        try:
            envelope=copy.deepcopy(self.envelope);envelope['signature']='AAAA';path.write_text(json.dumps(envelope),encoding='utf-8')
            with self.assertRaises(Exception):verify_approval(self.root,self.report,self.trust)
        finally:path.write_bytes(original)
    def test_same_project_concurrent_run_is_rejected(self):
        from scripts.quality_gate import report_directory
        path=report_directory(self.root)/'active.lock';path.write_text('fixture lock',encoding='utf-8')
        try:self.assertEqual(run_gate(self.root)['errors'][0]['rule'],'CONCURRENT')
        finally:path.unlink()
    def test_hidden_canvas_is_rejected_before_execution(self):
        from scripts.quality_browser import inspect_browser
        from scripts.quality_gate import report_directory
        path=self.root/'index.html';original=path.read_bytes()
        try:
            path.write_bytes(original+b'<script>document.querySelector("canvas").style.opacity=0</script>')
            r=inspect_browser(self.root,read_json(self.root/'vibe.project.json'),read_json(self.root/'scene.json'),read_json(self.root/'quality-plan.json'),Path(self.report['evidenceRoot']))
            self.assertEqual(r['browserErrors'][0]['rule'],'RUNTIME');self.assertEqual(r['screenshots'],[])
        finally:path.write_bytes(original)
    def test_signed_package_and_consumer_contract(self):
        with patch.dict(os.environ,{'VIBE_TRUST_STORE':str(self.trust)}):
            report=run_gate(self.root,release=True)
            self.assertEqual(report['status'],'release_passed',report['errors'])
            package=self.fixture.base/'signed-release';publish(self.root,report,package)
            self.assertTrue((package/'quality-evidence/index.json').is_file())
            with self.assertRaises(ValueError):publish(self.root,report,package)
            build_root=Path(os.environ.get('VIBE_TEST_ARTIFACTS',str(self.fixture.base/'consumer-build')))
            assembly=build_root/'bin/ConsumerContract/debug/ConsumerContract.dll'
            command=['dotnet','build','tests/ConsumerContract/ConsumerContract.csproj','--artifacts-path',str(build_root),'-p:UseSharedCompilation=false','--verbosity','quiet']
            if os.environ.get('VIBE_CONSUMER_REPO'):
                command.append('-p:WeMediaForgeRoot='+str(Path(os.environ['VIBE_CONSUMER_REPO']).resolve()))
            r=subprocess.run(command,capture_output=True,text=True,encoding='utf-8')
            self.assertEqual(r.returncode,0,(r.stdout or '')+(r.stderr or ''))
            def consume():return subprocess.run(['dotnet',str(assembly),str(package),str(package/'vibe-runtime/scene.mjs')],capture_output=True,text=True,encoding='utf-8')
            result=consume();self.assertEqual(result.returncode,0,(result.stdout or '')+(result.stderr or ''))
            (package/'quality-evidence/index.json').write_text('[]',encoding='utf-8')
            self.assertNotEqual(consume().returncode,0)
            (package/'release.attestation.json').unlink()
            self.assertNotEqual(consume().returncode,0)


if __name__=='__main__':unittest.main()
