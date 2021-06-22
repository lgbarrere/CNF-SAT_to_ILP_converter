#! /usr/bin/env python3
# coding: utf8

"""
File : pulp_converter.py
Author : lgbarrere
Brief : To convert an ILP file into an ILP pulp problem
"""


import pulp
import converter as conv


class PulpConverter:
    """
    Brief : Get an ILP instance to create its PuLP version
    """
    
    def __init__(self):
        pass


def main():
    """
    Brief : Test some uses of this library
    Return : None
    """
    converter = conv.Converter()
    converter.convert_from_file("test.cnf")
    prefix = "z"
    z = pulp.LpVariable(prefix, 0, 1)
    var_dict = pulp.LpVariable.dicts(prefix, converter.var_match, cat='Binary')

    prob = pulp.LpProblem("myProblem", pulp.LpMaximize)
    prob += z # Objective function

    constraints = converter.get_constraints()

    for constraint in constraints :
    	var = pulp.LpVariable(constraint, 0, 1)
    	prob += var

    # Solution
    status = prob.solve()
    print("Status : " + str(pulp.LpStatus[status]))
    print("Objective function value : " + str(pulp.value(prob.objective)))
    print("values : " + str(var_dict.values()))


if __name__ == "__main__":
    main()
