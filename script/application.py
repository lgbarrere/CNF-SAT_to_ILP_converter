#! /usr/bin/env python3
# coding: utf8

"""
File : application.py
Author : lgbarrere
Brief : Create an API for the converter
"""
import os
from os import path
import datetime
import tkinter as tk
from tkinter import filedialog as fd
from enum import Enum, auto

import numpy as np
import matplotlib.pyplot as plt
import pulp

from manager.utility import Constants, path_tail, lines_from_file
from manager.sat import SatManager
from manager.converter import PulpConverter


class ColorTheme(Enum):
    """
    Brief : Enumerate the User Interface color themes
    """
    LIGHT = auto()
    DARK = auto()


class Color(Enum):
    """
    Brief : Enumerate the User Interface colors
    """
    ANTHRACITE = '#151515'
    LIGHT_GREY = '#E5E5E5'


class Histogram(Constants):
    """
    Brief : Create a histogram of the execution time for each solver
    """
    __TITLE = 'Time elapsed on\nthe problems'
    __X_LABEL = 'Solvers SAT & ILP'
    __Y_LABEL = 'Execution & conversion time'


    def __init__(self, sat_manager, converter, sat_file_list, ilp_file_list,
                 sat_solver_list, ilp_solver_list):
        super().__init__()
        self.sat_manager = sat_manager
        self.converter = converter
        self.sat_file_list = sat_file_list
        self.ilp_file_list = ilp_file_list
        self.sat_solver_list = sat_solver_list
        self.ilp_solver_list = ilp_solver_list


    def show(self):
        """
        Brief : Show the histogram in a new window
        Return : None
        """
        # Initialisations
        solver_time_dict = {}
        convert_time_dict = {}
        label_time_dict = {}
        solution_dict = {}
        converted = False # Check if at least one file has been converted

        if self.sat_file_list:
            for solver in self.sat_solver_list :
                solver_time_dict[solver] = []
                convert_time_dict[solver] = []
        if self.ilp_file_list:
            for solver in self.ilp_solver_list :
                solver_time_dict[solver] = []
                convert_time_dict[solver] = []

        # Set SAT features for the histogram
        for file in self.sat_file_list :
            # Get the name of the file without path and extension
            file = path_tail(file)
            problem_name = path.splitext(file)[0]
            if problem_name not in solution_dict:
                label_time_dict[problem_name] = {}
            for solver in self.sat_solver_list :
                sat_problem = self.sat_manager.get_problem(file)
                info = sat_problem.get_solver_info(solver)
                time = info.get_time()
                label_time_dict[problem_name][solver] = time

                # Display if the formula is SAT/UNSAT/Unsolved
                status = info.get_solution()
                label_unsolved = problem_name + '\nUnsolved'
                if problem_name not in solution_dict \
                   or solution_dict[problem_name] == label_unsolved:
                    if status == True:
                        solution_dict[problem_name] = problem_name + '\nSAT'
                    elif status == False and time != 'Timeout' \
                         and time != 'Stopped':
                        solution_dict[problem_name] = problem_name + '\nUNSAT'
                    else:
                        solution_dict[problem_name] = label_unsolved
                
                if time != 'Timeout' and time != 'Stopped':
                    time = round(time, 2)
                else:
                    time = 0
                solver_time_dict[solver].append(time)
                convert_time_dict[solver].append(0)

        # Set ILP features for the histogram
        for file in self.ilp_file_list :
            file = path_tail(file)
            problem_name = path.splitext(file)[0]
            if problem_name not in solution_dict:
                label_time_dict[problem_name] = {}
            for solver in self.ilp_solver_list :
                ilp_problem = self.converter.get_problem(file)
                info = ilp_problem.get_solver_info(solver)
                time = info.get_time()
                label_time_dict[problem_name][solver] = time

                # Display if the formula is SAT/UNSAT/Unsolved
                status = info.get_status()
                label_unsolved = problem_name + '\nUnsolved'
                if problem_name not in solution_dict \
                   or solution_dict[problem_name] == label_unsolved:
                    if status == 'Optimal':
                        solution_dict[problem_name] = problem_name + '\nSAT'
                    elif status == 'Infeasible':
                        solution_dict[problem_name] = problem_name + '\nUNSAT'
                    else:
                        solution_dict[problem_name] = label_unsolved

                if time != 'Timeout' and time != 'Stopped':
                    time = round(time, 2)
                else:
                    time = 0
                solver_time_dict[solver].append(time)
                convert_time = self.converter.get_convert_time(file)
                if convert_time is None:
                    convert_time_dict[solver].append(0)
                else:
                    convert_time_dict[solver].append(convert_time)
                    converted = True

        label_time_len = len(label_time_dict)
        nb_sat_solvers = len(self.sat_solver_list)
        nb_ilp_solvers = len(self.ilp_solver_list)
        x_list = np.arange(label_time_len) # Label locations
        width = 0.8/(nb_sat_solvers + nb_ilp_solvers)

        # Plot build
        fig, axis_x = plt.subplots()

        # Calculus of positions
        i_list = {}
        for solver in solver_time_dict :
            i_list[solver] = []

        prob_num = 0
        for problem_name in label_time_dict :
            solver_num = 0
            for solver in label_time_dict[problem_name] :
                nb_time = len(label_time_dict[problem_name])
                pos_list = x_list[prob_num] + \
                           (solver_num - ((nb_time - 1) / 2)) * width
                i_list[solver].append(pos_list)
                solver_time = label_time_dict[problem_name][solver]
                y_text = 0
                if solver_time != 'Timeout' and solver_time != 'Stopped':
                    solver_time = round(solver_time, 2)
                    y_text = solver_time
                if solver in convert_time_dict:
                    y_text += convert_time_dict[solver][prob_num]
                text = f'{solver_time}'
                plt.text(
                    i_list[solver][prob_num],
                    y_text,
                    text, ha = 'center'
                    )
                solver_num += 1
            prob_num += 1


        ## Make bars
        if converted:
            # Turn into single lists to make sure the conversion time
            # has one color only in the legend
            pos_list = []
            convert_time_list = []
            for solver in convert_time_dict:
                for item in i_list[solver]:
                    pos_list.append(item)
                for item in convert_time_dict[solver]:
                    convert_time_list.append(item)
            # Conversion time bars
            axis_x.bar(
                pos_list, convert_time_list,
                width, label='Conversion time'
                )

        # Execution time bars
        for solver in solver_time_dict :
            if solver in i_list :
                axis_x.bar(
                    i_list[solver], solver_time_dict[solver],
                    width, label=solver, bottom=convert_time_dict[solver]
                    )

        # Add title, axis' texts, custom x-axis tick labels and a legend
        axis_x.set_title(
            self.__TITLE, fontsize=20, fontweight='bold',
            color='darkred'
            )
        axis_x.set_xlabel(
            self.__X_LABEL, fontsize=14, fontweight='bold',
            color='lightseagreen'
            )
        axis_x.set_ylabel(
            self.__Y_LABEL, fontsize=14, fontweight='bold',
            color='lightseagreen'
            )
        axis_x.set_xticks(x_list)
        axis_x.set_xticklabels(solution_dict.values())
        plt.legend(loc='lower left', bbox_to_anchor=(0.8, 1))

        plt.subplots_adjust(top=0.8)
        fig.tight_layout()
        plt.show()


class Application(Constants):
    """
    Brief : Create the UI that uses the converter
    """
    __FONT_THEME = 'Arial'

    def __init__(self):
        super().__init__()
        # SAT manager
        self.sat_manager = SatManager()
        # Converter
        self.converter = PulpConverter()
        self.sat_file_tuple = ()
        self.ilp_file_tuple = ()
        self.sat_folder = None
        self.ilp_folder = None
        self.nb_dimacs = 0
        self.nb_ilp = 0
        # Histogram
        self.histogram = None
        # Color theme
        self.color_theme = ColorTheme.DARK
        self.bg_color = Color.ANTHRACITE.value
        self.invert_bg_color = Color.LIGHT_GREY.value
        self.fg_color = Color.LIGHT_GREY.value
        self.invert_fg_color = Color.ANTHRACITE.value
        # Window
        self.widget_ref = {}
        window = tk.Tk()
        self.widget_ref['window'] = window
        #self.window.iconbitmap('logo.ico')
        window.title('SAT-ILP converter')
        window.geometry('1000x600')
        window.minsize(1000, 600)
        window.config(bg=self.bg_color)
        # Locate solver (from extra window)
        self.locate_solver = None
        self.select_window = None
        self.locate_var = tk.StringVar()
        self.locate_var.set(pulp.listSolvers()[0])
        # Configurations
        self.radiobutton_var = tk.IntVar()
        self.radiobutton_var.set(1) # Set to dark theme
        self.load_config()
        self.sat_checkbox_var = []
        self.ilp_checkbox_var = []
        # Frames
        header_frame = tk.Frame(
            window, bg=self.bg_color, width=580, height=180
            )
        self.widget_ref['header_frame'] = header_frame
        # Components
        self.create_widgets()
        self.switch_theme()


    def create_widgets(self):
        """
        Brief : Create the UI widgets
        Return : None
        """
        self.create_menu()
        self.header_component()
        self.main_component()
        self.solver_component()
        self.control_panel()
        self.dimacs_component()
        self.separator()
        self.ilp_component()
        self.result_component()


    def create_menu(self):
        """
        Brief : Create the UI menu
        Return : None
        """
        # Menu
        menu_bar = tk.Menu(self.widget_ref['window'])
        self.widget_ref['menu_bar'] = menu_bar
        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label='Select DIMACS file', command=self.get_dimacs_files)
        file_menu.add_command(label='Select DIMACS folder', command=self.get_dimacs_folder)
        file_menu.add_command(label='Select ILP file', command=self.get_ilp_files)
        file_menu.add_command(label='Select ILP folder', command=self.get_ilp_folder)
        file_menu.add_separator()
        file_menu.add_command(label='Locate ILP solver', command=self.ask_new_solver)
        file_menu.add_separator()
        file_menu.add_command(
            label='Clear ILP folder',
            command=self.converter.clear_all_save_folder
            )
        file_menu.add_command(
            label='Save configuration',
            command=self.save_config
            )
        file_menu.add_separator()
        file_menu.add_command(
            label='Exit', command=self.widget_ref['window'].destroy
            )
        menu_bar.add_cascade(label='File', menu=file_menu)
        # Theme menu
        theme_menu = tk.Menu(menu_bar, tearoff=0)
        theme_menu.add_radiobutton(
            label='Light theme', command=self.switch_theme,
            variable=self.radiobutton_var, value=0
            )
        theme_menu.add_radiobutton(
            label='Dark theme', command=self.switch_theme,
            variable=self.radiobutton_var, value=1
            )
        menu_bar.add_cascade(label='Theme', menu=theme_menu)
        self.widget_ref['window'].config(menu=menu_bar)


    def header_component(self):
        """
        Brief : Create the header components containing the head labels
        Return : None
        """
        # Title
        label_title = tk.Label(
            self.widget_ref['header_frame'], text='Converter',
            font=(self.__FONT_THEME, 28), bg=self.bg_color,
            fg=self.fg_color
            )
        self.widget_ref['label_title'] = label_title
        # Display
        self.widget_ref['header_frame'].pack()
        label_title.pack(pady=20)


    def main_component(self):
        """
        Brief : Create the main component (frame)
        Return : None
        """
        main_frame = tk.Frame(self.widget_ref['window'], bg=self.bg_color)
        self.widget_ref['main_frame'] = main_frame
        # Display
        main_frame.pack()


    def solver_component(self):
        """
        Brief : Create the solver component (frame)
        Return : None
        """
        # Container
        solver_frame = tk.Frame(
            self.widget_ref['main_frame'], relief='solid',
            bg=self.bg_color,
            highlightbackground=self.fg_color,
            highlightcolor=self.fg_color, highlightthickness=5
            )
        self.widget_ref['solver_frame'] = solver_frame
        # Display
        solver_frame.pack(side='left', fill='y', padx=20, ipadx=20)


    def control_time(self):
        if self.time_checkbox_var.get() == 0 :
            self.widget_ref['spinbox_time'].config(state='disable')
        else :
            self.widget_ref['spinbox_time'].config(state='normal')


    def control_panel(self):
        """
        Brief : Create a panel to control solving options
        Return : None
        """
        # Container
        control_frame = tk.Frame(
            self.widget_ref['solver_frame'], relief='solid',
            bg=self.bg_color
            )
        self.widget_ref['control_frame'] = control_frame
        # Time limit
        self.time_checkbox_var = tk.IntVar()
        check_time = tk.Checkbutton(
            control_frame, font=(self.__FONT_THEME, 14),
            text='Time limit', bg=self.bg_color,
            fg=self.fg_color, bd=0, highlightthickness=0,
            selectcolor=self.bg_color,
            activebackground=self.bg_color,
            activeforeground=self.fg_color,
            variable=self.time_checkbox_var, onvalue=1, offvalue=0,
            command=self.control_time
            )
        self.widget_ref['check_time'] = check_time
        self.spinbox_time = tk.Spinbox(
            control_frame, font=(self.__FONT_THEME, 14), justify='right',
            exportselection=0, from_=1, to=3600, increment=1, width=4,
            disabledbackground='grey', disabledforeground='black', state='disable'
            )
        self.widget_ref['spinbox_time'] = self.spinbox_time
        label_time_unit = tk.Label(
            control_frame, text='s',
            font=(self.__FONT_THEME, 14), bg=self.bg_color,
            fg=self.fg_color
            )
        self.widget_ref['label_time_unit'] = label_time_unit
        # Start solving button
        solve_button = tk.Button(
            control_frame, text='Start solving',
            font=(self.__FONT_THEME, 16),
            bg='grey', fg=self.invert_fg_color, command=self.solve_selection
            )
        self.widget_ref['solve_button'] = solve_button
        # Display
        control_frame.pack(side='bottom', fill='x', pady=40)
        check_time.pack(side='left', padx=10)
        self.spinbox_time.pack(side='left')
        label_time_unit.pack(side='left')
        solve_button.pack(side='left', expand=True, padx=20)


    def dimacs_component(self):
        """
        Brief : Create the component to interact with the DIMACS
        Return : None
        """
        # Container
        sat_frame = tk.Frame(
            self.widget_ref['solver_frame'], relief='solid',
            bg=self.bg_color,
            )
        self.widget_ref['sat_frame'] = sat_frame
        sat_header = tk.Frame(
            self.widget_ref['sat_frame'], relief='solid',
            bg=self.bg_color,
            )
        self.widget_ref['sat_header'] = sat_header
        # Select label
        label_sat = tk.Label(
            sat_frame, text='SAT solvers',
            font=(self.__FONT_THEME, 20), bg=self.bg_color,
            fg=self.fg_color
            )
        self.widget_ref['label_sat'] = label_sat
        # Tell how many file are selected
        label_sat_selected = tk.Label(
            sat_header, text='DIMACS files : 0',
            font=(self.__FONT_THEME, 16), bg=self.bg_color,
            fg=self.fg_color
            )
        self.widget_ref['label_sat_selected'] = label_sat_selected
        # Convert button
        convert_button = tk.Button(
            sat_header, text='Convert',
            font=(self.__FONT_THEME, 16), bg='grey',
            fg=self.invert_fg_color, command=self.convert_files
            )
        self.widget_ref['convert_button'] = convert_button
        # Check-boxes
        check_list = []
        i = 0
        for solver in self.sat_manager.get_solvers() :
            self.sat_checkbox_var.append(tk.IntVar())
            if i == 0 :
                self.sat_checkbox_var[i].set(1)
            button = tk.Checkbutton(
                sat_frame, font=(self.__FONT_THEME, 14),
                text=solver, bg=self.bg_color,
                fg=self.fg_color, bd=0, highlightthickness=0,
                selectcolor=self.bg_color,
                activebackground=self.bg_color,
                activeforeground=self.fg_color,
                variable=self.sat_checkbox_var[i], onvalue=1, offvalue=0,
                )
            check_list.append(button)
            self.widget_ref[solver] = button
            i += 1
        # Display
        sat_frame.pack(side='left', anchor='w', fill='y', ipadx=20)
        label_sat.pack(pady=10)
        sat_header.pack(anchor='w', fill='x')
        label_sat_selected.pack(side='left', padx=(10, 0))
        convert_button.pack(side='right', padx=(0, 20))
        for check in check_list :
            check.pack(anchor='w', padx=(10, 0))


    def separator(self):
        """
        Brief : Create a line separator between solver component's widgets
        Return : None
        """
        separator = tk.Frame(
            self.widget_ref['solver_frame'], relief='solid',
            bg=self.invert_bg_color, width=5
            )
        self.widget_ref['separator'] = separator
        separator.pack(side='left', expand=True, fill='y', pady=20)


    def ilp_component(self):
        """
        Brief : Create the left component containing the solver selection
        Return : None
        """
        # Container
        ilp_frame = tk.Frame(
            self.widget_ref['solver_frame'], relief='solid',
            bg=self.bg_color,
            )
        self.widget_ref['ilp_frame'] = ilp_frame
        # Select label
        label_solver = tk.Label(
            ilp_frame, text='ILP solvers',
            font=(self.__FONT_THEME, 20), bg=self.bg_color,
            fg=self.fg_color
            )
        self.widget_ref['label_solver'] = label_solver
        label_ilp_selected = tk.Label(
            ilp_frame, text='ILP files : 0',
            font=(self.__FONT_THEME, 16), bg=self.bg_color,
            fg=self.fg_color
            )
        self.widget_ref['label_ilp_selected'] = label_ilp_selected
        # Check-boxes
        check_list = []
        i = 0
        for solver in self.converter.get_solvers() :
            self.ilp_checkbox_var.append(tk.IntVar())
            if i == 0 :
                self.ilp_checkbox_var[i].set(1)
            button = tk.Checkbutton(
                ilp_frame, font=(self.__FONT_THEME, 14),
                text=solver, bg=self.bg_color,
                fg=self.fg_color, bd=0, highlightthickness=0,
                selectcolor=self.bg_color,
                activebackground=self.bg_color,
                activeforeground=self.fg_color,
                variable=self.ilp_checkbox_var[i], onvalue=1, offvalue=0,
                )
            check_list.append(button)
            self.widget_ref[solver] = button
            i += 1
        # Display
        ilp_frame.pack(side='right', anchor='c', fill='y', ipadx=20)
        label_solver.pack(pady=10)
        label_ilp_selected.pack(anchor='w', padx=(10, 0))
        for check in check_list:
            check.pack(anchor='w', padx=(10, 0))


    def result_component(self):
        """
        Brief : Create the rigth component containing the output display
        Return : None
        """
        # Result labels
        result_frame = tk.Frame(
            self.widget_ref['main_frame'], relief='solid',
            bg=self.bg_color,
            highlightbackground=self.fg_color,
            highlightcolor=self.fg_color, highlightthickness=5
            )
        self.widget_ref['result_frame'] = result_frame
        label_result = tk.Label(
            result_frame, text='Display result',
            font=(self.__FONT_THEME, 20), bg=self.bg_color,
            fg=self.fg_color
            )
        self.widget_ref['label_result'] = label_result
        # Output display area
        output_frame = tk.Frame(
            result_frame, bg=self.invert_bg_color, width=200, height=80
            )
        self.widget_ref['output_frame'] = output_frame
        label_output = tk.Label(
            output_frame, text='',
            font=(self.__FONT_THEME, 12), bg=self.invert_bg_color,
            fg=self.invert_fg_color, wraplength=200, justify='left'
            )
        self.widget_ref['label_output'] = label_output
        label_satus = tk.Label(
            result_frame, text='Status :\nNone',
            font=(self.__FONT_THEME, 16), bg=self.bg_color,
            fg=self.fg_color
            )
        self.widget_ref['label_satus'] = label_satus
        # Detail information buttons
        histogram_button = tk.Button(
            result_frame, text='H', font=(self.__FONT_THEME, 18),
            bg='grey', fg=self.invert_fg_color, command=None
            )
        self.widget_ref['histogram_button'] = histogram_button
        # Display
        result_frame.pack(side='right', fill='y', padx=20, ipadx=20)
        label_result.pack(pady=10)
        output_frame.pack_propagate(0)
        output_frame.pack()
        label_output.pack(anchor='w')
        label_satus.pack(pady=5)
        histogram_button.pack(pady=20)


    def switch_theme(self):
        """
        Brief : Switch between UI color themes
        Return : None
        """
        var = self.radiobutton_var.get()
        if var == 0:
            self.color_theme = ColorTheme.LIGHT
            self.bg_color = Color.LIGHT_GREY.value
            self.invert_bg_color = Color.ANTHRACITE.value
            self.fg_color = Color.ANTHRACITE.value
            self.invert_fg_color = Color.LIGHT_GREY.value
        elif var == 1:
            self.color_theme = ColorTheme.DARK
            self.bg_color = Color.ANTHRACITE.value
            self.invert_bg_color = Color.LIGHT_GREY.value
            self.fg_color = Color.LIGHT_GREY.value
            self.invert_fg_color = Color.ANTHRACITE.value
        self.set_interface_colors()


    def set_interface_colors(self):
        """
        Brief : Change all the colors for each widgets
        depending to UI's color theme
        Return : None
        """
        # Main
        self.widget_ref['window'].config(bg=self.bg_color)
        # Header component
        self.widget_ref['header_frame'].config(bg=self.bg_color)
        self.widget_ref['main_frame'].config(bg=self.bg_color)
        self.widget_ref['label_title'].config(
            bg=self.bg_color, fg=self.fg_color
            )
        self.widget_ref['label_sat_selected'].config(
            bg=self.bg_color, fg=self.fg_color
            )
        # Solvers component
        self.widget_ref['solver_frame'].config(
            bg=self.bg_color,
            highlightbackground=self.fg_color,
            highlightcolor=self.fg_color
            )
        # Dimacs component
        self.widget_ref['sat_frame'].config(
            bg=self.bg_color
            )
        self.widget_ref['sat_header'].config(
            bg=self.bg_color
            )
        self.widget_ref['label_sat'].config(
            bg=self.bg_color, fg=self.fg_color
            )
        self.widget_ref['label_sat_selected'].config(
            bg=self.bg_color, fg=self.fg_color
            )
        for solver in self.sat_manager.get_solvers() :
            self.widget_ref[solver].config(
                bg=self.bg_color, fg=self.fg_color,
                selectcolor=self.bg_color,
                activebackground=self.bg_color,
                activeforeground=self.fg_color
                )
        # Separator
        self.widget_ref['separator'].config(
            bg=self.invert_bg_color
            )
        # ILP component
        self.widget_ref['ilp_frame'].config(
            bg=self.bg_color,
            highlightbackground=self.fg_color,
            highlightcolor=self.fg_color
            )
        self.widget_ref['label_solver'].config(
            bg=self.bg_color, fg=self.fg_color
            )
        self.widget_ref['label_ilp_selected'].config(
            bg=self.bg_color, fg=self.fg_color
            )
        for text in self.converter.get_solvers() :
            self.widget_ref[text].config(
                bg=self.bg_color, fg=self.fg_color,
                selectcolor=self.bg_color,
                activebackground=self.bg_color,
                activeforeground=self.fg_color
                )
        # Control panel
        self.widget_ref['control_frame'].config(
            bg=self.bg_color
            )
        self.widget_ref['check_time'].config(
            bg=self.bg_color,
            fg=self.fg_color,
            selectcolor=self.bg_color,
            activebackground=self.bg_color,
            activeforeground=self.fg_color
            )
        self.widget_ref['label_time_unit'].config(
            bg=self.bg_color,
            fg=self.fg_color
            )
        # Result component
        self.widget_ref['result_frame'].config(
            bg=self.bg_color,
            highlightbackground=self.fg_color,
            highlightcolor=self.fg_color
            )
        self.widget_ref['label_result'].config(
            bg=self.bg_color, fg=self.fg_color
            )
        self.widget_ref['output_frame'].config(
            bg=self.invert_bg_color
            )
        self.widget_ref['label_output'].config(
            bg=self.invert_bg_color, fg=self.invert_fg_color
            )
        self.widget_ref['label_satus'].config(
            bg=self.bg_color, fg=self.fg_color
            )


    def update_selected_files(self):
        """
        Brief : Update selection file labels
        Return : None
        """
        sat_text = 'DIMACS files : ' + str(self.nb_dimacs)
        self.widget_ref['label_sat_selected'].config(text=sat_text)
        ilp_text = 'ILP files : ' + str(self.nb_ilp)
        self.widget_ref['label_ilp_selected'].config(text=ilp_text)


    def get_dimacs_files(self):
        """
        Brief : Ask the user some DIMACS files to get
        Return : None
        """
        filetypes = (
            ('All files', '*.*'),
            ('Text files', '*.txt'),
            ('CNF text files', '*.cnf'),
            )

        # choose files
        path_to_folder = self.get_data_path()
        file_tuple = fd.askopenfilenames(
            parent=self.widget_ref['window'], title='Choose files',
            initialdir=path_to_folder, filetypes=filetypes
            )
        if file_tuple :
            self.sat_file_tuple = file_tuple
            self.sat_folder = path_tail(path.dirname(file_tuple[0]))
            if self.sat_folder == self.get_data_folder() :
                self.sat_folder = None
            for file_name in file_tuple :
                file_name = path_tail(file_name)
                self.sat_manager.load_file(file_name, self.sat_folder)
            self.nb_dimacs = len(self.sat_file_tuple)
            self.update_selected_files()
            if len(file_tuple) == 1:
                text = 'File selected :\n' + path_tail(file_tuple[0])
                self.widget_ref['label_output'].config(text=text)
            else:
                self.widget_ref['label_output'].config(text='Files selected')
            self.widget_ref['label_satus'].config(text='Status :\nNone')


    def get_dimacs_folder(self):
        """
        Brief : Ask the user to select a folder to get all DIMACS files in
        Return : None
        """
        # choose a directory
        path_to_folder = self.converter.get_data_path()
        folder = fd.askdirectory(
            parent=self.widget_ref['window'], title='Choose a folder',
            initialdir=path_to_folder
            )
        # Reset the file list because a folder is asked
        self.sat_file_tuple = ()
        if folder == '' or path_tail(folder) == self.get_data_folder() :
            self.sat_folder = None
            self.nb_dimacs = len(files_from_folder(path_to_folder))
        else :
            self.sat_folder = path_tail(folder)
            self.nb_dimacs = len(files_from_folder(folder))
        self.sat_manager.load_folder(self.sat_folder)
        self.update_selected_files()
        self.widget_ref['label_output'].config(text='Files selected')
        self.widget_ref['label_satus'].config(text='Status :\nNone')


    def get_ilp_files(self):
        """
        Brief : Ask the user some ILP files to get
        Return : None
        """
        filetypes = (
            ('All files', '*.*'),
            ('CNF text files', '*.lpt'),
            )

        # choose files
        path_to_folder = self.converter.get_save_path()
        file_tuple = fd.askopenfilenames(
            parent=self.widget_ref['window'], title='Choose files',
            initialdir=path_to_folder, filetypes=filetypes
            )
        if file_tuple :
            self.ilp_file_tuple = file_tuple
            self.ilp_folder = path_tail(path.dirname(file_tuple[0]))
            if self.ilp_folder == self.get_save_folder() :
                self.ilp_folder = None
            for file_name in file_tuple :
                self.converter.ilp_from_file(
                    path_tail(file_name), option_folder=self.ilp_folder
                    )
            self.nb_ilp = len(self.ilp_file_tuple)
            self.update_selected_files()
            if len(file_tuple) == 1:
                text = 'File selected :\n' + path_tail(file_tuple[0])
                self.widget_ref['label_output'].config(text=text)
            else:
                self.widget_ref['label_output'].config(text='Files selected')
            self.widget_ref['label_satus'].config(text='Status :\nNone')


    def get_ilp_folder(self):
        """
        Brief : Ask the user to select a folder to get all ILP files in
        Return : None
        """
        # choose a directory
        path_to_folder = self.get_save_path()
        folder = fd.askdirectory(
            parent=self.widget_ref['window'], title='Choose a folder',
            initialdir=path_to_folder
            )
        # Reset the file list because a folder is asked
        self.ilp_file_tuple = ()
        if folder == '' or path_tail(folder) == self.get_save_folder() :
            self.ilp_folder = None
            self.nb_ilp = len(files_from_folder(path_to_folder))
        else :
            self.ilp_folder = path_tail(folder)
            self.nb_ilp = len(files_from_folder(folder))
        self.converter.ilp_from_folder(self.ilp_folder)
        self.update_selected_files()
        self.widget_ref['label_output'].config(text='Files selected')
        self.widget_ref['label_satus'].config(text='Status :\nNone')


    def get_selected_solver(self):
        for solver_name in pulp.listSolvers():
            if self.locate_var.get() == solver_name:
                self.locate_solver = solver_name
        self.select_window.quit()
        self.select_window.destroy()


    def select_solver_window(self):
        # Main
        self.select_window = tk.Toplevel(self.widget_ref['window'])

        

        # Header
        #self.select_window.overrideredirect(1)
        label = tk.Label(self.select_window, text='Select the solver to locate :')

        # Solver selector
        solver_list = pulp.listSolvers()
        radiobutton_list = []

        for solver_name in solver_list:
            radiobutton_list.append(tk.Radiobutton(
                self.select_window, text=solver_name,
                variable=self.locate_var, value=solver_name
                ))

        # Validation button
        ok_button = tk.Button(
            self.select_window, text='OK', bg='light blue', fg='black',
            command=self.get_selected_solver, width=10
            )

        # Display
        label.pack(pady=10)
        for i in range(len(solver_list)):
            radiobutton_list[i].pack(anchor='w', padx=20)
        ok_button.pack(pady=10)

        # Center the toplevel window
        self.select_window.update()
        windowWidth = 300
        windowHeight = self.select_window.winfo_reqheight()
        screenWidth = self.select_window.winfo_screenwidth()
        screenHeight = self.select_window.winfo_screenheight()
        rightPos = int((screenWidth - windowWidth) / 2)
        downPos = int((screenHeight - windowHeight) / 2)
        self.select_window.geometry('{}x{}+{}+{}'.format(
            windowWidth, windowHeight, rightPos, downPos
            ))

        self.select_window.mainloop()


    def ask_new_solver(self):
        """
        Brief : Ask the user to select a solver to locate from its path
        Return : None
        """
        filetypes = (
            ('All', '*.*'),
            ('Windows app', '*.exe')
            )

        # Select a solver to locate
        self.select_solver_window()

        # Ask the path
        if self.locate_solver is not None:
            path_to_folder = self.converter.get_root_path()
            executable_path = fd.askopenfilename(
                parent=self.widget_ref['window'],
                title='Locate solver\'s executable',
                initialdir=path_to_folder, filetypes=filetypes
                )
            if executable_path == '':
                return
            check_add = self.converter.add_solver(
                self.locate_solver, executable_path
                )
            if not check_add:
                return
            text = 'Solver ' + self.locate_solver + ' loaded'
            self.widget_ref['label_output'].config(text=text)
            self.widget_ref['label_satus'].config(text='Status :\nNone')

            # Check-boxes
            if self.locate_solver not in self.widget_ref:
                ilp_var = tk.IntVar()
                self.ilp_checkbox_var.append(ilp_var)
                button = tk.Checkbutton(
                    self.widget_ref['ilp_frame'], font=(self.__FONT_THEME, 14),
                    text=self.locate_solver, bg=self.bg_color,
                    fg=self.fg_color, bd=0,
                    selectcolor=self.bg_color,
                    activebackground=self.bg_color,
                    activeforeground=self.fg_color,
                    variable=ilp_var, onvalue=1, offvalue=0,
                    )
                self.widget_ref[self.locate_solver] = button
                # Display
                button.pack(anchor='w', padx=(10, 0))


    def convert_files(self):
        """
        Brief : Convert all DIMACS files into ILP files
        Return : None
        """
        # Do nothing if no sat file is loaded
        if self.nb_dimacs == 0 :
            return
        # Otherwise, check if we loaded a folder or some files
        if not self.sat_file_tuple :
            self.converter.convert_from_folder(self.sat_folder)
            self.converter.save_all_in_folder(self.ilp_folder)
        else :
            for file in self.sat_file_tuple :
                file = path_tail(file)
                self.converter.convert_from_file(file, self.sat_folder)
                self.converter.save_ilp_in_file(file, self.sat_folder)
        # Update selected files
        self.ilp_file_tuple = self.sat_file_tuple
        self.ilp_folder = self.sat_folder
        self.nb_ilp = self.nb_dimacs
        self.update_selected_files()
        self.widget_ref['label_output'].config(text='Files converted')


    def solve_selection(self):
        """
        Brief : Solve selected ILP file with selected solvers
        Return : None
        """
        if self.nb_dimacs == 0 and self.nb_ilp == 0 :
            return
        if self.nb_ilp > 0 :
            if self.ilp_file_tuple :
                for file in self.ilp_file_tuple :
                    file_name = path_tail(file)
                    self.converter.define_problem(file_name)
            else :
                self.converter.define_problem_from_folder(self.ilp_folder)
        self.widget_ref['label_satus'].config(text='Status :\nSolving')
        self.widget_ref['window'].update()
        # Check time limit
        time_limit = None
        if self.time_checkbox_var.get() == 1 :
            time_limit = int(self.spinbox_time.get())
        solve_try = False
        sat_solver_list = []
        ilp_solver_list = []
        # Solve CNF-SAT
        i = 0
        for solver in self.sat_manager.get_solvers() :
            if self.sat_checkbox_var[i].get() == 1 :
                sat_solver_list.append(solver)
                if self.nb_dimacs > 0 :
                    if self.sat_file_tuple :
                        for file in self.sat_file_tuple :
                            file = path_tail(file)
                            text = 'Solving file ' + file + ' with ' + solver
                            self.widget_ref['label_output'].config(text=text)
                            self.widget_ref['window'].update()
                            self.sat_manager.solve(
                                file_name=file, folder=self.sat_folder,
                                solver_name=solver, time_limit=time_limit
                                )
                            self.widget_ref['label_output'].config(
                                text='Finished solving'
                                )
                            problem = self.sat_manager.get_problem(file)
                            solver_info = problem.get_solver_info(solver)
                            text = None
                            time = solver_info.get_time()
                            if time == 'Timeout':
                                text = 'Status :\n' + time
                            else:
                                solution = solver_info.get_solution()
                                if solution == True:
                                    solution = 'SAT'
                                elif solution == False:
                                    solution = 'UNSAT'
                                else:
                                    solution = 'Unsolved'
                                text = 'Status :\n' + solution
                            self.widget_ref['label_satus'].config(text=text)
                    else :
                        tmp_folder = self.sat_folder
                        if tmp_folder is None:
                            tmp_folder = self.get_data_folder()
                        text = 'Solving folder' + tmp_folder + \
                        ' with ' + solver
                        self.widget_ref['label_output'].config(text=text)
                        self.widget_ref['window'].update()
                        self.sat_manager.solve_folder(
                            folder=self.sat_folder, solver_name=solver,
                            time_limit=time_limit
                            )
                        self.widget_ref['label_output'].config(
                            text='Finished solving'
                            )
                        text = 'Status :\nSolved all'
                        self.widget_ref['label_satus'].config(text=text)
                solve_try = True
            i += 1

        # Solve ILP
        i = 0
        for solver in self.converter.get_solvers() :
            if self.ilp_checkbox_var[i].get() == 1 :
                ilp_solver_list.append(solver)
                if self.nb_ilp > 0 :
                    if self.ilp_file_tuple :
                        for file in self.ilp_file_tuple :
                            file = path_tail(file)
                            text = 'Solving file ' + file + ' with ' + solver
                            self.widget_ref['label_output'].config(text=text)
                            self.widget_ref['window'].update()
                            self.converter.solve(
                                file, solver, time_limit=time_limit
                                )
                            self.widget_ref['label_output'].config(
                                text='Finished solving'
                                )
                            problem = self.converter.get_problem(file)
                            solver_info = problem.get_solver_info(solver)
                            text = None
                            time = solver_info.get_time()
                            if time == 'Timeout':
                                text = 'Status :\n' + time
                            else:
                                status = solver_info.get_status()
                                if status == 'Optimal':
                                    status = 'SAT'
                                elif status == 'Infeasible':
                                    status = 'UNSAT'
                                else:
                                    status = 'Unsolved'
                                text = 'Status :\n' + status
                            self.widget_ref['label_satus'].config(text=text)
                    else :
                        if tmp_folder is None:
                            tmp_folder = self.get_save_folder()
                        text = 'Solving folder ' + tmp_folder + \
                               ' with ' + solver
                        self.widget_ref['label_output'].config(text=text)
                        self.widget_ref['window'].update()
                        self.converter.solve_folder(
                            self.ilp_folder, solver, time_limit=time_limit
                            )
                        self.widget_ref['label_output'].config(
                            text='Finished solving'
                            )
                        text = 'Status :\nSolved all'
                        self.widget_ref['label_satus'].config(text=text)
                    solve_try = True
            i += 1

        if solve_try :
            sat_file_list = []
            ilp_file_list = []
            if self.nb_dimacs > 0 :
                if self.sat_file_tuple :
                    sat_file_list = self.sat_file_tuple
                else :
                    directory = path.dirname(path.dirname(__file__))
                    data_folder = self.get_data_path()
                    path_to_folder = path.join(directory, data_folder)
                    if self.sat_folder is not None :
                        path_to_folder = path.join(path_to_folder, self.sat_folder)
                    for file_name in files_from_folder(path_to_folder) :
                        sat_file_list.append(file_name)
            if self.nb_ilp > 0 :
                if self.ilp_file_tuple :
                    ilp_file_list = self.ilp_file_tuple
                else :
                    directory = path.dirname(path.dirname(__file__))
                    save_folder = self.get_save_path()
                    path_to_folder = path.join(directory, save_folder)
                    if self.ilp_folder is not None :
                        path_to_folder = path.join(path_to_folder, self.ilp_folder)
                    for file_name in files_from_folder(path_to_folder) :
                        ilp_file_list.append(file_name)
            # Histogram calculation
            self.histogram = Histogram(
                self.sat_manager, self.converter, sat_file_list,
                ilp_file_list, sat_solver_list, ilp_solver_list
                )
            self.widget_ref['histogram_button'].config(
                command=self.histogram.show
                )
            date = datetime.datetime.now()
            current_date = f'{date.day}-{date.month}-{date.year}'
            current_time = f'{date.hour}-{date.minute}-{date.second}'
            result_file = f'result_{current_date}_{current_time}.sol'
            self.sat_manager.save_results(result_file)
            self.converter.save_results(result_file)
        else :
            self.widget_ref['label_output'].config(
                text='No solver was selected'
                )
            text = 'Status :\nNone'
            self.widget_ref['label_satus'].config(text=text)


    def save_config(self):
        """
        Brief : Save configurations in a file (created if missing)
        Return : None
        """
        folder = self.get_root_path()
        file_name = 'loader.config'
        file_path = path.join(folder, file_name)
        with open(file_path, 'w') as file:
            theme = self.radiobutton_var.get()
            file.write('Theme :\n')
            file.write(f'  {theme}\n')
            file.write('Solvers :\n')
            for solver_name in self.converter.get_solvers() :
                solver_path = self.converter.get_solver_path(solver_name)
                if solver_path is not None:
                    file.write(f'  {solver_name} : {solver_path}\n')
            file.write('End\n')



    def load_config(self):
        """
        Brief : Load configurations from a file
        Return : None
        """
        folder = self.get_root_path()
        file_name = 'loader.config'
        file_path = path.join(folder, file_name)
        if not path.isfile(file_path):
            return
        lines = lines_from_file(file_path)
        lines.append('EOF')
        i = 0
        while lines[i] != 'EOF':
            if lines[i] == 'Theme :\n':
                i += 1
                self.radiobutton_var.set(int(lines[i].strip()))
            if lines[i] == 'Solvers :\n':
                i += 1
                while lines[i] != 'End\n':
                    solver_config = lines[i].split(' : ')
                    solver_name = solver_config[0].strip()
                    solver_path = solver_config[1].strip()
                    self.converter.add_solver(solver_name, solver_path)
                    i += 1
            i += 1


def files_from_folder(path_to_folder):
    """
    Brief : Get all files from a folder path
    Return : The files in a list
    > path_to_folder : The path to the folder to get all files
    """
    return [file for file in os.listdir(path_to_folder) \
            if os.path.isfile(os.path.join(path_to_folder, file))]


def function_todo():
    """
    Brief : Temporary void function, will be replaced by functions depending of
    which UI element the user interacted with
    Return : None
    """
    print('In developpment.')


# processes
app = Application()
app.widget_ref['window'].mainloop()
