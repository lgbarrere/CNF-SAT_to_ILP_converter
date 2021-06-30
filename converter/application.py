#! /usr/bin/env python3
# coding: utf8

"""
File : application.py
Author : lgbarrere
Brief : Create a windowed User Interface for the converter
"""
import os
from os import path
from os import listdir
import tkinter as tk
from tkinter import filedialog as fd
from enum import Enum, auto

import pulp

import converter as conv
from converter import PulpConverter


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


class Application:
    """
    Brief : Create the UI that uses the converter
    """
    __FONT_THEME = 'Arial'

    def __init__(self):
        # Converter
        self.converter = PulpConverter()
        self.file_list = []
        self.folder = None
        self.nb_dimacs = 0
        self.nb_ilp = 0
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
        window.geometry('640x480')
        window.minsize(640, 480)
        window.config(bg=self.bg_color)
        # Configurations
        self.radiobutton_var = tk.IntVar()
        self.radiobutton_var.set(1) # Set to dark theme
        self.checkbox_var = []
        # Frames
        header_frame = tk.Frame(
            window, bg=self.bg_color, width=580, height=180
            )
        self.widget_ref['header_frame'] = header_frame
        main_frame = tk.Frame(window, bg=self.bg_color)
        self.widget_ref['main_frame'] = main_frame
        # Components
        self.create_widgets()


    def create_widgets(self):
        """
        Brief : Create the UI widgets
        Return : None
        """
        self.create_menu()
        self.header_component()
        self.left_component()
        self.right_component()


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
        file_menu.add_command(label='Select file', command=self.get_files)
        file_menu.add_command(label='Select folder', command=self.get_folder)
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
        # Tell how many file are selected
        label_sat_selected = tk.Label(
            self.widget_ref['header_frame'], text='DIMACS files loaded : 0',
            font=(self.__FONT_THEME, 16), bg=self.bg_color,
            fg=self.fg_color
            )
        self.widget_ref['label_sat_selected'] = label_sat_selected
        # Convert button
        convert_button = tk.Button(
            self.widget_ref['header_frame'], text='Convert',
            font=(self.__FONT_THEME, 16), bg='grey',
            fg=self.invert_fg_color, command=self.convert_files
            )
        self.widget_ref['convert_button'] = convert_button
        # Display
        self.widget_ref['header_frame'].pack_propagate(0)
        self.widget_ref['header_frame'].pack()
        label_title.pack(side='top', pady=20)
        label_sat_selected.pack(side='top', anchor='w')
        self.widget_ref['convert_button'].pack(
            side='top', anchor='w', pady=(10,0)
            )
        self.widget_ref['main_frame'].pack(expand=True, side='top')


    def left_component(self):
        """
        Brief : Create the left component containing the solver selection
        Return : None
        """
        # Container
        select_frame = tk.Frame(
            self.widget_ref['main_frame'], relief='solid',
            bg=self.bg_color,
            highlightbackground=self.fg_color,
            highlightcolor=self.fg_color, highlightthickness=5
            )
        self.widget_ref['select_frame'] = select_frame
        # Select label
        label_solver = tk.Label(
            select_frame, text='Solver check-boxes',
            font=(self.__FONT_THEME, 20), bg=self.bg_color,
            fg=self.fg_color
            )
        self.widget_ref['label_solver'] = label_solver
        label_ilp_selected = tk.Label(
            select_frame, text='ILP files : 0',
            font=(self.__FONT_THEME, 16), bg=self.bg_color,
            fg=self.fg_color
            )
        self.widget_ref['label_ilp_selected'] = label_ilp_selected
        # Check-boxes
        check_list = []
        i = 0
        for solver in self.converter.get_solvers() :
            self.checkbox_var.append(tk.IntVar())
            if i == 0 :
                self.checkbox_var[i].set(1)
            button = tk.Checkbutton(
                select_frame, font=(self.__FONT_THEME, 14),
                text=solver, bg=self.bg_color,
                fg=self.fg_color, bd=0,
                selectcolor=self.bg_color,
                activebackground=self.bg_color,
                activeforeground=self.fg_color,
                variable=self.checkbox_var[i], onvalue=1, offvalue=0,
                )
            check_list.append(button)
            self.widget_ref[solver] = button
            i += 1

        # Start solving button
        solve_button = tk.Button(
            select_frame, text='Start solving', font=(self.__FONT_THEME, 16),
            bg='grey', fg=self.invert_fg_color, command=self.solve_selection
            )
        self.widget_ref['solve_button'] = solve_button
        # Display
        select_frame.pack(side='left', fill='y', padx=(0, 20), ipadx=20)
        label_solver.pack(side='top', pady=10)
        label_ilp_selected.pack(side='top', anchor='w', padx=(10, 0))
        for check in check_list:
            check.pack(anchor='w', side='top', padx=10, pady=5)
        solve_button.pack(side='bottom', pady=20)


    def right_component(self):
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
        output_frame = tk.Frame(
            result_frame, bg=self.invert_bg_color, width=200, height=60
            )
        self.widget_ref['output_frame'] = output_frame
        label_output = tk.Label(
            output_frame, text='',
            font=(self.__FONT_THEME, 12), bg=self.invert_bg_color,
            fg=self.invert_fg_color, wraplength=200, justify='left'
            )
        self.widget_ref['label_output'] = label_output
        label_satus = tk.Label(
            result_frame, text='Status :',
            font=(self.__FONT_THEME, 16), bg=self.bg_color,
            fg=self.fg_color
            )
        self.widget_ref['label_satus'] = label_satus
        # Detail information buttons
        histogram_button = tk.Button(
            result_frame, text='H', font=(self.__FONT_THEME, 18),
            bg='grey', fg=self.invert_fg_color, command=function_todo
            )
        self.widget_ref['histogram_button'] = histogram_button
        solution_button = tk.Button(
            result_frame, text='S', font=(self.__FONT_THEME, 18),
            bg='grey', fg=self.invert_fg_color, command=function_todo
            )
        self.widget_ref['solution_button'] = solution_button
        # Display
        result_frame.pack(side='right', fill='y', padx=(20, 0), ipadx=20)
        label_result.pack(side='top', pady=10)
        output_frame.pack_propagate(0)
        output_frame.pack(side='top')
        label_output.pack(side='top', anchor='w')
        label_satus.pack(side='top', pady=5)
        histogram_button.pack(anchor='s', side='left', pady=20, expand=True)
        solution_button.pack(anchor='s', side='right', pady=20, expand=True)


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
        # Left component
        self.widget_ref['select_frame'].config(
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
        for text in self.solver_list:
            self.widget_ref[text].config(
                bg=self.bg_color,
                fg=self.fg_color, bd=0,
                selectcolor=self.bg_color,
                activebackground=self.bg_color,
                activeforeground=self.fg_color
                )
        self.widget_ref['solve_button'].config(
            bg='grey', fg=self.invert_fg_color
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
        self.widget_ref['histogram_button'].config(
            bg='grey', fg=self.invert_fg_color
            )
        self.widget_ref['solution_button'].config(
            bg='grey', fg=self.invert_fg_color
            )


    def update_selected_files(self):
        """
        Brief : Update selection file labels
        Return : None
        """
        sat_text = 'DIMACS files loaded : ' + str(self.nb_dimacs)
        self.widget_ref['label_sat_selected'].config(text=sat_text)
        ilp_text = 'ILP files : ' + str(self.nb_ilp)
        self.widget_ref['label_ilp_selected'].config(text=ilp_text)


    def get_folder(self):
        """
        Brief : Ask the user to select a folder to get all files in
        Return : None
        """
        # choose a directory
        directory = path.dirname(path.dirname(__file__))
        path_to_folder = path.join(directory, 'data')
        folder = fd.askdirectory(
            parent=self.widget_ref['window'], title='Choose a folder',
            initialdir=path_to_folder
            )
        # Reset the file list because a folder is asked
        self.file_list = []
        if folder == '' or conv.path_tail(folder) == 'data':
            self.folder = None
            self.nb_dimacs = len(
                [file for file in os.listdir(path_to_folder) \
                 if os.path.isfile(os.path.join(path_to_folder, file))]
                )
        else :
            self.folder = conv.path_tail(folder)
            self.nb_dimacs = len(listdir(folder))
        self.update_selected_files()
        self.widget_ref['label_output'].config(text='Files selected')
        self.widget_ref['label_satus'].config(text='Status :')


    def get_files(self):
        """
        Brief : Ask the user some files to get
        Return : None
        """
        filetypes = (
            ('All files', '*.*'),
            ('Text files', '*.txt'),
            ('CNF text files', '*.cnf'),
            )

        # choose files
        directory = path.dirname(path.dirname(__file__))
        data_folder = self.converter.get_data_folder()
        path_to_folder = path.join(directory, data_folder)
        file_list = fd.askopenfilenames(
            parent=self.widget_ref['window'], title='Choose files',
            initialdir=path_to_folder, filetypes=filetypes
            )
        if file_list :
            self.file_list = file_list
            self.folder = conv.path_tail(path.dirname(self.file_list[0]))
            if self.folder == data_folder :
                self.folder = None
            self.nb_dimacs = len(self.file_list)
            self.update_selected_files()
            self.widget_ref['label_output'].config(text='Files selected')
            self.widget_ref['label_satus'].config(text='Status :')


    def convert_files(self):
        """
        Brief : Convert all DIMACS files into ILP files
        Return : None
        """
        # Do nothing if no sat file is loaded
        if self.nb_dimacs == 0 :
            return
        # Otherwise, check if we loaded a folder or some files
        if not self.file_list :
            self.converter.convert_from_folder(self.folder)
            self.converter.save_all_in_folder(self.folder)
        else :
            for file in self.file_list :
                file = conv.path_tail(file)
                self.converter.convert_from_file(file, self.folder)
                self.converter.save_ilp_in_file(file, self.folder)
        # Update selected files
        self.nb_ilp = self.nb_dimacs
        self.nb_dimacs = 0
        self.update_selected_files()
        self.widget_ref['label_output'].config(text='Files converted')


    def solve_selection(self):
        """
        Brief : Solve selected ILP file with selected solvers
        Return : None
        """
        if self.nb_ilp == 0 :
            return
        if self.file_list :
            for file in self.file_list :
                file_name = conv.path_tail(file)
                self.converter.define_problem(file_name)
        else :
            self.converter.define_problem_from_folder(self.folder)
        self.widget_ref['label_output'].config(text='Solving')
        self.widget_ref['label_satus'].config(text='Status :')
        self.widget_ref['window'].update()
        i = 0
        solve_try = False
        
        for solver in self.converter.get_solvers() :
            if self.checkbox_var[i].get() == 1 :
                if self.file_list :
                    for file in self.file_list :
                        file = conv.path_tail(file)
                        self.converter.solve(file, solver)
                        self.widget_ref['label_output'].config(
                            text='Finished solving'
                            )
                        problem = self.converter.get_problem(file)
                        status = problem.get_solver_info(solver).get_status()
                        text = 'Status : ' + status
                        self.widget_ref['label_satus'].config(text=text)
                else :
                    self.converter.solve_folder(
                        self.folder, solver
                        )
                    self.widget_ref['label_output'].config(
                        text='Finished solving'
                        )
                    text = 'Status : Solved all'
                    self.widget_ref['label_satus'].config(text=text)
                solve_try = True
            i += 1

        if solve_try :
            self.converter.save_results()
        else :
            self.widget_ref['label_output'].config(
                text='No solver was selected'
                )
            text = 'Status : None'
            self.widget_ref['label_satus'].config(text=text)


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
