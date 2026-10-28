import copy
import json
import math
import struct
import tempfile
import unittest
import wave
from pathlib import Path
from types import SimpleNamespace

from scripts.build_fast_project import build, digest, editorial_subtitles, runtime_root
from scripts.quality_gate import (REVIEW_CHECKS, input_fingerprint, read_json,
                                  run_gate, static_checks, validate_review)


def fixture():
    rows = [dict(Char=c, StartSeconds=i*.25, EndSeconds=(i+1)*.25)
            for i,c in enumerate('甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午未申酉戌亥天地')]
    duration = len(rows)*250000
    nodes = [
        dict(id='title',type='text',x=150,y=220,width=780,height=80,size=48,text='测试知识动画'),
        dict(id='graphic',type='path',x=380,y=700,width=300,height=300,path='M20 20 L200 20 L110 180 Z',pulse=True),
        dict(id='step-one',type='text',x=160,y=1120,width=760,height=80,size=48,text='第一阶段',enterUs=1000000),
        dict(id='step-two',type='text',x=160,y=1260,width=760,height=80,size=48,text='第二阶段',enterUs=3000000),
    ]
    scene=dict(background=dict(color='#071d1b',particles=True,seed=1),subtitleSize=46,
        scenes=[dict(id='test-scene',startUs=0,endUs=duration,nodes=nodes)],
        subtitles=editorial_subtitles(rows,[''.join(r['Char'] for r in rows[i:i+6]) for i in range(0,len(rows),6)],duration))
    plan=dict(version=1,profile='knowledge-portrait-v1',authorId='fixture-author',facts=[],background=dict(implementation='shared particles',rationale='test fixture only'),scenes=[dict(
        sceneId='test-scene',purpose='测试分镜阶段',visualIntent='三角形为受控测试图形',visualFamily='test-diagram',
        roles=dict(title=['title'],graphic=['graphic'],content=['step-one','step-two'],panel=[]),
        beats=[dict(timeUs=t,quote=rows[t//250000]['Char'],nodeIds=[nid],meaning='显示新的讲解阶段')
               for t,nid in [(1000000,'step-one'),(3000000,'step-two')]],intentionalOverlaps=[])])
    return dict(width=1080,height=1920,durationUs=duration),scene,rows,plan


class StaticQualityTests(unittest.TestCase):
    def setUp(self):
        self.m,self.s,self.rows,self.p=fixture()

    def rules(self):
        return {e['rule'] for e in static_checks(self.m,self.s,self.rows,self.p)}

    def test_valid_automated_fixture(self):
        self.assertEqual(self.rules(),set())

    def test_missing_plan_blocks(self):
        self.p=None
        self.assertIn('PLAN',self.rules())

    def test_false_quote_blocks(self):
        self.p['scenes'][0]['beats'][0]['quote']='不存在的口播'
        self.assertIn('BEAT',self.rules())

    def test_beat_without_rendered_entry_blocks(self):
        self.p['scenes'][0]['beats'][0]['nodeIds']=['graphic']
        self.assertIn('BEAT',self.rules())

    def test_background_motion_not_information(self):
        self.s['scenes'][0]['nodes'][-1]['enterUs']=1500000
        self.p['scenes'][0]['beats'][-1].update(timeUs=1500000,quote=self.rows[6]['Char'])
        self.assertIn('RHYTHM',self.rules())

    def test_content_static_blocks_even_with_particles(self):
        self.s['scenes'][0]['nodes'][1]['pulse']=False
        self.assertIn('MOTION',self.rules())

    def test_non_timestamp_entry_blocks(self):
        self.s['scenes'][0]['nodes'][-1]['enterUs']=3000001
        self.assertIn('SYNC',self.rules())

    def test_short_shot_blocks(self):
        self.s['scenes'][0]['endUs']=5900000
        self.assertIn('RHYTHM',self.rules())

    def test_small_text_blocks(self):
        self.s['scenes'][0]['nodes'][0]['size']=20
        self.assertIn('TYPE',self.rules())

    def test_three_zone_gap_blocks(self):
        self.s['scenes'][0]['nodes'][1]['y']=310
        self.assertIn('LAYOUT',self.rules())

    def test_caption_typo_blocks(self):
        self.s['subtitles'][0]['chars'][0]['text']='错'
        self.assertIn('CAPTION',self.rules())

    def test_caption_timing_drift_blocks(self):
        self.s['subtitles'][0]['chars'][0]['startUs']+=1
        self.assertIn('CAPTION',self.rules())

    def test_protected_term_split_blocks(self):
        self.s['protectedTerms']=['己庚']
        self.assertIn('CAPTION',self.rules())

    def test_missing_role_assignment_blocks(self):
        self.p['scenes'][0]['roles']['content'].pop()
        self.assertIn('PLAN',self.rules())

    def test_text_cannot_pretend_to_be_graphic(self):
        self.p['scenes'][0]['roles']['graphic']=['title']
        self.assertIn('GRAPHIC',self.rules())

    def test_explicit_caption_preserves_internal_and_sentence_punctuation(self):
        text='甲乙，丙丁。戊己庚辛。'
        rows=[dict(Char=c,StartSeconds=i*.2,EndSeconds=(i+1)*.2) for i,c in enumerate(text)]
        units=editorial_subtitles(rows,['甲乙丙丁','戊己庚辛'],3000000)
        self.assertEqual([''.join(c['text'] for c in u['chars']) for u in units],['甲乙，丙丁。','戊己庚辛。'])

    def test_explicit_caption_rejects_omission(self):
        with self.assertRaises(ValueError):
            editorial_subtitles(self.rows,['甲乙丙丁'],self.m['durationUs'])


class BrowserReleaseTests(unittest.TestCase):
    """Real Chromium/file:// regression. Synthetic audio proves signal only, not narration quality."""
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.base=Path(cls.temp.name)
        m,s,rows,plan=fixture()
        for name,value in [('scene.json',s),('rows.json',rows),('captions.json',[''.join(r['Char'] for r in rows[i:i+6]) for i in range(0,len(rows),6)]),('sfx.json',dict(version=1,events=[dict(timeUs=1000000,source='assets/sounds/click.wav',gain=.2),dict(timeUs=3000000,source='assets/sounds/ding.wav',gain=.2),dict(timeUs=4500000,source='assets/sounds/chime.wav',gain=.2)]))]:
            (cls.base/name).write_text(json.dumps(value,ensure_ascii=False),encoding='utf-8')
        (cls.base/'script.txt').write_text(''.join(r['Char'] for r in rows),encoding='utf-8')
        with wave.open(str(cls.base/'voice.wav'),'wb') as wav:
            wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(16000)
            wav.writeframes(b''.join(struct.pack('<h',round(math.sin(i/16000*math.tau*440)*5000)) for i in range(96000)))
        from scripts.build_fast_project import preset_wave
        for kind in ['click','ding','chime']:
            sound=cls.base/f'assets/sounds/{kind}.wav';sound.parent.mkdir(parents=True,exist_ok=True);preset_wave(sound,kind)
        cls.project=cls.base/'project'
        build(SimpleNamespace(scene=cls.base/'scene.json',out=cls.project,runtime=runtime_root(),title='测试知识动画',
            width=1080,height=1920,duration_us=None,voice=cls.base/'voice.wav',timestamps=cls.base/'rows.json',
            script=cls.base/'script.txt',caption_groups=cls.base/'captions.json',sfx=cls.base/'sfx.json',skip_browser_audit=True))
        (cls.project/'quality-plan.json').write_text(json.dumps(plan,ensure_ascii=False),encoding='utf-8')
        cls.report=run_gate(cls.project)

    def test_hud_is_positioned_and_player_replay_checks_pass(self):
        self.assertEqual(self.report['errors'],[])
        self.assertAlmostEqual(self.report['devHud']['left'],.04,places=2)
        self.assertAlmostEqual(self.report['devHud']['top'],.032,places=2)

    def test_progress_controls_are_visible_and_keep_mobile_video_clear(self):
        self.assertEqual(self.report['errors'],[])
        self.assertEqual([p['viewport'] for p in self.report['progressControls']],['320x640','440x956'])
        for sample in self.report['progressControls']:
            boxes=sample['boxes']
            self.assertGreaterEqual(boxes['#controls']['y'],boxes['canvas']['y']+boxes['canvas']['height'])
            self.assertGreaterEqual(boxes['#seek']['height'],44)

    def test_missing_visible_progress_is_rejected(self):
        from scripts.quality_browser import inspect_browser
        target=self.project/'index.html';original=target.read_bytes()
        try:
            target.write_text(original.decode('utf-8').replace('id="seek"','id="removed-seek"'),encoding='utf-8')
            result=inspect_browser(self.project,read_json(self.project/'vibe.project.json'),read_json(self.project/'scene.json'),read_json(self.project/'quality-plan.json'),Path(self.report['evidenceRoot']))
            self.assertEqual(result['browserErrors'][0]['rule'],'RUNTIME')
            self.assertEqual(result['screenshots'],[])
        finally:target.write_bytes(original)

    def test_removing_hud_is_rejected_before_browser_execution(self):
        from scripts.quality_browser import inspect_browser
        target=self.project/'index.html';original=target.read_bytes()
        try:
            target.write_text(original.decode('utf-8').replace('id="chapText"','id="removed-hud"'),encoding='utf-8')
            result=inspect_browser(self.project,read_json(self.project/'vibe.project.json'),read_json(self.project/'scene.json'),read_json(self.project/'quality-plan.json'),Path(self.report['evidenceRoot']))
            self.assertEqual(result['browserErrors'][0]['rule'],'RUNTIME')
            self.assertEqual(result['screenshots'],[])
        finally:target.write_bytes(original)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_browser_voice_signal_and_coverage(self):
        self.assertEqual(self.report['errors'],[])
        self.assertEqual(self.report['status'],'needs_review')
        self.assertTrue(any(l['kind']=='voice' and l['rms']>.001 for l in self.report['audioLevels']))
        self.assertTrue(any(s['viewport']=='440x956' for s in self.report['screenshots']))
        self.assertGreaterEqual(len(self.report['screenshots']),6)

    def test_missing_review_blocks_release(self):
        self.assertTrue(validate_review(self.project,self.report))

    def test_full_release_without_review_is_blocked(self):
        result=run_gate(self.project,release=True)
        self.assertEqual(result['status'],'blocked')
        self.assertTrue(any(e['rule']=='REVIEW' for e in result['errors']))

    def test_pending_or_stale_review_blocks(self):
        review=dict(version=1,status='pending',reviewer='',inputFingerprint='old',evidenceDigest='old',checks={},scenes=[])
        (self.project/'quality-review.json').write_text(json.dumps(review),encoding='utf-8')
        try:
            self.assertGreaterEqual(len(validate_review(self.project,self.report)),4)
        finally:
            (self.project/'quality-review.json').unlink()

    def test_review_schema_accepts_explicit_fixture_record_and_rejects_missing_evidence(self):
        # This is fabricated TEST DATA for schema validation, never a product signoff.
        review=dict(version=1,status='passed',reviewer='schema-test-fixture',inputFingerprint=self.report['inputFingerprint'],
            evidenceDigest=self.report['evidenceDigest'],checks={key:dict(status='passed',observations='Synthetic test record for validator behavior only') for key in REVIEW_CHECKS},
            scenes=[dict(sceneId='test-scene',status='passed',observations='Synthetic scene record for validator behavior only',
                         evidence=[self.report['screenshots'][0]['file']])])
        path=self.project/'quality-review.json'
        try:
            path.write_text(json.dumps(review),encoding='utf-8')
            self.assertEqual(validate_review(self.project,self.report),[])
            review['scenes'][0]['evidence']=['not-a-current-screenshot.png']
            path.write_text(json.dumps(review),encoding='utf-8')
            self.assertTrue(validate_review(self.project,self.report))
            review['scenes'][0]['evidence']=[self.report['screenshots'][0]['file']]
            path.write_text(json.dumps(review),encoding='utf-8')
            from scripts.quality_gate import report_directory
            shot=Path(self.report['evidenceRoot'])/self.report['screenshots'][0]['file']
            original=shot.read_bytes()
            try:
                shot.write_bytes(b'changed screenshot')
                self.assertTrue(any('Screenshot' in e['detail'] for e in validate_review(self.project,self.report)))
            finally:
                shot.write_bytes(original)
        finally:
            path.unlink()

    def test_changed_plan_invalidates_fingerprint(self):
        path=self.project/'quality-plan.json';original=path.read_bytes()
        try:
            plan=read_json(path);plan['scenes'][0]['purpose']='changed meaning'
            path.write_text(json.dumps(plan),encoding='utf-8')
            self.assertNotEqual(input_fingerprint(self.project),self.report['inputFingerprint'])
        finally:
            path.write_bytes(original)

    def test_local_file_voice_regression_is_detected(self):
        from scripts.quality_browser import inspect_browser
        from scripts.quality_gate import report_directory
        path=self.project/'index.html';original=path.read_text(encoding='utf-8')
        try:
            import re
            path.write_text(re.sub(r'<audio src="data:audio/wav;base64,[^"]+"','<audio src="assets/voice.wav"',original),encoding='utf-8')
            m=read_json(self.project/'vibe.project.json');s=read_json(self.project/'scene.json');p=read_json(self.project/'quality-plan.json')
            report=inspect_browser(self.project,m,s,p,report_directory(self.project))
            self.assertTrue(any(e['rule']=='RUNTIME' for e in report['browserErrors']))
        finally:
            path.write_text(original,encoding='utf-8')

    def test_actual_vector_escape_and_collision_are_detected(self):
        from scripts.quality_browser import inspect_browser
        from scripts.quality_gate import report_directory
        path=self.project/'index.html';original=path.read_text(encoding='utf-8')
        scene_path=self.project/'scene.json';original_scene=scene_path.read_bytes()
        try:
            scene=read_json(scene_path)
            scene['scenes'][0]['nodes'][1]['path']='M-40 -40 L200 20 L110 180 Z'
            scene['scenes'][0]['nodes'][-1]['y']=1120
            scene_path.write_text(json.dumps(scene),encoding='utf-8')
            from scripts.preview_template import canonical_html
            path.write_text(canonical_html(self.project,read_json(self.project/'vibe.project.json')),encoding='utf-8')
            report=inspect_browser(self.project,read_json(self.project/'vibe.project.json'),scene,
                read_json(self.project/'quality-plan.json'),report_directory(self.project))
            self.assertTrue(any(e['rule']=='GEOMETRY' for e in report['browserErrors']))
            self.assertTrue(any(e['rule']=='COLLISION' for e in report['browserErrors']))
        finally:
            path.write_text(original,encoding='utf-8');scene_path.write_bytes(original_scene)


if __name__=='__main__':
    unittest.main()
