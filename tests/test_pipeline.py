import copy
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import wave

from scripts import pipeline as p
from scripts.pipeline_contracts import check
from scripts.pipeline_svg import sanitize

class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name);self.root=self.base/'project'
        self.rows=[dict(Char=c,StartSeconds=i*.25,EndSeconds=(i+1)*.25) for i,c in enumerate('甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午未申酉戌亥天地')]
        p.write(self.base/'rows.json',self.rows);(self.base/'script.txt').write_text(''.join(r['Char'] for r in self.rows),encoding='utf-8')
        p.write(self.base/'style.json',dict(version=1,title='网页知识测试',authorId='test',backgroundPreset='bio-bubbles',protectedTerms=[]))
        with wave.open(str(self.base/'voice.wav'),'wb') as audio:audio.setnchannels(1);audio.setsampwidth(2);audio.setframerate(8000);audio.writeframes(b'\0\0'*48000)
        self.args=SimpleNamespace(project=self.root,voice=self.base/'voice.wav',timestamps=self.base/'rows.json',script=self.base/'script.txt',style=self.base/'style.json',captions=None)
        self.shots=dict(version=1,shots=[dict(id='one',startIndex=0,endIndex=12,goal='理解第一个观点',relation='focus',reason='前半原文围绕一个论点',beats=[dict(index=1,quote='乙',purpose='展示第一个重点'),dict(index=6,quote='庚',purpose='补充说明内容')]),dict(id='two',startIndex=12,endIndex=24,goal='理解第二个观点',relation='cause',reason='后半原文转到后续结果',beats=[dict(index=13,quote='卯',purpose='展示后续变化'),dict(index=18,quote='申',purpose='明确相关结果')])])

    def intake(self):p.intake(self.args);return p.load_state(self.root)
    def submit(self,state,name,value):
        f=self.base/(name+'.json');p.write(f,value);return getattr(p,name)(self.root,state,f)
    def segment(self):
        state=self.intake();self.submit(state,'segment',self.shots);return state
    def direct(self):
        state=self.segment();briefs=[]
        for shot in self.shots['shots']:
            briefs.append(dict(shotId=shot['id'],focus=shot['goal'],composition='大字与解释构成视觉层级',rationale='观点表达采用文字与留白',opening='标题先建立阅读方向',development='按真实口播展示重点',ending='保留结论方便阅读',continuity='共用主题与背景保持一致',constraints=['不增加文案事实与数字'],assetRequests=[],sketch=[dict(slot='hero',label='核心观点',form='text')]))
        self.submit(state,'direct',dict(version=1,briefs=briefs));return state
    def spec(self):
        return dict(version=1,scenes=[dict(shotId=s['id'],family='typography',reason='文字承载本镜核心观点',elements=[dict(id='claim',kind='text',slot='hero',index=s['beats'][0]['index'],text='核心观点',entrance='zoom'),dict(id='note',kind='text',slot='hero-label',index=s['beats'][1]['index'],text='解释关系',entrance='fade-up')]) for s in self.shots['shots']])

    def test_intake_preserves_originals_and_reports_mismatch(self):
        state=self.intake();self.assertEqual(p.stage_status(self.root,state,'intake'),'ready')
        self.assertEqual((self.root/'sources/voice.wav').read_bytes(),self.args.voice.read_bytes())
        other=self.base/'bad';self.args.project=other;self.args.script.write_text('错误识别',encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'mismatch'):p.intake(self.args)
        self.assertEqual(p.load_state(other)['stages']['intake']['status'],'blocked')
        self.assertTrue(list(other.glob('runs/intake-*/alignment.json')))

    def test_exact_coverage_quotes_and_duplicate_ids(self):
        for mode in ('gap','duplicate','quote','equal-time'):
            with self.subTest(mode=mode):
                state=self.intake() if not self.root.exists() else p.load_state(self.root)
                bad=copy.deepcopy(self.shots)
                if mode=='gap':bad['shots'][1]['startIndex']=13
                if mode=='duplicate':bad['shots'][1]['id']='one'
                if mode=='quote':bad['shots'][0]['beats'][0]['quote']='不存在'
                if mode=='equal-time':bad['shots'][0]['endIndex']=0
                with self.assertRaises(ValueError):self.submit(state,'segment',bad)

    def test_briefs_unknown_fields_and_missing_stage_rejected(self):
        state=self.intake()
        with self.assertRaisesRegex(ValueError,'segment'):p.direct(self.root,state)
        with self.assertRaisesRegex(ValueError,'unknown'):check('shots',dict(self.shots,css='evil'))

    def test_source_tool_and_artifact_changes_invalidate(self):
        state=self.segment();self.assertEqual(p.stage_status(self.root,state,'segment'),'ready')
        path=self.root/state['stages']['segment']['result'];raw=path.read_bytes();path.write_bytes(raw+b' ')
        self.assertEqual(p.stage_status(self.root,state,'segment'),'stale');path.write_bytes(raw)
        with patch.object(p,'tool_identity',return_value={'new-tool':'hash'}):self.assertEqual(p.stage_status(self.root,state,'intake'),'stale')
        (self.root/'sources/script.txt').write_text('changed',encoding='utf-8')
        self.assertEqual(p.stage_status(self.root,state,'segment'),'stale')

    def test_refresh_and_request_revision_history(self):
        state=self.segment();old=state['stages']['intake']['result']
        p.refresh(self.root,state)
        self.assertNotEqual(old,state['stages']['intake']['result'])
        self.assertTrue((self.root/old).exists())
        self.assertEqual(p.stage_status(self.root,state,'segment'),'stale')
        p.segment(self.root,state)
        self.assertEqual(p.stage_status(self.root,state,'segment'),'ready')

    def test_single_shot_rework_reuses_other_and_blocks_assembly(self):
        state=self.direct();spec=self.spec();path=self.base/'impl.json';p.write(path,spec)
        with patch.object(p,'preview_check'):
            first=p.produce(self.root,state,path);self.assertEqual(first['produced'],['one','two'])
            old=copy.deepcopy(state['shots']['two'])
            spec['scenes'][0]['elements'][0]['text']='改变一个重点';p.write(path,spec)
            result=p.produce(self.root,state,path,only='one')
            self.assertEqual(result['produced'],['one']);self.assertEqual(result['reused'],['two']);self.assertEqual(old,state['shots']['two'])
            spec['scenes'][1]['elements'][0]['text']='改变另一个重点';p.write(path,spec)
            result=p.produce(self.root,state,path,only='one');self.assertEqual(result['remaining'],['two'])
            with self.assertRaisesRegex(ValueError,'produce'):p.assemble(self.root,state)

    def test_preview_data_and_assembly_scene_identity(self):
        state=self.direct();path=self.base/'impl.json';p.write(path,self.spec())
        with patch.object(p,'preview_check'):p.produce(self.root,state,path)
        p.assemble(self.root,state)
        project=self.root/p.output(self.root,state['stages']['assemble'])['project']
        doc=p.read(project/'scene.json')
        self.assertEqual(doc['scenes'],[p.output(self.root,state['shots'][s['id']])['scene'] for s in self.shots['shots']])
        self.assertEqual((project/'assets/voice.wav').read_bytes(),self.args.voice.read_bytes())
        self.assertIn('assets/production-provenance.json',p.read(project/'vibe.project.json')['assetHashes'])

    def test_window_preview_matches_assembled_render_pixels(self):
        from playwright.sync_api import sync_playwright
        state=self.direct();path=self.base/'impl.json';p.write(path,self.spec())
        p.produce(self.root,state,path);p.assemble(self.root,state)
        full=self.root/p.output(self.root,state['stages']['assemble'])['project']/'index.html'
        single=(self.root/state['shots']['two']['result']).parent/'index.html'
        with sync_playwright() as pw:
            browser=pw.chromium.launch()
            try:
                a=browser.new_page();b=browser.new_page()
                for page,file in ((a,single),(b,full)):
                    page.goto(file.as_uri());page.evaluate('()=>window.__vibe_ready')
                for seconds in (.1,1.25,2.75):
                    a.evaluate('(t)=>window.__vibe_seekTo(t)',seconds);b.evaluate('(t)=>window.__vibe_seekTo(t)',seconds+3)
                    self.assertEqual(a.locator('canvas').screenshot(),b.locator('canvas').screenshot())
            finally:browser.close()

    def test_lock_and_dashboard_escape(self):
        state=self.direct()
        with p.locked(self.root):
            with self.assertRaisesRegex(ValueError,'active'):
                with p.locked(self.root):pass
        data=p.output(self.root,state['stages']['direct']);data['briefs'][0]['focus']='<script>alert(1)</script>'
        p.write(self.root/state['stages']['direct']['result'],data);p.inspect(self.root,state)
        text=(self.root/'index.html').read_text(encoding='utf-8');self.assertNotIn('<script>alert',text);self.assertIn('&lt;script&gt;',text)

    def test_svg_subset_rejects_active_external_and_unbounded_content(self):
        allowed=b'<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512"><circle cx="256" cy="256" r="100" fill="#65efb5"/></svg>'
        self.assertEqual(sanitize(allowed)[1],[512,512])
        for bad in (allowed.replace(b'<circle',b'<script'),allowed.replace(b'fill="#65efb5"',b'fill="url(http://evil)"'),allowed.replace(b'<circle',b'<image href="http://evil"'),allowed.replace(b'512',b'999999'),b'<!DOCTYPE svg>'+allowed):
            with self.assertRaises((ValueError,Exception)):sanitize(bad)

    def test_svg_import_keeps_alpha_and_source(self):
        from scripts.media_assets import import_image
        from PIL import Image
        svg=self.base/'shape.svg';svg.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512"><circle cx="256" cy="256" r="100" fill="#65efb5"/></svg>')
        entry=import_image(svg,self.base/'assets-root','circle','local','Original test artwork','original')
        with Image.open(self.base/'assets-root'/entry['source']) as image:self.assertEqual(image.getchannel('A').getextrema(),(0,255))
        self.assertTrue((self.base/'assets-root/assets/sources/circle.svg').exists())
