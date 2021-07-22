# CNF-SAT_to_ILP_converter
Python software project that converts a given CNF-SAT formula f into ILP constraints to check if f is satisfiable or not by solving it.

This work is in progress, please wait for the future updates.

## Setup
Open a terminal and clone this projet with `git clone [URL]`.

Go to the root folder of this projet by using `cd [PathToFolder]`.

Simply use `pip install -r requirements.txt` to get all required dependances.

## Launch
Once in the root folder, use the command :

* `python converter/application.py` if you are on Windows
* `python3 converter/application.py` if you are on Linux or Mac

## Usage
The converter window should be opened.

Before starting, it is strongly recommanded to move your DIMACS files (or a folder containing your files) in the **data/** folder of this projet.

* **Conversion**

You can open some DIMACS files (.txt or .cnf) or a folder containing DIMACS files with the menu bar at the top.

Once the dimacs files are selected, the interface should show how many DIMACS files are selected.

You can convert all of them into ILP by clicking on the "**Convert**" button, this will save each ILP in a dedicated file in the **saves/** folder.

* **Solver selection**

All converted files will be loaded as ILP files, the user interface shows how many ILP files are selected as well.

You can choose which solver the program must use to solve all selected ILP by selecting or deselecting check-boxes in the left component.

* **Solving and displays**

By clicking the "**Start solving**" button, you will make the program try to solve each ILP with each selected solvers.

The right component of the interface will show details on what happens (If a file is selected, if each ILP is being solved, what is the solver status, ...).

Once the program finished solving, a summary will be saved in the **result/result.sol** (text file).

## Testing
Use `python setup.py pytest` to launch all the tests.
