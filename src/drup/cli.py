import sys
import argparse

from . import checker

def main():
	parser = argparse.ArgumentParser(
                    prog='drup',
                    description='Checks DRUP & DRAT proofs against DIMACS source.\nReturns 0 if the proof is valid, -1 if not, or a negative error code if the input is invalid.',
                    epilog='For more information visit https://github.com/cmu-transparency/verified_rup')
	parser.add_argument('dimacs', help='Path to a DIMACS CNF formula')
	parser.add_argument('drup', help='Path to a DRUP/DRAT proof')
	args = parser.parse_args()

	result = checker.check_proof_from_file(bytes(args.dimacs, 'utf-8'), bytes(args.drup, 'utf-8'))
	
	if result == -2:
		print(
			(
				f"Error parsing formula or file '{args.dimacs}' not found. " 
				f"Check that the DIMACS input is properly formatted."
			),
			file=sys.stderr
		)
		return -4
	elif result == -2:
		print(
			(
				f"Error parsing proof or file '{args.proof}' not found. " 
				f"Check that the proof input is properly formatted."
			),
			file=sys.stderr
		)
		return -5
	elif result == -6:
		print(
			(
				"Unknown error checking certificate. "
				"Please submit an issue at https://github.com/cmu-transparency/verified_rup/issues, "
				"including the formula and proof you are checking."
			),
			file=sys.stderr
		)
		return -6
	else:
		if result == 0:
			print("valid")
			return 0
		else:
			print("invalid")
			return -1

if __name__ == '__main__':
	main()