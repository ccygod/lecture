import unittest
from editor_workflow import plan
class RelevanceTests(unittest.TestCase):
 def bridge(self):
  return {'audience_anchor':'四年本科新生','content_fact':'2030年产业预测','mechanism':'机会需要与可交付能力匹配','consequence':'毕业时的选择与准备','action':'完成可核验项目','link_status':'conditional','wording_strength':'conditional','boundary':'规模不直接等于岗位或录用','evidence':['产业报告与岗位材料'],'timeline':{'start_year':2026,'years':4,'target_year':2030}}
 def request(self):
  return {'beats':[{'id':'a','claim_id':'c','need':'connect_value','relevance':self.bridge()}]}
 def test_connect_value_has_concrete_bridge(self):
  x=plan(self.request())['beats'][0]
  self.assertEqual(x['relevance']['timeline']['calculated_year'],2030)
  self.assertIsNone(x['options'][0]['inspiration'])
  self.assertEqual(x['generation'],'direct')
 def test_empty_mechanism_does_not_count_as_relevance(self):
  r=self.request();r['beats'][0]['relevance']['mechanism']=''
  with self.assertRaises(ValueError):plan(r)
 def test_guarantee_cannot_be_inferred_from_forecast(self):
  r=self.request();r['beats'][0]['relevance']['wording_strength']='guaranteed'
  with self.assertRaises(ValueError):plan(r)
 def test_wrong_graduation_alignment_rejected(self):
  r=self.request();r['beats'][0]['relevance']['timeline']['target_year']=2029
  with self.assertRaises(ValueError):plan(r)
 def test_without_time_window_works_for_manager(self):
  r=self.request();b=r['beats'][0]['relevance'];del b['timeline'];b['audience_anchor']='采购负责人';b['content_fact']='方案部署时间';b['consequence']='项目延期风险'
  self.assertIn('relevance',plan(r)['beats'][0])
 def test_plain_explanation_needs_no_forced_bridge(self):
  r={'beats':[{'id':'p','claim_id':'c','need':'plain'}]};self.assertEqual(plan(r)['beats'][0]['generation'],'direct')
 def test_topic_label_does_not_replace_audience_anchor(self):
  r=self.request();del r['beats'][0]['relevance']['audience_anchor']
  with self.assertRaises(ValueError):plan(r)
 def test_missing_bridge_rejected(self):
  r=self.request();del r['beats'][0]['relevance']
  with self.assertRaises(ValueError):plan(r)
if __name__=='__main__':unittest.main()
