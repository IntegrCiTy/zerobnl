#!/usr/bin/env python
# -*- coding: utf-8 -*-

# largely inspired by https://github.com/kennethreitz/setup.py/blob/master/setup.py

import io
import os
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command

# Package meta-data.
NAME = "zerobnl"
DESCRIPTION = "Distributed co-simulation tool based on ZeroMQ, Docker (Swarm and Compose)"
URL = "https://github.com/IntegrCiTy/zerobnl"
EMAIL = "zerobnl@????.ch"
AUTHOR = "Pablo Puerto"
REQUIRES_PYTHON = ">=3.5.0"
VERSION = None

REQUIRED = [
    "zmq==0.0.0",
    "docker==3.5.1",
    "pyyaml>=3.0",
    "redis>=3.0",
    "numpy==1.15",
    "networkx>=2.0",
    "pandas>=0.23",
]

EXTRAS = {
    "tests": ["pytest"],
    "formatting": ["black"],
    "examples": ["jupyter==1.0.0"]
}

here = os.path.abspath(os.path.dirname(__file__))

try:
    with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
        long_description = "\n" + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

about = {}
if not VERSION:
    with open(os.path.join(here, NAME, "__version__.py")) as f:
        exec(f.read(), about)
else:
    about["__version__"] = VERSION

setup(
    name=NAME,
    version=about["__version__"],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=("tests", "examples", "docs")),
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    license="Apache-2.0",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Physics",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: POSIX :: Linux"
    ],
)
