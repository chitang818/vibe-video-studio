import copy
import importlib.util
import json
import os
import re
import tempfile
import unittest
from pathlib import Path
from playwright.sync_api import sync_playwright


class BackgroundSourceTests(unittest.TestCase):
    def setUp(self):
        self.root=Path(os.environ.get('VIBE_BG_SOURCE_ROOT','assets/runtime'))
        spec=importlib.util.spec_from_file_location('test_bg_builder',self.root/'build_runtime.py')
        self.builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.builder)

    def test_bundle_is_self_contained_and_reproducible(self):
        self.assertEqual(self.builder.compile_runtime(self.root),self.builder.compile_runtime(self.root))
        self.builder.verify(self.root)
        source=(self.root/'scene.mjs').read_text(encoding='utf-8')
        self.assertNotRegex(source,r'(?m)^import ')
        self.assertEqual(self.builder.catalog(self.root)['libraryVersion'],'1.0.0')

    def test_edited_recipe_requires_new_locked_version(self):
        import shutil
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            for p in self.builder.source_paths(self.root):
                dest=root/p.relative_to(self.root);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
            path=root/'backgrounds/catalog.json';data=json.loads(path.read_text(encoding='utf-8'));data['presets'][0]['recipe']['nearCount']+=1;path.write_text(json.dumps(data),encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'version lock'):self.builder.compile_runtime(root)

    def test_stale_generated_bundle_is_rejected(self):
        import shutil
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            for p in self.builder.source_paths(self.root):
                dest=root/p.relative_to(self.root);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
            (root/'scene.mjs').write_bytes(self.builder.compile_runtime(root)+b'\n// changed')
            with self.assertRaisesRegex(ValueError,'stale'):self.builder.verify(root)

    def test_recipe_keys_must_be_used_by_renderer(self):
        import shutil
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            for p in self.builder.source_paths(self.root):
                dest=root/p.relative_to(self.root);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
            path=root/'backgrounds/catalog.json';data=json.loads(path.read_text(encoding='utf-8'));data['presets'][0]['recipe']['fakeStyle']=1;path.write_text(json.dumps(data),encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'actual renderer use'):self.builder.compile_runtime(root)


class BackgroundRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=sync_playwright().start();cls.browser=cls.p.chromium.launch()
        root=Path(os.environ.get('VIBE_BG_SOURCE_ROOT','assets/runtime'))
        cls.page=cls.browser.new_page();cls.page.set_content('<canvas width="270" height="480"></canvas>')
        cls.page.add_script_tag(content=re.sub(r'(?m)^export ','',(root/'scene.mjs').read_text(encoding='utf-8')))

    @classmethod
    def tearDownClass(cls):cls.browser.close();cls.p.stop()

    def test_all_presets_are_pixel_identical_to_frozen_v16_baseline(self):
        old=self.browser.new_page();old.set_content('<canvas width="270" height="480"></canvas>')
        old.add_script_tag(content=re.sub(r'(?m)^export ','',Path('tests/fixtures/background-runtime-1.1.2.mjs').read_text(encoding='utf-8')))
        probe='''()=>{const c=document.querySelector('canvas'),x=c.getContext('2d'),result={};for(const id of ['bio-bubbles','constellation','dna-spiral','cyber-grid','aurora-dust'])for(const seed of [1,8])for(const time of [0,4,30,80]){x.fillStyle='#071d1b';x.fillRect(0,0,270,480);drawBackground(x,{preset:id,seed},time*1e6,270,480);result[id+'/'+seed+'/'+time]=c.toDataURL();}return result;}'''
        try:
            before=old.evaluate(probe);after=self.page.evaluate(probe)
            for key in before:self.assertTrue(before[key]==after[key],'Visual refactor changed '+key)
        finally:old.close()

    def test_catalog_is_deeply_frozen_and_cannot_be_reconfigured(self):
        result=self.page.evaluate('''()=>{const p=getBackgroundPreset('bio-bubbles');return {list:Object.isFrozen(BACKGROUND_CATALOG),recipe:Object.isFrozen(p.recipe),qa:Object.isFrozen(p.qa),id:p.id};}''')
        self.assertTrue(result['list'] and result['recipe'] and result['qa'])

    def test_unknown_template_and_revision_are_rejected(self):
        with self.assertRaisesRegex(Exception,'Unknown background'):self.page.evaluate("getBackgroundPreset('unknown')")
        with self.assertRaisesRegex(Exception,'version mismatch'):
            self.page.evaluate("validateScene({background:{preset:'bio-bubbles',templateVersion:'9.9.9'},scenes:[{id:'s',startUs:0,endUs:1000000,nodes:[{id:'r',type:'rect',x:100,y:300,width:10,height:10}]}]},{width:1080,height:1920,durationUs:1000000})")

    def test_per_style_qa_regions_are_visible(self):
        result=self.page.evaluate('''()=>{const c=document.querySelector('canvas'),x=c.getContext('2d'),result=[];
          for(const e of BACKGROUND_CATALOG.filter(e=>e.qa.dynamic))for(const time of [0,4,15]){
            x.fillStyle='#071d1b';x.fillRect(0,0,270,480);drawBackground(x,{preset:e.id,seed:8},time*1e6,270,480);const pixels=x.getImageData(0,0,270,480).data,qa=e.qa,cells=Array(qa.columns*qa.rows).fill(0),regions=qa.regions.map(()=>0);
            for(let y=0;y<480;y++)for(let xx=0;xx<270;xx++){const i=(y*270+xx)*4;if(Math.abs(pixels[i]-7)+Math.abs(pixels[i+1]-29)+Math.abs(pixels[i+2]-27)<=12)continue;cells[Math.floor(y/(480/qa.rows))*qa.columns+Math.floor(xx/(270/qa.columns))]++;qa.regions.forEach((r,j)=>{const [a,b,w,h]=r.box;if(xx>=a*270&&xx<(a+w)*270&&y>=b*480&&y<(b+h)*480)regions[j]++;});}
            result.push({id:e.id,time,covered:cells.filter(n=>n>=qa.minPixelsPerCell).length,required:qa.minCoveredCells,regions:regions.map((n,j)=>({actual:n,required:qa.regions[j].minPixels}))});
          }return result;}''')
        for row in result:
            self.assertGreaterEqual(row['covered'],row['required'],str(row))
            for region in row['regions']:self.assertGreaterEqual(region['actual'],region['required'],str(row))


class BackgroundCompilerTests(unittest.TestCase):
    def test_forged_scene_recipe_identity_is_rejected(self):
        from scripts.components import compile_story
        from scripts.quality_gate import static_checks
        from tests.test_presentation import fixture
        story,rows,duration=fixture();scene,plan=compile_story(story,rows,duration)
        scene['background']['recipeSha256']='0'*64
        rules={e['rule'] for e in static_checks(dict(width=1080,height=1920,durationUs=duration,title=story['title']),scene,rows,plan)}
        self.assertIn('BACKGROUND_IDENTITY',rules)

    def test_compiler_pins_actual_template_version_and_recipe(self):
        from scripts.components import compile_story
        from scripts.background_library import preset
        from tests.test_presentation import fixture
        story,rows,duration=fixture();scene,_=compile_story(story,rows,duration);expected=preset('bio-bubbles')
        self.assertEqual(scene['background']['templateVersion'],expected['version'])
        self.assertEqual(scene['background']['recipeSha256'],expected['recipeSha256'])
        story['backgroundTemplateVersion']='9.0.0'
        with self.assertRaisesRegex(ValueError,'version'):compile_story(story,rows,duration)
        story.pop('backgroundTemplateVersion');story['backgroundDensity']=50
        with self.assertRaisesRegex(ValueError,'unknown'):compile_story(story,rows,duration)

    def test_helix_does_not_require_full_width_but_requires_both_strands(self):
        from scripts.background_library import preset,background_errors
        entry=preset('dna-spiral')
        probe=dict(visiblePixels=1000,changedPixels=1000,coverage=[dict(coveredCells=6,regions=[dict(name='left-strand',visiblePixels=100),dict(name='right-strand',visiblePixels=0)])])
        errors=background_errors(probe,entry)
        self.assertTrue(any(rule=='BACKGROUND_REGION' for rule,_ in errors))
        probe['coverage'][0]['regions'][1]['visiblePixels']=100
        self.assertEqual(background_errors(probe,entry),[])


class BackgroundGalleryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from scripts.background_library import gallery
        cls.temp=tempfile.TemporaryDirectory();cls.path=gallery(Path(cls.temp.name)/'gallery')
        cls.p=sync_playwright().start();cls.browser=cls.p.chromium.launch()

    @classmethod
    def tearDownClass(cls):cls.browser.close();cls.p.stop();cls.temp.cleanup()

    def setUp(self):
        self.page=self.browser.new_page(viewport=dict(width=1100,height=900));self.errors=[];self.requests=[]
        self.page.on('pageerror',lambda e:self.errors.append(str(e)));self.page.on('request',lambda r:self.requests.append(r.url))
        self.page.goto(self.path.as_uri());self.page.wait_for_function('window.__galleryReady===true')

    def tearDown(self):self.page.close()

    def test_all_templates_overlay_switching_and_reverse_seek(self):
        from scripts.background_library import catalog
        self.page.locator('#play').click()
        for entry in catalog():
            self.page.select_option('#preset',entry['id']);self.page.wait_for_function('id=>window.__galleryReady&&window.__galleryScene.background.preset===id',arg=entry['id'])
            self.page.evaluate('window.__gallerySeek(4)');a=self.page.locator('canvas').screenshot()
            self.page.evaluate('window.__gallerySeek(15)');self.page.evaluate('window.__gallerySeek(4)')
            self.assertEqual(a,self.page.locator('canvas').screenshot())
            self.page.locator('#overlay').uncheck();self.page.wait_for_function('window.__galleryReady');self.page.evaluate('window.__gallerySeek(4)')
            self.assertNotEqual(a,self.page.locator('canvas').screenshot())
            self.page.locator('#overlay').check();self.page.wait_for_function('window.__galleryReady')
        self.assertEqual(self.errors,[])

    def test_pause_time_and_native_keyboard_seek(self):
        self.page.locator('#play').click();self.page.evaluate('window.__gallerySeek(4)')
        before=self.page.locator('canvas').screenshot();self.page.wait_for_timeout(150)
        self.assertEqual(before,self.page.locator('canvas').screenshot())
        self.page.locator('#time').focus();self.page.keyboard.press('End')
        self.assertEqual(self.page.locator('#clock').inner_text(),'00:30')
        self.page.locator('#reset').click();self.assertEqual(self.page.locator('#clock').inner_text(),'00:00')

    def test_mobile_does_not_overflow_and_no_external_requests(self):
        for width in (320,440):
            self.page.set_viewport_size(dict(width=width,height=956))
            self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
        self.assertFalse(any(x.startswith(('http:','https:')) for x in self.requests))


if __name__=='__main__':unittest.main()
