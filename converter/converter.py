#! /usr/bin/env python3
# coding: utf8

# File : converter.py
# Author : lgbarrere
# Purpose : To convert a CNF-SAT formula into its ILP version



from os import path
import logging as lg


class Converter:
    def __init__(self):
        self.fileName = "" # Name of the CNF-SAT file
        self.__converted = False # Convertion applied or not
        self.constraints = "" # ILP constraints
        self.n = 0 # Number of variables
        self.m = 0 # Number of clauses
    

    
    # Brief : Transform the given DIMACS format lines into an ILP in string
    # Return : NONE
    # > lines : The lines from a DIMACS file format
    def __formula_to_constraints(self, lines):
        self.constraints = ""
        nbClauses = 1

        if lines == None:
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
                    self.n = eval(words[i])
                    self.m = eval(words[i+1])
                # Start writting the constraints
                else:
                    self.constraints += "C" + str(nbClauses) + " : "
                    i = 0
                    while True:
                        # Get each variable as int (to know if it's positive)
                        val = eval(words[i])
                        if val < 0:
                            # Respect the rule : "not(x) = 1 - x"
                            self.constraints += "(1 - x" + str(-val) + ")"
                        elif val > 0:
                            self.constraints += "x" + words[i]
                        # This condition means the line ended, break the loop
                        else:
                            self.constraints += " >= 1\n"
                            break
                        # if the line is not ended, add "+" in the constraint
                        if words[i+1] != "0":
                            self.constraints += " + "
                        i += 1
                    nbClauses += 1
        self.__converted = True



    # Brief : Open a DIMACS file with its given name to get each line
    # Return : Each line as an element of the returned list
    # > fileName : The name of the file to open
    def _read_dimacs_file(self, fileName):
        self.fileName = fileName
        directory = path.dirname(path.dirname(__file__))
        pathToFile = path.join(directory, "data", fileName)
        
        try:
            with open(pathToFile, "r") as file:
                lg.debug("Reading file "+ fileName +"...")
                lines = file.readlines()
                return lines
        except FileNotFoundError as e:
            lg.critical("The file was not found. {}".format(e))



    # Brief : Check if the conveter has already applied a convertion
    # Return : True is a convertion has been done, False otherwise
    def is_converted(self):
        if self.__converted:
            return True
        return False
    


    # Brief : Print the converted formula from CNF-SAT into ILP
    # Return : None
    def print_ILP(self):
        if self.is_converted():
            print("Constraints : \n" + self.constraints)
        else:
            lg.warning("No CNF-SAT has been converted into ILP by this converter so far.\n")



    # Brief : Convert a CNF-SAT formula into ILP from the given fileName
    # Return : None
    # > fileName : The name of the file to open
    def convert_from_file(self, fileName):
        lines = self._read_dimacs_file(fileName)
        self.__formula_to_constraints(lines)



def main():
    lg.basicConfig(level=lg.DEBUG)
    converter = Converter()
    converter.convert_from_file("test.cnf")
    converter.print_ILP()


    
if __name__ == "__main__":
    main()
    
