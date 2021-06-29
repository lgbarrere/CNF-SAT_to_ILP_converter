#! /usr/bin/env python3
# coding: utf8

"""
File : converter.py
Author : lgbarrere
Brief : To convert a CNF-SAT formula into its ILP version
"""


import os
from os import path
from os.path import isfile, join
from os import listdir
import shutil
from pathlib import Path
import logging as lg
import time

import pulp


class Constants:
    """
    Brief : Constants
    """
    __ROOT_FOLDER_NAME = path.dirname(path.dirname(__file__)) # Project folder
    __DATA_FOLDER_NAME = 'data' # Folder containing files to convert
    __SAVE_FOLDER_NAME = 'saves' # Folder to save the converted files
    __RESULT_FOLDER_NAME = 'result' # Folder to save ILP solutions
    __RESULT_FILE_NAME = 'result.sol' # File to save ILP solutions


    def __init__(self):
        pass


    ## Getters
    def get_root_folder(self):
        """
        Brief : Getter for the root folder name
        Return : The root folder name
        """
        return self.__ROOT_FOLDER_NAME


    def get_data_folder(self):
        """
        Brief : Getter for the data folder name
        Return : The date folder name
        """
        return self.__DATA_FOLDER_NAME


    def get_save_folder(self):
        """
        Brief : Getter for the save folder name
        Return : The save folder name
        """
        return self.__SAVE_FOLDER_NAME


    def get_result_folder(self):
        """
        Brief : Getter for the result folder name
        Return : The result folder name
        """
        return self.__RESULT_FOLDER_NAME


    def get_result_file(self):
        """
        Brief : Getter for the result file name
        Return : The result file name
        """
        return self.__RESULT_FILE_NAME


class ILPFormula:
    """
    Brief : Store every local ILP formula
    """
    __PREFIX = 'z' # Prefix of converted variables
    __OBJECTIVE = f'Maximize\n  Obj: {__PREFIX}\n' # Objective


    def __init__(self):
        self.converted = False # Conversion state
        self.constraint_dict = {} # ILP constraints {name : (term_list, goal)}
        self.binary_dict = {} # Binaries {sat_variable : ilp_variable}
        self.size = (0, 0) # Respectively number of variables and clauses


    ## Getters
    def is_converted(self):
        """
        Brief : Check if the conveter has already applied a convertion
        Return : True is a convertion has been done, False otherwise
        """
        return self.converted


    def get_prefix(self):
        """
        Brief : Getter for the prefix of ILP variables
        Return : The prefix
        """
        return self.__PREFIX


    def get_objective(self):
        """
        Brief : Getter for the Objective function of ILP variables
        Return : The objective function
        """
        return self.__OBJECTIVE


    def get_constraint(self):
        """
        Brief : Getter for the constraints
        Return : The constraints
        """
        return self.constraint_dict


    def get_binaries(self):
        """
        Brief : Getter for the binaries
        Return : The binaries
        """
        return self.binary_dict


    def get_nb_variables(self):
        """
        Brief : Getter for the number of variables
        Return : The number of variables
        """
        return self.size[0]


    def get_nb_clauses(self):
        """
        Brief : Getter for the number of clauses
        Return : The number of clauses
        """
        return self.size[1]


    def __repr__(self):
        if self.converted:
            constraint_list = []
            constraint_list.append('Subject To\n')
            for name in self.constraint_dict :
                expr, goal = self.constraint_dict[name]
                expr_str = ' '.join(expr)
                constraint_list.append(f'  {name}: {expr_str} >= {goal}\n')
            tmp_binaries = '\n  '.join(self.binary_dict.values())
            binaries = f'Binary\n  {tmp_binaries}\n'
            return self.__OBJECTIVE + ''.join(constraint_list) + \
                   binaries + 'End'
        lg.warning("No CNF-SAT has been converted into ILP so far.")
        return f'Formula : {str(None)}\n'


class Converter(Constants):
    """
    Brief : Allows to convert a CNF-SAT into an ILP instance
    with a given file name or CNF string
    """
    def __init__(self):
        super().__init__()
        self.__formula_dict = {} # formula associated to a file name
        self.__ilp_string_dict = {} # string of ILP associated to a file name


    ## Getters
    def get_formula(self, file_name):
        """
        Brief : Get the ILP formula from file_name
        Return : The formula
        """
        return self.__formula_dict[to_ilp_suffix(file_name)]


    def get_ilp_string(self, file_name):
        """
        Brief : Get the string of an ILP from file_name
        Return : The ILP string
        """
        return self.__ilp_string_dict[to_ilp_suffix(file_name)]


    ## Methods
    def get_data_path(self, optional_dir = None):
        """
        Brief : Get the path to data folder
        Return : The path (string)
        """
        directory = path.dirname(path.dirname(__file__))
        path_to_folder = path.join(directory, self.get_data_folder())
        if optional_dir is not None:
            path_to_folder = path.join(path_to_folder, optional_dir)
        return path_to_folder


    def get_save_path(self, optional_dir = None):
        """
        Brief : Get the path to data folder
        Return : The path (string)
        """
        directory = path.dirname(path.dirname(__file__))
        path_to_folder = path.join(directory, self.get_save_folder())
        if optional_dir is not None:
            path_to_folder = path.join(path_to_folder, optional_dir)
        return path_to_folder


    def __read_dimacs_file(self, file_name, optional_dir = None):
        """
        Brief : Open a DIMACS file with its given name to get each line
        Return : Each line as an element of the returned list
        > file_name : The name of the file to open
        """
        lg.debug("Reading file %s.", file_name)
        path_to_folder = self.get_data_path(optional_dir)
        path_to_file = path.join(path_to_folder, file_name)

        try:
            with open(path_to_file, 'r') as file:
                lines = file.readlines()
                lg.debug("Read done !")
                return lines
        except FileNotFoundError as error:
            lg.critical("The file was not found. %s", error)
        return None


    def __convert_to_ilp(self, lines, file_name):
        """
        Brief : Convert a CNF-SAT formula into ILP
        Return : None
        > lines : lines got from the file
        > file_name : The name of the file to get formula
        """
        # Initializations
        file_name = to_ilp_suffix(file_name)
        formula = self.__formula_dict[file_name]
        formula.converted = False
        formula.binary_dict = {} # Match SAT variables to ILP variables
         # Consider key 0 as objective
        formula.binary_dict[0] = formula.get_prefix()
        nb_clauses = 1

        # Process
        for line in lines:
            words = line.split()
            # Ignore DIMACS comments
            if words[0] == 'c' or words[0] == '\n':
                continue
            # Get the number of variables and clauses
            if words[0] == 'p':
                i = 1
                if words[i] == 'cnf':
                    i += 1
                formula.size = (int(words[i]), int(words[i + 1]))
            # Start writting the constraints
            else:
                word_list = []
                i = 0
                val = int(words[i])
                goal = 1
                while val != 0:
                    # Get each variable as int (to know if it's positive)
                    if val < 0:
                        # Respect the rule : not(0) = 1 and not(1) = 0
                        val = -val
                        word_list.append('-')
                        goal -= 1
                    elif val > 0 and i > 0:
                        word_list.append('+')
                    # Set the CNF-SAT variables as binaries
                    formula.binary_dict[val] = f'{formula.binary_dict[0]}{val}'
                    word_list.append(formula.binary_dict[val])
                    i += 1
                    val = int(words[i])
                formula.constraint_dict[f'C{nb_clauses}'] = (word_list, goal)
                nb_clauses += 1
        formula.converted = True


    def __ilp_to_string(self, file_name):
        """
        Brief : Convert the ILP from file_name to a string
        Return : None
        """
        file_name = to_ilp_suffix(file_name)
        formula = self.__formula_dict[file_name]
        self.__ilp_string_dict[file_name] = str(formula)


    def convert_from_file(self, file_name, optional_dir = None):
        """
        Brief : Convert a CNF-SAT formula into ILP from the given file_name
        Return : None
        > file_name : The name of the file to open
        > optional_dir : sub folder with the file to convert
        """
        lines = self.__read_dimacs_file(file_name, optional_dir)
        if lines is None:
            return
        file_name = to_ilp_suffix(file_name)
        # If the conversion has not already been set
        if file_name not in self.__formula_dict :
            self.__formula_dict[file_name] = ILPFormula()
            self.__convert_to_ilp(lines, file_name)
            self.__ilp_to_string(file_name)
        else :
            lg.warning("This file has already been converted.")


    def convert_from_folder(self, optional_dir = None):
        """
        Brief : Convert all CNF files into ILP files from the given folder_name
        and save the result in the saves folder, if a folder_name is given,
        the file is saves in
        Return : None
        > optional_dir : The name of the folder to convert files from
        """
        path_to_folder = self.get_data_path(optional_dir)

        if optional_dir is None:
            lg.debug("Converting files in folder %s.", self.get_data_folder())
        else :
            relative_path = f'{self.get_data_folder()}/{optional_dir}'
            lg.debug("Converting files in folder %s.", relative_path)

        lg.disable(level=lg.DEBUG)
        for file_name in listdir(path_to_folder):
            path_to_file = join(path_to_folder, file_name)
            if isfile(path_to_file):
                try:
                    with open(path_to_file, 'r'):
                        self.convert_from_file(file_name, optional_dir)
                except FileNotFoundError as error:
                    lg.critical("The file was not found. %s", error)
        lg.disable(level=lg.NOTSET)
        lg.debug("Folder conversion done !")


    def save_ilp_in_file(self, file_name, optional_dir = None):
        """
        Brief : Save a converted ILP in a file (created if missing)
        Return : None
        > file_name : The name of the file to open
        > optional_dir : folder to save the file (created if missing)
        """
        if file_name is None :
            lg.critical("No save file name was given.")
            return
        file_name = to_ilp_suffix(file_name)
        # If nothing has been converted earlier, don't save anything
        if not self.__formula_dict[file_name].is_converted() :
            lg.warning("Can't save a non converted ILP.")
            return

        lg.debug("Saving in file %s.", file_name)
        directory = path.dirname(path.dirname(__file__))
        path_to_folder = path.join(directory, self.get_save_folder())
        if optional_dir is not None:
            path_to_folder = path.join(path_to_folder, optional_dir)
        path_to_file = path.join(path_to_folder, file_name)
        # Create folder and/or file if missing, then save the ILP
        os.makedirs(path_to_folder, exist_ok=True)
        if not os.path.isfile(path_to_file) :
            with open(path_to_file, 'w') as file:
                file.write(self.get_ilp_string(file_name))
            lg.debug("Save done !")
        else :
            lg.warning("This save already exists.")


    def save_all_in_folder(self, optional_dir=None):
        """
        Brief : Save all converted ILP in a folder
        Return : None
        > optional_dir : folder to save the files (created if missing)
        """
        if optional_dir is None :
            lg.debug("Saving all in %s.", self.get_save_folder())
        else :
            relative_path = f'{self.get_save_folder()}/{optional_dir}'
            lg.debug("Saving all in %s.", relative_path)
        lg.disable(level=lg.DEBUG)
        for file_name in self.__formula_dict :
            self.save_ilp_in_file(file_name, optional_dir)
        lg.disable(level=lg.NOTSET)
        lg.debug("Folder save done !")


    def clear_save_folder(self, optional_dir = None):
        """
        Brief : Delete all files in the given folder_name
        Return : None
        > folder_name : The name of the folder to clear
        """
        directory = path.dirname(path.dirname(__file__))
        path_to_folder = path.join(directory, self.get_save_folder())
        if optional_dir is not None:
            path_to_folder = path.join(path_to_folder, optional_dir)
            relative_saves_path = f'{self.__SAVE_FOLDER_NAME}/{optional_dir}'
            lg.debug("Clearing folder %s.", relative_saves_path)
        else:
            lg.debug("Clearing folder %s.", self.get_save_folder())
        if not os.path.exists(path_to_folder):
            lg.warning("The folder to clear doesn't exist.")
            return
        for file_name in listdir(path_to_folder):
            path_to_file = join(path_to_folder, file_name)
            try:
                if isfile(path_to_file):
                    os.remove(path_to_file)
            except OSError as error:
                lg.critical("The file was not found. %s", error)
        lg.debug("Folder cleared !")


    def clear_all_save_folder(self):
        """
        Brief : Delete all files and folder in the save folder
        Return : None
        """
        directory = path.dirname(path.dirname(__file__))
        path_to_folder = path.join(directory, self.get_save_folder())
        lg.debug("Clearing folder %s.", self.get_save_folder())

        for file_name in listdir(path_to_folder):
            file_path = join(path_to_folder, file_name)
            try:
                if isfile(file_path):
                    os.remove(file_path)
                elif path.isdir(file_path):
                    shutil.rmtree(file_path)
            except OSError as error:
                lg.critical("Failed to delete %s. %s", file_path, error)
        lg.debug("Folder cleared !")


class PulpProblem:
    """
    Brief : Defines a PuLP problem
    """
    def __init__(self):
        self.problem = None
        self.status = pulp.LpStatusUndefined
        self.var_dict = {}
        self.time = 0


    def is_solved(self):
        """
        Brief : Check if the problem has been solved or not
        Return : True if the problem is solved, False otherwise
        """
        return self.status != pulp.LpStatusNotSolved and \
               self.status != pulp.LpStatusUndefined


    ## Getters
    def get_status(self):
        """
        Brief : Getter for the status
        Return : string of status
        """
        return str(pulp.LpStatus[self.status])


    def __repr__(self):
        print_list = []
        print_list.append('Problem : ' + str(self.problem))
        if self.status != pulp.LpStatusUndefined :
            print_list.append('Objective : ' + str(self.problem.objective))
        else :
            print_list.append('Objective : None')
        print_list.append('Status : ' + str(pulp.LpStatus[self.status]))
        print_list.append('Execution time : ' + str(self.time))
        return '\n'.join(print_list) + '\n'


class PulpConverter(Converter):
    """
    Brief : Get an ILP instance to create its PuLP version
    """
    def __init__(self):
        super().__init__()
        self.__solver_list = pulp.listSolvers(onlyAvailable=True)
        self.__problem_dict = {}


    ## Getters
    def get_problem(self, file_name):
        """
        Brief : Getter for the ILP problem from file_name
        Return : The ILP problem
        """
        return self.__problem_dict[to_ilp_suffix(file_name)]


    def get_solvers(self):
        """
        Brief : Getter for the available solvers
        Return : The solver list
        """
        return self.__solver_list


    ## Methods
    def define_problem(self, file_name, name='NoName'):
        """
        Brief : If a dimacs has been converted into ILP, define the problem
        on this converted problem
        Return : True if the problem is defined, False otherwise
        """
        file_name = to_ilp_suffix(file_name)
        formula = self.get_formula(file_name)
        if not formula.is_converted() :
            return False
        if file_name in self.__problem_dict :
            lg.warning("Problem already defined.")
            return False

        pulp_problem = PulpProblem()
        self.__problem_dict[file_name] = pulp_problem
        pulp_problem.problem = pulp.LpProblem(name=name, sense=pulp.LpMaximize)

        # Variables
        binary_dict = formula.get_binaries()
        pulp_problem.var_dict = {}
        for (key, value) in binary_dict.items():
            pulp_problem.var_dict[value] = pulp.LpVariable(
                name=binary_dict[key], cat=pulp.LpBinary
                )

        # Constraints
        constraint_dict = formula.get_constraint()
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
                var_list.insert(0, (pulp_problem.var_dict[term[i]], sign))
                i += 1

            pulp_problem.problem += pulp.LpConstraint(
                e=pulp.LpAffineExpression(e=var_list),
                sense=pulp.LpConstraintGE,
                rhs=constraint[1]
                )

        # Objective function
        pulp_problem.problem += pulp.LpVariable(
            name=binary_dict[0], lowBound=1, upBound=1
            )
        pulp_problem.status = pulp.LpStatusNotSolved
        return True


    def define_problem_from_folder(self, optional_dir, name='NoName'):
        """
        Brief : Define problems from a folder converted into ILP,
        define the problem on all converted problems
        Return : None
        """
        if optional_dir is None :
            lg.debug("Define all from %s.", self.get_data_folder())
        else :
            relative_path = f'{self.get_save_folder()}/{optional_dir}'
            lg.debug("Define all from %s.", relative_path)
        lg.disable(level=lg.DEBUG)
        path_to_folder = self.get_data_path(optional_dir)
        for file_name in listdir(path_to_folder) :
            path_to_file = os.path.join(path_to_folder, file_name)
            if os.path.isfile(path_to_file) :
                self.define_problem(file_name, name)
        lg.disable(level=lg.NOTSET)
        lg.debug("Folder definition done !")


    def solve(self, file_name, solver=None):
        """
        Brief : Start solving and set the time to proceed
        Return : None
        """
        file_name = to_ilp_suffix(file_name)
        pulp_problem = self.__problem_dict[file_name]
        if not pulp_problem.is_solved() :
            start_time = time.time()
            # If the solver is interrupted, consider the problem is unsolved
            try :
                pulp_problem.status = pulp_problem.problem.solve(solver)
            except pulp.apis.core.PulpSolverError :
                lg.warning("Interrupted solver.")
                pulp_problem.status = pulp.LpStatusNotSolved
            pulp_problem.time = time.time() - start_time
        else :
            lg.warning("Undefined problem or already solved.")



    def solve_folder(self, optional_dir, solver=None):
        """
        Brief : Start solving an entire folder and set the time to proceed
        Return : None
        """
        if optional_dir is None :
            lg.debug("Solving all from %s.", self.get_data_folder())
        else :
            relative_path = f'{self.get_save_folder()}/{optional_dir}'
            lg.debug("Solving all from %s.", relative_path)
        lg.disable(level=lg.DEBUG)
        path_to_folder = self.get_data_path(optional_dir)
        for file_name in listdir(path_to_folder) :
            path_to_file = os.path.join(path_to_folder, file_name)
            if os.path.isfile(path_to_file) :
                self.solve(file_name, solver)
        lg.disable(level=lg.NOTSET)
        lg.debug("Folder solve done !")


    def save_results(self):
        """
        Brief : Save all solved ILP results in a file (created if missing)
        Return : None
        """
        # If the file has been solved
        folder = self.get_result_folder()
        lg.debug("Saving solutions in folder %s.", folder)
        path_to_folder = path.join(self.get_root_folder(), folder)
        path_to_file = path.join(path_to_folder, self.get_result_file())
        # Create folder and/or file if missing, then save the solutions
        os.makedirs(path_to_folder, exist_ok=True)
        with open(path_to_file, 'w') as file:
            for (file_name, problem) in self.__problem_dict.items() :
                file.write(f'File : {file_name} | ')
                file.write(f'Status : {problem.get_status()} | ')
                file.write(f'Execution time : {problem.time}\n')
        lg.debug("Solutions Saved !")


def path_tail(path_name):
    """
    Brief : Get the name of the last element (tail) in path_name
    Return : The tail of path_name
    """
    head, tail = path.split(path_name)
    return tail or path.basename(head)


def to_ilp_suffix(file):
    """
    Brief : Change the extension of the given file name by '.lpt'
    Return : The modified file name
    """
    return Path(file).with_suffix('.lpt')


def main():
    """
    Brief : Test some uses of this library
    Return : None
    """
    # verbose debug and prepare the tests
    lg.basicConfig(level=lg.DEBUG)
    test_folder_name = 'dimacs'
    converter = PulpConverter()
    converter.clear_all_save_folder()

    # test limits in example files
    test_file = 'test.cnf'
    converter.convert_from_file(test_file)
    converter.save_ilp_in_file(test_file)
    print(f'n = {converter.get_formula(test_file).get_nb_variables()}')
    print(f'm = {converter.get_formula(test_file).get_nb_clauses()}')
    converter.convert_from_folder()

    lg.disable(level=lg.DEBUG)
    example_file = 'example.cnf'
    converter.convert_from_file(example_file)
    converter.define_problem(example_file)
    converter.solve(example_file)
    converter.save_results()
    print(converter.get_formula(example_file))
    print(converter.get_problem(example_file))

    # test with important data folder
    lg.disable(level=lg.NOTSET)
    converter.convert_from_folder(test_folder_name)
    converter.save_all_in_folder(test_folder_name)


if __name__ == "__main__":
    main()
