import os
import sys
import shutil
import subprocess
import setuptools

from pathlib import Path
from setuptools import setup
from setuptools.dist import Distribution
from setuptools.command.sdist import sdist as _sdist

def extract_checker():
    cmd = [
        "why3", "extract", "-D", "ocaml64", 
        "src/ocaml/rup_pure.mlw", "-o", "src/ocaml/rup.ml"
    ]
    subprocess.run(cmd, check=True, stdout=sys.stdout, stderr=sys.stderr)

def build_checker():
    cmd = ["dune", "build"]
    subprocess.run(cmd, check=True, stdout=sys.stdout, stderr=sys.stderr)

class SDist(_sdist):
    def run(self) -> None:
        extract_checker()
        build_checker()
        shutil.copy("_build/default/src/ocaml/checker.so", "src/verified_rup/checker.so")
        super().run()
        cmd = ["dune", "clean"]
        subprocess.run(cmd, check=True, stdout=sys.stdout, stderr=sys.stderr)
        os.unlink("src/verified_rup/checker.so")
        os.unlink("src/ocaml/rup.ml")

class ForcedBinaryDistribution(Distribution):
    def has_ext_modules(foo):
        return True

setup(
    cmdclass={'sdist': SDist},
    packages=['verified_rup'],
    package_dir={'verified_rup': 'src/verified_rup'},
    package_data={'checker': ['checker.so']},
    distclass=ForcedBinaryDistribution
)