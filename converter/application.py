#! /usr/bin/env python3
# coding: utf8

"""
File : application.py
Author : lgbarrere
Brief : Create a windowed User Interface for the converter
"""
import tkinter as tk
from enum import Enum, auto


class ColorTheme(Enum):
    """
    Brief : Enumerate the User Interface color themes
    """
    LIGHT = auto()
    DARK = auto()


class Application:
    """
    Brief : Create the UI that uses the converter
    """
    __ANTHRACITE = "#151515"
    __LIGHT_GREY = "#E5E5E5"
    __FONT_THEME = "Arial"
    color_theme = ColorTheme.DARK

    def __init__(self):
        # Window
        self.widget_ref = {}
        window = tk.Tk()
        self.widget_ref["window"] = window
        window.title("SAT-ILP converter")
        window.geometry("640x480")
        window.minsize(640, 480)
        #self.window.iconbitmap("logo.ico")
        # Configurations
        self.radiobutton_var = tk.IntVar()
        if self.color_theme == ColorTheme.LIGHT:
            self.bg_color = [self.__LIGHT_GREY, self.__ANTHRACITE]
            self.fg_color = [self.__ANTHRACITE, self.__LIGHT_GREY]
            self.radiobutton_var.set(0)
        elif self.color_theme == ColorTheme.DARK:
            self.bg_color = [self.__ANTHRACITE, self.__LIGHT_GREY]
            self.fg_color = [self.__LIGHT_GREY, self.__ANTHRACITE]
            self.radiobutton_var.set(1)
        window.config(bg=self.bg_color[0])
        # Solver names
        self.text_list = []
        self.text_list.append("Glucose")
        self.text_list.append("CPLEX")
        self.text_list.append("lp_solve")
        self.text_list.append("...")
        # Frames
        header_frame = tk.Frame(window, bg=self.bg_color[0])
        self.widget_ref["header_frame"] = header_frame
        main_frame = tk.Frame(window, bg=self.bg_color[0])
        self.widget_ref["main_frame"] = main_frame
        # components
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
        menu_bar = tk.Menu(self.widget_ref["window"])
        self.widget_ref["menu_bar"] = menu_bar
        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open file", command=function_todo)
        file_menu.add_command(label="Open folder", command=function_todo)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.widget_ref["window"].destroy)
        menu_bar.add_cascade(label="File", menu=file_menu)
        # Theme menu
        theme_menu = tk.Menu(menu_bar, tearoff=0)
        theme_menu.add_radiobutton(label="Light theme",
                                   command=self.switch_theme,
                                   variable=self.radiobutton_var, value=0)
        theme_menu.add_radiobutton(label="Dark theme",
                                   command=self.switch_theme,
                                   variable=self.radiobutton_var, value=1)
        menu_bar.add_cascade(label="Theme", menu=theme_menu)
        self.widget_ref["window"].config(menu=menu_bar)


    def header_component(self):
        """
        Brief : Create the header components containing the head labels
        Return : None
        """
        # Title
        label_title = tk.Label(self.widget_ref["header_frame"],
                               text="Converter",
                               font=(self.__FONT_THEME, 28),
                               bg=self.bg_color[0],
                               fg=self.fg_color[0])
        self.widget_ref["label_title"] = label_title
        # Tell which file or folder is selected
        label_selected = tk.Label(self.widget_ref["header_frame"],
                                  text="File loaded",
                                  font=(self.__FONT_THEME, 16),
                                  bg=self.bg_color[0],
                                  fg=self.fg_color[0])
        self.widget_ref["label_selected"] = label_selected
        # Display
        self.widget_ref["header_frame"].pack(expand=True, side="top", ipadx=200)
        label_title.pack(side="top", pady=20)
        label_selected.pack(side="left", anchor="n")
        self.widget_ref["main_frame"].pack(expand=True, side="top")


    def left_component(self):
        """
        Brief : Create the left component containing the solver selection
        Return : None
        """
        # Container
        select_frame = tk.Frame(self.widget_ref["main_frame"], relief="solid",
                                     bg=self.bg_color[0],
                                     highlightbackground=self.fg_color[0],
                                     highlightcolor=self.fg_color[0],
                                     highlightthickness=5)
        self.widget_ref["select_frame"] = select_frame
        # Select label
        label_select = tk.Label(select_frame,
                                     text="Solver check-boxes",
                                     font=(self.__FONT_THEME, 20),
                                     bg=self.bg_color[0],
                                     fg=self.fg_color[0])
        self.widget_ref["label_select"] = label_select
        # Check-boxes
        check_list = []

        for text in self.text_list:
            button = tk.Checkbutton(select_frame,
                                    font=(self.__FONT_THEME, 16),
                                    text=text,
                                    bg=self.bg_color[0],
                                    fg=self.fg_color[0], bd=0,
                                    selectcolor=self.bg_color[0],
                                    activebackground=self.bg_color[0],
                                    activeforeground=self.fg_color[0],
                                    command=function_todo)
            check_list.append(button)
            self.widget_ref[text] = button

        # Start solving button
        solve_button = tk.Button(select_frame, text="Start solving",
                                      font=(self.__FONT_THEME, 16),
                                      bg="grey",
                                      fg=self.fg_color[1],
                                      command=function_todo)
        self.widget_ref["solve_button"] = solve_button
        # Display
        select_frame.pack(side="left", fill="y", padx=(0, 20), ipadx=20)
        label_select.pack(side="top", pady=10)
        for check in check_list:
            check.pack(anchor="w", side="top", padx=10, pady=5)
        solve_button.pack(side="bottom", pady=20)


    def right_component(self):
        """
        Brief : Create the rigth component containing the output display
        Return : None
        """
        # Result labels
        result_frame = tk.Frame(self.widget_ref["main_frame"], relief="solid",
                                     bg=self.bg_color[0],
                                     highlightbackground=self.fg_color[0],
                                     highlightcolor=self.fg_color[0],
                                     highlightthickness=5)
        self.widget_ref["result_frame"] = result_frame
        label_result = tk.Label(result_frame, text="Display result",
                                     font=(self.__FONT_THEME, 20),
                                     bg=self.bg_color[0],
                                     fg=self.fg_color[0])
        self.widget_ref["label_result"] = label_result
        output_frame = tk.Frame(result_frame,
                                     bg=self.bg_color[1],
                                     width=200, height=60)
        self.widget_ref["output_frame"] = output_frame
        label_output = tk.Label(output_frame, text="Processing",
                                     font=(self.__FONT_THEME, 12),
                                     bg=self.bg_color[1],
                                     fg=self.fg_color[1],
                                     wraplength=200, justify="left")
        self.widget_ref["label_output"] = label_output
        label_satisfied = tk.Label(result_frame,
                                        text="Satisfied : yes",
                                        font=(self.__FONT_THEME, 16),
                                        bg=self.bg_color[0],
                                        fg=self.fg_color[0])
        self.widget_ref["label_satisfied"] = label_satisfied
        # Detail information buttons
        histogram_button = tk.Button(result_frame, text="H",
                                          font=(self.__FONT_THEME, 18),
                                          bg="grey",
                                          fg=self.fg_color[1],
                                          command=function_todo)
        self.widget_ref["histogram_button"] = histogram_button
        solution_button = tk.Button(result_frame, text="S",
                                         font=(self.__FONT_THEME, 18),
                                         bg="grey",
                                         fg=self.fg_color[1],
                                         command=function_todo)
        self.widget_ref["solution_button"] = solution_button
        # Display
        result_frame.pack(side="right", fill="y", padx=(20, 0), ipadx=20)
        label_result.pack(side="top", pady=10)
        output_frame.pack_propagate(0)
        output_frame.pack(side="top")
        label_output.pack(side="top", anchor="w")
        label_satisfied.pack(side="top", pady=5)
        histogram_button.pack(anchor="s", side="left", pady=20, expand=True)
        solution_button.pack(anchor="s", side="right", pady=20, expand=True)


    def switch_theme(self):
        """
        Brief : Switch between UI color themes
        Return : None
        """
        var = self.radiobutton_var.get()
        if var == 0:
            self.color_theme = ColorTheme.LIGHT
            self.bg_color = [self.__LIGHT_GREY, self.__ANTHRACITE]
            self.fg_color = [self.__ANTHRACITE, self.__LIGHT_GREY]
        elif var == 1:
            self.color_theme = ColorTheme.DARK
            self.bg_color = [self.__ANTHRACITE, self.__LIGHT_GREY]
            self.fg_color = [self.__LIGHT_GREY, self.__ANTHRACITE]
        self.set_interface_colors()
        self.widget_ref["window"].update()


    def set_interface_colors(self):
        """
        Brief : Change all the colors for each widgets
        depending to UI's color theme
        Return : None
        """
        #self.window
        self.widget_ref["window"].config(bg=self.bg_color[0])
        self.widget_ref["header_frame"].config(bg=self.bg_color[0])
        self.widget_ref["main_frame"].config(bg=self.bg_color[0])
        self.widget_ref["label_title"].config(bg=self.bg_color[0],
                                               fg=self.fg_color[0])
        self.widget_ref["label_selected"].config(bg=self.bg_color[0],
                                  fg=self.fg_color[0])
        self.widget_ref["select_frame"].config(bg=self.bg_color[0],
                                     highlightbackground=self.fg_color[0],
                                     highlightcolor=self.fg_color[0])
        self.widget_ref["label_select"].config(bg=self.bg_color[0],
                                     fg=self.fg_color[0])
        for text in self.text_list:
            self.widget_ref[text].config(bg=self.bg_color[0],
                                         fg=self.fg_color[0], bd=0,
                                         selectcolor=self.bg_color[0],
                                         activebackground=self.bg_color[0],
                                         activeforeground=self.fg_color[0])
        self.widget_ref["solve_button"].config(bg="grey",
                                      fg=self.fg_color[1])
        self.widget_ref["result_frame"].config(bg=self.bg_color[0],
                                     highlightbackground=self.fg_color[0],
                                     highlightcolor=self.fg_color[0])
        self.widget_ref["label_result"].config(bg=self.bg_color[0],
                                     fg=self.fg_color[0])
        self.widget_ref["output_frame"].config(bg=self.bg_color[1])
        self.widget_ref["label_output"].config(bg=self.bg_color[1],
                                     fg=self.fg_color[1])
        self.widget_ref["label_satisfied"].config(bg=self.bg_color[0],
                                        fg=self.fg_color[0])
        self.widget_ref["histogram_button"].config(bg="grey",
                                          fg=self.fg_color[1])
        self.widget_ref["solution_button"].config(bg="grey",
                                         fg=self.fg_color[1])


def function_todo():
    """
    Brief : Temporary void function, will be replaced by functions depending of
    which UI element the user interacted with
    Return : None
    """
    print("In developpment.")


# processes
app = Application()
app.widget_ref["window"].mainloop()

##    # choose a file
##    tk.filedialog
