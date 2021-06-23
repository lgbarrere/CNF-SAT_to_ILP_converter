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


def convert_to_pulp_constraint(constraint, var_dict):
    cons_split = constraint.split()
    i = 0
    var_list = []

    while cons_split[i] != '>=':
        sign = 1
        if cons_split[i] == '-':
            i += 1
            sign = -1
        elif cons_split[i] == '+':
            i += 1
        tuple_var = (var_dict[cons_split[i]], sign)
        var_list.insert(0, tuple_var)
        i += 1

    expr = pulp.LpAffineExpression(e=var_list)
    constraint_target = int(cons_split[i+1])
    return pulp.LpConstraint(e=expr, sense=pulp.LpConstraintGE,
                             rhs=constraint_target)


def main():
    """
    Brief : Test some uses of this library
    Return : None
    """
    converter = conv.Converter()
    #converter.convert_from_file('test.cnf')
    converter.convert_from_file('example.cnf')
    prefix = converter.get_prefix()
    z_var = pulp.LpVariable(prefix, cat='Binary')
    prob = pulp.LpProblem('ProblemTest', pulp.LpMaximize)
    # variables
    binary_dict = converter.get_binaries()
    var_dict = {}
    for (key, value) in binary_dict.items():
        var_dict[value] = pulp.LpVariable(name=binary_dict[key], cat='Binary')

    # constraints
    constraints = converter.get_constraints()
    for constraint in constraints :
        prob += convert_to_pulp_constraint(constraint, var_dict)
    prob += z_var # Objective function
    print("Problem = \n" + str(prob))

    # Solution
    status = prob.solve()
    print("Status : " + str(pulp.LpStatus[status]))
    print("Objective function : " + str(prob.objective))
    print("Objective function value : " + str(pulp.value(prob.objective)))
    print("values : " + str(var_dict.values()))


if __name__ == "__main__":
    main()
