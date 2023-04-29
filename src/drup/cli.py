__all__ = []

import sys
import argparse

from drup.wrappers import (
  check_proof_from_files,
  check_derivation_from_files
)

def main():
	parser = argparse.ArgumentParser(
                    prog='drup',
                    description='Checks DRUP & DRAT proofs against DIMACS source.\nReturns 0 if the proof is valid, -1 if not, or a negative error code if the input is invalid.',
                    epilog='For more information visit https://github.com/cmu-transparency/verified_rup')
	parser.add_argument('dimacs', help='Path to a DIMACS CNF formula')
	parser.add_argument('drup', help='Path to a DRUP/DRAT proof')
	parser.add_argument('-d', '--derivation', action='store_true', help='Check each step, ignore absence of empty clause')
	parser.add_argument('-v', '--verbose', action='store_true', help='Print detailed information about failed checks')
	args = parser.parse_args()

	if not args.derivation:
		print(check_proof_from_files(args.dimacs, args.drup, verbose=args.verbose))
	else:
		print(check_derivation_from_files(args.dimacs, args.drup, verbose=args.verbose))

if __name__ == '__main__':
	main()