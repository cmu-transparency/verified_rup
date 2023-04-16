
from . import checker

def check_from_strings(dimacs, drup):
	"""Check a DRUP proof for a DIMACS CNF formula.

	Args:
		dimacs (str): DIMACS CNF formula.
		drup (str): DRUP proof.

	Returns:
		int: 0 if the proof is valid, -1 otherwise.
	
	Raises:
		ValueError: If the formula or proof cannot be parsed.
	"""
	result = checker.check_from_strings(bytes(dimacs, 'utf-8'), bytes(drup, 'utf-8'))
	if result == -4:
		raise ValueError(
			"Error parsing formula. Check that the DIMACS input is properly formatted."
		)
	elif result == -5:
		raise ValueError(
			"Error parsing proof. Check that the DRUP input is properly formatted."
		)
	elif result == -6:
		raise ValueError(
			"Unknown error checking certificate. "
			"Please submit an issue at https://github.com/cmu-transparency/verified_rup/issues, "
			"including the formula and proof you are checking."
		)
	else:
		return result

def check_from_files(dimacs, drup):
	"""Check a DRUP proof for a DIMACS CNF formula,
	   reading the formula and proof from files.

	Args:
		dimacs (str): Path to a DIMACS CNF formula.
		drup (str): Path to a DRUP proof.

	Returns:
		int: 0 if the proof is valid, -1 otherwise.

	Raises:
		ValueError: If the formula or proof cannot be parsed, or either file cannot be opened.
	"""
	result = checker.check_from_file(bytes(dimacs, 'utf-8'), bytes(drup, 'utf-8'))
	if result == -2:
		raise ValueError(
			f"Error parsing formula or file '{dimacs}' not found. " 
			f"Check that the DIMACS input is properly formatted."
		)
	elif result == -3:
		raise ValueError(
			f"Error parsing proof or file '{drup}' not found. "
			f"Check that the DRUP input is properly formatted."
		)
	elif result == -6:
		raise ValueError(
			"Unknown error checking certificate. "
			"Please submit an issue at https://github.com/cmu-transparency/verified_rup/issues, "
			"including the formula and proof you are checking."
		)
	else:
		return result