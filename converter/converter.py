#! /usr/bin/env python3
# coding: utf8

"""
File : converter.py
Author : lgbarrere
Brief : To convert a CNF-SAT formula into its ILP version
"""


import os
from os import path
import logging as lg
from ast import literal_eval


class Converter:
    """
    Brief : Allows to convert a CNF-SAT into an ILP instance
    with a given file name or CNF string
    """
    def __init__(self):
        self.file_name = "" # Name of the CNF-SAT file
        self.__converted = False # Convertion applied or not
        self.__maximize = "" # CNF-SAT formula
        self.__constraints = "" # ILP constraints
        self.__binary = "" # Specify each CNF-SAT variable as binary
        self.nb_variables = 0 # Number of variables
        self.nb_clauses = 0 # Number of clauses
        self.__prefix = "z"


    def _formula_to_constraints(self, lines):
        """
        Brief : Transform the given DIMACS format lines into an ILP in string
        Return : None
        > lines : The lines from a DIMACS file format
        """
        self.__maximize = "Maximize\n"
        self.__constraints = "Subject To\n"
        self.__binary = "Binary\n"
        nb_clauses = 1

        if lines is None:
            return

        for line in lines:
            words = line.split()
            # Ignore DIMACS comments
            if words[0] != "c" and words[0] != "\n":
                # Get the number of variables and clauses
                if words[0] == "p":
                    i = 1
                    if words[i] == "cnf":
                        i += 1
                    self.nb_variables = literal_eval(words[i])
                    self.nb_clauses = literal_eval(words[i+1])

                    # Set the CNF-SAT variables to maximize and as binaries
                    self.__maximize += "  Obj: "
                    self.__binary += "  "
                    for i in range(1, self.nb_variables+1):
                        self.__maximize += self.__prefix + str(i)
                        self.__binary += self.__prefix + str(i)
                        if i < self.nb_variables:
                            self.__maximize += " + "
                            self.__binary += " "
                    self.__maximize += "\n"
                    self.__binary += "\n"
                # Start writting the constraints
                else:
                    self.__constraints += "  C" + str(nb_clauses) + " : "
                    i = 0
                    while True:
                        # Get each variable as int (to know if it's positive)
                        val = literal_eval(words[i])
                        if val < 0:
                            # Respect the rule : "not(x) = 1 - x"
                            self.__constraints += "(1 - " + self.__prefix + \
                                                str(abs(val)) + ")"
                        elif val > 0:
                            self.__constraints += self.__prefix + words[i]
                        # This condition means the line ended, break the loop
                        else:
                            self.__constraints += " >= 1\n"
                            break
                        # if the line is not ended, add "+" in the constraint
                        if words[i+1] != "0":
                            self.__constraints += " + "
                        i += 1
                    nb_clauses += 1
        self.__converted = True


    def _read_dimacs_file(self, file_name):
        """
        Brief : Open a DIMACS file with its given name to get each line
        Return : Each line as an element of the returned list
        > fileName : The name of the file to open
        """
        self.file_name = file_name
        directory = path.dirname(path.dirname(__file__))
        path_to_file = path.join(directory, "data", file_name)

        try:
            with open(path_to_file, "r") as file:
                lg.debug("Reading file %s...", file_name)
                lines = file.readlines()
                return lines
        except FileNotFoundError as error:
            lg.critical("The file was not found. %s", error)
        return None


    def is_converted(self):
        """
        Brief : Check if the conveter has already applied a convertion
        Return : True is a convertion has been done, False otherwise
        """
        if self.__converted:
            return True
        return False


    def print_ilp(self):
        """
        Brief : Print the converted formula from CNF-SAT into ILP
        Return : None
        """
        if self.is_converted():
            print(self.__maximize + self.__constraints + self.__binary + "End")
        else:
            lg.warning("No CNF-SAT has been converted into ILP so far.\n")


    def save_ilp_in_file(self, file_name):
        """
        Brief : Save a converted ILP in a file (created if missing) with a name
        Return : None
        > fileName : The name of the file to open
        """
        # If nothing has been converted earlier, don't save anything
        if not self.is_converted():
            lg.warning("Can't save a non-existent ILP.\n")
            return
        
        save_folder_name = "saves"
        directory = path.dirname(path.dirname(__file__))
        path_to_folder = path.join(directory, save_folder_name)
        path_to_file = path.join(path_to_folder, file_name)

        # Create folder and/or file if missing, then save the ILP
        os.makedirs(path_to_folder, exist_ok=True)        
        with open(path_to_file, "w") as file:
            lg.debug("Saving in file %s...", file_name)
            file.write(self.__maximize)
            file.write(self.__constraints)
            file.write(self.__binary)
            file.write("End")


    def convert_from_file(self, file_name):
        """
        Brief : Convert a CNF-SAT formula into ILP from the given fileName
        Return : None
        > fileName : The name of the file to open
        """
        lines = self._read_dimacs_file(file_name)
        self._formula_to_constraints(lines)


def main():
    """
    Brief : Test some uses of this library
    Return : None
    """
    lg.basicConfig(level=lg.DEBUG)
    converter = Converter()
    converter.convert_from_file("test.cnf")
    converter.save_ilp_in_file("test.ilp")
    converter.print_ilp()
    print("n = " + str(converter.nb_variables) + " m = " + str(converter.nb_clauses))


if __name__ == "__main__":
    main()
