#! /usr/bin/env python3
# coding: utf8

"""
File : sat_manager.py
Author : lgbarrere
Brief : Read and solve DIMACS files with PySAT
"""

import sys
import ast
import os
from os import path, listdir
import subprocess as subp

from pysat.formula import CNF
from pysat.solvers import Solver

from .utility import Constants, build_path


class Solverinformation:
    """
    Brief : Give solver information
    """
    def __init__(self):
        self.solution = None
        self.model = None
        self.time = 0


    # Getters
    def get_solution(self):
        """
        Brief : Get the solution
        Return : The solution
        """
        return self.solution


    def get_model(self):
        """
        Brief : Get the model
        Return : The model
        """
        return self.model


    def get_time(self):
        """
        Brief : Get the path to the data folder
        Return : The path
        """
        return self.time


class SatProblem :
    """
    Brief : Define a SAT problem
    """
    def __init__(self, cnf=None, solver_name='Cadical'):
        self.cnf = cnf
        self.solver_dict = {}
        self.solver_dict[solver_name] = Solverinformation()


    # Getters
    def get_solver_info(self, solver_name='Cadical'):
        """
        Brief : Get the information of the given solver
        Return : The solver information
        > solver_name : The name of the solver
        """
        return self.solver_dict[solver_name]


class SatManager(Constants):
    """
    Brief : Allows PySAT solvers to solve CNF-SAT formulas
    """
    def __init__(self):
        # List of every available solvers
        # Note : MapleCM, Minicard, Minisat22 and Minisat-gh not used here
        # because they seem to have a bug that occurs sometimes
        # if used after another use of a solver
        super().__init__()
        self.__avail_solver_list = [
            'Cadical', 'Gluecard3', 'Gluecard4', 'Glucose3',
            'Glucose4', 'Lingeling', 'Maplechrono', 'Mergesat3'
            ]

        self.__problem_dict = {} # file_name : SatProblem


    ## Getters
    def get_problem(self, file_name):
        """
        Brief : Get the problem with the given file name
        Return : The problem
        > file_name : The loaded file
        """
        return self.__problem_dict[file_name]


    def get_solvers(self) :
        """
        Brief : Get a list of available CNF-SAT solvers
        Return : The list of solvers
        """
        return self.__avail_solver_list


    def get_solution(self, file_name, solver_name='Cadical'):
        """
        Brief : Check if the formula is solved or not
        Return : None if didn't try to solve, True if solved, False otherwise
        > file_name : The loaded file
        > solver_name : Name of the solver
        """
        return self.__problem_dict[file_name].solver_dict[solver_name].solution


    ## Methods
    def load_file(self, file_name, folder=None):
        """
        Brief : Load the given DIMACS file from the data folder
        Return : None
        > file_name : The file to load
        > folder : Optional sub folder from which to load the file
        """
        file_path = build_path(self.get_data_path(), folder, file_name)
        if path.isfile(file_path) :
            self.__problem_dict[file_name] = SatProblem(
                cnf=CNF(from_file=file_path)
                )


    def load_folder(self, folder=None):
        """
        Brief : Load all DIMACS files from the data folder
        Return : None
        > folder : Optional sub folder from which to load the files
        """
        folder_path = build_path(self.get_data_path(), folder)
        for file_name in listdir(folder_path) :
            self.load_file(file_name, folder)


    def solve(self, file_name, folder=None, solver_name='Cadical', time_limit=None):
        """
        Brief : Solve a CNF with the given solver
        Return : None
        > file_name : The loaded file
        > folder : The name of the subfolder containing the DIMACS file
        > solver_name : The name of the solver to use
        > time_limit : The maximum time taken to solve before interruption
        """
        problem = self.__problem_dict[file_name]
        if solver_name not in problem.solver_dict :
            problem.solver_dict[solver_name] = Solverinformation()
        info = problem.solver_dict[solver_name]
        clauses = problem.cnf.clauses
        solve_script = path.join('manager', 'processing.py')
        file_path = build_path(self.get_data_path(), folder, file_name)
        try:
            process = subp.run(
                [sys.executable, solve_script, solver_name, file_path, '-sat'],
                capture_output=True, text=True, timeout=time_limit
                )
            out = process.stdout.split('\n')
            info.solution = ast.literal_eval(out[0])
            info.model = ast.literal_eval(out[1])
            info.time = float(out[2])
        except subp.TimeoutExpired:
            info.time = 'Timeout'


    def solve_folder(self, folder, solver_name='Cadical', time_limit=None):
        """
        Brief : Start solving an entire folder and set the time to proceed
        Return : None
        > folder : The name of the folder from which to solve all DIMACS files
        > solver_name : The name of the solve to use
        > time_limit : The maximum time taken to solve before interruption
        """
        folder_path = build_path(self.get_data_path(), folder)
        for file_name in listdir(folder_path) :
            file_path = path.join(folder_path, file_name)
            if path.isfile(file_path) :
                self.solve(file_name=file_name, folder=folder, solver_name=solver_name)


    def save_results(self, result_file):
        """
        Brief : Save all solved SAT results in a file (created if missing)
        Return : None
        """
        # If the file has been solved
        folder = self.get_result_folder()
        folder_path = path.join(self.get_root_path(), folder)
        file_path = path.join(folder_path, result_file)
        # Create folder and/or file if missing, then save the solutions
        os.makedirs(folder_path, exist_ok=True)
        with open(file_path, 'a') as file:
            for (file_name, problem) in self.__problem_dict.items() :
                file.write(f'File : {file_name}\n')
                for solver_name in problem.solver_dict :
                    solver_info = problem.solver_dict[solver_name]
                    file.write(f'  Solver : {solver_name}')
                    file.write(f' | Solution : {solver_info.solution}')
                    file.write(f' | Execution time : {solver_info.time}\n')


    def __repr__(self):
        text_list = []
        for file_name in self.__problem_dict :
            info = self.__problem_dict[file_name]
            text_list.append('Problem : ' + file_name)
            text_list.append('  CNF : ' + str(info.cnf.clauses))
            tmp = []
            tmp.append('  Solvers :')
            for solver_name in info.solver_dict :
                tmp.append(solver_name)
            text_list.append(' '.join(tmp))
        return '\n'.join(text_list)


def main():
    """
    Brief : Test some uses of this library
    Return : None
    """
    # Global test
    sat_manager = SatManager()
    sat_manager.load_folder()
    for file_name in sat_manager.__problem_dict :
        print(file_name)
        for solver_name in sat_manager.get_solvers() :
            sat_manager.solve(file_name=file_name, solver_name=solver_name)
    print(sat_manager)

if __name__ == '__main__':
    main()
