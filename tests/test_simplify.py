import sys
sys.path.append('.')

import drup

cnf = [[1, 2, 3], [-1, 2, 3], [1, -2, 3], [1, 2, -3], [-1, -2, 3], [-1, 2, -3], [1, -2, -3], [-1, -2, -3]]

cnf = drup.extend_and_simplify(cnf, [1,3])
cnf = drup.extend_and_simplify(cnf, [-1, -3])
cnf = drup.extend_and_simplify(cnf, [-1])
print(cnf)