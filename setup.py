#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import zerobnl

setup(
    name="zerobnl",
    version=zerobnl.__version__,
    packages=find_packages(),
    author="Pablo Puerto",
    author_email="zerobnl@crem.ch",
    description="Distributed co-simulation tool based on ZeroMQ, Docker (Swarm and Compose)",
    long_description=open("README.md").read(),
    # TODO: read from requirements.txt (or read/fill requirements.txt from setup.py ?)
    install_requires=[],
    include_package_data=True,
    url="",
    classifiers=[
        "Natural Language :: English",
        "Operating GraphCreator :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Topic :: Simulation",
    ],
)
