import copy
import unittest
from scene_review import packet, accept

class SceneTests(unittest.TestCase):
    def setUp(self):
        self.spoken=['假设要做课表。', '读到旧通知。', '文件打开却不能用。', '先查学期，再查来源。', '任务做成要看条件。']
        self.plan={'scenes':[{'id':'s','kind':'case','basis':{'status':'hypothetical','evidence':'教学设想'}, 'anchors':{'goal':self.spoken[0], 'obstacle':self.spoken[1], 'consequence':self.spoken[2], 'response':self.spoken[3], 'insight':self.spoken[4]}}]}
    def test_context_extracted_from_spoken(self):
        p=packet(self.spoken,self.plan)
        self.assertEqual(p['scenes'][0]['context'],self.spoken)
    def test_meta_quote_rejected(self):
        p=copy.deepcopy(self.plan);p['scenes'][0]['anchors']['goal']='只存在于映射'
        with self.assertRaises(ValueError):packet(self.spoken,p)
    def test_unknown_basis_rejected(self):
        p=copy.deepcopy(self.plan);p['scenes'][0]['basis']['status']='everyone_believes'
        with self.assertRaises(ValueError):packet(self.spoken,p)
    def test_callback_cannot_precede_introduction(self):
        p={'scenes':[{'id':'c','kind':'callback','basis':{'status':'hypothetical','evidence':'设想'},'anchors':{'introduction':self.spoken[4],'payoff':self.spoken[0]}}]}
        with self.assertRaises(ValueError):packet(self.spoken,p)
    def test_plain_does_not_need_story(self):
        self.assertEqual(packet(self.spoken,{'scenes':[]})['scenes'],[])
    def test_review_is_invalidated_by_draft_change(self):
        p=packet(self.spoken,self.plan);r={'packet_sha256':p['packet_sha256'],'items':[{'id':'s','grounded':True,'relation_preserved':True,'speakable':True,'useful':True,'feedback':'先查学期对应旧材料问题。'}]}
        self.assertTrue(accept(p,r)['accepted'])
        changed=packet(self.spoken+['增加一个转场。'],self.plan)
        with self.assertRaises(ValueError):accept(changed,r)
    def test_failed_semantic_gate_blocks_acceptance(self):
        p=packet(self.spoken,self.plan);r={'packet_sha256':p['packet_sha256'],'items':[{'id':'s','grounded':False,'relation_preserved':True,'speakable':True,'useful':True,'feedback':'凭空推断学生都持此误解。'}]}
        self.assertFalse(accept(p,r)['accepted'])
    def test_analogy_needs_relation_and_return(self):
        p=copy.deepcopy(self.plan);p['scenes'][0]['kind']='analogy'
        with self.assertRaises(ValueError):packet(self.spoken,p)
    def causal(self):
        return {'scenes':[{'id':'causal','kind':'causal','basis':{'status':'hypothetical','evidence':'明确教学假设'},'anchors':{'baseline':self.spoken[0],'intervention':self.spoken[1],'mediating_change':self.spoken[2],'outcome':self.spoken[3],'boundary':self.spoken[4]}}]}
    def test_causal_packet_extracts_mechanism(self):
        p=packet(self.spoken,self.causal())
        self.assertEqual(p['scenes'][0]['positions']['mediating_change'],2)
    def test_causal_claim_without_baseline_is_rejected(self):
        p=self.causal();del p['scenes'][0]['anchors']['baseline']
        with self.assertRaises(ValueError):packet(self.spoken,p)
    def test_causal_claim_without_intervention_is_rejected(self):
        p=self.causal();del p['scenes'][0]['anchors']['intervention']
        with self.assertRaises(ValueError):packet(self.spoken,p)
    def test_causal_review_cannot_promote_false_relation(self):
        p=packet(self.spoken,self.causal());r={'packet_sha256':p['packet_sha256'],'items':[{'id':'causal','grounded':True,'relation_preserved':False,'speakable':True,'useful':True,'feedback':'仅原有认真程度不同，没有技术改变的中间过程。'}]}
        self.assertFalse(accept(p,r)['accepted'])

if __name__=='__main__':unittest.main()
