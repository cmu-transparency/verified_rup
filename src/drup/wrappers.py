from typing import Iterable, Optional
from enum import Enum

import ctypes

from pysat.formula import CNF as pyCnf

from . import (
	Chain_struct,
	checker,
	Clause_struct,
	Cnf_struct,
	Lit_struct,
	Ratinfo_struct,
	Result_struct,
	Rupinfo_struct
)

Lit = int
Clause = Iterable[Lit]
Cnf = Iterable[Clause]
Chain = Iterable[Lit]
Proof = Cnf

Outcome = Enum("Outcome", ["VALID", "INVALID"])

class RupInfo:

	def __init__(self, clause : Clause, chain : Chain):
		self.clause = clause
		self.chain = chain

	def __str__(self):
		return f"RupInfo({str(self.clause)}, {str(self.chain)})"

class RatInfo:

	def __init__(self, clause : Clause, pivot_clause : Clause, rup_info : RupInfo):
		self.clause = clause
		self.pivot_clause = pivot_clause
		self.rup_info = rup_info

	def __str__(self):
		return f"RatInfo({str(self.clause)}, {str(self.pivot_clause)}, {str(self.rup_info)})"

class CheckerResult:

	def __init__(self, outcome : Outcome, steps : Optional[Cnf], rup_info : Optional[RupInfo], rat_info : Optional[RatInfo]):
		self.outcome = outcome
		self.steps = steps
		self.rup_info = rup_info
		self.rat_info = rat_info

	def __str__(self):
		if self.outcome == Outcome.VALID:
			return f"CheckerResult({self.outcome})"
		else:
			if self.steps is not None and self.rup_info is not None and self.rat_info is not None:
				steps = " ".join(str(step) for step in self.steps)
				rup = str(self.rup_info)
				rat = str(self.rat_info)
				return f"CheckerResult({self.outcome}, [{steps}], {rup}, {rat})"
			else:
				return f"CheckerResult({self.outcome})"

def clause_to_struct(lits : Clause) -> Clause_struct:
	"""Convert a list of literals to a Clause_struct struct.

	Args:
		lits (Clause): Iterable of literals, represented as integers. The
		list need not end with a 0, as 0 is a valid positive literal.

	Returns:
		Clause_struct: Clause_struct struct representing the list of literals.
	"""
	clause = Clause_struct()
	clause.len = len(lits)
	clause.lits = (Lit_struct * clause.len)()
	for i, lit in enumerate(lits):
		clause.lits[i].var = abs(lit)
		clause.lits[i].sign = -1 if lit < 0 else 1
	return clause

def cnf_to_struct(clauses : Cnf) -> Cnf_struct:
	"""Convert a list of clauses to a Cnf_struct struct.

	Args:
		clauses (Cnf): Iterable of clauses, each represented as a list of integers.
		Negative integers represent negated literals, and clauses need not end with 0.

	Returns:
		Cnf_struct: Cnf_struct struct representing the list of clauses.
	"""
	struct = Cnf_struct()
	struct.len = len(clauses)
	struct.clauses = (Clause_struct * struct.len)()
	for i, clause in enumerate(clauses):
		struct.clauses[i] = clause_to_struct(clause)
	return struct

def struct_to_clause(clause : Clause_struct) -> Clause:
	"""Convert a Clause_struct struct to a list of literals.

	Args:
		clause (Clause_struct): Clause_struct struct representing a clause.

	Returns:
		Clause: List of literals, represented as integers.
	"""
	def sign(x : int):
		return -1 if x <= 0 else 1
	return [clause.lits[i].var * sign(clause.lits[i].sign) for i in range(clause.len)]

def struct_to_cnf(cnf : Cnf_struct) -> Cnf:
	"""Convert a Cnf_struct struct to a list of clauses.

	Args:
		Cnf_struct (Cnf_struct): Cnf_struct struct representing a CNF formula.

	Returns:
		Cnf: List of clauses, each represented as a list of integers.
	"""
	return [struct_to_clause(cnf.clauses[i]) for i in range(cnf.len)]

def struct_to_chain(chain : Chain_struct) -> Chain:
	"""Convert a Chain_struct struct to a list of literals.

	Args:
		chain (Chain_struct): Chain_struct struct representing a chain.

	Returns:
		Chain: List of literals, represented as integers.
	"""
	def sign(x : int):
		return -1 if x <= 0 else 1
	return [chain.lits[i].var * sign(chain.lits[i].sign) for i in range(chain.len)]

def check_proof_from_structs(
	formula : Cnf_struct, 
	proof : Cnf_struct, 
	verbose : bool = False
) -> CheckerResult:
	"""Check a derivation against a DIMACS Cnf_struct formula.

	Args:
		formula (Cnf_struct): Cnf_struct as a ctypes struct.
		proof (Cnf_struct): Sequence of RUP or RAT clauses.
		verbose (bool, optional): Return detailed information
			if the check fails. Defaults to False.

	Returns:
		CheckerResult: CheckerResult struct representing the result of the check.
	
	Raises:
		ValueError: If the formula or derivation cannot be parsed.
	"""
	result = checker.check_from_data(ctypes.byref(formula), ctypes.byref(proof)).contents
	if result.valid > 0:
		checker.free_result(result)
		return CheckerResult(Outcome.VALID, None, None, None)
	else:
		if verbose:
			res =   CheckerResult(
						Outcome.INVALID,
						struct_to_cnf(result.steps),
						RupInfo(
							struct_to_clause(result.rup_info.clause),
							struct_to_chain(result.rup_info.chain)
						),
						RatInfo(
							struct_to_clause(result.rat_info.clause),
							struct_to_clause(result.rat_info.pivot_clause),
							RupInfo(
								struct_to_clause(result.rat_info.rup_info.clause),
								struct_to_chain(result.rat_info.rup_info.chain)
							)
						)
					)
		else:
			res = CheckerResult(Outcome.INVALID, None, None, None)
		
		if result.valid == 0:
			checker.free_rup_info(result.rup_info)
			checker.free_result(result)
		else:
			checker.free_rup_info(result.rup_info)
			checker.free_rat_info(result.rat_info)
			checker.free_result(result)
		
		return res

def check_proof_from_iterables(formula : Cnf, proof : Proof, verbose : bool = False) -> CheckerResult:
	"""Check a sequence of RUP and RAT clauses against a CNF.

	Args:
		formula (Cnf): Cnf as a list of lists of integers.
		proof (Cnf): Sequence of RUP or RAT clauses.
		verbose (bool, optional): Return detailed information
			if the check fails. Defaults to False.

	Returns:
		CheckerResult: CheckerResult struct representing the result of the check.
	
	Raises:
		ValueError: If the formula or proof cannot be formatted.
	"""
	return check_proof_from_structs(cnf_to_struct(formula), cnf_to_struct(proof), verbose)

def check_proof_from_strings(formula : str, proof : str, verbose : bool = False) -> CheckerResult:
	"""Check a sequence of RUP and RAT clauses against a CNF.

	Args:
		formula (str): Cnf as a string in DIMACS format. The header
			is ignored if present.
		proof (str): Sequence of RUP or RAT clauses format.
		verbose (bool, optional): Return detailed information
			if the check fails. Defaults to False.
	
	Returns:
		CheckerResult: CheckerResult struct representing the result of the check.

	Raises:
		ValueError: If the formula or proof cannot be parsed or formatted.
	"""
	def read_clauses(clauses : str) -> Cnf:
		clauses = clauses.replace('\n', '')
		lines = [
			line.strip() for line in clauses.split(' 0')
			if 	not line.strip().startswith('c') and 
				not line.strip().startswith('d') and 
				not line.strip().startswith('p') and
				not line.strip() == '0' and
				not len(line.strip()) == 0
		]
		return [list(map(int, line.split(' '))) for line in lines]
	try:
		if '\n' in formula and formula.split('\n')[0].strip().startswith('p'):
			formula = '\n'.join(formula.split('\n')[1:])
		formula = read_clauses(formula)
	except:
		raise ValueError("Error parsing formula. Check that the input is properly formatted.")
	try:
		proof = read_clauses(proof)
	except:
		raise ValueError("Error parsing proof. Check that the input is properly formatted.")

	return check_proof_from_iterables(formula, proof, verbose)

def check_proof_from_files(formula_file : str, proof_file : str, verbose : bool = False) -> CheckerResult:
	"""Check a sequence of RUP and RAT clauses against a CNF.

	Args:
		formula_file (str): Path to a file containing a CNF in DIMACS format.
		proof_file (str): Path to a file containing a sequence of RUP or RAT clauses.
		verbose (bool, optional): Return detailed information
			if the check fails. Defaults to False.

	Returns:
		CheckerResult: CheckerResult struct representing the result of the check.

	Raises:
		ValueError: If the formula or proof cannot be parsed or formatted.
	"""
	try:
		with open(formula_file, 'r') as f:
			formula = f.read()
	except:
		raise ValueError(f"Error reading formula from: {formula_file}")
	try:
		with open(proof_file, 'r') as f:
			proof = f.read()
	except:
		raise ValueError(f"Error reading proof from: {proof_file}")

	return check_proof_from_strings(formula, proof, verbose)


