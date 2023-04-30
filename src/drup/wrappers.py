__all__ = []

from typing import Iterable, Optional
from enum import Enum

import ctypes
import re

from . import (
  _Chain_struct,
  _checker,
  _Clause_struct,
  _Cnf_struct,
  _Lit_struct,
  _Ratinfo_struct,
  _Result_struct,
  _Rupinfo_struct
)

Lit = int
Clause = Iterable[Lit]
Cnf = Iterable[Clause]
Chain = Iterable[Lit]
Proof = Cnf

Outcome = Enum("Outcome", ["VALID", "INVALID"])

class RupInfo:

  '''
  Information on a failed RUP check.

  **Attributes**:
    
    clause (`Clause`): The clause that failed the RUP check.

    chain (`Chain`): A sequence of unit literals that failed to
      derive an empty clause via propagation, with no further 
      opportunities to propagate.
  '''

  def __init__(self, clause : Clause, chain : Chain):
    self.clause = clause
    self.chain = chain

  def __str__(self):
    return f"RupInfo({str(self.clause)}, {str(self.chain)})"

class RatInfo:

  '''
  Information on a failed RAT check.

  **Attributes**:
    clause (`Clause`): The clause that failed the RAT check.

    pivot_clause (`Clause`): A pivot clause that failed a RUP check.

    rup_info (`RupInfo`): Information on the failed RUP check.
  '''

  def __init__(self, clause : Clause, pivot_clause : Clause, rup_info : RupInfo):
    self.clause = clause
    self.pivot_clause = pivot_clause
    self.rup_info = rup_info

  def __str__(self):
    return f"RatInfo({str(self.clause)}, {str(self.pivot_clause)}, {str(self.rup_info)})"

class CheckerResult:

  '''
  Result of a proof check.

  **Attributes**:

    outcome (`Outcome`): The outcome of the check. If the check
      succeeded, this will be Outcome.VALID. If the check failed,
      this will be Outcome.INVALID.

    steps (`Optional[Cnf]`): Completed proof steps prior to an invalid step, 
      if the proof was invalid.

    rup_info (`Optional[RupInfo]`): Information on a failed RUP check,
      if the proof was invalid.

    rat_info (`Optional[RatInfo]`): Information on a failed RAT check,
      if the proof was invalid. The RAT clause in this object will
      be the same as the RUP clause in `rup_info`.
  '''

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

def _read_clauses(clauses : str) -> Cnf:
  """Read a list of clauses from a string.

  **Args:**
    clauses (str): String containing clauses in DIMACS format.
      The clauses should not include the header line.
  
  **Returns:**
    Cnf: List of clauses, each represented as a list of integers.

  **Raises:**
    ValueError: If the clauses are not in DIMACS format.
  """
  clauses = clauses.replace('\n', '')
  lines = [
    line.strip() for line in clauses.split(' 0')
    if  not line.strip().startswith('c') and 
        not line.strip().startswith('d') and 
        not line.strip().startswith('p') and
        not line.strip() == '0' and
        not len(line.strip()) == 0
  ]
  return [list(map(int, line.split(' '))) for line in lines]

def _clause_to_struct(lits : Clause) -> _Clause_struct:
  """Convert a list of literals to a _Clause_struct struct.

  **Args:**
    lits (Clause): Iterable of literals, represented as integers. The
    list need not end with a 0, as 0 is a valid positive literal.

  **Returns:**
    _Clause_struct: _Clause_struct struct representing the list of literals.
  """
  clause = _Clause_struct()
  clause.len = len(lits)
  clause.lits = (_Lit_struct * clause.len)()
  for i, lit in enumerate(lits):
    clause.lits[i].var = abs(lit)
    clause.lits[i].sign = -1 if lit < 0 else 1
  return clause

def _cnf_to_struct(clauses : Cnf) -> _Cnf_struct:
  """Convert a list of clauses to a _Cnf_struct struct.

  **Args:**
    clauses (`Cnf`): Iterable of clauses, each represented as a list of integers.
    Negative integers represent negated literals, and clauses need not end with 0.

  **Returns:**
    _Cnf_struct: _Cnf_struct struct representing the list of clauses.
  """
  struct = _Cnf_struct()
  struct.len = len(clauses)
  struct.clauses = (_Clause_struct * struct.len)()
  for i, clause in enumerate(clauses):
    struct.clauses[i] = _clause_to_struct(clause)
  return struct

def _struct_to_clause(clause : _Clause_struct) -> Clause:
  """Convert a _Clause_struct struct to a list of literals.

  **Args:**
    clause (_Clause_struct): _Clause_struct struct representing a clause.

  **Returns:**
    Clause: List of literals, represented as integers.
  """
  def sign(x : int):
    return -1 if x <= 0 else 1
  return [clause.lits[i].var * sign(clause.lits[i].sign) for i in range(clause.len)]

def _struct_to_cnf(cnf : _Cnf_struct) -> Cnf:
  """Convert a _Cnf_struct struct to a list of clauses.

  **Args:**
    _Cnf_struct (_Cnf_struct): _Cnf_struct struct representing a CNF formula.

  **Returns:**
    Cnf: List of clauses, each represented as a list of integers.
  """
  return [_struct_to_clause(cnf.clauses[i]) for i in range(cnf.len)]

def _struct_to_chain(chain : _Chain_struct) -> Chain:
  """Convert a _Chain_struct struct to a list of literals.

  **Args:**
    chain (_Chain_struct): _Chain_struct struct representing a chain.

  **Returns:**
    Chain: List of literals, represented as integers.
  """
  def sign(x : int):
    return -1 if x <= 0 else 1
  return [chain.lits[i].var * sign(chain.lits[i].sign) for i in range(chain.len)]

def _check_proof_from_structs(
  formula : _Cnf_struct, 
  proof : _Cnf_struct, 
  verbose : bool = False
) -> CheckerResult:
  """Check a proof against a formula. This is function interfaces directly with
  the C wrappers, and expects inputs to be ctypes structs.

  **Args:**
    formula (_Cnf_struct): _Cnf_struct as a ctypes struct.
    proof (_Cnf_struct): Sequence of RUP or RAT clauses.
    verbose (bool, optional): Return detailed information
      if the check fails. Defaults to False.

  **Returns:**
    `CheckerResult`: CheckerResult struct representing the result of the check.
      The result will be Outcome.VALID only if each step of the proof is either
      RUP or RAT, and the last clause is empty.
  
  **Raises:**
    ValueError: If the formula or proof cannot be parsed.
  """
  if verbose:
    result = _checker.check(ctypes.byref(formula), ctypes.byref(proof)).contents
    if result.valid > 0:
      _checker.free_result(result)
      return CheckerResult(Outcome.VALID, None, None, None)
    else:
      res = CheckerResult(
              Outcome.INVALID,
              _struct_to_cnf(result.steps),
              RupInfo(
                _struct_to_clause(result.rup_info.clause),
                _struct_to_chain(result.rup_info.chain)
              ),
              RatInfo(
                _struct_to_clause(result.rat_info.clause),
                _struct_to_clause(result.rat_info.pivot_clause),
                RupInfo(
                  _struct_to_clause(result.rat_info.rup_info.clause),
                  _struct_to_chain(result.rat_info.rup_info.chain)
                )
              )
            )
      if result.valid == 0:
        _checker.free_rup_info(result.rup_info)
      elif result.valid == -1:
        _checker.free_rup_info(result.rup_info)
        _checker.free_rat_info(result.rat_info)
      _checker.free_result(result)
      return res
  else:
    result = _checker.check_fast(ctypes.byref(formula), ctypes.byref(proof)).contents
    if result.valid > 0:
      _checker.free_result(result)
      return CheckerResult(Outcome.VALID, None, None, None)
    else:
      _checker.free_result(result)
      return CheckerResult(Outcome.INVALID, None, None, None)

def check_proof(formula : Cnf, proof : Proof, verbose : bool = False) -> CheckerResult:
  """Check a sequence of RUP and RAT clauses against a CNF. Inputs are Python iterables
  of clauses, where each clause is an iterable of signed Python ints.

  **Args:**
    formula (`Cnf`): Cnf as an iterable of clauses.

    proof (`Proof`): Iterable of RUP or RAT clauses.
    
    verbose (bool, optional): Return detailed information
      if the check fails. Defaults to False.

  **Returns:**
    `CheckerResult`: CheckerResult struct representing the result of the check.
  
  **Raises:**
    ValueError: If the formula or proof cannot be formatted.
  """
  return _check_proof_from_structs(_cnf_to_struct(formula), _cnf_to_struct(proof), verbose)

def check_proof_from_strings(formula : str, proof : str, verbose : bool = False) -> CheckerResult:
  """Check a sequence of RUP and RAT clauses against a CNF.

  **Args:**
    formula (str): Cnf as a string in DIMACS format. The header
      is ignored if present.
    proof (str): Sequence of RUP or RAT clauses format.
    verbose (bool, optional): Return detailed information
      if the check fails. Defaults to False.
  
  **Returns:**
    `CheckerResult`: CheckerResult struct representing the result of the check.

  **Raises:**
    ValueError: If the formula or proof cannot be parsed or formatted.
  """
  try:
    formula = re.sub(' +', ' ', formula)
    if '\n' in formula and formula.split('\n')[0].strip().startswith('p'):
      formula = '\n'.join(formula.split('\n')[1:])
    formula = _read_clauses(formula)
  except:
    raise ValueError("Error parsing formula. Check that the input is properly formatted.")
  try:
    proof = re.sub(' +', ' ', proof)
    proof = _read_clauses(proof)
  except:
    raise ValueError("Error parsing proof. Check that the input is properly formatted.")

  return check_proof(formula, proof, verbose)

def check_proof_from_files(formula_file : str, proof_file : str, verbose : bool = False) -> CheckerResult:
  """Check a sequence of RUP and RAT clauses against a CNF.

  **Args:**
    formula_file (str): Path to a file containing a CNF in DIMACS format.
    proof_file (str): Path to a file containing a sequence of RUP or RAT clauses.
    verbose (bool, optional): Return detailed information
      if the check fails. Defaults to False.

  **Returns:**
    `CheckerResult`: CheckerResult struct representing the result of the check.

  **Raises:**
    ValueError: If the formula or proof cannot be parsed or formatted.
    FileNotFoundError: If the formula or proof file cannot be found.
  """
  with open(formula_file, 'r') as f:
    formula = f.read()
  with open(proof_file, 'r') as f:
    proof = f.read()

  return check_proof_from_strings(formula, proof, verbose)

def _check_derivation_from_structs(
  formula : _Cnf_struct, 
  derivation : _Cnf_struct, 
  verbose : bool = False
) -> CheckerResult:
  """Check a derivation against a formula. This is function interfaces directly with
  the C wrappers, and expects inputs to be ctypes structs.

  **Args:**
    formula (_Cnf_struct): _Cnf_struct as a ctypes struct.
    derivation (_Cnf_struct): Sequence of RUP or RAT clauses.
    verbose (bool, optional): Return detailed information
      if the check fails. Defaults to False.

  **Returns:**
    `CheckerResult`: CheckerResult struct representing the result of the check.
      If each step in the derivation is either RUP or RAT, then the result will
      be Outcome.VALID. Otherwise, the result will be Outcome.INVALID.
      The derivation does not need to contain the empty clause.
  
  **Raises:**
    ValueError: If the formula or derivation cannot be parsed.
  """
  if verbose:
    result = _checker.check_derivation(ctypes.byref(formula), ctypes.byref(derivation)).contents
    if result.valid > 0:
      _checker.free_result(result)
      return CheckerResult(Outcome.VALID, None, None, None)
    else:
      res = CheckerResult(
              Outcome.INVALID,
              _struct_to_cnf(result.steps),
              RupInfo(
                _struct_to_clause(result.rup_info.clause),
                _struct_to_chain(result.rup_info.chain)
              ),
              RatInfo(
                _struct_to_clause(result.rat_info.clause),
                _struct_to_clause(result.rat_info.pivot_clause),
                RupInfo(
                  _struct_to_clause(result.rat_info.rup_info.clause),
                  _struct_to_chain(result.rat_info.rup_info.chain)
                )
              )
            )
      if result.valid == 0:
        _checker.free_rup_info(result.rup_info)
      elif result.valid == -1:
        _checker.free_rup_info(result.rup_info)
        _checker.free_rat_info(result.rat_info)
      _checker.free_result(result)
      return res
  else:
    result = _checker.check_derivation_fast(ctypes.byref(formula), ctypes.byref(derivation)).contents
    if result.valid > 0:
      _checker.free_result(result)
      return CheckerResult(Outcome.VALID, None, None, None)
    else:
      _checker.free_result(result)
      return CheckerResult(Outcome.INVALID, None, None, None)

def check_derivation(formula : Cnf, derivation : Proof, verbose : bool = False) -> CheckerResult:
  """Check a sequence of RUP and RAT clauses against a CNF. Inputs are Python iterables
  of clauses, where each clause is an iterable of signed Python ints.

  **Args:**
    formula (`Cnf`): Cnf as an iterable of clauses.

    derivation (`Proof`): Iterable of RUP or RAT clauses.
    
    verbose (bool, optional): Return detailed information
      if the check fails. Defaults to False.

  **Returns:**
    `CheckerResult`: CheckerResult struct representing the result of the check.
      If each step in the derivation is either RUP or RAT, then the result will
      be Outcome.VALID. Otherwise, the result will be Outcome.INVALID.
      The derivation does not need to contain the empty clause.
  
  **Raises:**
    ValueError: If the formula or derivation cannot be formatted.
  """
  return _check_derivation_from_structs(_cnf_to_struct(formula), _cnf_to_struct(derivation), verbose)

def check_derivation_from_strings(formula : str, derivation : str, verbose : bool = False) -> CheckerResult:
  """Check a sequence of RUP and RAT clauses against a CNF.

  **Args:**
    formula (str): Cnf as a string in DIMACS format. The header
      is ignored if present.
    
    proof (str): Sequence of RUP or RAT clauses format.
    
    verbose (bool, optional): Return detailed information
      if the check fails. Defaults to False.
  
  **Returns:**
    `CheckerResult`: CheckerResult struct representing the result of the check.
      If each step in the derivation is either RUP or RAT, then the result will
      be Outcome.VALID. Otherwise, the result will be Outcome.INVALID.
      The derivation does not need to contain the empty clause.

  **Raises:**
    ValueError: If the formula or proof cannot be parsed or formatted.
  """
  try:
    formula = re.sub(' +', ' ', formula)
    if '\n' in formula and formula.split('\n')[0].strip().startswith('p'):
      formula = '\n'.join(formula.split('\n')[1:])
    formula = _read_clauses(formula)
  except:
    raise ValueError("Error parsing formula. Check that the input is properly formatted.")
  try:
    derivation = re.sub(' +', ' ', derivation)
    derivation = _read_clauses(derivation)
  except:
    raise ValueError("Error parsing derivation. Check that the input is properly formatted.")

  return check_derivation(formula, derivation, verbose)

def check_derivation_from_files(formula_file : str, derivation_file : str, verbose : bool = False) -> CheckerResult:
  """Check a sequence of RUP and RAT clauses against a CNF.

  **Args:**
    
    formula_file (str): Path to a file containing a CNF in DIMACS format.
    
    derivation_file (str): Path to a file containing a sequence of RUP or RAT clauses.
    
    verbose (bool, optional): Return detailed information
      if the check fails. Defaults to False.

  **Returns:**
    `CheckerResult`: CheckerResult struct representing the result of the check.
      If each step in the derivation is either RUP or RAT, then the result will
      be Outcome.VALID. Otherwise, the result will be Outcome.INVALID.
      The derivation does not need to contain the empty clause.

  **Raises:**
    ValueError: If the formula or proof cannot be parsed or formatted.
    FileNotFoundError: If the formula or proof file cannot be found.
  """
  with open(formula_file, 'r') as f:
    formula = f.read()
  with open(derivation_file, 'r') as f:
    derivation = f.read()

  return check_derivation_from_strings(formula, derivation, verbose)