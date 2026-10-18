"""Regression tests for structural validation, not a speech quality benchmark."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name('check_output.py')
spec = importlib.util.spec_from_file_location('lecture_check', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

PLAIN = '''# 第一部分 口播内容与对应映射
## 主题单元 数据比较
### 口播段落一
同样一百项任务，A完成九十项，B完成九十六项。B多完成了六项，但每项复核多用一分钟。
### 本段对应的知识点与PPT内容
- 口播作用：解释结果与代价。
- 对应知识点：百分点和复核成本。
- PPT内容：同批任务结果。
- 互动与过渡：直接解释，随后讲试点安排。
# 第二部分 PPT内容与制作说明
# 第三部分 教学框架
知识与技能：区分百分点与复核成本。
过程与方法：比较同一批任务的结果。
重点与难点：识别分母与代价。
情感态度价值观：依据证据判断。
学生误区：只比较成功数。
理解证据：说明效果与成本。
'''
PAGE = '''## 页面1 同批任务结果
- 页面角色：数据比较
- 页面中心句：B成功更多，复核时间也更多。
- 认知动作：区分效果与代价。
- 视觉论证：同分母并列比较。
- 上屏文字：A 90/100；B 96/100。
- 布局与阅读顺序：先读成功数，再读复核时间。
- 讲者配合：一次展示，说明测试条件。
- 制作模式：整页ImageGen
- 验收标准：分母相同，数值准确。
- 生图提示词：逐字显示上屏文案。Text policy: exact。
'''

class StructureTests(unittest.TestCase):
    def test_plain_explanation_needs_no_hook_or_audience_question(self):
        self.assertEqual(module.check(PLAIN)['errors'], [])

    def test_preamble_mentions_do_not_replace_section_headings(self):
        text = '本稿第一部分是口播，第二部分是页面，第三部分是框架。\n' + PLAIN
        self.assertEqual(module.check(text)['errors'], [])

    def test_section_names_in_prose_do_not_count_as_sections(self):
        text = PLAIN.replace('# 第一部分', '第一部分').replace('# 第二部分', '第二部分').replace('# 第三部分', '第三部分')
        self.assertIn('missing-major-section', {e['code'] for e in module.check(text)['errors']})

    def test_field_name_in_comment_does_not_count_as_content(self):
        broken = PLAIN.replace('- 对应知识点：百分点和复核成本。', '备注：待补对应知识点')
        self.assertIn('partial-mapping-fields', {e['code'] for e in module.check(broken)['errors']})

    def test_each_mapping_needs_its_own_knowledge(self):
        broken = PLAIN.replace('- 对应知识点：百分点和复核成本。\n', '')
        self.assertIn('partial-mapping-fields', {e['code'] for e in module.check(broken)['errors']})

    def test_later_mapping_cannot_supply_missing_field(self):
        broken = PLAIN.replace('- 对应知识点：百分点和复核成本。\n', '')
        second = '\n### 本段对应的知识点与PPT内容\n- 口播作用：复盘\n- 对应知识点：百分点\n- PPT内容：结果\n- 互动与过渡：收尾\n'
        broken = broken.replace('# 第二部分', second + '# 第二部分')
        self.assertIn('partial-mapping-fields', {e['code'] for e in module.check(broken)['errors']})

    def test_structural_success_does_not_certify_speech(self):
        warnings = {w['code'] for w in module.check(PLAIN)['warnings']}
        self.assertIn('oral-review-required', warnings)

    def test_full_slide_valid_contract(self):
        self.assertEqual(module.check_page_briefs(PAGE)['errors'], [])

    def test_full_slide_cannot_forbid_text(self):
        bad = PAGE.replace('逐字显示上屏文案。', 'NO text of any kind。')
        codes = {e['code'] for e in module.check_page_briefs(bad)['errors']}
        self.assertIn('full-slide-text-conflict', codes)

    def test_pending_mode_cannot_compile_prompt(self):
        bad = PAGE.replace('整页ImageGen', '待确认')
        codes = {e['code'] for e in module.check_page_briefs(bad)['errors']}
        self.assertIn('pending-mode-production', codes)

    def test_spoken_only_request_does_not_require_deck(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'speech.txt'
            path.write_text('先看这批任务的结果，再看复核花了多少时间。', encoding='utf-8')
            result = subprocess.run([sys.executable, str(SCRIPT), str(path), '--scope', 'spoken', '--audit-only', '--json'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertIn('oral-review-required', result.stdout)

    def test_empty_spoken_script_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'speech.txt'
            path.write_text('  ', encoding='utf-8')
            result = subprocess.run([sys.executable, str(SCRIPT), str(path), '--scope', 'spoken', '--audit-only', '--json'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1, result.stderr + result.stdout)

if __name__ == '__main__':
    unittest.main()
