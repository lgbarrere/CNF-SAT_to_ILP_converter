# -*- coding: utf8 -*-

# File : converter.py
# Author : lgbarrere
# Purpose : To convert a CNF-SAT formula into its ILP version



# Brief : Transform the given DIMACS format lines into an ILP in string
# Return : The string containing the ILP version of the CNF-SAT
# > lines : The lines from a DIMACS file format
def formula_to_constraints(lines):
    constraints = ""
    n = 0
    m = 0
    nbClauses = 1
    
    for line in lines:
        words = line.split()
        # Ignore DIMACS comments
        if words[0] != "c" and words[0] != "\n":
            # Get the number of variables and clauses
            if words[0] == "p":
                i = 1
                if words[i] == "cnf":
                    i += 1
                n = eval(words[i]) # Number of variables
                m = eval(words[i+1]) # Number of clauses
            # Start writting the constraints
            else:
                constraints += "C" + str(nbClauses) + " : "
                i = 0
                while True:
                    # Get each variable as int (to know if it's positive)
                    val = eval(words[i])
                    if val < 0:
                        # Respect the rule : "not(x) = 1 - x"
                        constraints += "(1 - x" + str(-val) + ")"
                    elif val > 0:
                        constraints += "x" + words[i]
                    # This condition means the line ended, break the loop
                    else:
                        constraints += " >= 1\n"
                        break
                    # if the line is not ended, add "+" in the constraint
                    if words[i+1] != "0":
                        constraints += " + "
                    i += 1
                nbClauses += 1
    
    return constraints



# Brief : Open a DIMACS file with its given name to get each line
# Return : Each line as an element of the returned list
# > fileName : The name of the file to open
def read_dimacs_file(fileName):
    with open(fileName, "r") as file:
        lines = file.readlines()
    return lines



def main():
    lines = read_dimacs_file("dimacs/test.cnf")
    constraints = formula_to_constraints(lines)
    print("Constraints : \n" + constraints)

main()
