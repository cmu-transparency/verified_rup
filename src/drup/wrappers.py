
from . import checker

def check_derivation(dimacs : str, cs : str) -> bool:
	"""Check a derivation against a DIMACS CNF formula.

	Args:
		dimacs (str): DIMACS CNF formula.
		cs (str): Sequence of RUP or RAT clauses.

	Returns:
		int: True if the derivation is valid, False otherwise.
	
	Raises:
		ValueError: If the formula or derivation cannot be parsed.
	"""
	result = checker.check_derivation(bytes(dimacs, 'utf-8'), bytes(cs, 'utf-8'))
	if result == -4:
		raise ValueError(
			"Error parsing formula. Check that the DIMACS input is properly formatted."
		)
	elif result == -5:
		raise ValueError(
			"Error parsing derivation. Check that the derivation input is properly formatted."
		)
	elif result == -6:
		raise ValueError(
			"Unknown error checking certificate. "
			"Please submit an issue at https://github.com/cmu-transparency/verified_rup/issues, "
			"including the formula and proof you are checking."
		)
	else:
		return result == 0

def check_lemma(dimacs : str, c : str) -> bool:
	"""Check a RUP or RAT lemma against a DIMACS CNF formula.

	Args:
		dimacs (str): DIMACS CNF formula.
		c (str): RUP or RAT lemma, or newline separated sequence of RUP or RAT clauses.

	Returns:
		int: True if the lemma is valid, False otherwise. If a list of lemmas is given,
		returns True if all lemmas are valid, False otherwise.
	
	Raises:
		ValueError: If the formula or lemma cannot be parsed.
	"""
	result = checker.check_step(bytes(dimacs, 'utf-8'), bytes(c, 'utf-8'))
	if result == -4:
		raise ValueError(
			"Error parsing formula. Check that the DIMACS input is properly formatted."
		)
	elif result == -5:
		raise ValueError(
			"Error parsing lemma. Check that the lemma input is properly formatted."
		)
	elif result == -6:
		raise ValueError(
			"Unknown error checking certificate. "
			"Please submit an issue at https://github.com/cmu-transparency/verified_rup/issues, "
			"including the formula and proof you are checking."
		)
	else:
		return result == 0

def check_proof_from_strings(dimacs : str, drup : str) -> bool:
	"""Check a DRUP proof for a DIMACS CNF formula.

	Args:
		dimacs (str): DIMACS CNF formula.
		drup (str): DRUP proof.

	Returns:
		int: True if the proof is valid, False otherwise.
	
	Raises:
		ValueError: If the formula or proof cannot be parsed.
	"""
	result = checker.check_proof_from_strings(bytes(dimacs, 'utf-8'), bytes(drup, 'utf-8'))
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
		return result == 0

def check_proof_from_files(dimacs : str, drup : str) -> bool:
	"""Check a DRUP proof for a DIMACS CNF formula,
	   reading the formula and proof from files.

	Args:
		dimacs (str): Path to a DIMACS CNF formula.
		drup (str): Path to a DRUP proof.

	Returns:
		int: True if the proof is valid, False otherwise.

	Raises:
		ValueError: If the formula or proof cannot be parsed, or either file cannot be opened.
	"""
	result = checker.check_proof_from_file(bytes(dimacs, 'utf-8'), bytes(drup, 'utf-8'))
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
		return result == 0