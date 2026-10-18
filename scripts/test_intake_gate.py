import copy,unittest,subprocess,sys,tempfile
from pathlib import Path
from intake_gate import start_run,check_gate,prepare_run
from test_outline_preflight import example_review
class IntakeGateTests(unittest.TestCase):
 def fixture(self):
  s='本次讲座大纲';r=prepare_run(start_run(s),s,example_review(s))
  receipt={'version':3,'run_id':r['run_id'],'source_sha256':r['source_sha256'],'preflight_sha256':r['preflight_sha256'],'preflight_display_receipt':'测试夹具中的首轮诊断位置，不是真实用户记录','question_receipt':'本轮问答测试夹具位置','answers':{k:{'value':'本轮选项','origin':'user_reply','evidence':'单元测试模拟答复，非真人证据'} for k in ('purpose','deliverable','slide_mode','brief')}}
  receipt['answers']['purpose']['mode']='teaching'
  return s,r,receipt
 def test_new_run_is_pending_even_when_outline_same(self):
  a=start_run('相同大纲');b=start_run('相同大纲');self.assertNotEqual(a['run_id'],b['run_id']);self.assertEqual(b['status'],'awaiting_user')
 def test_current_complete_reply_passes(self):
  self.assertFalse(check_gate(*self.fixture())['errors'])
 def test_no_reply_blocks(self):
  s,r,_=self.fixture();self.assertTrue(check_gate(s,r,{})['errors'])
 def test_old_reply_cannot_pass_new_run(self):
  s,r,c=self.fixture();r=start_run(s);self.assertTrue(check_gate(s,r,c)['errors'])
 def test_source_changed_blocks(self):
  s,r,c=self.fixture();self.assertTrue(check_gate(s+'换了受众',r,c)['errors'])
 def test_missing_one_answer_blocks(self):
  s,r,c=self.fixture();del c['answers']['slide_mode'];self.assertTrue(check_gate(s,r,c)['errors'])
 def test_ai_inference_is_not_user_reply(self):
  s,r,c=self.fixture();c['answers']['brief']['origin']='inferred_from_history';self.assertTrue(check_gate(s,r,c)['errors'])
 def test_empty_receipt_does_not_count(self):
  s,r,c=self.fixture();c['question_receipt']='';self.assertTrue(check_gate(s,r,c)['errors'])
 def test_empty_evidence_blocks(self):
  s,r,c=self.fixture();c['answers']['deliverable']['evidence']='';self.assertTrue(check_gate(s,r,c)['errors'])
 def test_explicit_delegation_is_current_answer(self):
  s,r,c=self.fixture();c['answers']['slide_mode'].update(origin='user_delegation',evidence='这次你帮我选');self.assertFalse(check_gate(s,r,c)['errors'])
 def test_question_inventory_cannot_omit_mode(self):
  s,r,c=self.fixture();r['questions']=r['questions'][:1];self.assertTrue(check_gate(s,r,c)['errors'])
 def test_three_answers_without_outline_review_do_not_pass(self):
  s,r,c=self.fixture();r=start_run(s);c.update(run_id=r['run_id'])
  self.assertTrue(check_gate(s,r,c)['errors'])
 def test_diagnosis_must_have_actual_display_location(self):
  s,r,c=self.fixture();del c['preflight_display_receipt'];self.assertTrue(check_gate(s,r,c)['errors'])
 def test_changed_review_invalidates_receipt(self):
  s,r,c=self.fixture();r['preflight']['recommendation']='新的建议';self.assertTrue(check_gate(s,r,c)['errors'])
 def test_separate_outline_requires_actual_outline_input(self):
  s='继续制作';o='面向大一新生的原始完整大纲';r=prepare_run(start_run(s,o),o,example_review(o));_,_,c=self.fixture();c.update(run_id=r['run_id'],source_sha256=r['source_sha256'],preflight_sha256=r['preflight_sha256'])
  self.assertTrue(check_gate(s,r,c)['errors']);self.assertFalse(check_gate(s,r,c,o)['errors'])
 def test_missing_critical_answer_cannot_hide_in_generic_confirmation(self):
  s,r,c=self.fixture();review=example_review(s);review['critical_questions']=[{'id':'prior','dimension':'audience','question':'学生是否能独立编程？','why':'决定是否让学生现场写代码。'}];review['questions']=r['questions'];review['questions'][2]['prompt']+='学生是否能独立编程？';r=prepare_run(start_run(s),s,review);c.update(run_id=r['run_id'],preflight_sha256=r['preflight_sha256'])
  self.assertTrue(check_gate(s,r,c)['errors'])
  c['resolutions']={'prior':{'value':'以从未写过代码为起点，现场只看讲者演示','origin':'user_reply','evidence':'单元测试模拟的当前用户选择'}}
  self.assertFalse(check_gate(s,r,c)['errors'])
 def test_critical_question_must_be_in_displayed_inventory(self):
  s,r,c=self.fixture();review=example_review(s);review['critical_questions']=[{'id':'q','dimension':'outcome','question':'当前需要作什么决定？','why':'影响主线。'}]
  with self.assertRaises(ValueError):prepare_run(start_run(s),s,review)
 def test_blank_prompt_after_prepare_blocks(self):
  s,r,c=self.fixture();r['questions'][2]['prompt']=''
  self.assertFalse(check_gate(s,r,c)['ready_for_generation'])
 def test_removed_critical_prompt_after_prepare_blocks(self):
  s,r,c=self.fixture();review=example_review(s)
  review['critical_questions']=[{'id':'goal','dimension':'outcome','question':'听完要作什么决定？','why':'决定主线。'}]
  review['questions']=copy.deepcopy(r['questions']);review['questions'][2]['prompt']+='听完要作什么决定？'
  r=prepare_run(start_run(s),s,review);c.update(run_id=r['run_id'],preflight_sha256=r['preflight_sha256'])
  c['resolutions']={'goal':{'value':'判断能否开展试点','origin':'user_reply','evidence':'合成测试答复，非真人授权'}}
  del r['preflight']['questions']
  from intake_gate import review_digest
  r['preflight_sha256']=c['preflight_sha256']=review_digest(r['preflight'])
  r['questions'][2]['prompt']='泛泛确认一下'
  self.assertFalse(check_gate(s,r,c)['ready_for_generation'])
 def test_output_cli_without_intake_blocks_authoring_validation(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'draft.md';p.write_text('可以朗读的正文',encoding='utf-8')
   x=subprocess.run([sys.executable,str(Path(__file__).with_name('check_output.py')),str(p),'--scope','spoken','--json'],capture_output=True,text=True)
   self.assertEqual(x.returncode,1);self.assertIn('missing-intake',x.stdout)
 def test_read_only_audit_explicitly_skips_authoring_gate(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'draft.md';p.write_text('已有稿件正文',encoding='utf-8')
   x=subprocess.run([sys.executable,str(Path(__file__).with_name('check_output.py')),str(p),'--scope','spoken','--audit-only','--json'],capture_output=True,text=True)
   self.assertEqual(x.returncode,0);self.assertIn('audit_only',x.stdout)
if __name__=='__main__':unittest.main()
