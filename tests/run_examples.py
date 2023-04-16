import os
import unittest
import glob
import rup

class ExampleTestCase(unittest.TestCase):
    
    def __init__(self, dimacs, drup):
        super().__init__()
        self.dimacs = dimacs
        self.drup = drup
    
    def test_from_file(self):
        print(f"Checking {self.dimacs} and {self.drup} from file...")
        self.assertEqual(rup.check_from_files(self.dimacs, self.drup), 0)

    def test_from_string(self):
        print(f"Checking {self.dimacs} and {self.drup} from string...")
        with open(self.dimacs, 'r') as f:
            dimacs = f.read()
        with open(self.drup, 'r') as f:
            drup = f.read()
        self.assertEqual(rup.check_from_strings(dimacs, drup), 0)

    def test_corrupt_proof(self):
        print(f"Checking {self.dimacs} and {self.drup} with corrupted proof...")
        with open(self.dimacs, 'r') as f:
            dimacs = f.read()
        with open(self.drup, 'r') as f:
            drup = f.read()
        drup_lines = drup.splitlines()
        drup = '\n'.join(drup_lines[len(drup_lines)//2:])
        self.assertEqual(rup.check_from_strings(dimacs, drup), -1)

    def test_from_file(self):
        print(f"Checking {self.dimacs} and {self.drup} with corrupted path...")
        with self.assertRaises(ValueError):
            rup.check_from_files(self.dimacs + '.bogus', self.drup)
        with self.assertRaises(ValueError):
            rup.check_from_files(self.dimacs, self.drup + '.bogus')
    
    def runTest(self):
        self.test_from_file()
        self.test_from_string()
        self.test_corrupt_proof()

def suite():
    suite = unittest.TestSuite()

    for dimacs in glob.glob("tests/examples/*.cnf"):
        base = os.path.basename(dimacs)
        dir = os.path.dirname(dimacs)
        test = base.split(".")[0]
        if not os.path.exists(f'{dir}/{test}.drup'):
            continue
        drup = f'{dir}/{test}.drup'
        suite.addTest(ExampleTestCase
    (dimacs, drup))
    
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=0)
    runner.run(suite())