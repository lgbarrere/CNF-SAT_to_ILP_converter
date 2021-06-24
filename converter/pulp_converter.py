#! /usr/bin/env python3
# coding: utf8

"""
File : pulp_converter.py
Author : lgbarrere
Brief : To convert an ILP file into an ILP pulp problem
"""


import pulp
import converter as conv


class PulpConverter(conv.Converter):
    """
    Brief : Get an ILP instance to create its PuLP version
    """
    def __init__(self):
        super().__init__()
        self.solver_list = pulp.listSolvers(onlyAvailable=True)
        self.problem = None
        self.status = pulp.LpStatusUndefined
        self.var_dict = {}


    def define_problem(self, name='NoName'):
        self.problem = pulp.LpProblem(name=name, sense=pulp.LpMaximize)
        ### Variables
        binary_dict = self.get_binaries()
        self.var_dict = {}
        for (key, value) in binary_dict.items():
            self.var_dict[value] = pulp.LpVariable(
                name=binary_dict[key], cat=pulp.LpBinary
                )

        ### Constraints
        constraints = self.get_constraints()
        for constraint in constraints :
            cons_split = constraint.split()
            i = 0
            var_list = []

            while cons_split[i] != '>=':
                sign = 1
                if cons_split[i] == '-':
                    sign = -1
                    i += 1
                elif cons_split[i] == '+':
                    i += 1
                tuple_var = (self.var_dict[cons_split[i]], sign)
                var_list.insert(0, tuple_var)
                i += 1

            expr = pulp.LpAffineExpression(e=var_list)
            constraint_target = int(cons_split[i+1])
        
            res = pulp.LpConstraint(
                e=expr, sense=pulp.LpConstraintGE, rhs=constraint_target
                )
            self.problem += res

        ### Objective function
        obj_var = binary_dict[0] # Get the objective variable
        objective = pulp.LpVariable(
            name=obj_var, lowBound=1, upBound=1)
        self.problem += objective
        self.status = pulp.LpStatusNotSolved


    def solve(self):
        self.status = self.problem.solve()


    def print_problem(self):
        print(self.problem)
        print("Objective function : " + str(self.problem.objective))
        print("Status : " + str(pulp.LpStatus[self.status]))


def main():
    """
    Brief : Test some uses of this library
    Return : None
    """
    converter = PulpConverter()
    #converter.convert_from_file('test.cnf')
    converter.convert_from_file('example.cnf')
    converter.define_problem()
    converter.solve()
    converter.print_problem()

if __name__ == "__main__":
    main()
