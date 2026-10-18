import unittest
from spoken_roles import ParagraphRoles
class SpokenRoleTests(unittest.TestCase):
 def test_only_spoken_paragraphs_get_spoken_role(self):
  r=ParagraphRoles()
  self.assertEqual(r.role('## 第一部分 口播内容与对应映射'),'heading')
  self.assertEqual(r.role('备课提示（不朗读）：材料边界'),'notes')
  self.assertEqual(r.role('**翻页提示：页面1**'),'notes')
  self.assertEqual(r.role('这句话可以直接讲给学生。'),'spoken')
  self.assertEqual(r.role('【不朗读：停顿十秒】'),'stage')
  self.assertEqual(r.role('停顿后继续讲。'),'spoken')
  self.assertEqual(r.role('#### 本段对应的知识点与PPT内容'),'heading')
  self.assertEqual(r.role('- 对应知识点：检查依据'),'notes')
  self.assertEqual(r.role('## 第二部分 PPT内容与制作说明'),'heading')
  self.assertEqual(r.role('生图提示词：做图'),'notes')
 def test_heading_stops_previous_spoken_block(self):
  r=ParagraphRoles();r.role('## 第一部分');r.role('**翻页提示：页面1**');r.role('口播')
  r.role('### 新单元');self.assertEqual(r.role('概要：先讲用途'),'notes')
 def test_spoken_only_scope_needs_no_slide_marker(self):
  r=ParagraphRoles(scope='spoken');self.assertEqual(r.role('口播正文'),'spoken');self.assertEqual(r.role('【不朗读：演示】'),'stage')
 def test_quoted_example_in_brief_is_not_spoken(self):
  r=ParagraphRoles();r.role('## 第二部分');self.assertEqual(r.role('“模型说得很稳，杯子还在原地。”'),'notes')
if __name__=='__main__':unittest.main()
