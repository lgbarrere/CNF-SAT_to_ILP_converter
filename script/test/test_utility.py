#! /usr/bin/env python3
# coding: utf8

"""
File : test_utility.py
Author : lgbarrere
Brief : Test utility
"""

from ..manager.utility import Constants


def test_constant():
    const = Constants()
    print(const.get_root_path())
