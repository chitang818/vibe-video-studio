import copy
import json
import re
import tempfile
import unittest
from pathlib import Path
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
from scripts.components import compile_story
from scripts.contracts import validate_document,load_profile
from scripts.media_assets import import_image,validate_registry
from scripts.build_fast_project import editorial_subtitles
from scripts.quality_gate import static_checks


def fixture(layout='cards'):
    rows=[dict(Char=c,StartSeconds=i*.25,EndSeconds=(i+1)*.25) for i,c in enumerate('甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午未申酉戌亥天地')]
    s=dict(version=2,title='动态演示测试',authorId='test',scenes=[dict(id='page-one',layout=layout,heading='清晰的页面重点',items=[dict(text='先展示重点',anchor=dict(quote='戊')),dict(text='再解释内容',anchor=dict(quote='寅'))])])
    if layout in ('hero-image','image-text'):
        s['assets']=[dict(id='sample',source='assets/images/sample.png')];s['scenes'][0]['image']='sample'
    return s,rows,6000000


class PresentationCompilerTests(unittest.TestCase):
    def test_skill_routes_to_current_mode_and_all_links_exist(self):
        root=Path('.agents/skills/vibe-knowledge-video')
        text=(root/'SKILL.md').read_text(encoding='utf-8')
        self.assertIn('story version=2',text)
        self.assertIn('presentation-profile.json',text)
        for p in [root/'SKILL.md',*(root/'references').glob('*.md')]:
            for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
                self.assertTrue((p.parent/target.split('#')[0]).resolve().exists(),f'{p}: {target}')
        prompt=(root/'references/prompt-template.md').read_text(encoding='utf-8')
        self.assertNotIn('requestAnimationFrame',prompt)
        self.assertNotIn('禁止裸文字',(root/'references/storyboard-template.md').read_text(encoding='utf-8'))

    def test_all_layouts_and_schema(self):
        for layout in ('statement','hero-image','image-text','cards','comparison','steps'):
            with self.subTest(layout=layout):
                s,r,d=fixture(layout);scene,plan=compile_story(s,r,d)
                validate_document('scene',scene);validate_document('quality-plan',plan)
                self.assertEqual(plan['profile'],'presentation-portrait-v1')
                self.assertFalse(scene['background']['particles'])

    def test_reading_hold_and_text_only_are_valid(self):
        s,r,d=fixture('statement');scene,plan=compile_story(s,r,d)
        scene['subtitles']=editorial_subtitles(r,[''.join(x['Char'] for x in r[i:i+6]) for i in range(0,len(r),6)],d)
        self.assertEqual(static_checks(dict(width=1080,height=1920,durationUs=d,title=s['title']),scene,r,plan),[])

    def test_card_spacing_two_to_four_in_all_panel_layouts(self):
        for layout in ('cards','steps','comparison'):
            for count in ((2,) if layout=='comparison' else (2,3,4)):
                s,r,d=fixture(layout)
                s['scenes'][0]['items']=[dict(text='清晰要点',anchor=dict(quote=r[k]['Char'])) for k in (2,5,8,11)[:count]]
                scene,plan=compile_story(s,r,d)
                cards=[n for n in scene['scenes'][0]['nodes'] if n['id'].startswith('card-')]
                self.assertTrue(all(b['y']-a['y']-a['height']>=56 for a,b in zip(cards,cards[1:])))
                self.assertLessEqual(cards[-1]['y']+cards[-1]['height']+24,1920*.78)

    def test_touching_and_tiny_gaps_fail_even_with_renamed_panels(self):
        for gap in (0,4,31):
            s,r,d=fixture();scene,plan=compile_story(s,r,d)
            nodes={n['id']:n for n in scene['scenes'][0]['nodes']}
            delta=nodes['card-1']['y']+nodes['card-1']['height']+gap-nodes['card-2']['y']
            for nid in ('card-2','item-2'):nodes[nid]['y']+=delta
            nodes['card-2']['id']='renamed-surface'
            plan['scenes'][0]['roles']['panel'].remove('card-2');plan['scenes'][0]['roles']['panel'].append('renamed-surface')
            errors=static_checks(dict(width=1080,height=1920,durationUs=d,title=s['title']),scene,r,plan)
            self.assertIn('CARD_SPACING',{e['rule'] for e in errors})

    def test_no_image_is_not_silently_substituted(self):
        s,r,d=fixture('hero-image');del s['scenes'][0]['image']
        with self.assertRaisesRegex(ValueError,'requires'):compile_story(s,r,d)

    def test_unknown_asset_rejected(self):
        s,r,d=fixture('image-text');s['assets']=[]
        with self.assertRaisesRegex(ValueError,'Unknown image'):compile_story(s,r,d)

    def test_capacity_unknown_fields_and_false_quotes(self):
        for change in ('capacity','unknown','quote'):
            s,r,d=fixture('statement')
            if change=='capacity':s['scenes'][0]['items']*=2
            elif change=='unknown':s['scenes'][0]['css']='evil'
            else:s['scenes'][0]['items'][0]['anchor']['quote']='不存在'
            with self.subTest(change=change),self.assertRaises(ValueError):compile_story(s,r,d)

    def test_repeated_quote_requires_occurrence(self):
        s,r,d=fixture();r[8]['Char']='戊'
        with self.assertRaisesRegex(ValueError,'ambiguous'):compile_story(s,r,d)

    def test_emphasis_has_a_real_anchored_event(self):
        s,r,d=fixture();s['scenes'][0]['items'][0]['emphasis']=dict(kind='marker',anchor=dict(quote='庚'))
        scene,plan=compile_story(s,r,d)
        self.assertEqual(len(plan['scenes'][0]['beats']),3)
        self.assertEqual(next(n for n in scene['scenes'][0]['nodes'] if n['id']=='item-1')['emphasis']['timeUs'],1500000)

    def test_fixed_group_stagger_preserves_original_entry(self):
        s,r,d=fixture();scene,_=compile_story(s,r,d)
        nodes={n['id']:n for n in scene['scenes'][0]['nodes']}
        self.assertEqual(nodes['card-1']['enterUs'],nodes['item-1']['enterUs'])
        self.assertEqual(nodes['item-1']['enterDelayUs'],90000)

    def test_emphasis_before_entry_is_rejected(self):
        s,r,d=fixture();s['scenes'][0]['items'][0]['emphasis']=dict(kind='marker',anchor=dict(quote='乙'))
        with self.assertRaisesRegex(ValueError,'Emphasis'):compile_story(s,r,d)

    def test_hidden_title_reclaims_space(self):
        s,r,d=fixture();s['titleMode']='hidden';scene,_=compile_story(s,r,d)
        self.assertFalse(any(n['id'].startswith('title') for n in scene['scenes'][0]['nodes']))
        self.assertEqual(scene['scenes'][0]['nodes'][0]['y'],220)

    def test_forged_emphasis_time_fails_gate(self):
        s,r,d=fixture();scene,plan=compile_story(s,r,d)
        scene['subtitles']=editorial_subtitles(r,[''.join(x['Char'] for x in r[i:i+6]) for i in range(0,len(r),6)],d)
        next(n for n in scene['scenes'][0]['nodes'] if n['id']=='item-1')['emphasis']=dict(kind='marker',timeUs=1000001)
        errors=static_checks(dict(width=1080,height=1920,durationUs=d,title=s['title']),scene,r,plan)
        self.assertIn('SYNC',{e['rule'] for e in errors})

    def test_profile_is_explicit_and_unknown_rejected(self):
        self.assertEqual(load_profile()['id'],'knowledge-portrait-v1')
        self.assertEqual(load_profile('presentation-portrait-v1')['id'],'presentation-portrait-v1')
        with self.assertRaises(ValueError):load_profile('anything')


class MediaTests(unittest.TestCase):
    def test_three_sources_round_trip_without_remote_calls(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);source=root/'original.png';Image.new('RGB',(800,500),'teal').save(source)
            for kind,origin,license in [('local','user source','user-provided'),('search','https://example.org/original','licensed'),('generate','provider job receipt and prompt','provider-terms')]:
                e=import_image(source,root,kind,kind,origin,license)
                ref=dict(id=kind,source=e['source'])
                self.assertEqual(len(validate_registry(root,[ref],'mixed')),1)
            self.assertEqual(len(json.loads((root/'assets/media-registry.json').read_text())['assets']),3)

    def test_tamper_policy_path_and_duplicate_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);source=root/'original.png';Image.new('RGB',(800,500),'teal').save(source)
            e=import_image(source,root,'sample','local','original drawing','original');a=[dict(id='sample',source=e['source'])]
            with self.assertRaises(ValueError):validate_registry(root,a,'generate')
            with self.assertRaises(ValueError):import_image(source,root,'sample','local','original drawing','original')
            with self.assertRaises(ValueError):validate_registry(root,[dict(id='sample',source='../outside.png')])
            Image.new('RGB',(800,500),'red').save(root/e['source'])
            with self.assertRaisesRegex(ValueError,'changed'):validate_registry(root,a)

    def test_bad_images_and_unresolved_search_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);p=root/'bad.png';p.write_bytes(b'bad image')
            with self.assertRaises(Exception):import_image(p,root,'bad','local','user','user-provided')
            Image.new('RGB',(32,32)).save(p)
            with self.assertRaises(ValueError):import_image(p,root,'tiny','local','user','user-provided')
            Image.new('RGB',(400,400)).save(p)
            with self.assertRaises(ValueError):import_image(p,root,'unlicensed','search','https://example.org','unknown')


class PresentationRasterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=sync_playwright().start();cls.browser=cls.p.chromium.launch();cls.page=cls.browser.new_page()
        cls.page.set_content('<canvas></canvas>');cls.page.add_script_tag(content=re.sub(r'(?m)^export ','',Path('assets/runtime/scene.mjs').read_text(encoding='utf-8')))

    @classmethod
    def tearDownClass(cls):cls.browser.close();cls.p.stop()

    def prepare(self,s):
        self.page.evaluate('''async s=>{window.r=await prepareScene(document.querySelector('canvas'),s,{width:1080,height:1920,durationUs:s.scenes.at(-1).endUs,assetBase:location.href,safeArea:true});window.frame=t=>{r.renderAt(t);return document.querySelector('canvas').toDataURL();};}''',s)

    def test_effects_render_and_reverse_seek_identically(self):
        for entrance in ('fade-up','slide-left','slide-right','zoom'):
            for emphasis in ('color','marker','underline'):
                s,r,d=fixture();s['scenes'][0]['items'][0].update(entrance=entrance,emphasis=dict(kind=emphasis,anchor=dict(quote='庚')))
                scene,_=compile_story(s,r,d);self.prepare(scene)
                frames=[self.page.evaluate('frame',t) for t in (1100000,1400000,1600000,1900000)]
                self.assertEqual(len(set(frames)),4)
                self.assertEqual(self.page.evaluate('frame',1100000),frames[0])

    def test_four_cards_keep_gap_during_all_entrances(self):
        from scripts.quality_gate import card_spacing_failures
        for entrance in ('fade-up','slide-left','slide-right','zoom'):
            s,r,d=fixture('steps')
            s['scenes'][0]['items']=[dict(text='清晰要点',anchor=dict(quote=r[k]['Char']),entrance=entrance) for k in (2,3,4,5)]
            scene,_=compile_story(s,r,d);self.prepare(scene)
            for t in range(500000,2000001,50000):
                boxes=self.page.evaluate('(t)=>r.layoutAt(t)',t)
                self.assertEqual(card_spacing_failures([b for b in boxes if b['id'].startswith('card-')],32),[])

    def test_transitions_are_sequential_and_seek_without_residuals(self):
        for transition in ('fade','push'):
            s,r,d=fixture();scene,_=compile_story(s,r,d)
            second=copy.deepcopy(scene['scenes'][0]);second.update(id='second',startUs=d,endUs=d*2,transition=transition)
            second['nodes'][-1]['text']='切换后的内容';scene['scenes'].append(second)
            self.prepare(scene)
            a=self.page.evaluate('frame',5900000);b=self.page.evaluate('frame',6200000);c=self.page.evaluate('frame',6500000)
            self.assertEqual(len({a,b,c}),3);self.assertEqual(self.page.evaluate('frame',5900000),a)

    def test_real_glyph_overflow_blocks_with_node_identity(self):
        s,r,d=fixture('statement');s['scenes'][0]['items'][0]['text']='很长的专业词汇需要拆页否则无法在页面中容纳'*2
        scene,_=compile_story(s,r,d)
        with self.assertRaisesRegex(Exception,'overflows'):self.prepare(scene)

    def test_image_fit_focus_zoom_are_real_and_deterministic(self):
        import base64,io
        im=Image.new('RGB',(800,400),'red');ImageDraw.Draw(im).rectangle((400,0,800,400),fill='blue');buf=io.BytesIO();im.save(buf,format='PNG')
        data='data:image/png;base64,'+base64.b64encode(buf.getvalue()).decode()
        s,r,d=fixture('hero-image');scene,_=compile_story(s,r,d);n=next(n for n in scene['scenes'][0]['nodes'] if n['type']=='image');n['source']=data
        for fit in ('cover','contain'):
            n.update(fit=fit,focusX=1,imageZoom=True);self.prepare(scene)
            a=self.page.evaluate('frame',2000000);self.page.evaluate('frame',5000000)
            self.assertEqual(self.page.evaluate('frame',2000000),a)
            pixel=self.page.evaluate("()=>Array.from(document.querySelector('canvas').getContext('2d').getImageData(940,850,1,1).data)")
            self.assertGreater(pixel[2],pixel[0])

    def test_isolated_qa_uses_inline_images_without_taint(self):
        import base64,io
        from scripts.quality_browser import MOTION
        im=Image.new('RGB',(800,500),'teal');buf=io.BytesIO();im.save(buf,format='PNG')
        data='data:image/png;base64,'+base64.b64encode(buf.getvalue()).decode()
        story,rows,duration=fixture('image-text');scene,plan=compile_story(story,rows,duration)
        self.page.evaluate('''async ({scene,data})=>{
          window.config={width:1080,height:1920,durationUs:6000000,assetBase:'file:///nonexistent/',safeArea:true,inlineImages:{'assets/images/sample.png':data}};
          window.__vibe_scene=scene;window.r=await prepareScene(document.querySelector('canvas'),scene,config);
        }''',dict(scene=scene,data=data))
        result=self.page.evaluate(MOTION,plan)
        self.assertTrue(all(e['changedPixels']>=16 for e in result[0]['events']))

    def test_step_bullets_remain_inside_cards_during_zoom(self):
        s,rows,d=fixture('steps')
        s['scenes'][0]['items']=[dict(text='简短步骤',anchor=dict(quote=rows[i]['Char']),entrance='zoom') for i in (2,6,10,14)]
        scene,_=compile_story(s,rows,d);self.prepare(scene)
        for i in (2,6,10,14):
            boxes=self.page.evaluate('t=>r.layoutAt(t)',i*250000+1000)
            mapping={n['id']:n for n in boxes}
            for j in range(1,5):
                if f'bullet-{j}' not in mapping:continue
                a=mapping[f'card-{j}'];b=mapping[f'bullet-{j}']
                self.assertGreaterEqual(b['x'],a['x'])
                self.assertLessEqual(b['x']+b['width'],a['x']+a['width'])

    def test_staggered_step_bullets_never_overlap_sliding_text(self):
        s,rows,d=fixture('steps')
        s['scenes'][0]['items']=[dict(text='步骤内容',anchor=dict(quote=rows[i]['Char'])) for i in (2,6,10,14)]
        scene,_=compile_story(s,rows,d);self.prepare(scene)
        for t in range(500000,4500000,25000):
            mapping={n['id']:n for n in self.page.evaluate('t=>r.layoutAt(t)',t)}
            for j in range(1,5):
                if f'item-{j}' not in mapping:continue
                a=mapping[f'bullet-{j}'];b=mapping[f'item-{j}']
                self.assertLessEqual(a['x']+a['width'],b['x'],f'item {j} at {t}')

    def test_emphasis_tracks_ink_instead_of_empty_text_box(self):
        s,rows,d=fixture('statement');s['backgroundPreset']='solid';s['scenes'][0]['items'][0]['text']='重点'
        s['scenes'][0]['items'][0]['emphasis']=dict(kind='marker',anchor=dict(quote='庚'))
        scene,_=compile_story(s,rows,d);self.prepare(scene);self.page.evaluate('frame',2200000)
        # The 220px text box has ample empty space below its ink: it must stay background.
        pixel=self.page.evaluate("()=>Array.from(document.querySelector('canvas').getContext('2d').getImageData(540,870,1,1).data)")
        self.assertEqual(pixel[:3],[7,29,27])


if __name__=='__main__':unittest.main()
