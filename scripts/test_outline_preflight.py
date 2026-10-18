import copy,unittest
from outline_preflight import check_preflight,digest

def example_review(outline):
    return {'version':1,'outline_sha256':digest(outline),
            'diagnosis':'已有对象与时间；目标和内容取舍需要对齐。','recommendation':'建议保留中心判断，把支线移到备查。',
            'checks':[{'id':k,'status':'provided' if k in ('audience','outcome','scope_time') else 'unknown','evidence':outline if k in ('audience','outcome','scope_time') else '','decision':'本单元测试只核对源绑定字段，语义另由行为测试检查。'} for k in ('audience','outcome','scope_time','claims_evidence','delivery')],
            'strengths':['保留用户主题主线。'],'risks':[],
            'critical_questions':[]}

class PreflightTests(unittest.TestCase):
    def test_complete_minimal_review_passes(self):
        r=example_review('主题与大纲');self.assertFalse(check_preflight('主题与大纲',r)['errors'])
    def test_changed_outline_rejects_review(self):
        self.assertTrue(check_preflight('新听众',example_review('旧大纲'))['errors'])
    def test_generic_pass_without_diagnosis_does_not_count(self):
        r=example_review('大纲');r['diagnosis']=''
        self.assertTrue(check_preflight('大纲',r)['errors'])
    def test_supplied_background_requires_real_evidence(self):
        r=example_review('大一新生');r['checks'][0].update(status='provided',evidence='已熟练编程')
        self.assertTrue(check_preflight('大一新生',r)['errors'])
    def test_no_risks_does_not_force_invented_problem(self):
        r=example_review('完整方案');r['recommendation']='当前框架适合目标，保留，不另加结构审批。'
        self.assertFalse(check_preflight('完整方案',r)['errors'])
    def test_followup_needs_design_consequence(self):
        r=example_review('大纲');r['critical_questions']=[{'id':'experience','dimension':'audience','question':'用过哪些工具？','why':''}]
        self.assertTrue(check_preflight('大纲',r)['errors'])
    def test_missing_review_dimension_rejected(self):
        r=example_review('大纲');r['checks'].pop()
        self.assertTrue(check_preflight('大纲',r)['errors'])
    def test_unknown_audience_cannot_be_silently_accepted(self):
        r=example_review('只给主题');r['checks'][0].update(status='unknown',evidence='')
        self.assertTrue(check_preflight('只给主题',r)['errors'])

if __name__=='__main__':unittest.main()
