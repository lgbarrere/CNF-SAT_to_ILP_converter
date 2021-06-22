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
from pathlib import Path
import logging as lg
from ast import literal_eval
import time

class Converter:
    """
    Brief : Allows to convert a CNF-SAT into an ILP instance
    with a given file name or CNF string
    """
    __DATA_FOLDER_NAME = "data" # Folder containing the cnf files to convert
    __SAVE_FOLDER_NAME = "saves" # Folder in which to save the converted files
    __PREFIX = "z" # Prefix of converted variables
    __OBJECTIVE = "Maximize\n  Obj: " + __PREFIX + "\n" # CNF-SAT formula

    def __init__(self):
        self.file_name = "" # Name of the CNF-SAT file
        self.__converted = False # Convertion applied or not
        self.__constraints = "" # ILP constraints
        self.__binary = "" # Specify each CNF-SAT variable as binary
        self.nb_variables = 0 # Number of variables
        self.nb_clauses = 0 # Number of clauses
        self.time = 0 # Total conversion time execution


    def _formula_to_constraints(self, lines):
        """
        Brief : Transform the given DIMACS format lines into an ILP in string
        Return : None
        > lines : The lines from a DIMACS file format
        """
        t_debut = time.time()
        
        self.__converted = False
        self.__constraints = "Subject To\n"
        self.__binary = "Binary\n"
        nb_clauses = 1

        var_match = {}

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

            # Start writting the constraints
            else:
                self.__constraints += "  C" + str(nb_clauses) + ": "
                i = 0
                val = int(words[i])
                constraint_value = 1
                while val != 0:
                    abs_val = abs(val)
                    var_match[abs_val] = self.__PREFIX + str(abs_val)
                    # Get each variable as int (to know if it's positive)
                    if val < 0:
                        # Respect the rule : not(0) = 1 and not(1) = 0
                        self.__constraints += "- " + var_match[abs_val] + " "
                        constraint_value -= 1
                    elif val > 0:
                        if i > 0:
                            self.__constraints += "+ "
                        self.__constraints += var_match[abs_val] + " "
                    i += 1
                    val = int(words[i])
                self.__constraints += ">= " + str(constraint_value) + "\n"
                nb_clauses += 1
        # Set the CNF-SAT variables as binaries
        self.__binary += "  " + self.__PREFIX + "\n"
        for i in var_match.values():
            self.__binary += "  " + i + "\n"
        self.__converted = True
        t_fin = time.time() - t_debut
        lg.debug("Conversion time : " + str(t_fin) + "s")
        self.time += t_fin


    def _read_dimacs_file(self, file_name, optionnal_dir = None):
        """
        Brief : Open a DIMACS file with its given name to get each line
        Return : Each line as an element of the returned list
        > file_name : The name of the file to open
        """
        lg.debug("Reading file %s.", file_name)
        self.file_name = file_name
        directory = path.dirname(path.dirname(__file__))
        path_to_file = path.join(directory, self.__DATA_FOLDER_NAME)

        if optionnal_dir is None:
            path_to_file = path.join(path_to_file, file_name)
        else:
            path_to_file = path.join(path_to_file, optionnal_dir, file_name)

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
            print(self.__OBJECTIVE + self.__constraints + self.__binary + "End")
        else:
            lg.warning("No CNF-SAT has been converted into ILP so far.\n")


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
            file_name = Path(self.file_name).with_suffix('.lpt')

        lg.debug("Saving in file %s.", file_name)
        directory = path.dirname(path.dirname(__file__))
        path_to_folder = path.join(directory, self.__SAVE_FOLDER_NAME)
        if optionnal_dir is not None:
            path_to_folder = path.join(path_to_folder, optionnal_dir)
        path_to_file = path.join(path_to_folder, file_name)

        # Create folder and/or file if missing, then save the ILP
        os.makedirs(path_to_folder, exist_ok=True)
        with open(path_to_file, "w") as file:
            file.write(self.__OBJECTIVE)
            file.write(self.__constraints)
            file.write(self.__binary)
            file.write("End")
        lg.debug("Saving done !")


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
            path_to_folder = path.join(path_to_folder, folder_name)
            relative_data_path = self.__DATA_FOLDER_NAME + "/" + folder_name
            lg.debug("Converting files in folder %s.", relative_data_path)
        else:
            lg.debug("Converting files in folder %s.", self.__DATA_FOLDER_NAME)

        for file_name in listdir(path_to_folder):
            self.file_name = file_name
            path_to_file = join(path_to_folder, file_name)
            if isfile(path_to_file):
                try:
                    with open(path_to_file, "r"):
                        self.convert_from_file(file_name, folder_name)
                        self.save_ilp_in_file(optionnal_dir=folder_name)
                except FileNotFoundError as error:
                    lg.critical("The file was not found. %s", error)
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
            relative_data_path = self.__DATA_FOLDER_NAME + "/" + folder_name
            lg.debug("Clearing folder %s.", relative_data_path)
        else:
            lg.debug("Clearing folder %s.", self.__DATA_FOLDER_NAME)
        if not os.path.exists(path_to_folder):
            return
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
    # verbose debug and prepare the tests
    lg.basicConfig(level=lg.DEBUG)
    test_folder_name = "dimacs"
    converter = Converter()
    converter.clear_save_folder(test_folder_name)
    converter.clear_save_folder()
    
    # test limits in example files
    t_debut = time.time()
    converter.convert_from_file("test.cnf")
    converter.save_ilp_in_file()
    converter.print_ilp()
    print("n = " + str(converter.nb_variables) + " m = " + str(converter.nb_clauses))
    converter.convert_from_folder()

    # test with important data folder
    converter.convert_from_folder(test_folder_name)
    t_fin = time.time() - t_debut
    lg.debug("Conversion execution time : " + str(converter.time) + "s")
    lg.debug("Total execution time : " + str(t_fin) + "s")

if __name__ == "__main__":
    main()
