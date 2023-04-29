# A Verified DRUP Proof Checker

As the title suggests, a verified implementation of a checker for propositional unsatisfiability proofs in the  [DRUP format](https://satcompetition.github.io/2022/certificates.html) that is produced by many solvers.
The core of the checker is written in [Why3](https://why3.lri.fr/), which is extracted to OCaml, compiled natively, and exported as a C library with Python bindings.

* The checker also supports RAT clauses, so DRAT proofs are accepted.
* The current implementation is not optimized, and will be considerably slower than [DRAT-trim](https://github.com/marijnheule/drat-trim) on large proofs (see [performance](#performance) below).
* Accordingly, the frontend does not accept proofs in binary format.

The verification can be checked by running `src/librupchecker/rup_pure.mlw` in Why3. 
Most of the verification conditions complete with the `Auto level 0` tactic, and the rest either with a few levels of splitting followed by `Auto 0` or `Auto 1`, or simply with `Auto 2`.
It was developed using Why3 1.5.1, Alt-Ergo 2.4.0, Z3 4.8.6, and CVC4 1.8.
Verification has not been attempted with earlier versions of Why3 or the provers.

## Installation

If you use a recent Linux distribution on x86_64, you should be able to install the compiled wheel from PyPI:
```bash
$ pip install drup
```
Otherwise, you need to have OCaml (>= 4.12), Ctypes (>=0.20), Why3 (>= 1.5.1), and Dune (>=2.9.3) installed.
The most straightforward way to install these is to use [opam](https://opam.ocaml.org/doc/Install.html), which is available in most package systems, and then install Why3 and Dune (a sufficiently recent version of OCaml should already be installed with Opam): 
```bash
$ opam install why3 dune
```
If you do not intend to check the verification of the library or develop it further, then you do not need to install Why3's IDE or any of the solvers that it supports.

Once OCaml and Why3 are installed, make sure that Python `build` is installed:
```bash
$ pip install build
```
Then, clone this repository, build, and install the package:
```bash
$ git clone https://github.com/cmu-transparency/verified_rup.git
$ cd verified_rup
$ python -m build
$ pip install dist/*.whl
```

## Usage

### Command line interface

The package provides a command line interface for checking proofs stored in files:
```bash
$ drup --help
usage: drup [-h] [-d] [-v] dimacs drup

Checks DRUP & DRAT proofs against DIMACS source. Returns 0 if the proof is valid, -1 if not, or a negative error code if the input is invalid.

positional arguments:
  dimacs            Path to a DIMACS CNF formula
  drup              Path to a DRUP/DRAT proof

optional arguments:
  -h, --help        show this help message and exit
  -d, --derivation  Check each step, ignore absence of empty clause
  -v, --verbose     Print detailed information about failed checks

For more information visit https://github.com/cmu-transparency/verified_rup
```

### As a Python module

See the documentation for details of the API.
The primary function is `drup.check_proof`, or alternatively, `drup.check_derivation` to check each step of the proof, ignoring the absence of an empty clause).
```python
def check_proof(formula : Cnf, proof : Proof, verbose : bool = False) -> CheckerResult:
  """Check a sequence of RUP and RAT clauses against a CNF. Inputs are Python iterables
  of clauses, where each clause is an iterable of signed Python ints.

  Args:
    formula (Cnf): Cnf as an iterable of clauses.
    proof (Proof): Iterable of RUP or RAT clauses.
    verbose (bool, optional): Return detailed information
      if the check fails. Defaults to False.

  Returns:
    CheckerResult: CheckerResult struct representing the result of the check.
  
  Raises:
    ValueError: If the formula or proof cannot be formatted.
  """
```
This takes a CNF and Proof as an iterable of iterables of signed integers, and returns a `CheckerResult`.
```python
class CheckerResult:

  '''
  Result of a proof check.

  Attributes:

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
```
There are corresponding convenience functions `check_proof_from_strings` and `check_proof_from_files`, similarly for `check_derivation`.


## Performance

At present, the implementation of RUP checking is not optimized, and drop lines are ignored.
Unit propagation does not take advantage of watched literals, and does not use mutable data structures.
Nonetheless, the performance compares well to that of [DRAT-trim](https://github.com/marijnheule/drat-trim) on small proofs (<200 variables, a few hundred clauses).

We measure this on random unsatisfiable instances generated by the procedure described in [[1]](#references).
To evaluate the performance of DRAT-trim without the overhead of creating and tearing down a new process for each instance, we compiled it into a library with the same `check_from_strings` interface as the C library, and called it using [ctypes](https://docs.python.org/3/library/ctypes.html).
In the table below, each configuration is run on 10,000 instances, with proofs generated by [Glucose 4](https://www.labri.fr/perso/lsimon/research/glucose/).

| # vars | # clauses (avg) | pf len (avg) | `drup (sec, avg)` | `drat-trim (sec, avg)` |
| ------ | --------------- | ------------ | ----------------- | ---------------------- |
| 25     | 147.7           | 7.3          | 0.001             | 0.085                  |
| 50     | 280.5           | 14.2         | 0.006             | 0.179                  |
| 75     | 413.5           | 26.3         | 0.022             | 0.217                  |
| 100    | 548.2           | 40.6         | 0.068             | 0.172                  |
| 150    | 811.8           | 102.7        | 0.407             | 0.326                  |
| 200    | 1079.5          | 227.9        | 1.916             | 0.292                  |

### References

[[1]](https://openreview.net/forum?id=HJMC_iA5tm) Daniel Selsam, Matthew Lamm, Benedikt Bünz, Percy Liang, Leonardo de Moura, David L. Dill. *Learning a SAT Solver from Single-Bit Supervision*. International Conference on Learning Representations (ICLR), 2019.

## Acknowledgements

Many thanks to [Frank Pfenning](http://www.cs.cmu.edu/~fp/), [Joseph Reeves](https://www.cs.cmu.edu/~jereeves/), and [Marijn Huele](https://www.cs.cmu.edu/~mheule/) for the ongoing insightful discussions that led to this project.