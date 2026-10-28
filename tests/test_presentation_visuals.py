"""Visual regressions for the reported lost backgrounds, off-centre ink and page ghosts."""
import copy
import os
import re
import unittest
from pathlib import Path
from playwright.sync_api import sync_playwright
from scripts.components import compile_story
from tests.test_presentation import fixture


class PresentationVisualTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=sync_playwright().start();cls.browser=cls.p.chromium.launch();cls.page=cls.browser.new_page()
        cls.page.set_content('<canvas id="main"></canvas>')
        source=Path(os.environ.get('VIBE_REPAIR_RUNTIME','assets/runtime/scene.mjs')).read_text(encoding='utf-8')
        cls.page.add_script_tag(content=re.sub(r'(?m)^export ','',source))

    @classmethod
    def tearDownClass(cls):cls.browser.close();cls.p.stop()

    def test_five_backgrounds_are_distinct_visible_and_seek_deterministic(self):
        signatures=[]
        for preset in ['bio-bubbles','constellation','dna-spiral','cyber-grid','aurora-dust']:
            with self.subTest(preset=preset):
                result=self.page.evaluate('''preset=>{
                    const c=document.querySelector('canvas');c.width=540;c.height=960;const ctx=c.getContext('2d');
                    const frame=t=>{ctx.fillStyle='#071d1b';ctx.fillRect(0,0,540,960);drawBackground(ctx,{preset,seed:8},t,540,960);return c.toDataURL();};
                    const a=frame(0),initial=ctx.getImageData(0,0,540,960).data,b=frame(4000000),last=ctx.getImageData(0,0,540,960).data;
                    let visible=0,moving=0;for(let i=0;i<last.length;i+=4){if(Math.abs(initial[i]-7)+Math.abs(initial[i+1]-29)+Math.abs(initial[i+2]-27)>12)visible++;if(Math.abs(initial[i]-last[i])+Math.abs(initial[i+1]-last[i+1])+Math.abs(initial[i+2]-last[i+2])>12)moving++;}
                    return {a,b,repeat:frame(0),visible,moving};
                }''',preset)
                self.assertGreater(result['visible'],300)
                self.assertGreater(result['moving'],300)
                self.assertEqual(result['a'],result['repeat'])
                self.assertNotEqual(result['a'],result['b']);signatures.append(result['b'])
        self.assertEqual(len(set(signatures)),5)

    def test_explicit_solid_and_bad_background(self):
        story,rows,duration=fixture();story['backgroundPreset']='solid'
        scene,plan=compile_story(story,rows,duration)
        self.assertEqual(scene['background']['preset'],'solid')
        story['backgroundPreset']='unimplemented-preset'
        with self.assertRaises(ValueError):compile_story(story,rows,duration)

    def test_compiler_centres_title_heading_and_content(self):
        for layout in ['statement','cards','comparison','steps']:
            story,rows,duration=fixture(layout);scene,_=compile_story(story,rows,duration)
            for n in scene['scenes'][0]['nodes']:
                if n['type']!='text':continue
                self.assertEqual(n['align'],'center')
                self.assertAlmostEqual(n['x']+n['width']/2,540)
                ink=self.page.evaluate('n=>prepareTextLayer(n,1080).inkRects',n)
                for b in ink:self.assertAlmostEqual(b['x']+b['width']/2,n['width']/2,delta=1)
                top=min(b['y'] for b in ink);bottom=max(b['y']+b['height'] for b in ink)
                self.assertAlmostEqual((top+bottom)/2,n['height']/2,delta=1)

    def test_explicit_left_alignment_is_available(self):
        story,rows,duration=fixture();story['contentAlign']='left'
        scene,plan=compile_story(story,rows,duration)
        self.assertEqual(plan['contentAlign'],'left')
        n=next(n for n in scene['scenes'][0]['nodes'] if n['id']=='heading')
        self.assertEqual(n['align'],'left')

    def test_step_marker_and_text_share_vertical_centre(self):
        story,rows,duration=fixture('steps');scene,_=compile_story(story,rows,duration)
        nodes={n['id']:n for n in scene['scenes'][0]['nodes']}
        for j in (1,2):
            marker=nodes[f'bullet-{j}'];text=nodes[f'item-{j}']
            self.assertAlmostEqual(marker['y']+marker['height']/2,text['y']+text['height']/2)

    def test_cut_never_draws_old_text_after_new_page_begins(self):
        for transition in ['fade','push']:
            nodes=[dict(id='heading',type='text',x=130,y=440,width=820,height=92,text='旧页标题',size=58,color='#ff3939',align='center',verticalAlign='center')]
            first=dict(id='old',startUs=0,endUs=6000000,nodes=nodes)
            second=copy.deepcopy(first);second.update(id='new',startUs=6000000,endUs=12000000,transition=transition)
            second['nodes'][0].update(text='新页标题',color='#3999ff')
            scene=dict(background=dict(color='#071d1b',preset='solid'),scenes=[first,second])
            result=self.page.evaluate('''async scene=>{
                const c=document.querySelector('canvas'),r=await prepareScene(c,scene,{width:1080,height:1920,durationUs:12000000,assetBase:location.href,safeArea:true});
                const colors=t=>{r.renderAt(t);const p=c.getContext('2d').getImageData(0,0,1080,1920).data;let red=0,blue=0;for(let i=0;i<p.length;i+=4){if(p[i]>p[i+1]+20&&p[i]>p[i+2]+20)red++;if(p[i+2]>p[i]+30&&p[i+2]>p[i+1]+30)blue++;}return {red,blue};};
                return {before:colors(5900000),after:[6050000,6100000,6200000,6300000].map(colors),selected:pageTransitionAt(scene,6100000)};
            }''',scene)
            self.assertGreater(result['before']['red'],100)
            self.assertEqual(result['before']['blue'],0)
            self.assertTrue(all(x['red']==0 for x in result['after']))
            self.assertGreater(result['after'][-1]['blue'],100)
            self.assertEqual(result['selected']['sceneId'],'new')

    def test_default_bio_and_vertical_entrances_are_retained(self):
        story,rows,duration=fixture();scene,_=compile_story(story,rows,duration)
        self.assertEqual(scene['background']['preset'],'bio-bubbles')
        for n in scene['scenes'][0]['nodes']:
            if n['type']=='text':self.assertNotIn(n.get('entrance'),('slide-left','slide-right'))

    def test_background_probe_rejects_metadata_without_renderer(self):
        from scripts.quality_browser import BACKGROUND_PROBE
        self.page.evaluate('''()=>{
          window.__vibe_scene={background:{color:'#071d1b',preset:'bio-bubbles',seed:8}};
          window.config={durationUs:6000000,assetBase:location.href};
          const c=document.querySelector('canvas');c.width=1080;c.height=1920;
        }''')
        real=self.page.evaluate(BACKGROUND_PROBE)
        self.assertGreater(real['changedPixels'],64)
        self.page.evaluate('window.savedBackground=drawBackground;drawBackground=()=>{}')
        try:
            broken=self.page.evaluate(BACKGROUND_PROBE)
            self.assertEqual(broken['preset'],'bio-bubbles')
            self.assertEqual(broken['changedPixels'],0)
        finally:self.page.evaluate('drawBackground=window.savedBackground')

    def test_bio_background_covers_canvas_across_seeds_and_times(self):
        results=self.page.evaluate('''()=>{
            const c=document.querySelector('canvas');c.width=270;c.height=480;const x=c.getContext('2d');const result=[];
            for(const seed of [1,8,42])for(const t of [0,4,30,80,159]){
                x.fillStyle='#071d1b';x.fillRect(0,0,270,480);drawBackground(x,{preset:'bio-bubbles',seed},t*1e6,270,480);
                const p=x.getImageData(0,0,270,480).data,cells=Array(24).fill(0);
                for(let y=0;y<480;y++)for(let xx=0;xx<270;xx++){const i=(y*270+xx)*4;if(Math.abs(p[i]-7)+Math.abs(p[i+1]-29)+Math.abs(p[i+2]-27)>12)cells[Math.floor(y/80)*4+Math.floor(xx/67.5)]++;}
                result.push({seed,t,covered:cells.filter(n=>n>=16).length,cells});
            }return result;
        }''')
        for r in results:
            self.assertGreaterEqual(r['covered'],20,str(r))

    def test_random_coordinate_streams_do_not_form_diagonal(self):
        correlation=self.page.evaluate('''()=>{
            const xs=[],ys=[];for(let i=0;i<80;i++){xs.push(seeded(8,i,1));ys.push(seeded(8,i,2));}
            const mx=xs.reduce((a,b)=>a+b)/80,my=ys.reduce((a,b)=>a+b)/80;
            let cov=0,vx=0,vy=0;for(let i=0;i<80;i++){cov+=(xs[i]-mx)*(ys[i]-my);vx+=(xs[i]-mx)**2;vy+=(ys[i]-my)**2;}
            return cov/Math.sqrt(vx*vy);
        }''')
        self.assertLess(abs(correlation),.3)

    def test_background_probe_distinguishes_local_motion_from_full_coverage(self):
        from scripts.quality_browser import BACKGROUND_PROBE
        self.page.evaluate('''()=>{
            window.__vibe_scene={background:{color:'#071d1b',preset:'bio-bubbles',seed:8}};
            window.config={durationUs:160000000,assetBase:location.href};
            const c=document.querySelector('canvas');c.width=1080;c.height=1920;
        }''')
        real=self.page.evaluate(BACKGROUND_PROBE)
        self.assertTrue(all(x['coveredCells']>=20 for x in real['coverage']))
        self.page.evaluate('''()=>{window.savedBackground=drawBackground;drawBackground=(ctx,bg,t)=>{ctx.fillStyle='#65efb5';ctx.fillRect(10+(t/1e6%8)*20,10,120,120);};}''')
        try:
            local=self.page.evaluate(BACKGROUND_PROBE)
            self.assertGreater(local['changedPixels'],64)
            self.assertTrue(all(x['coveredCells']<20 for x in local['coverage']))
        finally:self.page.evaluate('drawBackground=window.savedBackground')


if __name__=='__main__':unittest.main()
