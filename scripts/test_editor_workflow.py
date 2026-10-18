import unittest
from editor_workflow import plan, select

class WorkflowTests(unittest.TestCase):
    def request(self,need='challenge_default',humor='light',critical=False):
        return {'humor':humor,'beats':[{'id':'b1','need':need,'claim_id':'c1','critical_instruction':critical}]}
    def test_luo_first_when_challenging_default(self):
        self.assertEqual(plan(self.request())['beats'][0]['options'][0]['inspiration'],'luo')
    def test_causal_explanation_routes_to_hunzi(self):
        self.assertEqual(plan(self.request('explain_mechanism'))['beats'][0]['options'][0]['inspiration'],'hunzi')
    def test_choice_story_routes_to_lei(self):
        self.assertEqual(plan(self.request('develop_choice'))['beats'][0]['options'][0]['inspiration'],'lei')
    def test_experience_routes_to_wang(self):
        self.assertEqual(plan(self.request('translate_impact'))['beats'][0]['options'][0]['inspiration'],'wang')
    def test_safety_operation_stays_plain(self):
        self.assertEqual([o['id'] for o in plan(self.request(critical=True))['beats'][0]['options']],['plain'])
    def test_humor_off_keeps_reasoning(self):
        options=plan(self.request(humor='off'))['beats'][0]['options']
        self.assertEqual(options[0]['inspiration'],'luo')
        self.assertTrue(all(o.get('requires_humor',False) is False for o in options))
    def test_plain_does_not_make_candidates(self):
        self.assertEqual(plan(self.request('plain'))['beats'][0]['generation'],'direct')
    def test_duplicates_rejected(self):
        r=self.request();r['beats']*=2
        with self.assertRaises(ValueError):plan(r)
    def test_invalid_need_rejected(self):
        with self.assertRaises(ValueError):plan(self.request('random'))
    def test_no_school_or_domain_keyword_routing(self):
        r=self.request('translate_impact');a=plan(r);r['topic']='历史与博物馆';self.assertEqual(plan(r),a)
    def test_semantic_veto_beats_preference(self):
        candidates=[{'id':'a','text':'漂亮却不忠实的句子'},{'id':'b','text':'清楚忠实的普通解释'}]
        review={'preferred':'a','reason':'更有反差','candidates':[
          {'id':'a','text':'漂亮却不忠实的句子','faithful':False,'grounded':True,'speakable':True,'useful':True,'evidence':'扩大了原主张'},
          {'id':'b','text':'清楚忠实的普通解释','faithful':True,'grounded':True,'speakable':True,'useful':True,'evidence':'保留条件'}]}
        self.assertEqual(select(candidates,review)['status'],'revision_required')
    def test_stale_review_rejected(self):
        c=[{'id':'a','text':'修改后的稿子'}]
        r={'preferred':'a','reason':'清楚','candidates':[{'id':'a','text':'旧稿子','faithful':True,'grounded':True,'speakable':True,'useful':True,'evidence':'清楚'}]}
        with self.assertRaises(ValueError):select(c,r)
    def test_no_numeric_humor_score(self):
        c=[{'id':'a','text':'可念解释'}]
        r={'preferred':'a','reason':'有具体解释','candidates':[{'id':'a','text':'可念解释','faithful':True,'grounded':True,'speakable':True,'useful':True,'evidence':'具体关系保留'}]}
        result=select(c,r);self.assertEqual(result['status'],'selected');self.assertEqual(result['audience_effect'],'not_measured')
    def test_every_candidate_needs_review(self):
        with self.assertRaises(ValueError):select([{'id':'a','text':'一'},{'id':'b','text':'二'}],{'preferred':'a','reason':'比较','candidates':[]})
    def test_booleans_cannot_be_strings(self):
        with self.assertRaises(ValueError):select([{'id':'a','text':'一'}],{'preferred':'a','reason':'比较','candidates':[{'id':'a','text':'一','faithful':'true','grounded':True,'speakable':True,'useful':True,'evidence':'原句'}]})
    def test_explicit_priority_overrides_default(self):
        r=self.request();r['inspiration_priority']=['wang','luo']
        self.assertEqual(plan(r)['beats'][0]['options'][0]['inspiration'],'wang')
    def test_allowed_inspirations_can_disable_default(self):
        r=self.request();r['allowed_inspirations']=['wang']
        self.assertEqual([o['inspiration'] for o in plan(r)['beats'][0]['options']],['wang',None])
    def test_unknown_inspiration_rejected(self):
        r=self.request();r['allowed_inspirations']=['unknown']
        with self.assertRaises(ValueError):plan(r)
    def test_no_available_mechanism_routes_direct(self):
        r=self.request();r['allowed_inspirations']=[]
        self.assertEqual(plan(r)['beats'][0]['generation'],'direct')
    def effect_review(self,passes=True):
        c=[{'id':'a','text':'一段清楚但需要判断效果的候选。'}]
        r={'required_effects':['humor'],'preferred':'a','reason':'按本处目标比较','candidates':[{'id':'a','text':c[0]['text'],'faithful':True,'grounded':True,'speakable':True,'useful':True,'evidence':'知识和条件保留。','effects':{'humor':{'passes':passes,'evidence':'这里只解释知识，没有意外落点。'}}}]}
        return c,r
    def test_clear_but_unfunny_cannot_pass_humor_target(self):
        c,r=self.effect_review(False)
        self.assertEqual(select(c,r)['status'],'revision_required')
    def test_requested_effect_cannot_be_left_unreviewed(self):
        c,r=self.effect_review();del r['candidates'][0]['effects']
        with self.assertRaises(ValueError):select(c,r)
    def test_effect_review_needs_specific_feedback(self):
        c,r=self.effect_review();r['candidates'][0]['effects']['humor']['evidence']=''
        with self.assertRaises(ValueError):select(c,r)
    def test_effect_pass_does_not_claim_audience_measurement(self):
        c,r=self.effect_review();result=select(c,r)
        self.assertEqual(result['audience_effect'],'not_measured')
        self.assertEqual(result['required_effects'],['humor'])
if __name__=='__main__':unittest.main()
