__version__ = '1.1.0'

import os
import sys
import ctypes

basedir = os.path.abspath(os.path.dirname(__file__))
checker = ctypes.cdll.LoadLibrary(os.path.join(basedir, "libdrupchecker.so"))

class Lit_struct(ctypes.Structure):
	_fields_=[("var", ctypes.c_int), ("sign", ctypes.c_int), ("root", ctypes.c_void_p)]

	def __str__(self):
		if self.sign <= 0:
			return f"-{self.var}"
		else:
			return f"{self.var}"

class Clause_struct(ctypes.Structure):
	_fields_=[("lits", ctypes.POINTER(Lit_struct)), ("len", ctypes.c_int), ("root", ctypes.c_void_p)]

	def __str__(self):
		r = " ".join([str(self.lits[i]) for i in range(self.len)])
		spacer = " " if self.len > 0 else ""
		return f"{r}{spacer}0"

class Cnf_struct(ctypes.Structure):
	_fields_=[("clauses", ctypes.POINTER(Clause_struct)), ("len", ctypes.c_int), ("root", ctypes.c_void_p)]

	def __str__(self):
		cs = "\n".join([str(self.clauses[i]) for i in range(self.len)])
		return f"{cs}"

class Chain_struct(ctypes.Structure):
	_fields_=[("lits", ctypes.POINTER(Lit_struct)), ("len", ctypes.c_int), ("root", ctypes.c_void_p)]

	def __str__(self):
		ls = " ".join([str(self.lits[i]) for i in range(self.len)])
		return f"<{ls}>"

class Rupinfo_struct(ctypes.Structure):
	_fields_=[("clause", Clause_struct), ("chain", Chain_struct), ("root", ctypes.c_void_p)]

	def __str__(self):
		rup_clause = str(self.clause)
		rup_chain = str(self.chain)
		return f"Rupinfo_struct({rup_clause}, {rup_chain})"

class Ratinfo_struct(ctypes.Structure):
	_fields_=[("clause", Clause_struct), ("pivot_clause", Clause_struct), ("rup_info", Rupinfo_struct), ("root", ctypes.c_void_p)]

	def __str__(self):
		rat_clause = str(self.clause)
		pivot_clause = str(self.pivot_clause)
		rup_info = str(self.rup_info)
		return f"Ratinfo_struct({rat_clause}, {pivot_clause}, {rup_info})"

class Result_struct(ctypes.Structure):
	_fields_=[("valid", ctypes.c_int), ("steps", Cnf_struct), ("rup_info", Rupinfo_struct), ("rat_info", Ratinfo_struct), ("root", ctypes.c_void_p)]

	def __str__(self):
		steps = ", ".join(str(self.steps.clauses[i]) for i in range(self.steps.len))
		rup = str(self.rup_info)
		rat = str(self.rat_info)
		return f"Result_struct({self.valid}, [{steps}], {rup}, {rat})"

checker.check_from_data.argtypes = [ctypes.POINTER(Cnf_struct), ctypes.POINTER(Cnf_struct)]
checker.check_from_data.restype = ctypes.POINTER(Result_struct)
checker.free_rup_info.argtypes = [ctypes.POINTER(Rupinfo_struct)]
checker.free_rat_info.argtypes = [ctypes.POINTER(Ratinfo_struct)]
checker.free_result.argtypes = [ctypes.POINTER(Result_struct)]

from drup.wrappers import (
	check_proof_from_files,
	check_proof_from_iterables,
	check_proof_from_strings,
	check_derivation,
	check_lemma,
)