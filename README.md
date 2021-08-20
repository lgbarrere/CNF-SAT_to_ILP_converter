# CNF-SAT_to_ILP_converter
Python software project that converts a given CNF-SAT formula f into ILP constraints to check if f is satisfiable or not by solving it.

This work is in progress, please wait for the future updates.

## Setup
Open a terminal and clone this projet with `git clone [URL]` or extract it from its archive.

Go to the root folder of this projet by using `cd [PathToFolder]` in the terminal.

Simply use `pip install -r requirements.txt` to get all required dependances.

## Launch
Like in the **Setup** section, it is strongly recommanded to be in the root folder of this projet by using `cd [PathToFolder]` in the terminal before starting.

Once in the root folder, use the command :

* `python script/application.py` if you are on Windows
* `python3 script/application.py` if you are on Linux or Mac

## Usage
The API should now be opened.

Before starting, it is necessary to move your DIMACS files (or a folder containing your files) in the **data/** folder of this projet and your ILP files (or a folder again) in the **saves/** folder if you have some. You can do it while in use but this is not recommanded, particularly if the API started solving loaded files.

* **Conversion**

You can open some DIMACS or ILP files (recommanded .txt or .cnf for DIMACS and .lpt for ILP files, but works with any selected file) or a folder containing DIMACS or ILP files with the "File" menu bar at the top.

A loaded file is assumed to be well formmated for now, but this could change in a future update.

Once the files are selected, the interface should show how many files are loaded.

You can convert all of the DIMACS files into ILP by clicking on the "**Convert**" button, this will save each ILP in a dedicated file in the **saves/** folder if not already done (this action will load the ILP by overwriting the previous ILP loads).

Every new loads overwrite the previous ones.

* **Adding solvers**

In the "File" menu bar, the "Locate ILP solver" option allows to choose a PuLP solver from its database and configure it from its given path, you must know where is the executable of the solver in your computer to use this option.

* **Solver selection**

You can choose which solver the program must use to solve all loaded DIMACS and ILP files by (de)selecting check-boxes in the left component.

* **Use of timers**

All the selected solvers can be interrupted while in use if a time limit is given. For this purpose you can select the "Time limit" checkbox and change the number of seconds before the current solver in use is interrupted.

If a solver reaches its time limit, "Timeout" will be displayed as a status in the Display result section. 

* **Solving and displays**

By clicking the "**Start solving**" button, you will make the program try to solve each loaded DIMACS and ILP with each respective selected solvers.

The right component of the interface will show details on what happens (If a file is selected, if each ILP is being solved, what is the solver status, ...).

Once the program finished solving, a summary will be saved in the **result/result.sol** (text file).

You can display the histogram of the execution time of each solver on each DIMACS and ILP file it ran on by clicking the "H" button. If both DIMACS and ILP have the same name (by excluding their extension) the problem is considered the same and will be merged in the histogram.

## Testing
To launch all the tests, if you are in the root folder of this projet (see the **Launch** section), use the command :

* `python script/setup.py pytest` if you are on Window
* `python3 script/setup.py pytest` if you are on Linux or Mac

All the tests should pass correctly, otherwise feel free to check out were this could come from or try to use the API anyway. It should work even if some tests doesn't pass, but you still can report any issue directly in this project.

## Miscellaneous
You can switch color themes with the dedicated **Theme** menu if you prefer the light mode to the dark one.
