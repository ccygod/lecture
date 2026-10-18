import hashlib
import unittest
from source_grounding import check

class SourceGroundingTests(unittest.TestCase):
    def setUp(self):
        self.body='开场说明一个问题。接着展示两种做法。再解释为什么结果不同。最后回到问题。'
        self.manifest={'sources':[{'id':'a','kind':'edited_speech','body_sha256':hashlib.sha256(self.body.encode()).hexdigest(),'extent':'complete_page','reviewed_ranges':[[0,len(self.body)]]}], 'analyses':[{'id':'m','source_id':'a','start':0,'end':len(self.body),'span_sha256':hashlib.sha256(self.body.encode()).hexdigest(),'inference':'从做法到不同结果的解释。'}]}
    def test_actual_body_can_support_analysis(self):
        self.assertEqual(check(self.manifest,{'a':self.body})['errors'],[])
    def test_changed_body_invalidates_analysis(self):
        self.assertTrue(check(self.manifest,{'a':self.body+'新句'})['errors'])
    def test_catalogue_cannot_be_used_as_transcript(self):
        self.manifest['sources'][0]['kind']='catalogue'
        self.assertTrue(check(self.manifest,{'a':self.body})['errors'])
    def test_summary_cannot_claim_complete_speech(self):
        self.manifest['sources'][0].update(kind='live_summary',extent='complete_speech_verified')
        self.assertTrue(check(self.manifest,{'a':self.body})['errors'])
    def test_span_must_match_actual_body(self):
        self.manifest['analyses'][0]['span_sha256']='bad'
        self.assertTrue(check(self.manifest,{'a':self.body})['errors'])
    def test_unreviewed_span_is_rejected(self):
        self.manifest['sources'][0]['reviewed_ranges']=[[0,5]]
        self.assertTrue(check(self.manifest,{'a':self.body})['errors'])
    def test_no_false_human_validation(self):
        r=check(self.manifest,{'a':self.body})
        self.assertEqual(r['read_and_interpretation_verified'],False)
    def test_known_interstitial_is_rejected_even_if_mislabelled(self):
        b='appkey: "CF_APP_WAF"; var requestInfo = {"data":""};'
        self.manifest['sources'][0]['body_sha256']=hashlib.sha256(b.encode()).hexdigest()
        self.manifest['sources'][0]['reviewed_ranges']=[[0,len(b)]]
        self.manifest['analyses'][0].update(start=0,end=len(b),span_sha256=hashlib.sha256(b.encode()).hexdigest())
        self.assertTrue(check(self.manifest,{'a':b})['errors'])
    def test_complete_speech_claim_requires_verification_record(self):
        self.manifest['sources'][0].update(kind='transcript',extent='complete_speech_verified')
        self.assertTrue(check(self.manifest,{'a':self.body})['errors'])

if __name__=='__main__':unittest.main()
