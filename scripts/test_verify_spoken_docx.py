import unittest,tempfile,zipfile
from pathlib import Path
from verify_spoken_docx import check_docx_roles
class DocxRoleTests(unittest.TestCase):
 def fixture(self,spoken_font='Microsoft YaHei',stage_style='LectureNotes',size='27'):
  td=tempfile.TemporaryDirectory();self.addCleanup(td.cleanup);p=Path(td.name)/'test.docx'
  xml=f'''<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:pPr><w:pStyle w:val="LectureSpoken"/></w:pPr><w:r><w:rPr><w:rFonts w:eastAsia="{spoken_font}"/><w:sz w:val="{size}"/></w:rPr><w:t>可念正文</w:t></w:r></w:p><w:p><w:pPr><w:pStyle w:val="{stage_style}"/></w:pPr><w:r><w:rPr><w:rFonts w:eastAsia="FangSong"/><w:sz w:val="22"/></w:rPr><w:t>【不朗读：停顿】</w:t></w:r></w:p></w:body></w:document>'''
  with zipfile.ZipFile(p,'w') as z:z.writestr('word/document.xml',xml);z.writestr('word/styles.xml','<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>')
  return p
 def test_actual_font_properties_pass(self):self.assertFalse(check_docx_roles(self.fixture())['errors'])
 def test_label_without_font_difference_fails(self):self.assertTrue(check_docx_roles(self.fixture(spoken_font='FangSong'))['errors'])
 def test_stage_direction_cannot_be_spoken_style(self):self.assertTrue(check_docx_roles(self.fixture(stage_style='LectureSpoken'))['errors'])
 def test_expected_paragraph_missing_fails(self):self.assertTrue(check_docx_roles(self.fixture(),expected=['缺失的口播'])['errors'])
 def test_wrong_size_fails(self):self.assertTrue(check_docx_roles(self.fixture(size='22'))['errors'])
if __name__=='__main__':unittest.main()
