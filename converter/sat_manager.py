#! /usr/bin/env python3
# coding: utf8

"""
File : sat_manager.py
Author : lgbarrere
Brief : To read and solve DIMACS files with PySAT
"""
from os import path
from os import listdir

from pysat.formula import CNF
from pysat.solvers import Solver

from converter import Constants


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
    def get_solver_info(self, solver_name):
        """
        Brief : Get the information of the given solver
        Return : The solver information
        > solver_name : The name of the solver
        """
        return self.solver_dict[solver_name]


class SatManager:
    """
    Brief : Allows PySAT solvers to solve CNF-SAT formulas
    """
    __CONST = Constants()
    __FOLDER_PATH = path.join(
        __CONST.get_root_folder(), __CONST.get_data_folder()
        )


    def __init__(self):
        self.__avail_solver_list = [
            'Cadical', 'Gluecard3', 'Gluecard4', 'Glucose3',
            'Glucose4', 'Lingeling', 'Maplechrono', 'Maplecm',
            'Mergesat3', 'Minicard', 'Minisat22', 'Minisat-gh'
            ]

        self.problem_dict = {} # file_name : SatInformation


    ## Getters
    def get_folder(self) :
        """
        Brief : Get the path to the data folder
        Return : The path
        """
        return self.__FOLDER_PATH


    def get_problem(self, file_name):
        """
        Brief : Get the problem with the given file name
        Return : The problem
        > file_name : The loaded file
        """
        return self.problem_dict[file_name]


    def get_solvers(self) :
        """
        Brief : Get a list of available CNF-SAT solvers
        Return : The list of solvers
        """
        return self.__avail_solver_list


    def get_solution(self, file_name, solver_name):
        """
        Brief : Check if the formula is solved or not
        Return : None if didn't try to solve, True if solved, False otherwise
        > file_name : The loaded file
        > solver_name : Name of the solver
        """
        return self.problem_dict[file_name].solver_dict[solver_name].solution


    ## Methods
    def load_file(self, file_name, folder=None):
        """
        Brief : Load the given DIMACS file from the data folder
        Return : None
        > file_name : The file to load
        > folder : Optional sub folder from which to load the file
        """
        folder_path = self.get_folder()
        if folder is not None :
            folder_path = path.join(folder_path, folder)
        
        file_path = path.join(folder_path, file_name)
        if path.isfile(file_path) :
            self.problem_dict[file_name] = SatProblem(
                cnf=CNF(from_file=file_path)
                )


    def load_folder(self, folder=None):
        """
        Brief : Load all DIMACS files from the data folder
        Return : None
        > folder : Optional sub folder from which to load the files
        """
        folder_path = self.get_folder()
        if folder is not None :
            folder_path = path.join(folder_path, folder)
        for file_name in listdir(folder_path) :
            self.load_file(file_name, folder)


    def solve(self, file_name=None, cnf=None, solver_name='Cadical'):
        """
        Brief : Solve a CNF with the given solver
        Return : None
        > file_name : The loaded file
        > cnf = The CNF to solve
        > solver_name : The solver to use
        """
        if file_name is None :
            if cnf is not None :
                with Solver(
                    name=solver_name, bootstrap_with=cnf.clauses
                    ) as solver :
                    solver.solve()
        else :
            problem = self.problem_dict[file_name]
            if solver_name not in problem.solver_dict :
                problem.solver_dict[solver_name] = Solverinformation()
            info = problem.solver_dict[solver_name]
            if cnf is None :
                cnf = problem.cnf
            with Solver(
                name=solver_name, bootstrap_with=cnf.clauses
                ) as solver :
                info.solution = solver.solve()
                info.model = solver.get_model()


    def solve_folder(self, folder, solver_name='Cadical'):
        """
        Brief : Start solving an entire folder and set the time to proceed
        Return : None
        """
        for file_name in listdir(__FOLDER_PATH) :
            file_path = os.path.join(__FOLDER_PATH, file_name)
            if os.path.isfile(file_path) :
                self.solve(file_name=file_name, solver_name=solver_name)


    def __repr__(self):
        text_list = []
        for file_name in self.problem_dict :
            info = self.problem_dict[file_name]
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

    sat_manager = SatManager()
    sat_manager.load_folder()
    for file_name in sat_manager.problem_dict :
        for solver_name in sat_manager.get_solvers() :
            sat_manager.solve(file_name=file_name, solver_name=solver_name)
    print(sat_manager)

if __name__ == "__main__":
    main()