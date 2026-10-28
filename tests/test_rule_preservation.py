import copy
import unittest
from pathlib import Path
from scripts.components import compile_story
from scripts.contracts import load_profile,validate_document
from scripts.preservation import scene_checks,sound_checks
from scripts.quality_gate import static_checks
from test_quality_gate import fixture


class PreservedRuleTests(unittest.TestCase):
    def setUp(self):
        self.m,self.scene,self.rows,self.plan=fixture();self.profile=load_profile()

    def title_rules(self):
        return {e['rule'] for e in scene_checks(self.m,self.scene,self.plan,self.profile)}

    def story(self,**options):
        story=dict(version=1,title='测试知识动画',authorId='test-author',scenes=[dict(id='one',kind='process',heading='原词推进',stages=[dict(text='阶段展开',anchor=dict(quote='戊己')),dict(text='机制建立',anchor=dict(quote='寅卯'))])])
        story.update(options);return story

    def test_hidden_header_has_no_empty_reserved_zone(self):
        s,p=compile_story(self.story(titleMode='hidden'),self.rows,self.m['durationUs'])
        s['subtitles']=self.scene['subtitles']
        self.assertEqual(p['scenes'][0]['roles']['title'],[])
        self.assertLessEqual(min(n['y'] for n in s['scenes'][0]['nodes']),self.m['height']*.20)
        self.assertEqual(static_checks(self.m,s,self.rows,p),[])

    def test_hidden_header_cannot_hide_existing_title_by_metadata(self):
        self.scene['titleMode']='hidden';self.assertIn('TITLE',self.title_rules())

    def test_explicit_long_title_is_two_semantic_nodes(self):
        title='丛枝菌根作用机制与土壤生态应用优势'
        s,p=compile_story(self.story(title=title,titleLines=['丛枝菌根作用机制','与土壤生态应用优势']),self.rows,self.m['durationUs'])
        self.assertEqual(len(p['scenes'][0]['roles']['title']),2)
        self.assertEqual(scene_checks(dict(self.m,title=title),s,p,self.profile),[])

    def test_long_title_without_semantic_lines_is_rejected(self):
        with self.assertRaises(ValueError):compile_story(self.story(title='丛枝菌根作用机制与土壤生态应用优势'),self.rows,self.m['durationUs'])

    def test_title_tail_cannot_be_an_orphan(self):
        with self.assertRaises(ValueError):compile_story(self.story(title='丛枝菌根作用与优势',titleLines=['丛枝菌根作用与','优势']),self.rows,self.m['durationUs'])

    def test_work_title_cannot_be_replaced_with_a_series_label(self):
        self.m['title']='作品真实名称';self.assertIn('TITLE',self.title_rules())

    def test_title_height_and_center_are_enforced(self):
        self.scene['scenes'][0]['nodes'][0]['x']=200
        self.scene['scenes'][0]['nodes'][0]['height']=140
        self.assertIn('TITLE',self.title_rules())

    def test_unknown_title_mode_rejected_by_schema(self):
        self.scene['titleMode']='hide-everything'
        with self.assertRaises(ValueError):validate_document('scene',self.scene)

    def test_unfounded_recap_opening_is_rejected(self):
        self.scene['scenes'][0]['nodes'].append(dict(id='heading',type='text',x=120,y=440,width=840,height=90,size=48,text='上期回顾'))
        self.plan['scenes'][0]['roles']['content'].append('heading')
        self.assertIn('OPENING',{e['rule'] for e in static_checks(self.m,self.scene,self.rows,self.plan)})

    def test_more_than_two_decorative_loops_is_rejected(self):
        for node in self.scene['scenes'][0]['nodes']:node['pulse']=True
        self.assertIn('MOTION',self.title_rules())

    def test_previous_episode_wording_is_a_valid_recap(self):
        for i,ch in enumerate('上一期'):
            self.rows[i]['Char']=ch;self.scene['subtitles'][0]['chars'][i]['text']=ch
        self.scene['scenes'][0]['nodes'].append(dict(id='heading',type='text',x=120,y=440,width=840,height=90,size=48,text='上期回顾'))
        self.plan['scenes'][0]['roles']['content'].append('heading')
        self.assertEqual(static_checks(self.m,self.scene,self.rows,self.plan),[])

    def test_small_title_cannot_pass_as_body_text(self):
        self.scene['scenes'][0]['nodes'][0]['size']=32
        self.assertIn('TYPE',self.title_rules())

    def test_ring_number_needs_geometric_clearance(self):
        nodes=self.scene['scenes'][0]['nodes'];nodes.extend([
            dict(id='ring',type='ring',x=380,y=700,width=300,height=300),
            dict(id='number',type='text',x=485,y=810,width=90,height=80,size=58,text='50%')])
        self.plan['scenes'][0]['intentionalOverlaps']=[dict(nodeIds=['ring','number'],design='ring-number',reason='受控圆环中心数字布局')]
        self.assertNotIn('COLLISION',self.title_rules())
        nodes[-1]['x']=580
        self.assertIn('COLLISION',self.title_rules())

    def test_ring_number_type_size_is_not_exempt(self):
        self.scene['scenes'][0]['nodes'].extend([
            dict(id='ring',type='ring',x=380,y=700,width=300,height=300),
            dict(id='number',type='text',x=485,y=810,width=90,height=80,size=40,text='50%')])
        self.plan['scenes'][0]['intentionalOverlaps']=[dict(nodeIds=['ring','number'])]
        self.assertIn('TYPE',self.title_rules())

    def sound_errors(self,events,metrics=None):
        return sound_checks(self.scene,dict(events=events),metrics or {},self.profile)

    def test_unknown_sound_name_rejected(self):
        self.assertTrue(self.sound_errors([dict(source='assets/laser.wav',timeUs=1000000)]))

    def test_ending_chime_required_and_complete(self):
        self.assertEqual(self.sound_errors([dict(source='assets/ding.wav',timeUs=1000000),dict(source='assets/chime.wav',timeUs=3000000)],{'assets/chime.wav':dict(durationUs=1200000)}),[])
        self.assertTrue(self.sound_errors([dict(source='assets/chime.wav',timeUs=5500000)],{'assets/chime.wav':dict(durationUs=1200000)}))
        self.assertTrue(self.sound_errors([dict(source='assets/click.wav',timeUs=1000000)]))

    def test_each_cut_needs_a_whoosh_at_the_cut(self):
        self.scene['scenes'].append(dict(self.scene['scenes'][0],id='next',startUs=6000000,endUs=12000000))
        events=[dict(source='assets/ding.wav',timeUs=3000000),dict(source='assets/chime.wav',timeUs=9000000)]
        self.assertTrue(self.sound_errors(events))
        events.append(dict(source='assets/whoosh.wav',timeUs=6000000))
        self.assertEqual(self.sound_errors(events),[])
