"""Real Chromium glyph raster regressions, including the exact previous defect."""
import re
import unittest
from pathlib import Path
from playwright.sync_api import sync_playwright
from scripts.quality_browser import GEOMETRY


class TextRasterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=sync_playwright().start();cls.browser=cls.p.chromium.launch()
        cls.page=cls.browser.new_page()
        source=Path('assets/runtime/scene.mjs').read_text(encoding='utf-8')
        cls.page.set_content('<canvas width="1080" height="1920"></canvas>')
        cls.page.add_script_tag(content=re.sub(r'(?m)^export ','',source))
        cls.page.evaluate('document.fonts.load(\'700 48px "Microsoft YaHei"\')')

    @classmethod
    def tearDownClass(cls):cls.browser.close();cls.p.stop()

    def probe(self,text,size=48,width=800,height=90,align='center',bold=True,damage=False,legacy=False):
        self.page.evaluate('''({text,size,width,height,align,bold,damage,legacy})=>{
          const n={id:'text',type:'text',x:140,y:440,width,height,text,size,align,bold,color:'#65efb5'};
          window.__vibe_scene={scenes:[{id:'sample',nodes:[n]}]};
          const p=prepareTextLayer(n,1080);let raster=p.canvas.getContext('2d');
          if(legacy){raster.clearRect(0,0,width,height);raster.textBaseline='top';raster.fillText(text,0,0);}
          if(damage)raster.clearRect(0,0,width,12);
          window.__vibe_textRaster=()=>raster.getImageData(0,0,p.canvas.width,p.canvas.height);
        }''',dict(text=text,size=size,width=width,height=height,align=align,bold=bold,damage=damage,legacy=legacy))
        return self.page.evaluate(GEOMETRY)[0]

    def test_reported_chinese_cases_are_pixel_complete(self):
        for text,size in [('丛枝菌根作用与优势',48),('回顾：菌剂与菌根',58),('真菌类菌剂的分类',48),('肥料类菌剂中的菌根',48)]:
            with self.subTest(text=text):
                r=self.probe(text,size)
                self.assertFalse(r['glyphClipped']);self.assertEqual(r['glyphMismatchPixels'],0)
                self.assertGreaterEqual(r['actual']['y'],442)

    def test_old_top_baseline_cache_is_detected(self):
        r=self.probe('真菌类菌剂的分类',align='left',legacy=True)
        self.assertTrue(r['glyphClipped']);self.assertGreater(r['glyphMismatchPixels'],0)

    def test_real_cache_damage_is_detected_even_when_layout_is_correct(self):
        r=self.probe('真菌类菌剂的分类',damage=True)
        self.assertTrue(r['glyphClipped']);self.assertGreater(r['glyphMismatchPixels'],0)

    def test_diacritics_descenders_bold_and_regular(self):
        for bold in [False,True]:
            for text in ['ÁÉgjpqy Ångström','中文：菌根，养分。','e\u0301 A\u030a g\u0323','（菌根）【磷】50%']:
                with self.subTest(text=text,bold=bold):self.assertFalse(self.probe(text,bold=bold)['glyphClipped'])

    def test_multiline_and_automatic_wrap_have_complete_ink(self):
        for text in ['中文第一行\n养分交换第二行','中文第一行养分交换第二行']:
            r=self.probe(text,width=220,height=260)
            self.assertGreater(len(r['lines']),1);self.assertFalse(r['glyphClipped'])

    def test_left_bearings_and_common_font_sizes(self):
        for size in [36,43.2,46,58,64]:
            with self.subTest(size=size):self.assertFalse(self.probe('Ágj中文菌根',size=size,width=799.5,height=110,align='left')['glyphClipped'])

    def test_wrap_keeps_combining_mark_with_its_base(self):
        r=self.probe('e\u0301e\u0301e\u0301',width=50,height=250)
        self.assertEqual(r['lines'],['e\u0301']*3);self.assertFalse(r['glyphClipped'])

    def test_too_small_cache_fails_instead_of_clipping(self):
        with self.assertRaisesRegex(Exception,'Text ink overflows'):
            self.probe('真菌类菌剂的分类',height=30)

    def test_prepare_scene_uses_complete_cache_and_seeks_deterministically(self):
        r=self.page.evaluate('''async()=>{
          const node={id:'text',type:'text',x:140,y:440,width:800,height:90,text:'真菌类菌剂的分类',size:48,color:'#65efb5'};
          const canvas=document.querySelector('canvas'),scene={background:{particles:false},scenes:[{id:'one',startUs:0,endUs:6000000,nodes:[node]}]};
          const renderer=await prepareScene(canvas,scene,{width:1080,height:1920,durationUs:6000000,safeArea:true});
          const actual=renderer.textRaster('one','text'),expected=prepareTextLayer(node,1080).canvas.getContext('2d').getImageData(0,0,800,90);
          let mismatch=0;for(let i=3;i<actual.data.length;i+=4)if(actual.data[i]!==expected.data[i])mismatch++;
          renderer.renderAt(1000000);const first=canvas.toDataURL();renderer.renderAt(5000000);renderer.renderAt(1000000);
          return {mismatch,deterministic:first===canvas.toDataURL()};
        }''')
        self.assertEqual(r['mismatch'],0);self.assertTrue(r['deterministic'])
