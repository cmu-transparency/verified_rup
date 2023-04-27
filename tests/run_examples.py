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

    def test_derivations(self):
        print(f"Checking {self.dimacs} and {self.proof} as derivations...")
        with open(self.dimacs, 'r') as f:
            dimacs = f.read()
        with open(self.proof, 'r') as f:
            proof = f.read()
        for line in proof.splitlines():
            if line.startswith('d'):
                continue
            if line == '-49 0':
                import pdb
                pdb.set_trace()
            result = drup.check_lemma(f"{dimacs.strip()}\n{line}", line)
            print(f"Checking lemma: {line} = {result}")
            if not drup.check_lemma(f"{dimacs.strip()}\n{line}", line):
                print(f"Failed lemma [{self.proof}]: {line}")
            else:
                dimacs = f"{dimacs.strip()}\n{line}"
            self.assertEqual(drup.check_lemma(f"{dimacs}\n{line}", line), True)

        # # print(f"Checking derivation: {self.proof}: {drup.check_proof_from_strings(dimacs, proof)}")
        try:
            print(f"Checking derivation: {self.proof}: {drup.check_proof_from_files(self.dimacs, self.proof)}")
        except:
            print(f"Failed derivation [{self.proof}]: {proof}")
        
        # self.assertEqual(drup.check_derivation(dimacs, proof), True)
    
    def runTest(self):
        self.test_derivations()
        # self.test_from_file()
        # self.test_from_string()
        # self.test_corrupt_proof()
        # self.test_from_corrupted_file()

def suite():
    suite = unittest.TestSuite()

    # for dimacs in glob.glob("tests/examples/*.cnf"):
    #     base = os.path.basename(dimacs)
    #     dir = os.path.dirname(dimacs)
    #     test = base.split(".")[0]
    #     if os.path.exists(f'{dir}/{test}.drup'):
    #         proof = f'{dir}/{test}.drup'
    #         suite.addTest(ProofExampleTestCase(dimacs, proof))
    #     if os.path.exists(f'{dir}/{test}.drat'):
    #         proof = f'{dir}/{test}.drat'
    #         suite.addTest(ProofExampleTestCase(dimacs, proof))
    suite.addTest(ProofExampleTestCase("tests/examples/uuf-50-3.cnf", "tests/examples/uuf-50-3.drat"))
    
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=0)
    runner.run(suite())