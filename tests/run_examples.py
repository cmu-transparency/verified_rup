import os
import unittest
import glob
import drup

class ProofExampleTestCase(unittest.TestCase):
    
    def __init__(self, dimacs, proof):
        super().__init__()
        self.dimacs = dimacs
        self.proof = proof
    
    def test_from_file(self):
        print(f"Checking {self.dimacs} and {self.proof} from file...")
        self.assertEqual(drup.check_proof_from_files(self.dimacs, self.proof), True)

    def test_from_string(self):
        print(f"Checking {self.dimacs} and {self.proof} from string...")
        with open(self.dimacs, 'r') as f:
            dimacs = f.read()
        with open(self.proof, 'r') as f:
            proof = f.read()
        self.assertEqual(drup.check_proof_from_strings(dimacs, proof), True)

    def test_corrupt_proof(self):
        print(f"Checking {self.dimacs} and {self.proof} with corrupted drup...")
        with open(self.dimacs, 'r') as f:
            dimacs = f.read()
        with open(self.proof, 'r') as f:
            proof = f.read()
        proof_lines = proof.splitlines()
        proof = '\n'.join(proof_lines[len(proof_lines)//2:])
        self.assertEqual(drup.check_proof_from_strings(dimacs, proof), False)

    def test_from_corrupted_file(self):
        print(f"Checking {self.dimacs} and {self.proof} with corrupted path...")
        with self.assertRaises(ValueError):
            drup.check_proof_from_files(self.dimacs + '.bogus', self.proof)
        with self.assertRaises(ValueError):
            drup.check_proof_from_files(self.dimacs, self.proof + '.bogus')
    
    def runTest(self):
        self.test_from_file()
        self.test_from_string()
        self.test_corrupt_proof()
        self.test_from_corrupted_file()

def suite():
    suite = unittest.TestSuite()

    for dimacs in glob.glob("tests/examples/*.cnf"):
        base = os.path.basename(dimacs)
        dir = os.path.dirname(dimacs)
        test = base.split(".")[0]
        if not os.path.exists(f'{dir}/{test}.drup'):
            continue
        proof = f'{dir}/{test}.drup'
        suite.addTest(ProofExampleTestCase
    (dimacs, proof))
    
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=0)
    runner.run(suite())