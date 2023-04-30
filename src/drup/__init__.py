"""
.. include:: ../../README.md
"""

__version__ = '1.2.0'

import os
import sys
import ctypes

_basedir = os.path.abspath(os.path.dirname(__file__))
_checker = ctypes.cdll.LoadLibrary(os.path.join(_basedir, "libdrupchecker.so"))

class _Lit_struct(ctypes.Structure):
  _fields_=[("var", ctypes.c_int), ("sign", ctypes.c_int), ("root", ctypes.c_void_p)]

  def __str__(self):
    if self.sign <= 0:
      return f"-{self.var}"
    else:
      return f"{self.var}"

class _Clause_struct(ctypes.Structure):
  _fields_=[("lits", ctypes.POINTER(_Lit_struct)), ("len", ctypes.c_int), ("root", ctypes.c_void_p)]

  def __str__(self):
    r = " ".join([str(self.lits[i]) for i in range(self.len)])
    spacer = " " if self.len > 0 else ""
    return f"{r}{spacer}0"

class _Cnf_struct(ctypes.Structure):
  _fields_=[("clauses", ctypes.POINTER(_Clause_struct)), ("len", ctypes.c_int), ("root", ctypes.c_void_p)]

  def __str__(self):
    cs = "\n".join([str(self.clauses[i]) for i in range(self.len)])
    return f"{cs}"

class _Chain_struct(ctypes.Structure):
  _fields_=[("lits", ctypes.POINTER(_Lit_struct)), ("len", ctypes.c_int), ("root", ctypes.c_void_p)]

  def __str__(self):
    ls = " ".join([str(self.lits[i]) for i in range(self.len)])
    return f"<{ls}>"

class _Rupinfo_struct(ctypes.Structure):
  _fields_=[("clause", _Clause_struct), ("chain", _Chain_struct), ("root", ctypes.c_void_p)]

  def __str__(self):
    rup_clause = str(self.clause)
    rup_chain = str(self.chain)
    return f"_Rupinfo_struct({rup_clause}, {rup_chain})"

class _Ratinfo_struct(ctypes.Structure):
  _fields_=[("clause", _Clause_struct), ("pivot_clause", _Clause_struct), ("rup_info", _Rupinfo_struct), ("root", ctypes.c_void_p)]

  def __str__(self):
    rat_clause = str(self.clause)
    pivot_clause = str(self.pivot_clause)
    rup_info = str(self.rup_info)
    return f"_Ratinfo_struct({rat_clause}, {pivot_clause}, {rup_info})"

class _Result_struct(ctypes.Structure):
  _fields_=[("valid", ctypes.c_int), ("steps", _Cnf_struct), ("rup_info", _Rupinfo_struct), ("rat_info", _Ratinfo_struct), ("root", ctypes.c_void_p)]

  def __str__(self):
    steps = ", ".join(str(self.steps.clauses[i]) for i in range(self.steps.len))
    rup = str(self.rup_info)
    rat = str(self.rat_info)
    return f"_Result_struct({self.valid}, [{steps}], {rup}, {rat})"

_checker.check.argtypes = [ctypes.POINTER(_Cnf_struct), ctypes.POINTER(_Cnf_struct)]
_checker.check.restype = ctypes.POINTER(_Result_struct)
_checker.check_derivation.argtypes = [ctypes.POINTER(_Cnf_struct), ctypes.POINTER(_Cnf_struct)]
_checker.check_derivation.restype = ctypes.POINTER(_Result_struct)
_checker.check_fast.argtypes = [ctypes.POINTER(_Cnf_struct), ctypes.POINTER(_Cnf_struct)]
_checker.check_fast.restype = ctypes.POINTER(_Result_struct)
_checker.check_derivation_fast.argtypes = [ctypes.POINTER(_Cnf_struct), ctypes.POINTER(_Cnf_struct)]
_checker.check_derivation_fast.restype = ctypes.POINTER(_Result_struct)
_checker.free_rup_info.argtypes = [ctypes.POINTER(_Rupinfo_struct)]
_checker.free_rat_info.argtypes = [ctypes.POINTER(_Ratinfo_struct)]
_checker.free_result.argtypes = [ctypes.POINTER(_Result_struct)]

import drup.wrappers

Lit = drup.wrappers.Lit
'''
A signed integer representing a literal.
'''

Clause = drup.wrappers.Clause
'''
A sequence of literals.
'''

Chain = drup.wrappers.Chain
'''
A sequence of clauses.
'''

Cnf = drup.wrappers.Cnf
'''
A sequence of literals.
'''

Proof = drup.wrappers.Proof
'''
A sequence of clauses.
'''

Outcome = drup.wrappers.Outcome
RupInfo = drup.wrappers.RupInfo
RatInfo = drup.wrappers.RatInfo
CheckerResult = drup.wrappers.CheckerResult
check_proof = drup.wrappers.check_proof
check_proof_from_files = drup.wrappers.check_proof_from_files
check_proof_from_strings = drup.wrappers.check_proof_from_strings
check_derivation = drup.wrappers.check_derivation
check_derivation_from_files = drup.wrappers.check_derivation_from_files
check_derivation_from_strings = drup.wrappers.check_derivation_from_strings

__all__ = [
  'Lit',
  'Clause',
  'Chain',
  'Cnf',
  'Proof',
  'Outcome',
  'RupInfo',
  'RatInfo',
  'CheckerResult',
  'check_proof',
  'check_proof_from_files',
  'check_proof_from_strings',
  'check_derivation',
  'check_derivation_from_files',
  'check_derivation_from_strings',
]