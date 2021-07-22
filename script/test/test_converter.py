#! /usr/bin/env python3
# coding: utf8

"""
File : test_converter.py
Author : lgbarrere
Brief : Test converter
"""

from ..manager.converter import *


def test_converter():
    """
    Brief : Test some uses of this library
    Return : None
    """
    # Verbose debug and prepare the tests
    lg.basicConfig(level=lg.DEBUG)
    test_folder_name = 'dimacs'
    converter = PulpConverter()
    converter.clear_all_save_folder()

    # Test limits in example files
    test_file = 'test.cnf'
    converter.convert_from_file(test_file)
    converter.save_ilp_in_file(test_file)
    print('n = ' + str(converter.get_nb_variables(test_file)))
    print('m = ' + str(converter.get_nb_clauses(test_file)))
    converter.convert_from_folder()

    # Test to get an ILP directly from an ILP file
    ilp_test = to_ilp_suffix(test_file)
    converter.ilp_from_file(ilp_test)
    converter.print_ilp(ilp_test)

    # Test with PuLP definitions
    lg.disable(level=lg.DEBUG)
    example_file = 'example.cnf'
    converter.convert_from_file(example_file)
    converter.define_problem(example_file)
    converter.solve(example_file)
    converter.save_results()

    # Test with important data folder
    lg.disable(level=lg.NOTSET)
    converter.convert_from_folder(test_folder_name)
    converter.save_all_in_folder(test_folder_name)
