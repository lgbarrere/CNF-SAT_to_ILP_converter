#! /usr/bin/env python3
# coding: utf8

"""
File : setup.py
Author : lgbarrere
Brief : Build the library
"""

from setuptools import find_packages, setup

lib_name = 'script'

setup(
    name=lib_name,
    packages=find_packages(include=[lib_name]),
    version='0.1.0',
    description='API to solve/convert SAT and ILP files',
    author='lgbarrere',
    license=None,
    install_requires=[],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='test',
)
