import unittest

import drup
import cnfgen
from cnfgen.families.pigeonhole import PigeonholePrinciple
from pysat.formula import CNF
from pysat.solvers import Glucose4

def run_reduction(N, verbose=True):
    cnf = CNF(from_string=PigeonholePrinciple(N, N-1).to_dimacs()).clauses

    x = [[1 + (N-1)*i + j for j in range(N-1)] for i in range(N)]
    y = [[1 + N*(N-1) + (N-2)*i + j for j in range(N-2)] for i in range(N-1)]

    clauses = []
    for i in range(N-1):
        for j in range(N-2):
            clauses.append([y[i][j], -x[i][j]])
            clauses.append([y[i][j], -x[N-1][j], -x[i][N-2]])
            clauses.append([-y[i][j], x[i][j], x[N-1][j]])
            clauses.append([-y[i][j], x[i][j], x[i][N-2]])
        clauses.append([y[i][j] for j in range(N-2)])
    for i in range(N-1):
        for j in range(N-2):
            for k in range(i+1, N-1):
                clauses.append([-y[i][j], -y[k][j], x[i][N-2]])
                clauses.append([-y[i][j], -y[k][j]])

    width = max([len(str(c)) for c in clauses])

    g = Glucose4(bootstrap_with=cnf+clauses, with_proof=True)
    g.solve()
    pf2 = g.get_proof()
    p_len2 = len(pf2)

    pf2 = [c for c in pf2 if not c.strip().startswith('d')]
    rat_proof = clauses + [[int(l) for l in line.split()[:-1]] for line in pf2]

    result = drup.check_proof(cnf, rat_proof, verbose=verbose)

    if verbose:
      g = Glucose4(bootstrap_with=cnf, with_proof=True)
      g.solve()
      pf1 = g.get_proof()
      p_len1 = len(pf1)
      print(f'length from {p_len1} to {p_len2 + len(clauses)} (with {len(clauses)} reduction steps)')
      print(result)
    
    return result

class PHPTestCase(unittest.TestCase):
  
  def __init__(self, N):
    super().__init__()
    self.N = N

  def runTest(self):

    print(f"Checking PHP({self.N})...", end=' ')
    result = run_reduction(self.N, verbose=False)
    print(result)
    self.assertEqual(result.outcome, drup.Outcome.VALID)


def suite():
  suite = unittest.TestSuite()
  
  for n in range(3, 9):
    suite.addTest(PHPTestCase(n))
  
  return suite

if __name__ == '__main__':
  runner = unittest.TextTestRunner(verbosity=0)
  runner.run(suite())