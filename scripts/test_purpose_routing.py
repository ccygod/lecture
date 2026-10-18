import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from intake_gate import start_run,prepare_run,check_gate
from test_outline_preflight import example_review
import check_output
from test_check_output import PLAIN
from editor_workflow import plan

BRIEFING='''# 第一部分 口播内容与对应映射
## 主题单元 先确认一个试点任务
这次建议先选一个任务试点，双方确认资料、责任与结果判断方式。
### 本段对应的核心信息与PPT内容
- 表达作用：说明建议与讨论入口。
- 核心信息：一个任务、双方责任、验证结果。
- PPT内容：试点范围与未决事项。
- 衔接与推进：请对方讨论任务优先级。
# 第二部分 PPT内容与制作说明
# 第三部分 汇报与推进框架
汇报目标：就试点范围达成初步共识。
关键依据：当前已提供的任务材料。
对方关切：先解决什么问题及如何判断结果。
能力与合作边界：双方尚未约定实际接口和责任。
下一步：双方确认任务和资料范围。
'''

class PurposeRoutingTests(unittest.TestCase):
 def fixture(self):
  source='客户沟通大纲，10分钟，讨论是否选一个任务试点。'
  run=prepare_run(start_run(source),source,example_review(source))
  answers={k:{'value':'合成的当前测试答复','origin':'user_reply','evidence':'合成夹具，非真人授权'} for k in ('purpose','deliverable','slide_mode','brief')}
  answers['purpose'].update(mode='briefing',value='客户汇报')
  receipt={'version':3,'run_id':run['run_id'],'source_sha256':run['source_sha256'],'preflight_sha256':run['preflight_sha256'],'preflight_display_receipt':'TEST_ONLY diagnosis','question_receipt':'TEST_ONLY questions','answers':answers}
  return source,run,receipt

 def test_purpose_is_first_mandatory_question(self):
  r=start_run('任意题目')
  self.assertEqual(r['questions'][0]['id'],'purpose')
  self.assertEqual(r['version'],3)

 def test_old_three_answers_cannot_pass_new_gate(self):
  s,r,c=self.fixture();del c['answers']['purpose']
  self.assertFalse(check_gate(s,r,c)['ready_for_generation'])

 def test_purpose_requires_explicit_current_mode(self):
  s,r,c=self.fixture();del c['answers']['purpose']['mode']
  self.assertFalse(check_gate(s,r,c)['ready_for_generation'])

 def test_confirmed_mode_reaches_downstream(self):
  result=check_gate(*self.fixture())
  self.assertTrue(result['ready_for_generation'])
  self.assertEqual(result['purpose_mode'],'briefing')

 def test_purpose_cannot_be_moved_after_ppt(self):
  s,r,c=self.fixture();review=example_review(s);review['questions']=r['questions'][1:]+r['questions'][:1]
  with self.assertRaises(ValueError):prepare_run(start_run(s),s,review)

 def test_past_v2_receipt_is_audit_only(self):
  s,r,c=self.fixture();r['version']=c['version']=2
  self.assertFalse(check_gate(s,r,c)['ready_for_generation'])

 def test_client_structure_does_not_require_student_fields(self):
  self.assertEqual(check_output.check(BRIEFING,purpose='briefing')['errors'],[])

 def test_teaching_still_uses_its_learning_mapping(self):
  self.assertTrue(check_output.check(BRIEFING,purpose='teaching')['errors'])

 def test_customer_report_must_keep_next_step_or_open_question(self):
  bad=BRIEFING.replace('下一步：双方确认任务和资料范围。','')
  self.assertTrue(check_output.check(bad,purpose='briefing')['errors'])

 def test_ceremonial_public_talk_does_not_require_trial_decision(self):
  talk=BRIEFING.replace('第三部分 汇报与推进框架','第三部分 表达与承接框架').replace('下一步：双方确认任务和资料范围。','收束：致谢与共同愿景。')
  self.assertEqual(check_output.check(talk,purpose='public_talk')['errors'],[])

 def test_public_talk_cannot_silently_reuse_teaching_framework(self):
  talk=BRIEFING[:BRIEFING.index('# 第三部分')]+'# 第三部分 教学框架\n学生误区：不理解术语。\n课后任务：写一个练习。\n'
  self.assertTrue(check_output.check(talk,purpose='public_talk')['errors'])

 def test_report_framework_requires_concerns_and_boundaries(self):
  bad=BRIEFING.replace('对方关切：先解决什么问题及如何判断结果。\n','').replace('能力与合作边界：双方尚未约定实际接口和责任。\n','')
  self.assertTrue(check_output.check(bad,purpose='briefing')['errors'])

 def test_report_headings_can_have_bullet_body(self):
  sample=BRIEFING
  for title in ('汇报目标','关键依据','对方关切','能力与合作边界','下一步'):
   sample=sample.replace(title+'：','### '+title+'\n- ')
  self.assertEqual(check_output.check(sample,purpose='briefing')['errors'],[])

 def test_empty_framework_field_cannot_borrow_next_field(self):
  bad=BRIEFING.replace('汇报目标：就试点范围达成初步共识。','### 汇报目标')
  errors=check_output.check(bad,purpose='briefing')['errors']
  self.assertIn('missing-report-goal',{x['code'] for x in errors})

 def test_teaching_cannot_use_reporting_framework(self):
  bad=PLAIN.replace('# 第三部分 教学框架','# 第三部分 汇报与推进框架')
  self.assertIn('purpose-framework-conflict',{x['code'] for x in check_output.check(bad,purpose='teaching')['errors']})

 def test_teaching_framework_cannot_be_empty(self):
  bad=PLAIN[:PLAIN.index('# 第三部分')]+'# 第三部分 教学框架\n'
  self.assertTrue(check_output.check(bad,purpose='teaching')['errors'])

 def test_documented_possible_concerns_alias_is_accepted(self):
  sample=BRIEFING.replace('对方关切：','对方可能关切：')
  self.assertEqual(check_output.check(sample,purpose='briefing')['errors'],[])

 def test_numbered_framework_fields_are_accepted(self):
  sample=BRIEFING
  for i,title in enumerate(('汇报目标','关键依据','对方关切','能力与合作边界','下一步'),1):
   sample=sample.replace(title+'：',str(i)+'. '+title+'：')
  self.assertEqual(check_output.check(sample,purpose='briefing')['errors'],[])

 def test_existing_teaching_descriptive_headings_are_accepted(self):
  sample=PLAIN.replace('知识与技能：区分百分点与复核成本。','### 核心主张与知识技能\n- 区分百分点与复核成本。')
  sample=sample.replace('学生误区：只比较成功数。','### 常见误区与纠偏\n- 只比较成功数。')
  sample=sample.replace('理解证据：说明效果与成本。','### 理解证据与现场处理\n- 说明效果与成本。')
  self.assertEqual(check_output.check(sample,purpose='teaching')['errors'],[])

 def test_briefing_does_not_default_to_humor_target(self):
  p=plan({'purpose_mode':'briefing','beats':[{'id':'x','claim_id':'c','need':'challenge_default'}]})
  self.assertEqual(p['humor'],'off')
  self.assertNotIn('humor',p['requested_effects'])

 def test_user_can_request_light_humor_for_briefing(self):
  p=plan({'purpose_mode':'briefing','humor':'light','beats':[{'id':'x','claim_id':'c','need':'challenge_default','required_effects':['humor']}]})
  self.assertTrue(p['ready_for_selection'])

 def test_cli_derives_structure_from_current_purpose(self):
  s,r,c=self.fixture()
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)
   for name,obj in [('run.json',r),('receipt.json',c)]: (p/name).write_text(json.dumps(obj,ensure_ascii=False))
   (p/'source.txt').write_text(s);(p/'draft.md').write_text(BRIEFING)
   args=[sys.executable,str(Path(check_output.__file__)),str(p/'draft.md'),'--intake-source',str(p/'source.txt'),'--intake-run',str(p/'run.json'),'--intake-receipt',str(p/'receipt.json'),'--json']
   result=subprocess.run(args,capture_output=True,text=True)
   self.assertEqual(result.returncode,0,result.stdout+result.stderr)
   self.assertEqual(json.loads(result.stdout)['assessment']['purpose_mode'],'briefing')

 def test_cli_cannot_override_confirmed_purpose(self):
  s,r,c=self.fixture()
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)
   for name,obj in [('run.json',r),('receipt.json',c)]: (p/name).write_text(json.dumps(obj,ensure_ascii=False))
   (p/'source.txt').write_text(s);(p/'draft.md').write_text('测试口播')
   args=[sys.executable,str(Path(check_output.__file__)),str(p/'draft.md'),'--scope','spoken','--purpose','teaching','--intake-source',str(p/'source.txt'),'--intake-run',str(p/'run.json'),'--intake-receipt',str(p/'receipt.json'),'--json']
   result=subprocess.run(args,capture_output=True,text=True)
   self.assertNotEqual(result.returncode,0)
   self.assertIn('purpose-mismatch',result.stdout)

if __name__=='__main__':unittest.main()
