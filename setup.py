import os
import sys
import shutil
import subprocess
import setuptools

from pathlib import Path
from setuptools import setup, Extension
from setuptools.command.sdist import sdist as _sdist

def extract_checker():
    cmd = [
        "why3", "extract", "-D", "ocaml64", 
        "src/librupchecker/rup_pure.mlw", "-o", "src/librupchecker/rup.ml"
    ]
    subprocess.run(cmd, check=True, stdout=sys.stdout, stderr=sys.stderr)

def build_checker():
    cmd = ["dune", "build"]
    subprocess.run(cmd, check=True, stdout=sys.stdout, stderr=sys.stderr)

class SDist(_sdist):
    def run(self) -> None:
        extract_checker()
        build_checker()
        shutil.copy("_build/default/src/librupchecker/checker.so", "src/rup/librupchecker.so")
        super().run()
        cmd = ["dune", "clean"]
        subprocess.run(cmd, check=True, stdout=sys.stdout, stderr=sys.stderr)
        os.unlink("src/rup/librupchecker.so")
        os.unlink("src/librupchecker/rup.ml")

setup(
    cmdclass={'sdist': SDist},
    packages=['rup'],
    package_dir={'rup': 'src/rup'},
    ext_modules=[Extension(name="rup.librupchecker", sources=[])]
)