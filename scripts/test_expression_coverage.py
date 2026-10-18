import copy
import unittest
import editor_workflow as workflow


class ExpressionCoverageTests(unittest.TestCase):
    def request(self):
        return {'humor':'moderate','required_effects':['curiosity'], 'beats':[
            {'id':'opening','claim_id':'c1','need':'challenge_default','required_effects':['humor','curiosity']},
            {'id':'explain','claim_id':'c2','need':'plain'}]}

    def candidate(self):
        c=[{'id':'a','text':'这是合成测试候选，非真实讲稿。'}]
        r={'preferred':'a','reason':'测试实际效果目标传递，不评估文学质量。','required_effects':['humor','curiosity'],
           'candidates':[{'id':'a','text':c[0]['text'],'faithful':True,'grounded':True,'speakable':True,'useful':True,
             'evidence':'合成的结构测试反馈，非真人反馈。','effects':{e:{'passes':True,'evidence':'合成判断，仅测试字段传递。'} for e in ('humor','curiosity')}}]}
        return c,r

    def selection(self):
        p=workflow.plan(self.request());c,r=self.candidate()
        return p,workflow.select(c,r,editorial_plan=p,beat_id='opening')

    def coverage(self,p,rows,spoken):
        return workflow.check_coverage(p,rows,spoken)

    def test_global_humor_cannot_silently_disappear(self):
        p=workflow.plan({'humor':'moderate','beats':[{'id':'x','claim_id':'c','need':'explain_mechanism'}]})
        self.assertFalse(p.get('ready_for_selection',True))
        self.assertIn('humor',p.get('unresolved_effects',[]))

    def test_plan_carries_effects_only_to_selected_positions(self):
        p=workflow.plan(self.request())
        self.assertEqual(p['beats'][0].get('required_effects'),['humor','curiosity'])
        self.assertEqual(p['beats'][1].get('required_effects'),[])

    def test_no_humor_request_has_no_forced_target(self):
        p=workflow.plan({'humor':'off','beats':[{'id':'x','claim_id':'c','need':'plain'}]})
        self.assertTrue(p.get('ready_for_selection',False))

    def test_editorial_omission_is_explicit_and_not_effect_success(self):
        r={'humor':'light','effect_omissions':{'humor':'当前仅写严肃操作步骤，幽默留给本次未处理的开场。'},'beats':[{'id':'x','claim_id':'c','need':'plain'}]}
        p=workflow.plan(r)
        self.assertTrue(p.get('ready_for_selection',False))
        self.assertTrue(p.get('effect_omissions',{}).get('humor'))

    def test_blank_omission_cannot_resolve_request(self):
        r=self.request();r['effect_omissions']={'curiosity':''}
        with self.assertRaises(ValueError):workflow.plan(r)

    def test_review_cannot_drop_plan_effect(self):
        p=workflow.plan(self.request());c,r=self.candidate();r['required_effects']=[]
        with self.assertRaises(ValueError):workflow.select(c,r,editorial_plan=p,beat_id='opening')

    def test_effect_order_does_not_create_false_coverage_failure(self):
        p=workflow.plan(self.request());c,r=self.candidate();r['required_effects'].reverse()
        s=workflow.select(c,r,editorial_plan=p,beat_id='opening')
        self.assertTrue(self.coverage(p,[s],s['text'])['ready_for_delivery'])

    def test_stale_plan_cannot_bind_selection(self):
        p=workflow.plan(self.request());p['beats'][0]['required_effects']=[];c,r=self.candidate()
        with self.assertRaises(ValueError):workflow.select(c,r,editorial_plan=p,beat_id='opening')

    def test_missing_selected_position_blocks_coverage(self):
        p,_=self.selection()
        self.assertFalse(self.coverage(p,[],'测试稿')['ready_for_delivery'])

    def test_selected_candidate_must_reach_actual_spoken_text(self):
        p,s=self.selection()
        self.assertFalse(self.coverage(p,[s],'只有另一个版本')['ready_for_delivery'])

    def test_matching_spoken_text_passes_without_human_effect_claim(self):
        p,s=self.selection();r=self.coverage(p,[s],'前文\n'+s['text']+'\n后文')
        self.assertTrue(r['ready_for_delivery'])
        self.assertEqual(r['audience_effect'],'not_measured')

    def test_legacy_unbound_selection_is_not_delivery_evidence(self):
        p=workflow.plan(self.request());c,r=self.candidate();s=workflow.select(c,r)
        self.assertFalse(self.coverage(p,[s],s['text'])['ready_for_delivery'])

    def test_changed_selection_payload_is_rejected(self):
        p,s=self.selection();s['text']='改动后的候选'
        self.assertFalse(self.coverage(p,[s],s['text'])['ready_for_delivery'])

    def test_selection_for_other_plan_is_rejected(self):
        p,s=self.selection();r=self.request();r['beats'][0]['need']='humanize';p2=workflow.plan(r)
        self.assertFalse(self.coverage(p2,[s],s['text'])['ready_for_delivery'])


if __name__=='__main__':unittest.main()
