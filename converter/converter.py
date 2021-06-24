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


class Converter:
    """
    Brief : Allows to convert a CNF-SAT into an ILP instance
    with a given file name or CNF string
    """
    __DATA_FOLDER_NAME = 'data' # Folder containing the cnf files to convert
    __SAVE_FOLDER_NAME = 'saves' # Folder in which to save the converted files
    __PREFIX = 'z' # Prefix of converted variables
    __OBJECTIVE = f'Maximize\n  Obj: {__PREFIX}\n' # CNF-SAT formula


    def __init__(self):
        self.__file_converted = ['', False] # SAT file name and conversion state
        self.__constraints_list = [] # ILP constraints in list
        self.__constraints = '' # ILP constraints
        self.__binary_dict = {} # Match SAT variables to ILP variables
        self.__binary = '' # Specify each CNF-SAT variable as binary
        self.__nb_variables = 0 # Number of variables
        self.__nb_clauses = 0 # Number of clauses


    ## Getters
    def get_prefix(self):
        """
        Brief : Getter for the prefix of ILP variables
        Return : The prefix
        """
        return self.__PREFIX


    def get_file_name(self):
        """
        Brief : Getter for the file name
        Return : The file name
        """
        return self.__file_converted[0]


    def get_constraints(self):
        """
        Brief : Getter for the constraints
        Return : The constraints
        """
        return self.__constraints_list


    def get_binaries(self):
        """
        Brief : Getter for the binaries
        Return : The binaries
        """
        return self.__binary_dict


    def get_nb_variables(self):
        """
        Brief : Getter for the number of variables
        Return : The number of variables
        """
        return self.__nb_variables


    def get_nb_clauses(self):
        """
        Brief : Getter for the number of clauses
        Return : The number of clauses
        """
        return self.__nb_clauses


    ## Methods
    def _formula_to_constraints(self, lines):
        """
        Brief : Transform the given DIMACS format lines into an ILP in string
        Return : None
        > lines : The lines from a DIMACS file format
        """
        # Initializations
        self.__file_converted[1] = False
        self.__constraints_list = []
        self.__binary_dict = {}
        # Consider key 0 to get the objective variable
        self.__binary_dict[0] = self.__PREFIX
        binary_list = []
        text_line_list = []
        nb_clauses = 1

        if lines is None:
            return

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
                self.__nb_variables = int(words[i])
                self.__nb_clauses = int(words[i + 1])
            # Start writting the constraints
            else:
                tmp_line_list = []
                i = 0
                val = int(words[i])
                constraint_value = 1
                while val != 0:
                    # Get each variable as int (to know if it's positive)
                    abs_val = val
                    if val < 0:
                        # Respect the rule : not(0) = 1 and not(1) = 0
                        abs_val = -val
                        tmp_line_list.append('- ')
                        constraint_value -= 1
                    elif val > 0 and i > 0:
                        tmp_line_list.append('+ ')
                    self.__binary_dict[abs_val] = f'{self.__PREFIX}{abs_val}'
                    tmp_line_list.append(f'{self.__binary_dict[abs_val]} ')
                    i += 1
                    val = int(words[i])
                tmp_line_list.append(f'>= {constraint_value}')
                constraint = ''.join(tmp_line_list)
                self.__constraints_list.append(constraint)
                text_line_list.append(f'  C{nb_clauses}: {constraint}\n')
                nb_clauses += 1
        # Set the CNF-SAT variables as binaries
        for binary in self.__binary_dict.values():
            binary_list.append(f'  {binary}\n')

        self.__constraints = 'Subject To\n' + ''.join(text_line_list)
        self.__binary = 'Binary\n' + ''.join(binary_list)
        self.__file_converted[1] = True


    def _read_dimacs_file(self, file_name, optionnal_dir = None):
        """
        Brief : Open a DIMACS file with its given name to get each line
        Return : Each line as an element of the returned list
        > file_name : The name of the file to open
        """
        lg.debug("Reading file %s.", file_name)
        self.__file_converted[0] = path_tail(file_name)
        directory = path.dirname(path.dirname(__file__))
        path_to_file = path.join(directory, self.__DATA_FOLDER_NAME)

        if optionnal_dir is None:
            path_to_file = path.join(path_to_file, file_name)
        else:
            path_to_file = path.join(path_to_file, optionnal_dir, file_name)

        try:
            with open(path_to_file, 'r') as file:
                lines = file.readlines()
                lg.debug("Read done !")
                return lines
        except FileNotFoundError as error:
            lg.critical("The file was not found. %s", error)
        return None


    def is_converted(self):
        """
        Brief : Check if the conveter has already applied a convertion
        Return : True is a convertion has been done, False otherwise
        """
        return self.__file_converted[1]


    def save_ilp_in_file(self, file_name = None, optionnal_dir = None):
        """
        Brief : Save a converted ILP in a file (created if missing) with a name
        Return : None
        > file_name : The optionnal name of the file to open
        > optionnal_dir : folder to save the file (created if missing)
        Note : If no file name is given, save the last converted file
        """
        # If nothing has been converted earlier, don't save anything
        if not self.is_converted():
            lg.warning("Can't save a non-existent ILP.\n")
            return
        # If no file name is given, use the last converted file instead
        if file_name is None :
            file_name = Path(self.__file_converted[0]).with_suffix('.lpt')

        lg.debug("Saving in file %s.", file_name)
        directory = path.dirname(path.dirname(__file__))
        path_to_folder = path.join(directory, self.__SAVE_FOLDER_NAME)
        if optionnal_dir is not None:
            path_to_folder = path.join(path_to_folder, optionnal_dir)
        path_to_file = path.join(path_to_folder, file_name)
        # Create folder and/or file if missing, then save the ILP
        os.makedirs(path_to_folder, exist_ok=True)
        with open(path_to_file, 'w') as file:
            file.write(self.__OBJECTIVE)
            file.write(self.__constraints)
            file.write(self.__binary)
            file.write('End')
        lg.debug("Save done !")


    def convert_from_file(self, file_name, optionnal_dir = None):
        """
        Brief : Convert a CNF-SAT formula into ILP from the given file_name
        Return : None
        > file_name : The name of the file to open
        """
        lines = self._read_dimacs_file(file_name, optionnal_dir)
        self._formula_to_constraints(lines)


    def convert_from_folder(self, folder_name = None):
        """
        Brief : Convert all CNF files into ILP files from the given folder_name
        Return : None
        > folder_name : The name of the folder to convert files from
        """
        directory = path.dirname(path.dirname(__file__))
        path_to_folder = path.join(directory, self.__DATA_FOLDER_NAME)
        if folder_name is not None:
            folder_name = path_tail(folder_name)
            path_to_folder = path.join(path_to_folder, folder_name)
            relative_saves_path = f'{self.__SAVE_FOLDER_NAME}/{folder_name}'
            lg.debug("Converting files in folder %s.", relative_saves_path)
        else:
            lg.debug("Converting files in folder %s.", self.__SAVE_FOLDER_NAME)

        lg.disable(level=lg.DEBUG)
        for file_name in listdir(path_to_folder):
            self.__file_converted[0] = file_name
            path_to_file = join(path_to_folder, file_name)
            if isfile(path_to_file):
                try:
                    with open(path_to_file, 'r'):
                        self.convert_from_file(file_name, folder_name)
                        self.save_ilp_in_file(optionnal_dir=folder_name)
                except FileNotFoundError as error:
                    lg.critical("The file was not found. %s", error)
        lg.disable(level=lg.NOTSET)
        lg.debug("Folder conversion done !")


    def clear_save_folder(self, folder_name = None):
        """
        Brief : Delete all files in the given folder_name
        Return : None
        > folder_name : The name of the folder to clear
        """
        directory = path.dirname(path.dirname(__file__))
        path_to_folder = path.join(directory, self.__SAVE_FOLDER_NAME)
        if folder_name is not None:
            path_to_folder = path.join(path_to_folder, folder_name)
            relative_saves_path = f'{self.__SAVE_FOLDER_NAME}/{folder_name}'
            lg.debug("Clearing folder %s.", relative_saves_path)
        else:
            lg.debug("Clearing folder %s.", self.__SAVE_FOLDER_NAME)
        if not os.path.exists(path_to_folder):
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
        path_to_folder = path.join(directory, self.__SAVE_FOLDER_NAME)
        lg.debug("Clearing folder %s.", self.__SAVE_FOLDER_NAME)

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


    def __repr__(self):
        if self.is_converted():
            return 'Converter :\n' + self.__OBJECTIVE + self.__constraints + \
                   self.__binary + 'End\n'
        lg.warning("No CNF-SAT has been converted into ILP so far.\n")
        return 'Converter : ' + str(None) + '\n'


class PulpConverter(Converter):
    """
    Brief : Get an ILP instance to create its PuLP version
    """
    def __init__(self):
        super().__init__()
        self.solver_list = pulp.listSolvers(onlyAvailable=True)
        self.__problem = None
        self.__status = pulp.LpStatusUndefined
        self.__var_dict = {}
        self.__time = 0


    def define_problem(self, name='NoName'):
        """
        Brief : If a dimacs has been converted into ILP, define the problem
        on this converted problem
        Return : True if the problem is defined, False otherwise
        """
        if self.is_converted() is False :
            return False

        self.__problem = pulp.LpProblem(name=name, sense=pulp.LpMaximize)

        ### Variables
        binary_dict = self.get_binaries()
        self.__var_dict = {}
        for (key, value) in binary_dict.items():
            self.__var_dict[value] = pulp.LpVariable(
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
                var_list.insert(0, (self.__var_dict[cons_split[i]], sign))
                i += 1

            res = pulp.LpConstraint(
                e=pulp.LpAffineExpression(e=var_list),
                sense=pulp.LpConstraintGE,
                rhs=int(cons_split[i+1])
                )
            self.__problem += res

        ### Objective function
        self.__problem += pulp.LpVariable(
            name=binary_dict[0], lowBound=1, upBound=1
            )
        self.__status = pulp.LpStatusNotSolved
        return True


    def solve(self):
        """
        Brief : Start solving and set the time to proceed
        Return : None
        """
        if self.__status != pulp.LpStatusUndefined :
            start_time = time.time()
            self.__status = self.__problem.solve()
            self.__time = time.time() - start_time


    def __repr__(self):
        print_list = []
        print_list.append(super().__repr__())
        print_list.append('Problem : ' + str(self.__problem))
        if self.__status != pulp.LpStatusUndefined :
            print_list.append('Objective : ' + str(self.__problem.objective))
        else :
            print_list.append('Objective : None')
        print_list.append('Status : ' + str(pulp.LpStatus[self.__status]))
        print_list.append('Execution time : ' + str(self.__time))
        return '\n'.join(print_list) + '\n'


def path_tail(path_name):
    """
    Brief : Get the name of the last element (tail) in path_name
    Return : The tail of path_name
    """
    head, tail = path.split(path_name)
    return tail or path.basename(head)


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
    converter.convert_from_file('test.cnf')
    converter.save_ilp_in_file()
    #print(converter)
    print(f'n = {converter.get_nb_variables()} m = {converter.get_nb_clauses()}')
    converter.convert_from_folder()

    lg.disable(level=lg.DEBUG)
    converter = PulpConverter()
    converter.convert_from_file('example.cnf')
    converter.define_problem()
    converter.solve()
    print(converter)

    # test with important data folder
    lg.disable(level=lg.NOTSET)
    converter.convert_from_folder(test_folder_name)


if __name__ == "__main__":
    main()
