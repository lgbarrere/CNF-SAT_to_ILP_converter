#! /usr/bin/env python3
# coding: utf8

"""
File : sat_manager.py
Author : lgbarrere
Brief : Test sat
"""

from ..manager.sat import SatManager


def test_sat():
    """
    Brief : Test some uses of this library
    Return : None
    """
    # Global test
    sat_manager = SatManager()
    sat_manager.load_folder()
    for file_name in sat_manager.problem_dict :
        print(file_name)
        for solver_name in sat_manager.get_solvers() :
            sat_manager.solve(file_name=file_name, solver_name=solver_name)
    print(sat_manager)
    # Test limit time
    limit_file = 'BA2_270_73_code_6_16.txt'
    sat_manager.load_file(limit_file, 'dimacs')
    sat_manager.solve(file_name=limit_file, time_limit=3)
