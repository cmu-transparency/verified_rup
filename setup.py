import os
import sys
import shutil
import subprocess
import setuptools

from pathlib import Path
from setuptools import setup, Extension
from setuptools.command.sdist import sdist as _sdist

def build_checker():
    cmd = ["dune", "build"]
    subprocess.run(cmd, check=True, stdout=sys.stdout, stderr=sys.stderr)

class SDist(_sdist):
    def run(self) -> None:
        build_checker()
        shutil.copy("_build/default/src/librupchecker/libdrupchecker.so", "src/drup/libdrupchecker.so")
        super().run()
        cmd = ["dune", "clean"]
        subprocess.run(cmd, check=False, stdout=sys.stdout, stderr=sys.stderr)
        os.unlink("src/drup/libdrupchecker.so")

setup(
    cmdclass={'sdist': SDist},
    packages=['drup'],
    package_dir={'drup': 'src/drup'},
    ext_modules=[Extension(name="drup.librupchecker", sources=[])],
	entry_points = {
        'console_scripts': ['drup=drup.cli:main'],
    }
)