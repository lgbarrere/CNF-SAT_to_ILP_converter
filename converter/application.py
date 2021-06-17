import tkinter as tk

class Application:
    __ANTHRACITE = "#111111"

    
    def __init__(self):
        # window
        self.window = tk.Tk()
        self.window.title("SAT-ILP converter")
        self.window.geometry("640x480")
        self.window.minsize(640, 480)
        #self.window.iconbitmap("logo.ico")
        self.window.config(background=self.__ANTHRACITE)

        # Title label
        label_title = tk.Label(self.window, text="Converter",
                               font=("Arial", 28), bg=self.__ANTHRACITE,
                               fg="white")

        # File selected label
        label_file_selected = tk.Label(self.window, text="File loaded",
                                       font=("Arial", 16),
                                       bg=self.__ANTHRACITE, fg="white")

        # frames
        self.main_frame = tk.Frame(self.window, bg=self.__ANTHRACITE)

        # components
        self.create_widgets()

        # Display placement
        label_title.pack(side="top", pady=20)
        label_file_selected.pack(anchor="w", side="top", padx=20)
        self.main_frame.pack(expand=True, side="top")


    def create_widgets(self):
        self.create_menu()
        self.left_component()
        self.right_component()


    def create_menu(self):
        # menu
        menu_bar = tk.Menu(self.window)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New", command=function_todo)
        file_menu.add_command(label="Quit", command=self.window.destroy)
        menu_bar.add_cascade(label="File", menu=file_menu)
        self.window.config(menu=menu_bar)


    def left_component(self):
        # Container
        self.select_frame = tk.Frame(self.main_frame, bg=self.__ANTHRACITE,
                                     highlightbackground="white",
                                     highlightcolor="white",
                                     highlightthickness=5)
        # Select label
        label_select = tk.Label(self.select_frame, text="Solver check-boxes",
                               font=("Arial", 20), bg=self.__ANTHRACITE, fg="white")

        # Check-boxes
        check_list = []
        check_list.append(tk.Checkbutton(self.select_frame, text="Glucose",
                             command=function_todo))
        check_list.append(tk.Checkbutton(self.select_frame, text="CPLEX",
                             command=function_todo))
        check_list.append(tk.Checkbutton(self.select_frame, text="lp_solve",
                             command=function_todo))
        check_list.append(tk.Checkbutton(self.select_frame, text="...",
                             command=function_todo))

        # Button
        solve_button = tk.Button(self.select_frame, text="Start solving",
                                font=("Arial", 16), bg="grey", fg=self.__ANTHRACITE,
                                command=function_todo)

        self.select_frame.pack(side="left", fill="y", padx=(0, 20), ipadx=20)
        label_select.pack(side="top", pady=10)
        for check in check_list:
            check.pack(anchor="w", side="top", padx=10, pady=5)
        solve_button.pack(side="bottom", pady=20)


    def right_component(self):
        # Result label
        self.result_frame = tk.Frame(self.main_frame, bg=self.__ANTHRACITE,
                                     bd=3, relief="solid",
                                     highlightbackground="white",
                                     highlightcolor="white",
                                     highlightthickness=5)
        label_result = tk.Label(self.result_frame, text="Display result",
                               font=("Arial", 20), bg=self.__ANTHRACITE, fg="white")
        label_display = tk.Label(self.result_frame, text="Processing",
                               font=("Arial", 12), bg=self.__ANTHRACITE, fg="white")
        label_satisfied = tk.Label(self.result_frame, text="Satisfied : yes",
                               font=("Arial", 16), bg=self.__ANTHRACITE, fg="white")

        # buttons
        histogram_button = tk.Button(self.result_frame, text="H",
                                font=("Arial, 18"), bg="grey", fg=self.__ANTHRACITE,
                                command=function_todo)
        solution_button = tk.Button(self.result_frame, text="S",
                                font=("Arial, 18"), bg="grey", fg=self.__ANTHRACITE,
                                command=function_todo)

        self.result_frame.pack(side="right", fill="y", padx=(20, 0), ipadx=20)
        label_result.pack(side="top", pady=10)
        label_display.pack(side="top", pady=0)
        label_satisfied.pack(side="top", pady=5)
        histogram_button.pack(anchor="s", side="left", pady=20, expand=True)
        solution_button.pack(anchor="s", side="left", pady=20, expand=True)


def function_todo():
    print("In developpment.")


# processes
app = Application()
app.window.mainloop()

##    # choose a file
##    tk.filedialog
