import unittest
import hashlib
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
import editor_workflow as workflow


class SourceEpisodeTests(unittest.TestCase):
    def test_hunzi_episode_has_visual_source_and_interpretation_boundary(self):
        row=workflow.source_episode('hunzi_relations_to_diagram')
        self.assertEqual(row['source']['kind'],'attributed_visual_repost')
        self.assertTrue(row['source']['visual_locations'])
        self.assertTrue(row['interpretation_boundary'])
        self.assertTrue(row['observed_sequence'])

    def test_luo_episode_has_contiguous_source_locator(self):
        row=workflow.source_episode('luo_supplier_reconsideration')
        self.assertEqual(row['source']['kind'],'edited_speech')
        self.assertLess(row['source']['char_span'][0],row['source']['char_span'][1])

    def test_unknown_episode_is_not_silently_substituted(self):
        with self.assertRaises(ValueError):workflow.source_episode('invented')

    def test_mechanism_episode_references_resolve(self):
        p=workflow.plan({'humor':'off','beats':[{'id':'x','claim_id':'c','need':'explain_mechanism'}]})
        ids=[ident for card in p['beats'][0]['options'] for ident in card.get('episode_ids',[])]
        self.assertTrue(ids)
        for ident in ids:self.assertEqual(workflow.source_episode(ident)['id'],ident)

    def fixture(self,directory,kind='edited_speech'):
        body='开头。正常尝试遇到具体问题，然后改变做法。后文。'
        source={'kind':kind,'body_sha256':hashlib.sha256(body.encode()).hexdigest(),'char_span':[3,len(body)-3]}
        source['span_sha256']=hashlib.sha256(body[3:-3].encode()).hexdigest()
        manifest=Path(directory)/'episodes.json';manifest.write_text(json.dumps({'episodes':[{'id':'test','source':source}]}))
        return body,manifest

    def test_actual_source_read_is_bound_to_body_and_span(self):
        with tempfile.TemporaryDirectory() as td:
            body,manifest=self.fixture(td)
            with patch.object(workflow,'EPISODES',manifest):row=workflow.source_episode('test',source_body=body)
            self.assertEqual(row['reading_material']['text'],body[3:-3])
            self.assertFalse(row['reading_material']['comprehension_verified'])

    def test_wrong_source_body_cannot_be_used_as_actual_original(self):
        with tempfile.TemporaryDirectory() as td:
            body,manifest=self.fixture(td)
            with patch.object(workflow,'EPISODES',manifest):
                with self.assertRaises(ValueError):workflow.source_episode('test',source_body=body+'改动')

    def test_visual_source_uses_actual_file_hash_without_claiming_viewed(self):
        with tempfile.TemporaryDirectory() as td:
            body,manifest=self.fixture(td,'attributed_visual_repost');f=Path(td)/'source.png';f.write_bytes(b'synthetic image identity fixture')
            obj=json.loads(manifest.read_text());obj['episodes'][0]['source']['visual_locations']=[{'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'url':'https://example.org/source.png'}];manifest.write_text(json.dumps(obj))
            with patch.object(workflow,'EPISODES',manifest):row=workflow.source_episode('test',image_files=[f])
            self.assertFalse(row['reading_material']['visual_reading_verified'])
            f.write_bytes(b'changed')
            with patch.object(workflow,'EPISODES',manifest):
                with self.assertRaises(ValueError):workflow.source_episode('test',image_files=[f])


if __name__=='__main__':unittest.main()
