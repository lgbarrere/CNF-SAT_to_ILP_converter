#! /usr/bin/env python3
# coding: utf8

"""
File : application.py
Author : lgbarrere
Brief : Create an API for the converter
"""
import os
from os import path
import tkinter as tk
from tkinter import filedialog as fd
from enum import Enum, auto

import numpy as np
import matplotlib.pyplot as plt

from manager.utility import Constants, path_tail
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


class ProblemData:
    """
    Brief : Define the data used by the application
    """


class Histogram(Constants):
    """
    Brief : Create a histogram of the execution time for each solver
    """
    def __init__(self, sat_manager, converter, sat_file_list, ilp_file_list,
                 sat_solver_list, ilp_solver_list):
        super().__init__()
        self.title = 'Solver execution time'
        self.x_label = 'Solver and ILP'
        self.y_label = 'Execution time'
        self.fig = None
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
        label_list = []
        solver_time_dict = {}
        label_time_dict = {}

        for solver in self.sat_solver_list :
            solver_time_dict[solver] = []

        for solver in self.ilp_solver_list :
            solver_time_dict[solver] = []

        for file in self.sat_file_list :
            file = path_tail(file)
            problem_name = path.splitext(file)[0]
            if problem_name not in label_list :
                label_list.append(problem_name)
                label_time_dict[problem_name] = {}
            for solver in self.sat_solver_list :
                info = self.sat_manager.get_problem(file).get_solver_info(solver)
                solver_time_dict[solver].append(round(info.get_time(), 2))
                label_time_dict[problem_name][solver] = info.get_time()

        for file in self.ilp_file_list :
            file = path_tail(file)
            problem_name = path.splitext(file)[0]
            if problem_name not in label_list :
                label_list.append(problem_name)
                label_time_dict[problem_name] = {}
            for solver in self.ilp_solver_list :
                info = self.converter.get_problem(file).get_solver_info(solver)
                solver_time_dict[solver].append(round(info.get_time(), 2))
                label_time_dict[problem_name][solver] = info.get_time()

        label_time_len = len(label_time_dict)
        nb_sat_solvers = len(self.sat_solver_list)
        nb_ilp_solvers = len(self.ilp_solver_list)
        x_list = np.arange(label_time_len) # Label locations
        width = 0.8/(nb_sat_solvers + nb_ilp_solvers)

        # Plot build
        self.fig, axis_x = plt.subplots()
        rect_list = []

        # Calculus of positions
        i_list = {}
        for solver in solver_time_dict :
            i_list[solver] = []

        prob_num = 0
        for problem_name in label_time_dict :
            tmp = 0
            for solver in label_time_dict[problem_name] :
                nb_time = len(label_time_dict[problem_name])
                i_list[solver].append(x_list[prob_num] + (tmp - ((nb_time - 1) / 2)) * width)
                tmp += 1
            prob_num += 1

        # Make bars
        for solver in solver_time_dict :
            nb_time = len(solver_time_dict[solver])
            if solver in i_list :
                rect = axis_x.bar(
                    i_list[solver], solver_time_dict[solver], width, label=solver
                    )
                rect_list.append(rect)

        # Add y-axis texts, title, custom x-axis tick labels and a legend
        axis_x.set_ylabel(self.y_label)
        axis_x.set_title(self.title)
        axis_x.set_xticks(x_list)
        axis_x.set_xticklabels(label_list)
        axis_x.legend()

        for rect in rect_list :
            axis_x.bar_label(rect)

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
        # Configurations
        self.radiobutton_var = tk.IntVar()
        self.radiobutton_var.set(1) # Set to dark theme
        self.sat_checkbox_var = []
        self.ilp_checkbox_var = []
        # Frames
        header_frame = tk.Frame(
            window, bg=self.bg_color, width=580, height=180
            )
        self.widget_ref['header_frame'] = header_frame
        # Components
        self.create_widgets()


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
        file_menu.add_command(
            label='Clear ILP folder',
            command=self.converter.clear_all_save_folder
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
            fg=self.fg_color, bd=0,
            selectcolor=self.bg_color,
            activebackground=self.bg_color,
            activeforeground=self.fg_color,
            variable=self.time_checkbox_var, onvalue=1, offvalue=0,
            )
        self.widget_ref['check_time'] = check_time
        self.spinbox_time = tk.Spinbox(
            control_frame, font=(self.__FONT_THEME, 14), justify='right',
            exportselection=0, from_=1, to=3600, increment=1, width=4
            )
        self.widget_ref['spinbox_time'] = self.spinbox_time
        label_time_unit = tk.Label(
            control_frame, text='ms',
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
        label_time_unit.pack(side='left', padx=(2, 0))
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
                fg=self.fg_color, bd=0,
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
                fg=self.fg_color, bd=0,
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
        solution_button = tk.Button(
            result_frame, text='S', font=(self.__FONT_THEME, 18),
            bg='grey', fg=self.invert_fg_color, command=function_todo
            )
        self.widget_ref['solution_button'] = solution_button
        # Display
        result_frame.pack(side='right', fill='y', padx=20, ipadx=20)
        label_result.pack(pady=10)
        output_frame.pack_propagate(0)
        output_frame.pack()
        label_output.pack(anchor='w')
        label_satus.pack(pady=5)
        histogram_button.pack(side='left', anchor='n', pady=20, expand=True)
        solution_button.pack(side='right', anchor='n', pady=20, expand=True)


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
        # Right component
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
                self.converter.save_ilp_in_file(file, self.ilp_folder)
        # Update selected files
        self.ilp_file_tuple = self.sat_file_tuple
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
        self.widget_ref['label_output'].config(text='Solving')
        self.widget_ref['label_satus'].config(text='Status :\nNone')
        self.widget_ref['window'].update()
        # Check time limit
        time_limit = None
        if self.time_checkbox_var.get() == 1 :
            time_limit = self.spinbox_time.get()
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
                            self.sat_manager.solve(
                                file_name=file, solver_name=solver,
                                time_limit=time_limit
                                )
                            self.widget_ref['label_output'].config(
                                text='Finished solving'
                                )
                            problem = self.sat_manager.get_problem(file)
                            solution = problem.get_solver_info(solver).get_solution()
                            text = 'Status :\n' + str(solution)
                            self.widget_ref['label_satus'].config(text=text)
                    else :
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
                            self.converter.solve(
                                file, solver, time_limit=time_limit
                                )
                            self.widget_ref['label_output'].config(
                                text='Finished solving'
                                )
                            problem = self.converter.get_problem(file)
                            status = problem.get_solver_info(solver).get_status()
                            text = 'Status :\n' + status
                            self.widget_ref['label_satus'].config(text=text)
                    else :
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
            self.converter.save_results()
        else :
            self.widget_ref['label_output'].config(
                text='No solver was selected'
                )
            text = 'Status :\nNone'
            self.widget_ref['label_satus'].config(text=text)


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
