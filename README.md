# Verified DRUP Proof Checker

As the title suggests, a verified implementation of a checker for propositional unsatisfiability proofs in the  [DRUP format](https://satcompetition.github.io/2022/certificates.html) that is produced by several solvers.
The core of the checker is written in [Why3](https://why3.lri.fr/), which is extracted to OCaml, compiled natively, and exported as a C library with Python bindings.

* The checker does not support DRAT proofs, but this may be added in the future.
* The current implementation is not optimized, and will be considerably slower than [DRAT-trim](https://github.com/marijnheule/drat-trim) on large proofs.
* Accordingly, the frontend does not accept proofs in binary format.
* There is currently no CLI, but one can be written as needed in a few minutes using the API described below.

The verification can be checked by running `src/librupchecker/rup_pure.mlw` in Why3. 
Most of the verification conditions complete with the `Auto level 0` tactic, and the rest either with a few levels of splitting followed by `Auto 0` or `Auto 1`, or simply with `Auto 2`.
It was developed using Why3 1.5.1, Alt-Ergo 2.4.0, Z3 4.8.6, and CVC4 1.8.
Verification has not been attempted with earlier versions of Why3 or the provers.

## Installation

If you use a recent Linux distribution on x86_64, you should be able to install the compiled wheel from PyPI:
```bash
$ pip install drup
```
Otherwise, `pip` will attempt to extract and compile the library, which means that you need to have OCaml (>= 4.12), Why3 (>= 1.5.1), and Dune (>=2.9.3) installed.
The most straightforward way to install these is to use [opam](https://opam.ocaml.org/doc/Install.html), which is available in most package systems, and then install Why3 and Dune (a sufficiently recent version of OCaml should already be installed with Opam): 
```bash
$ opam install why3 dune
```
If you do not intend to check the verification of the library or develop it further, then you do not need to install Why3's IDE or any of the solvers that it supports.

Once OCaml and Why3 are installed, you can use the `pip` command above to compile and install the library from source.

## Usage

If you do not intend to use the Python bindings, then you will find the C shared object in the Python package directory:
```bash
$(PYTHON_PATH)/site-packages/rup/librupchecker.{so|dll}
```
The C library exposes two wrappers around the core checker:
```C
int check_from_file(const char *dimacs_path, const char *drup_path);
int check_from_strings(const char *dimacs, const char *drup);
```
Before either of these can be called, the library must be initialized with a call to `do_startup` passing the current `argv`, which calls `caml_startup`:
```C
int do_startup(char **argv);
```
Either function returns `0` if the proof is valid, and `-1` otherwise.

The Python bindings expose these same functions, but will call `do_startup` automatically automatically when the package is imported, so there is no need to call it manually.
If the arguments given to the Python bindings cannot be opened (in the case of files) or parsed, then they raise `ValueError`.

As described, the package is straightforward to use:
```python
import drup

cnf = """
p cnf 4 8
 1  2 -3 0
-1 -2  3 0
 2  3 -4 0
-2 -3  4 0
 1  3  4 0
-1 -3 -4 0
-1  2  4 0
 1 -2 -4 0
"""

pf = """
1 2 0
1 0
2 0
0
"""

if drup.check_from_strings(cnf, pf) == 0:
    print("Valid")
else:
    print("Invalid")
```