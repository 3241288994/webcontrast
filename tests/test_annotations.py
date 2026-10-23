import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from annotation_io import assemble, sha

class AssemblyTest(unittest.TestCase):
    def setUp(self):
        self.annotations=[dict(id='demo',observation_sha256=sha('exact page'))]
        self.observations=[dict(id='demo',observation='exact page')]
    def test_exact_join(self):
        self.assertEqual(assemble(self.annotations,self.observations)[0]['observation'],'exact page')
    def test_refuses_changed_observation(self):
        rows=copy.deepcopy(self.observations);rows[0]['observation']='different raw HTML'
        with self.assertRaisesRegex(ValueError,'hash mismatch'): assemble(self.annotations,rows)
    def test_refuses_missing(self):
        with self.assertRaisesRegex(ValueError,'Missing observation'): assemble(self.annotations,[])
    def test_refuses_duplicate(self):
        with self.assertRaisesRegex(ValueError,'Duplicate observation'): assemble(self.annotations,self.observations*2)

if __name__=='__main__':unittest.main()
