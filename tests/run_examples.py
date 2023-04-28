import os
import unittest
import glob
import drup

from drup import Outcome

class ProofExampleTestCase(unittest.TestCase):
  
  def __init__(self, dimacs, proof):
    super().__init__()
    self.dimacs = dimacs
    self.proof = proof
  
  def test_from_file(self):
    print(f"Checking {self.dimacs} and {self.proof} from file...")
    outcome = Outcome.VALID if not 'invalid' in self.dimacs else Outcome.INVALID
    self.assertEqual(drup.check_proof_from_files(self.dimacs, self.proof).outcome, outcome)

  def test_from_string(self):
    print(f"Checking {self.dimacs} and {self.proof} from string...")
    with open(self.dimacs, 'r') as f:
      dimacs = f.read()
    with open(self.proof, 'r') as f:
      proof = f.read()
    outcome = Outcome.VALID if not 'invalid' in self.dimacs else Outcome.INVALID
    self.assertEqual(drup.check_proof_from_strings(dimacs, proof).outcome, outcome)

  def test_corrupt_proof(self):
    print(f"Checking {self.dimacs} and {self.proof} with corrupted drup...")
    with open(self.dimacs, 'r') as f:
      dimacs = f.read()
    with open(self.proof, 'r') as f:
      proof = f.read()
    proof_lines = proof.splitlines()
    proof = '\n'.join(proof_lines[len(proof_lines)//2:])
    self.assertEqual(drup.check_proof_from_strings(dimacs, proof).outcome, Outcome.INVALID)

  def test_from_corrupted_file(self):
    print(f"Checking {self.dimacs} and {self.proof} with corrupted path...")
    with self.assertRaises(FileNotFoundError):
      drup.check_proof_from_files(self.dimacs + '.bogus', self.proof)
    with self.assertRaises(FileNotFoundError):
      drup.check_proof_from_files(self.dimacs, self.proof + '.bogus')

  def test_derivations(self):
    if not 'invalid' in self.dimacs:
      with open(self.dimacs, 'r') as f:
        dimacs = f.read()
      with open(self.proof, 'r') as f:
        proof = f.read()
      for i, line in enumerate(proof.splitlines()):
        line = line.strip()
        if line.startswith('d'):
          continue
        print(f"Checking {self.dimacs} and {self.proof}:{i}...")
        self.assertEqual(drup.check_derivation_from_strings(dimacs, line).outcome, Outcome.VALID)
        dimacs = f"{dimacs}\n{line}"
    else:
      self.skipTest("Skipping derivations for invalid formula")

  def runTest(self):
    self.test_from_file()
    self.test_from_string()
    self.test_derivations()
    self.test_corrupt_proof()
    self.test_from_corrupted_file()

def suite():
  suite = unittest.TestSuite()

  for dimacs in glob.glob("tests/examples/*.cnf"):
    base = os.path.basename(dimacs)
    dir = os.path.dirname(dimacs)
    test = base.split(".")[0]
    if os.path.exists(f'{dir}/{test}.drup'):
      proof = f'{dir}/{test}.drup'
      suite.addTest(ProofExampleTestCase(dimacs, proof))
    if os.path.exists(f'{dir}/{test}.drat'):
      proof = f'{dir}/{test}.drat'
      suite.addTest(ProofExampleTestCase(dimacs, proof))
  
  return suite

if __name__ == '__main__':
  runner = unittest.TextTestRunner(verbosity=0)
  runner.run(suite())