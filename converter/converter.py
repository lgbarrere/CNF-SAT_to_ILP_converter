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
import logging as lg
from ast import literal_eval


class Converter:
    """
    Brief : Allows to convert a CNF-SAT into an ILP instance
    with a given file name or CNF string
    """
    __DATA_FOLDER_NAME = "data" # Folder containing the cnf files to convert
    __SAVE_FOLDER_NAME = "saves" # Folder in which to save the converted files
    __PREFIX = "z" # Prefix of converted variables
    __INVERTER = "_1" # Name of the constant set to 1, to invert a binary value
    __OBJECTIVE = "Maximize\n  Obj:\n" # CNF-SAT formula
    __BOUND = "Bounds\n  1 <= " + __INVERTER + " <= 1\n" # Bound of inverter

    def __init__(self):
        self.file_name = "" # Name of the CNF-SAT file
        self.__converted = False # Convertion applied or not
        self.__constraints = "" # ILP constraints
        self.__binary = "" # Specify each CNF-SAT variable as binary
        self.nb_variables = 0 # Number of variables
        self.nb_clauses = 0 # Number of clauses


    def _formula_to_constraints(self, lines):
        """
        Brief : Transform the given DIMACS format lines into an ILP in string
        Return : None
        > lines : The lines from a DIMACS file format
        """
        self.__converted = False
        self.__constraints = "Subject To\n"
        self.__binary = "Binary\n"
        nb_clauses = 1

        if lines is None:
            return

        for line in lines:
            words = line.split()
            # Ignore DIMACS comments
            if words[0] == "c" or words[0] == "\n":
                continue
            # Get the number of variables and clauses
            if words[0] == "p":
                i = 1
                if words[i] == "cnf":
                    i += 1
                self.nb_variables = literal_eval(words[i])
                self.nb_clauses = literal_eval(words[i + 1])

                # Set the CNF-SAT variables to maximize and as binaries
                self.__binary += "  "
                for i in range(1, self.nb_variables + 1):
                    self.__binary += self.__PREFIX + str(i)
                    if i < self.nb_variables:
                        self.__binary += " "
                self.__binary += "\n"
            # Start writting the constraints
            else:
                self.__constraints += "  C" + str(nb_clauses) + ": "
                i = 0
                val = literal_eval(words[i])
                while val != 0:
                    if i > 0:
                        self.__constraints += "+ "
                    # Get each variable as int (to know if it's positive)
                    if val < 0:
                        # Respect the rule : not(0) = 1 and not(1) = 0
                        self.__constraints += self.__INVERTER + " - " + \
                                              self.__PREFIX + \
                                              str(abs(val)) + " "
                    elif val > 0:
                        self.__constraints += self.__PREFIX + words[i] + " "
                    i += 1
                    val = literal_eval(words[i])
                self.__constraints += ">= 1\n"
                nb_clauses += 1
        self.__converted = True


    def _read_dimacs_file(self, file_name):
        """
        Brief : Open a DIMACS file with its given name to get each line
        Return : Each line as an element of the returned list
        > file_name : The name of the file to open
        """
        lg.debug("Reading file %s...", file_name)
        self.file_name = file_name
        directory = path.dirname(path.dirname(__file__))
        path_to_file = path.join(directory, self.__DATA_FOLDER_NAME, file_name)

        try:
            with open(path_to_file, "r") as file:
                lines = file.readlines()
                lg.debug("Reading done !")
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
            print(self.__OBJECTIVE + self.__constraints + self.__BOUND + \
                  self.__binary + "End")
        else:
            lg.warning("No CNF-SAT has been converted into ILP so far.\n")


    def save_ilp_in_file(self, file_name):
        """
        Brief : Save a converted ILP in a file (created if missing) with a name
        Return : None
        > file_name : The name of the file to open
        """
        # If nothing has been converted earlier, don't save anything
        if not self.is_converted():
            lg.warning("Can't save a non-existent ILP.\n")
            return

        lg.debug("Saving in file %s...", file_name)
        directory = path.dirname(path.dirname(__file__))
        path_to_folder = path.join(directory, self.__SAVE_FOLDER_NAME)
        path_to_file = path.join(path_to_folder, file_name)

        # Create folder and/or file if missing, then save the ILP
        os.makedirs(path_to_folder, exist_ok=True)
        with open(path_to_file, "w") as file:
            file.write(self.__OBJECTIVE)
            file.write(self.__constraints)
            file.write(self.__BOUND)
            file.write(self.__binary)
            file.write("End")
        lg.debug("Saving done !")


    def convert_from_file(self, file_name):
        """
        Brief : Convert a CNF-SAT formula into ILP from the given file_name
        Return : None
        > file_name : The name of the file to open
        """
        lines = self._read_dimacs_file(file_name)
        self._formula_to_constraints(lines)


    def convert_from_folder(self, folder_name = None):
        """
        Brief : Convert all CNF files into ILP files from the given folder_name
        Return : None
        > folder_name : The name of the folder to convert files from
        """
        lg.debug("Converting all files in folder %s...", folder_name)
        directory = path.dirname(path.dirname(__file__))
        path_to_folder = path.join(directory, self.__DATA_FOLDER_NAME)
        if folder_name is not None:
            path_to_folder = path.join(path_to_folder, folder_name)

        for file_name in listdir(path_to_folder):
            self.file_name = file_name
            path_to_file = join(path_to_folder, file_name)
            if isfile(path_to_file):
                try:
                    with open(path_to_file, "r"):
                        self.convert_from_file(file_name)
                        save_file_name = file_name.replace(".cnf", ".lpt")
                        self.save_ilp_in_file(save_file_name)
                except FileNotFoundError as error:
                    lg.critical("The file was not found. %s", error)
        lg.debug("Folder conversion done !")


    def clear_save_folder(self, folder_name = None):
        """
        Brief : Delete all files in the given folder_name
        Return : None
        > folder_name : The name of the folder to clear
        """
        lg.debug("Clearing folder %s...", folder_name)
        directory = path.dirname(path.dirname(__file__))
        path_to_folder = path.join(directory, self.__SAVE_FOLDER_NAME)
        if folder_name is not None:
            path_to_folder = path.join(path_to_folder, folder_name)

        for file_name in listdir(path_to_folder):
            path_to_file = join(path_to_folder, file_name)
            if isfile(path_to_file):
                try:
                    os.remove(path_to_file)
                except OSError as error:
                    lg.critical("The file was not found. %s", error)
        lg.debug("Folder clearing done !")


def main():
    """
    Brief : Test some uses of this library
    Return : None
    """
    lg.basicConfig(level=lg.DEBUG)
    converter = Converter()
    converter.clear_save_folder()
    converter.convert_from_folder()
    converter.convert_from_file("test.cnf")
    converter.save_ilp_in_file("test.lpt")
    converter.print_ilp()
    print("n = " + str(converter.nb_variables) + " m = " + str(converter.nb_clauses))


if __name__ == "__main__":
    main()
