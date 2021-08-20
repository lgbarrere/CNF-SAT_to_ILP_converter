#! /usr/bin/env python3
# coding: utf8

"""
File : converter.py
Author : lgbarrere
Brief : Convert a CNF-SAT formula into its ILP version
"""
import os
from os import path, listdir
import shutil
import logging as lg
import time

import pulp

from .utility import Constants, to_ilp_suffix, lines_from_file, split, build_path


class ILPFormula:
    """
    Brief : Defines a local ILP formula
    """
    __PREFIX = 'z' # Prefix of converted variables
    __OBJECTIVE = f'Maximize\n  Obj: {__PREFIX}\n' # Objective


    def __init__(self):
        self.converted = False # Conversion state
        self.constraint_dict = {} # ILP constraints {name : (term_list, goal)}
        self.binary_list = [] # Binaries
        self.nb_variables = 0 # Number of variables
        self.nb_clauses = 0 # Number of clauses


    ## Getters
    def get_prefix(self):
        """
        Brief : Get the prefix of ILP variables
        Return : The prefix
        """
        return self.__PREFIX


    def get_objective(self):
        """
        Brief : Get the Objective function string of ILP variables
        Return : The objective function string
        """
        return self.__OBJECTIVE


    def __repr__(self):
        if self.converted:
            constraint_list = []
            constraint_list.append('Subject To\n')
            for name in self.constraint_dict :
                expr, goal = self.constraint_dict[name]
                expr_str = ' '.join(expr)
                constraint_list.append(f'  {name}: {expr_str} >= {goal}\n')
            tmp_binaries = '\n  '.join(self.binary_list)
            binaries = f'Binary\n  {tmp_binaries}\n'
            return self.__OBJECTIVE + ''.join(constraint_list) + \
                   binaries + 'End'
        lg.warning("No CNF-SAT has been converted into ILP so far.")
        return 'Formula : None\n'


class Converter(Constants):
    """
    Brief : Allows to convert a CNF-SAT into an ILP instance
    with a given file name
    """
    def __init__(self):
        super().__init__()
        self._formula_dict = {} # formula associated to a file name
        self.__ilp_string_dict = {} # string of ILP associated to a file name


    ## Getters
    def get_ilp_string(self, file_name):
        """
        Brief : Get the string of an ILP from file name
        Return : The ILP string
        > file_name : Name of the DIMACS or ILP file concerned
        """
        return self.__ilp_string_dict[to_ilp_suffix(file_name)]


    def is_converted(self, file_name):
        """
        Brief : Check if the formula has already been converted
        Return : True is a convertion has been done, False otherwise
        > file_name : Name of the DIMACS or ILP file concerned
        """
        return self._formula_dict[to_ilp_suffix(file_name)].converted


    def get_constraint(self, file_name):
        """
        Brief : Get the constraints in a dictionary
        Return : The constraints
        > file_name : Name of the DIMACS or ILP file concerned
        """
        return self._formula_dict[to_ilp_suffix(file_name)].constraint_dict


    def get_binaries(self, file_name):
        """
        Brief : Get the binaries in a list
        Return : The binaries
        > file_name : Name of the DIMACS or ILP file concerned
        """
        return self._formula_dict[to_ilp_suffix(file_name)].binary_list


    def get_nb_variables(self, file_name):
        """
        Brief : Get the number of ILP variables
        Return : The number of ILP variables
        > file_name : Name of the DIMACS or ILP file concerned
        """
        return self._formula_dict[to_ilp_suffix(file_name)].nb_variables


    def get_nb_clauses(self, file_name):
        """
        Brief : Get the number of clauses
        Return : The number of clauses
        > file_name : Name of the DIMACS or ILP file concerned
        """
        return self._formula_dict[to_ilp_suffix(file_name)].nb_clauses


    ## Methods
    def print_ilp(self, file_name):
        """
        Brief : Print the formula linked to the given file name
        Return : None
        > file_name : Name of the DIMACS or ILP file concerned
        """
        print(self._formula_dict[to_ilp_suffix(file_name)])


    def __read_dimacs_file(self, file_name, option_folder=None):
        """
        Brief : Get every lines from a dimacs file
        Return : Every lines in a list
        > file_name : The name of the file to read
        > option_folder : If given, search the file in this sub folder
        """
        lg.debug("Reading file %s.", file_name)
        file_path = build_path(
            self.get_data_path(), option_folder, file_name
            )
        return lines_from_file(file_path)


    def __read_ilp_file(self, file_name, option_folder=None):
        """
        Brief : Get every lines from an ILP file
        Return : Every lines in a list
        > file_name : The name of the file to read
        > option_folder : If given, search the file in this sub folder
        """
        lg.debug("Reading file %s.", file_name)
        file_path = build_path(
            self.get_save_path(), option_folder, file_name
            )
        return lines_from_file(file_path)


    def __convert_to_ilp(self, lines, file_name):
        """
        Brief : Convert a CNF-SAT formula into ILP
        Return : None
        > lines : The lines got from the file
        > file_name : The name of the file to get formula
        """
        # Initializations
        file_name = to_ilp_suffix(file_name)
        formula = ILPFormula()
        self._formula_dict[file_name] = formula
        formula.converted = False
        binary_dict = {} # Match SAT variables to ILP variables
        # Consider key 0 as objective
        prefix = formula.get_prefix()
        binary_dict[0] = prefix
        nb_clauses = 0

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
                formula.nb_variables = int(words[i])
                formula.nb_clauses = int(words[i + 1])
            # Start writting the constraints
            else:
                word_list = []
                i = 0
                val = int(words[i])
                goal = 1
                nb_clauses += 1
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
                    if val not in binary_dict :
                        binary_dict[val] = f'{prefix}{val}'
                    word_list.append(binary_dict[val])
                    i += 1
                    val = int(words[i])
                formula.constraint_dict[f'C{nb_clauses}'] = (word_list, goal)
        for binary in binary_dict.values() :
            formula.binary_list.append(binary)
        formula.converted = True


    def __ilp_to_string(self, file_name):
        """
        Brief : Convert the ILP from a given file name to a string
        Return : None
        > file_name : The name of the file concerned by  the conversion
        """
        file_name = to_ilp_suffix(file_name)
        formula = self._formula_dict[file_name]
        self.__ilp_string_dict[file_name] = str(formula)


    def convert_from_file(self, file_name, option_folder=None):
        """
        Brief : Convert a CNF-SAT formula into ILP from the given file_name
        Return : None
        > file_name : The name of the file to open
        > option_folder : sub folder with the file to convert
        """
        lines = self.__read_dimacs_file(file_name, option_folder)
        if lines is None:
            return
        file_name = to_ilp_suffix(file_name)
        # If the conversion has not already been set
        if file_name not in self._formula_dict :
            self.__convert_to_ilp(lines, file_name)
            self.__ilp_to_string(file_name)
        else :
            lg.warning("This file has already been converted.")


    def __set_ilp(self, lines, file_name):
        """
        Brief : Set the ILP from a file in the formula dictionary
        Return : None
        > lines : The lines got from the file
        > file_name : The name of the file to open
        """
        # Initializations
        file_name = to_ilp_suffix(file_name)
        formula = ILPFormula()
        self._formula_dict[file_name] = formula
        formula.binary_list = []
        binary_list = []
        # Consider key 0 as objective
        prefix = formula.get_prefix()
        binary_list.append(prefix)
        nb_clauses = 0
        nb_variables = 0
        lines = ''.join(lines)
        lines = split(lines, ['Subject To\n', 'Binary\n', 'End'])

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
            nb_clauses += 1
            formula.constraint_dict[constraint_name] = (term_list, goal)

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
            nb_variables += 1

        for binary in binary_list :
            formula.binary_list.append(binary)
        formula.nb_variables = nb_variables
        formula.nb_clauses = nb_clauses
        formula.converted = True


    def ilp_from_file(self, file_name, option_folder=None):
        """
        Brief : Load ILP from the given file_name
        Return : None
        > file_name : The name of the file to open
        > option_folder : sub folder with the file to convert
        """
        lines = self.__read_ilp_file(file_name, option_folder)
        if lines is None:
            return
        file_name = to_ilp_suffix(file_name)
        # If the conversion has not already been set
        if file_name not in self._formula_dict :
            self.__set_ilp(lines, file_name)
            self.__ilp_to_string(file_name)
        else :
            lg.warning("This ilp file has already been read.")


    def ilp_from_folder(self, option_folder=None):
        """
        Brief : Load all ILP files from the given folder_name
        Return : None
        > option_folder : The name of the folder to convert files from
        """
        folder_path = build_path(self.get_save_path(), option_folder)
        relative_path = build_path(self.get_save_folder(), option_folder)
        lg.debug("Reading ILP files in folder %s.", relative_path)
        lg.disable(level=lg.DEBUG)
        for file_name in listdir(folder_path):
            file_path = path.join(folder_path, file_name)
            if path.isfile(file_path):
                try:
                    with open(file_path, 'r'):
                        self.ilp_from_file(file_name, option_folder)
                except FileNotFoundError as error:
                    lg.critical("The file was not found. %s", error)
        lg.disable(level=lg.NOTSET)
        lg.debug("Folder read !")


    def convert_from_folder(self, option_folder=None):
        """
        Brief : Convert all CNF files into ILP files from the given folder_name
        Return : None
        > option_folder : The name of the folder to convert files from
        """
        folder_path = build_path(self.get_data_path(), option_folder)
        relative_path = build_path(self.get_data_folder(), option_folder)
        lg.debug("Converting files in folder %s.", relative_path)
        lg.disable(level=lg.DEBUG)
        for file_name in listdir(folder_path):
            file_path = path.join(folder_path, file_name)
            if path.isfile(file_path):
                try:
                    with open(file_path, 'r'):
                        self.convert_from_file(file_name, option_folder)
                except FileNotFoundError as error:
                    lg.critical("The file was not found. %s", error)
        lg.disable(level=lg.NOTSET)
        lg.debug("Folder conversion done !")


    def save_ilp_in_file(self, file_name, option_folder=None):
        """
        Brief : Save a converted ILP in a file (created if missing)
        Return : None
        > file_name : The name of the file to open
        > option_folder : folder to save the file (created if missing)
        """
        if file_name is None :
            lg.critical("No save file name was given.")
            return
        file_name = to_ilp_suffix(file_name)
        # If nothing has been converted earlier, don't save anything
        if not self.is_converted(file_name) :
            lg.warning("Can't save a non converted ILP.")
            return

        lg.debug("Saving in file %s.", file_name)
        folder_path = build_path(self.get_save_path(), option_folder)
        file_path = path.join(folder_path, file_name)
        # Create folder and/or file if missing, then save the ILP
        os.makedirs(folder_path, exist_ok=True)
        if not path.isfile(file_path) :
            with open(file_path, 'w') as file:
                file.write(self.get_ilp_string(file_name))
            lg.debug("Save done !")
        else :
            lg.warning("This save already exists.")


    def save_all_in_folder(self, option_folder=None):
        """
        Brief : Save all converted ILP in a folder
        Return : None
        > option_folder : folder to save the files (created if missing)
        """
        relative_path = build_path(self.get_save_folder(), option_folder)
        lg.debug("Saving all in %s.", relative_path)
        lg.disable(level=lg.DEBUG)
        for file_name in self._formula_dict:
            self.save_ilp_in_file(file_name, option_folder)
        lg.disable(level=lg.NOTSET)
        lg.debug("Folder save done !")


    def clear_save_folder(self, option_folder=None):
        """
        Brief : Delete all files in the given folder_name
        Return : None
        > folder_name : The name of the folder to clear
        """
        folder_path = build_path(self.get_save_path(), option_folder)
        relative_path = build_path(self.get_save_folder(), option_folder)
        lg.debug("Clearing folder %s.", relative_path)
        if not path.exists(folder_path):
            lg.warning("The folder to clear doesn't exist.")
            return
        for file_name in listdir(folder_path):
            file_path = path.join(folder_path, file_name)
            try:
                if path.isfile(file_path):
                    os.remove(file_path)
            except OSError as error:
                lg.critical("The file was not found. %s", error)
        lg.debug("Folder cleared !")


    def clear_all_save_folder(self):
        """
        Brief : Delete everything in the save folder
        Return : None
        """
        folder_path = self.get_save_path()
        lg.debug("Clearing folder %s.", self.get_save_folder())

        for file_name in listdir(folder_path):
            file_path = path.join(folder_path, file_name)
            try:
                if path.isfile(file_path):
                    os.remove(file_path)
                elif path.isdir(file_path):
                    shutil.rmtree(file_path)
            except OSError as error:
                lg.critical("Failed to delete %s. %s", file_name, error)
        lg.debug("Folder cleared !")


class SolverInformation:
    """
    Brief : Give solver information
    """
    def __init__(self, solver=None, status=pulp.LpStatusUndefined):
        self.solver = solver
        self.status = status
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
        Return : The status in a string
        """
        return str(pulp.LpStatus[self.status])


    def get_time(self):
        """
        Brief : Getter for the execution time
        Return : The time
        """
        return self.time


    def __repr__(self):
        return 'Solver : ' + self.solver.name + \
               '\nStatus : ' + self.get_status() + \
               '\nExecution time : ' + str(self.time) + '\n'


class PulpProblem:
    """
    Brief : Defines a PuLP problem
    """
    def __init__(self):
        self.problem = None
        self.var_dict = {}
        self.solver_dict = {}


    ## Getters
    def get_solver_info(self, solver_name='PULP_CBC_CMD'):
        """
        Brief : Getter for the solver information (from its name)
        Return : The solver information
        > solver_name : The name of the solver to get the information
        """
        return self.solver_dict[solver_name]


    def __repr__(self):
        print_list = []
        print_list.append('Problem : ' + str(self.problem))
        print_list.append('Objective : ' + str(self.problem.objective))
        for solver_info in self.solver_dict.values() :
            print_list.append(str(solver_info))
        return '\n'.join(print_list)


class PulpConverter(Converter):
    """
    Brief : Get an ILP instance to create its PuLP version
    """
    def __init__(self):
        super().__init__()
        self.__avail_solver_dict = {}
        for solver_name in pulp.listSolvers(onlyAvailable=True):
            self.__avail_solver_dict[solver_name] = None
        self.__problem_dict = {}


    ## Getters
    def get_problem(self, file_name):
        """
        Brief : Get the ILP problem from a file name
        Return : The ILP problem
        > file_name : The name of the file to get the ILP problem
        """
        return self.__problem_dict[to_ilp_suffix(file_name)]


    def get_solvers(self):
        """
        Brief : Get the list of the available solvers
        Return : The solver list
        """
        return self.__avail_solver_dict.keys()



    def get_solver_path(self, solver_name):
        """
        Brief : Get the path of a solver from its name
        Return : The path in a string (if no path, return None)
        note : The solver must
        """
        return self.__avail_solver_dict[solver_name]


    ## Methods
    def add_solver(self, solver_name, solver_path):
        model = pulp.LpProblem('Check_solver', pulp.LpMinimize)
        model += pulp.LpVariable('v') == 1
        try:
            model.solve(pulp.getSolver(solver_name, path=solver_path))
            self.__avail_solver_dict[solver_name] = solver_path
        except pulp.apis.core.PulpSolverError:
            lg.critical(
                "The solver requested " + solver_name + \
                " can\'t be used with the path " + solver_path
                )


    def define_problem(self, file_name, name='NoName'):
        """
        Brief : Define the problem from a loaded ILP given by a file name
        Return : True if the problem is defined, False otherwise
        > file_name : The name of the ILP file
        > name : An optional name for the problem
        """
        file_name = to_ilp_suffix(file_name)
        if not self.is_converted(file_name) :
            return False
        if file_name in self.__problem_dict :
            lg.warning("Problem already defined.")
            # If a new solver has been registered, add it to this problem
            pulp_problem = self.__problem_dict[file_name]
            for solver_name in self.__avail_solver_dict.keys():
                if solver_name not in pulp_problem.solver_dict:
                    pulp_problem.solver_dict[solver_name] = SolverInformation(
                        pulp.getSolver(solver_name), pulp.LpStatusNotSolved
                        )
            return False

        pulp_problem = PulpProblem()
        self.__problem_dict[file_name] = pulp_problem
        pulp_problem.problem = pulp.LpProblem(name=name, sense=pulp.LpMaximize)

        # Variables
        binary_list = self.get_binaries(file_name)
        pulp_problem.var_dict = {}
        for value in binary_list:
            pulp_problem.var_dict[value] = pulp.LpVariable(
                name=value, cat=pulp.LpBinary
                )

        # Constraints
        constraint_dict = self.get_constraint(file_name)
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
            name=self._formula_dict[file_name].get_prefix(),
            lowBound=1, upBound=1
            )

        for solver_name in self.__avail_solver_dict.keys() :
            pulp_problem.solver_dict[solver_name] = SolverInformation(
                pulp.getSolver(solver_name), pulp.LpStatusNotSolved
                )
        return True


    def define_problem_from_folder(self, option_folder=None, name='NoName'):
        """
        Brief : Define problems from a folder converted into ILP,
        if the given folder is None, problems are defined from the saves folder
        Return : None
        > option_folder : The name of the sub folder to define problems from
        > name : The name of the problems
        """
        folder_path = build_path(self.get_save_path(), option_folder)
        relative_path = build_path(self.get_save_folder(), option_folder)
        lg.debug("Define all from %s.", relative_path)
        lg.disable(level=lg.DEBUG)
        for file_name in listdir(folder_path) :
            file_path = path.join(folder_path, file_name)
            if path.isfile(file_path) :
                self.define_problem(file_name, name)
        lg.disable(level=lg.NOTSET)
        lg.debug("Folder definition done !")


    def solve(self, file_name, solver_name='PULP_CBC_CMD', path=None, time_limit=None):
        """
        Brief : Solve a problem from its file name, updating its information
        Return : None
        > file_name : The name of the file used to define a problem to solve
        > solver_name : The name of the solver to use
        > time_limit : The maximum time taken to solve before interruption
        """
        file_name = to_ilp_suffix(file_name)
        pulp_problem = self.__problem_dict[file_name]
        solver_info = pulp_problem.solver_dict[solver_name]
        if not solver_info.is_solved() :
            start_time = time.time()
            # If the solver is interrupted, consider the problem is unsolved
            try :
                solver_info.status = pulp_problem.problem.solve(
                    pulp.getSolver(solver_name, path=path, timeLimit=time_limit)
                    )
            except pulp.apis.core.PulpSolverError :
                lg.warning("Interrupted solver.")
                solver_info.status = pulp.LpStatusNotSolved
            if solver_info.status == pulp.LpStatusNotSolved:
                solver_info.time = 'Timeout'
            else:
                solver_info.time = time.time() - start_time
        else :
            lg.warning("Undefined problem or already solved.")


    def solve_folder(
        self, option_folder=None, solver_name='PULP_CBC_CMD', time_limit=None
        ):
        """
        Brief : Start solving an entire folder and set the time to proceed
        Return : None
        > option_folder : The name of the sub folder to define problems from
        > solver_name : The name of the solver to use
        > time_limit : The maximum time taken to solve before interruption
        """
        folder_path = build_path(self.get_save_path(), option_folder)
        relative_path = build_path(self.get_save_folder(), option_folder)
        lg.debug("Solving all from %s.", relative_path)
        lg.disable(level=lg.DEBUG)
        for file_name in listdir(folder_path) :
            file_path = path.join(folder_path, file_name)
            if path.isfile(file_path) :
                self.solve(file_name, solver_name, time_limit)
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
        folder_path = path.join(self.get_root_path(), folder)
        file_path = path.join(folder_path, self.get_result_file())
        # Create folder and/or file if missing, then save the solutions
        os.makedirs(folder_path, exist_ok=True)
        with open(file_path, 'w') as file:
            for (file_name, problem) in self.__problem_dict.items() :
                file.write(f'File : {file_name}\n')
                for solver_name in self.__avail_solver_dict.keys() :
                    solver_info = problem.solver_dict[solver_name]
                    file.write(f'  Solver : {solver_name}')
                    file.write(f' | Status : {solver_info.get_status()}')
                    file.write(f' | Execution time : {solver_info.time}\n')
        lg.debug("Solutions Saved !")


def main():
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


if __name__ == "__main__":
    main()
