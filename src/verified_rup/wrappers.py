
from . import checker

def check_from_strings(dimacs, drup):
	"""Check a DRUP proof for a DIMACS CNF formula.

	Args:
		dimacs (str): DIMACS CNF formula.
		drup (str): DRUP proof.

	Returns:
		int: 0 if the proof is valid, -1 otherwise.
	"""
	return checker.check_from_strings(bytes(dimacs, 'utf-8'), bytes(drup, 'utf-8'))

def check_from_files(dimacs, drup):
	"""Check a DRUP proof for a DIMACS CNF formula.

	Args:
		dimacs (str): Path to a DIMACS CNF formula.
		drup (str): Path to a DRUP proof.

	Returns:
		int: 0 if the proof is valid, -1 otherwise.
	"""
	return checker.check_from_file(bytes(dimacs, 'utf-8'), bytes(drup, 'utf-8'))