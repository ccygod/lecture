import unittest
from compile_slide_refs import compile_refs
class SlideRefTests(unittest.TestCase):
 def test_refs_move_with_order(self):
  pages=[{'id':'opening','title':'开场'},{'id':'practice','title':'练习'}]
  self.assertEqual(compile_refs('看{{slide:practice}}',pages),'看页面2')
  pages.insert(1,{'id':'data','title':'数据'})
  self.assertEqual(compile_refs('看{{slide:practice}}',pages),'看页面3')
 def test_unknown_id_rejected_even_when_numbers_in_range(self):
  with self.assertRaises(ValueError):compile_refs('{{slide:missing}}',[{'id':'a','title':'甲'}])
 def test_duplicate_ids_rejected(self):
  with self.assertRaises(ValueError):compile_refs('文字',[{'id':'a','title':'甲'},{'id':'a','title':'乙'}])
 def test_no_unrelated_numbers_rewritten(self):
  self.assertEqual(compile_refs('2026到2030，75.26%',[]),'2026到2030，75.26%')
 def test_ranges_use_two_stable_ids(self):
  x=[{'id':'a','title':'甲'},{'id':'b','title':'乙'}]
  self.assertEqual(compile_refs('{{slide:a}}—{{slide:b}}',x),'页面1—页面2')
if __name__=='__main__':unittest.main()
