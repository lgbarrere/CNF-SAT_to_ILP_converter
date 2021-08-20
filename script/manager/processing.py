#! /usr/bin/env python3
# coding: utf8

"""
File : subprocess.py
Author : lgbarrere
Brief : Run a solver in a subprocess
"""

import sys

from pysat.formula import CNF
from pysat.solvers import Solver
import pulp

def sub_sat_solve(solver_name, file_name):
    clauses=CNF(from_file=file_name)
    with Solver(
        name=solver_name, bootstrap_with=clauses, use_timer=True
        ) as solver :
        solution = solver.solve()
        model = solver.get_model()
        time = solver.time()
        # If called as subprocess, the result is got in stdout (not printed)
        print(solution)
        print(model)
        print(time)


def lines_from_file(file_path):
    """
    Brief : Open a file from the given path to get every lines
    Return : Every lines in a list
    > file_path : Path of the file to open
    """
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            return lines
    except FileNotFoundError as error:
        return None
    return None


def split(string, splitter_list):
    """
    Brief : Split the given string with a list of splitters
    Return : Splitted string in a list of string list
    > string : String to split
    > splitter_list : List containing the strings used to split
    """
    txt_list = []
    for i in range(len(splitter_list)-1) :
        theme_list = []
        pos1 = string.find(splitter_list[i]) + len(splitter_list[i])
        pos2 = string.find(splitter_list[i + 1])
        tmp_pos = pos1
        while pos1 < pos2 :
            if string[tmp_pos] == '\n' :
                theme_list.append(string[pos1:tmp_pos])
                pos1 = tmp_pos + 1
            tmp_pos += 1
        txt_list.append(theme_list)
    return txt_list


def get_ilp(file_name):
    """
    Brief : Set the ILP from a file in the formula dictionary
    Return : the ilp in tuple
    > lines : The lines got from the file
    > file_name : The name of the file to open
    """
    lines = lines_from_file(file_name)
    # Initializations
    binary_list = []
    # Consider key 0 as objective
    prefix = 'z'
    binary_list.append(prefix)
    lines = ''.join(lines)
    lines = split(lines, ['Subject To\n', 'Binary\n', 'End'])

    constraint_dict = {}

    # Constraints
    for line in lines[0] :
        words = line.split()
        i = 0
        term_list = []
        while words[i] == '' :
            i += 1
        constraint_name = words[i].replace(':', '')
        i += 1
        while words[i] != '>=' :
            term_list.append(words[i])
            i += 1
        goal = int(words[i + 1])
        constraint_dict[constraint_name] = (term_list, goal)

    # Binaries
    for line in lines[1] :
        words = line.split()
        i = 0
        while words[i] == '' :
            i += 1
        if words[i] == prefix :
            continue
        if words[i] not in binary_list :
            binary_list.append(words[i])

    return (constraint_dict, binary_list)


def define_problem(file_name):
    ilp_tuple = get_ilp(file_name)
    problem = pulp.LpProblem(sense=pulp.LpMaximize)

    # Variables
    binary_list = ilp_tuple[1]
    var_dict = {}
    for value in binary_list:
        var_dict[value] = pulp.LpVariable(
            name=value, cat=pulp.LpBinary
            )

    # Constraints
    constraint_dict = ilp_tuple[0]
    for constraint in constraint_dict.values() :
        var_list = []
        term = constraint[0]
        for (i, _) in enumerate(term) :
            sign = 1
            if term[i] == '-':
                sign = -1
                i += 1
            elif term[i] == '+':
                i += 1
            var_list.insert(0, (var_dict[term[i]], sign))
            i += 1

        problem += pulp.LpConstraint(
            e=pulp.LpAffineExpression(e=var_list),
            sense=pulp.LpConstraintGE,
            rhs=constraint[1]
            )

    # Objective function
    problem += pulp.LpVariable(name='z', lowBound=1, upBound=1)

    return problem


def sub_ilp_solve(solver_name, file_name):
##    converter.ilp_from_file(file_name)
    problem = define_problem(file_name)
    status = problem.solve(
        pulp.getSolver(solver_name)
        )
    solution = status
    time = problem.get_time()
    # If called as subprocess, the result is got in stdout (not printed)
    print(solution)
##    print(model)
    print(time)


def main():
    solver_name = sys.argv[1] # Get name of the solver
    file_name = sys.argv[2] # Get the name of the file
    option = sys.argv[3] # Check if we want to use SAT or ILP solver
    if option == '-sat':
        sub_sat_solve(solver_name, file_name)
    elif option == '-ilp':
        sub_ilp_solve(solver_name, file_name)
    else :
        print('Wrong option.')


main()
