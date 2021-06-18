import tkinter as tk
from enum import Enum, auto


class ColorTheme(Enum):
        DARK = auto()
        LIGHT = auto()


class Application:
    __ANTHRACITE = "#151515"
    __LIGHT = "#E5E5E5"
    __FONT_THEME = "Arial"
    color_theme = ColorTheme.DARK
    
    def __init__(self):
        # Configurations
        if self.color_theme == ColorTheme.LIGHT:
            self.main_bg_color = self.__LIGHT
            self.main_fg_color = self.__ANTHRACITE
            self.sub_bg_color = self.__ANTHRACITE
            self.sub_fg_color = self.__LIGHT
        if self.color_theme == ColorTheme.DARK:
            self.main_bg_color = self.__ANTHRACITE
            self.main_fg_color = self.__LIGHT
            self.sub_bg_color = self.__LIGHT
            self.sub_fg_color = self.__ANTHRACITE
        
        # Window
        self.window = tk.Tk()
        self.window.title("SAT-ILP converter")
        self.window.geometry("640x480")
        self.window.minsize(640, 480)
        #self.window.iconbitmap("logo.ico")
        self.window.config(bg=self.main_bg_color)

        # Title
        self.label_title = tk.Label(self.window, text="Converter",
                                    font=(self.__FONT_THEME, 28),
                                    bg=self.main_bg_color,
                                    fg=self.main_fg_color)

        # Tell which file or folder is selected
        self.label_selected = tk.Label(self.window, text="File loaded",
                                       font=(self.__FONT_THEME, 16),
                                       bg=self.main_bg_color,
                                       fg=self.main_fg_color)

        # frames
        self.main_frame = tk.Frame(self.window, bg=self.main_bg_color)

        # components
        self.create_widgets()
        self.render()


    def render(self):
        # main
        self.label_title.pack(side="top", pady=20)
        self.label_selected.pack(anchor="w", side="top", padx=20)
        self.main_frame.pack(expand=True, side="top")
        
        # left component
        self.select_frame.pack(side="left", fill="y", padx=(0, 20), ipadx=20)
        self.label_select.pack(side="top", pady=10)
        for check in self.check_list:
            check.pack(anchor="w", side="top", padx=10, pady=5)
        self.solve_button.pack(side="bottom", pady=20)

        # right component
        self.result_frame.pack(side="right", fill="y", padx=(20, 0), ipadx=20)
        self.label_result.pack(side="top", pady=10)
        self.output_frame.pack_propagate(0)
        self.output_frame.pack(side="top")
        self.label_output.pack(side="top", anchor="w")
        self.label_satisfied.pack(side="top", pady=5)
        self.histogram_button.pack(anchor="s", side="left", pady=20, expand=True)
        self.solution_button.pack(anchor="s", side="left", pady=20, expand=True)


    def create_widgets(self):
        self.create_menu()
        self.left_component()
        self.right_component()


    def create_menu(self):
        # menu
        self.menu_bar = tk.Menu(self.window)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="New", command=function_todo)
        self.file_menu.add_command(label="Quit", command=self.window.destroy)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.window.config(menu=self.menu_bar)


    def left_component(self):
        # Container
        self.select_frame = tk.Frame(self.main_frame, relief="solid",
                                     bg=self.main_bg_color,
                                     highlightbackground=self.main_fg_color,
                                     highlightcolor=self.main_fg_color,
                                     highlightthickness=5)
        # Select label
        self.label_select = tk.Label(self.select_frame,
                                     text="Solver check-boxes",
                                     font=(self.__FONT_THEME, 20),
                                     bg=self.main_bg_color,
                                     fg=self.main_fg_color)

        # Check-boxes
        self.check_list = []
        text_list = []

        text_list.append("Glucose")
        text_list.append("CPLEX")
        text_list.append("lp_solve")
        text_list.append("...")

        for text in text_list:
            self.check_list.append(tk.Checkbutton(self.select_frame,
                                              font=(self.__FONT_THEME, 16),
                                              text=text,
                                              bg=self.main_bg_color,
                                              fg=self.main_fg_color, bd=0,
                                              selectcolor=self.main_bg_color,
                                              activebackground=self.main_bg_color,
                                              activeforeground=self.main_fg_color,
                                              command=function_todo))

        # Start solving button
        self.solve_button = tk.Button(self.select_frame, text="Start solving",
                                      font=(self.__FONT_THEME, 16),
                                      bg="grey",
                                      fg=self.sub_fg_color,
                                      command=function_todo)


    def right_component(self):
        # Result labels
        self.result_frame = tk.Frame(self.main_frame, relief="solid",
                                     bg=self.main_bg_color,
                                     highlightbackground=self.main_fg_color,
                                     highlightcolor=self.main_fg_color,
                                     highlightthickness=5)
        self.label_result = tk.Label(self.result_frame, text="Display result",
                                     font=(self.__FONT_THEME, 20),
                                     bg=self.main_bg_color,
                                     fg=self.main_fg_color)
        self.output_frame = tk.Frame(self.result_frame,
                                     bg=self.sub_bg_color,
                                     width=200, height=60)
        self.label_output = tk.Label(self.output_frame, text="Processing",
                                     font=(self.__FONT_THEME, 12),
                                     bg=self.sub_bg_color,
                                     fg=self.sub_fg_color,
                                     wraplength=200, justify="left")
        self.label_satisfied = tk.Label(self.result_frame,
                                        text="Satisfied : yes",
                                        font=(self.__FONT_THEME, 16),
                                        bg=self.main_bg_color,
                                        fg=self.main_fg_color)

        # Detail buttons
        self.histogram_button = tk.Button(self.result_frame, text="H",
                                          font=(self.__FONT_THEME, 18),
                                          bg="grey",
                                          fg=self.sub_fg_color,
                                          command=function_todo)
        self.solution_button = tk.Button(self.result_frame, text="S",
                                         font=(self.__FONT_THEME, 18),
                                         bg="grey",
                                         fg=self.sub_fg_color,
                                         command=function_todo)


def function_todo():
    print("In developpment.")


# processes
app = Application()
app.window.mainloop()

##    # choose a file
##    tk.filedialog
