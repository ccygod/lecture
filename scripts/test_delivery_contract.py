import copy
import unittest
from check_delivery_contract import check,digest

class ContractTests(unittest.TestCase):
    def fixture(self, topic='管理'):
        cases={'管理':('降低成本不能靠省掉验收。','少一次检查，可能多一次返工。'),
               '科技':('工具降低起点，也可能放大能力差距。','同样起步，不同终点。'),
               '安全':('先确认断电再检修。','确认电源已隔离。'),
               '人文':('同一故事在不同叙述者口中会改变。','故事没换，读者站的位置换了。')}
        source,line=cases[topic]
        draft=f'<spoken>情境说明。{line}条件与机制解释。</spoken><slides>{line}</slides><notes>明确收窄适用范围。</notes>'
        c={'version':1,'source_sha256':digest(source),'draft_sha256':digest(draft),
           'regions':{k:{'start':f'<{k}>','end':f'</{k}>'} for k in ('spoken','slides','notes')},
           'claims':[{'id':'c','source_quote':source,'kind':'thesis','status':'preserved','spoken_quote':line,'on_slide':True,'slide_quote':line}],
           'landings':[{'id':'l','claim_id':'c','setup':'情境说明。','line':line,'explanation':'条件与机制解释。','semantic_review':'需要在真实写作中核对其含义。'}]}
        return source,draft,c
    def test_different_topics(self):
        for topic in ('管理','科技','人文'):
            with self.subTest(topic=topic): self.assertFalse(check(*self.fixture(topic))['errors'])
    def test_no_humor_required(self):
        s,d,c=self.fixture('安全');c['landings']=[];c['no_landings_reason']='紧急安全培训，直接清晰说明操作。'
        self.assertFalse(check(s,d,c)['errors'])
    def test_stale_draft(self):
        s,d,c=self.fixture();self.assertTrue(check(s,d+'新修改',c)['errors'])
    def test_stale_source(self):
        s,d,c=self.fixture();self.assertTrue(check(s+'补充主张',d,c)['errors'])
    def test_missing_claim_in_spoken_even_when_in_slide(self):
        s,d,c=self.fixture();line=c['claims'][0]['spoken_quote'];d=d.replace(line,'无关文字',1);c['draft_sha256']=digest(d)
        self.assertTrue(check(s,d,c)['errors'])
    def test_missing_slide(self):
        s,d,c=self.fixture();c['claims'][0]['slide_quote']='不存在的页面文案'
        self.assertTrue(check(s,d,c)['errors'])
    def test_undisclosed_rewrite(self):
        s,d,c=self.fixture();c['claims'][0]['status']='qualified'
        self.assertTrue(check(s,d,c)['errors'])
    def test_disclosed_rewrite(self):
        s,d,c=self.fixture();c['claims'][0].update(status='qualified',reason='范围太广',disclosure_quote='明确收窄适用范围。')
        self.assertFalse(check(s,d,c)['errors'])
    def test_fake_source(self):
        s,d,c=self.fixture();c['claims'][0]['source_quote']='模型自行发明的用户主张'
        self.assertTrue(check(s,d,c)['errors'])
    def test_reversed_setup(self):
        s,d,c=self.fixture();c['landings'][0]['setup']='条件与机制解释。'
        self.assertTrue(check(s,d,c)['errors'])
    def test_duplicate_boundaries(self):
        s,d,c=self.fixture();d+='<spoken>';c['draft_sha256']=digest(d)
        self.assertTrue(check(s,d,c)['errors'])
    def test_unknown_claim(self):
        s,d,c=self.fixture();c['landings'][0]['claim_id']='absent'
        self.assertTrue(check(s,d,c)['errors'])
    def test_empty_inventory(self):
        s,d,c=self.fixture();c['claims']=[];self.assertTrue(check(s,d,c)['errors'])
    def test_spoken_only(self):
        s,d,c=self.fixture();del c['regions']['slides'];c['claims'][0]['on_slide']=False
        self.assertFalse(check(s,d,c)['errors'])



class FlexibleDeliveryTests(unittest.TestCase):
    def test_explanation_before_summary_is_valid(self):
        s,d,c=ContractTests().fixture()
        row=c['landings'][0];d=d.replace(row['line']+row['explanation'],row['explanation']+row['line'])
        c.update(version=2,draft_sha256=digest(d));row['sequence']=['setup','explanation','line']
        self.assertFalse(check(s,d,c)['errors'])
    def test_declared_sequence_must_match_actual_order(self):
        s,d,c=ContractTests().fixture();c['version']=2;c['landings'][0]['sequence']=['setup','explanation','line']
        self.assertTrue(check(s,d,c)['errors'])
    def test_sequence_cannot_drop_explanation(self):
        s,d,c=ContractTests().fixture();c['version']=2;c['landings'][0]['sequence']=['setup','line']
        self.assertTrue(check(s,d,c)['errors'])
    def test_two_supports_can_be_in_same_paragraph(self):
        s,d,c=ContractTests().fixture();c['version']=2;c['landings'][0]['sequence']=['setup','line','explanation']
        self.assertFalse(check(s,d,c)['errors'])

if __name__=='__main__': unittest.main()
