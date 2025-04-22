# -*- coding: utf-8 -*-
import sys
import os
import tkinter as tk
from tkinter import filedialog, scrolledtext
from AST_Tree import ASTParser, print_tree, ASTNode
from io import StringIO
from semantics import SemanticAnalyzer
from Interpreter import Interpreter
from lexer import Lexer, TokenType
from parser import Parser
# cspell:ignore _MEIPASS
# cspell:ignore MULT_OP
# cspell: ignore darkgreen
# cspell: ignore padx
# cspell: ignore pady
# cspell: ignore yscrollcommand
# cspell: ignore highlightthickness
# cspell: ignore insertbackground
# cspell: ignore takefocus
# cspell: ignore tearoff



# Helper Functions
# allows Program1 & Program2 to load when using EITHER the PyInstaller Executable or just running the .py file itself
def get_resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.abspath(".")) # get the base path of the executable or script
    return os.path.join(base_path, relative_path) # get the full path to the resource


# draggable handle to adjust input and output frames accordingly
class DraggableHandle(tk.Frame):
    # initialize the handle with the parent frame and the input/output frames
    def __init__(self, parent, input_frame, output_frame, *args, **kwargs):
        super().__init__(parent, *args, **kwargs) # call the parent constructor
        # store the input and output frame references
        self.input_frame = input_frame
        self.output_frame = output_frame
        self.configure(bg="#444", height=5, cursor="sb_v_double_arrow") # handle's appearance
        self.bind("<Button-1>", self.start_drag) # bind left mouse button click to start dragging
        self.bind("<B1-Motion>", self.drag) # bind mouse movement while dragging to adjust the frames
        # initialize variables to store the initial mouse position and frame heights
        self.initial_y = 0
        self.initial_input_height = 0
        self.initial_output_height = 0
        self.total_height = 0

    # start_drag is called when the user clicks the left mouse button on the handle
    def start_drag(self, event):
        # store the initial mouse position and frame heights
        self.initial_y = event.y_root
        self.initial_input_height = self.input_frame.winfo_height()
        self.initial_output_height = self.output_frame.winfo_height()
        self.total_height = self.initial_input_height + self.initial_output_height # calculate the total height of the input and output frames

    # drag is called when the user moves the mouse while holding down the left button
    def drag(self, event):
        delta_y = event.y_root - self.initial_y # calculate the change in mouse position
        new_input_height = self.initial_input_height + delta_y # calculate the new height of the input frame
        new_input_height = max(50, min(new_input_height, self.total_height - 50)) # ensure it stays within bounds
        new_output_height = self.total_height - new_input_height # calculate the new height of the output frame
        # set the new heights of the input and output frames
        self.input_frame.config(height=new_input_height)
        self.output_frame.config(height=new_output_height)

# Main Class
class LanGU:
    
    # for handling token colors
    # colors for dark mode
    DARK_TOKEN_COLORS = {
        TokenType.PROGRAM:     "#569CD6",
        TokenType.END_P:       "#569CD6",
        TokenType.IF_STMT:     "#569CD6",
        TokenType.END_IF:      "#569CD6",
        TokenType.LOOP:        "#569CD6",
        TokenType.END_LOOP:    "#569CD6",
        TokenType.PRINT:       "#C586C0",
        TokenType.IDENT:       "#D4D4D4",
        TokenType.STRING_LIT:  "#CE9178",
        TokenType.INT_LIT:     "#B5CEA8",
        TokenType.COMMENT:     "#6A9955",
        # operators & punctuation
        TokenType.ADD_OP:      "#B8860B",
        TokenType.SUB_OP:      "#B8860B",
        TokenType.MULT_OP:     "#B8860B",
        TokenType.DIV_OP:      "#B8860B",
        TokenType.MOD_OP:      "#B8860B",
        TokenType.ASSIGN_OP:   "#B8860B",
        TokenType.EQUALS:      "#B8860B",
        TokenType.NOT_EQUALS:  "#B8860B",
        TokenType.GREATER_THAN:"#B8860B",
        TokenType.LESS_THAN:   "#B8860B",
        TokenType.GREATER_EQ:  "#B8860B",
        TokenType.LESS_EQ:     "#B8860B",
        TokenType.LOGICAL_AND: "#B8860B",
        TokenType.LOGICAL_OR:  "#B8860B",
        TokenType.SEMI:        "#D4D4D4",
        TokenType.COLON:       "#D4D4D4",
        TokenType.LEFT_PAREN:  "#D4D4D4",
        TokenType.RIGHT_PAREN: "#D4D4D4",
        TokenType.UNKNOWN:     "#FF0000",
    }

    # colors for light mode
    LIGHT_TOKEN_COLORS = {
        TokenType.PROGRAM:    "blue",
        TokenType.END_P:      "blue",
        TokenType.IF_STMT:    "blue",
        TokenType.END_IF:     "blue",
        TokenType.LOOP:       "blue",
        TokenType.END_LOOP:   "blue",
        TokenType.PRINT:      "purple",
        TokenType.IDENT:      "black",
        TokenType.STRING_LIT: "darkgreen",
        TokenType.INT_LIT:    "#D35400",
        TokenType.COMMENT:    "gray50",
        # operators & punctuation
        TokenType.ADD_OP:     "red",
        TokenType.SUB_OP:     "red",
        TokenType.MULT_OP:    "red",
        TokenType.DIV_OP:     "red",
        TokenType.MOD_OP:     "red",
        TokenType.ASSIGN_OP:  "red",
        TokenType.EQUALS:     "red",
        TokenType.NOT_EQUALS: "red",
        TokenType.GREATER_THAN:"red",
        TokenType.LESS_THAN:  "red",
        TokenType.GREATER_EQ: "red",
        TokenType.LESS_EQ:    "red",
        TokenType.LOGICAL_AND:"red",
        TokenType.LOGICAL_OR: "red",
        TokenType.SEMI:       "black",
        TokenType.COLON:      "black",
        TokenType.LEFT_PAREN: "black",
        TokenType.RIGHT_PAREN:"black",
        TokenType.UNKNOWN:    "magenta",
    }

    
    # initialize
    def __init__(self, root):
        self.root = root
        self.root.title("LanGU") 
        self.interpreter_step_gen = None # generator for step-interpreter
        self.current_step = 1 # current step
        self.dark_mode = True # default theme is dark mode
        self.token_colors = self.DARK_TOKEN_COLORS

        # main gui container layout
        self.create_main_container() # entire gui app
        self.create_input_area() # input area for entering code
        self.create_button_frame() # button frame for holding action buttons
        self.create_output_area() # output area for displaying results and errors/warnings

        # set theme and initial state
        self.set_theme()
        self.update_line_numbers() # update line numbers in the text area
        self.setup_window() # set up window properties

    # components
    # create the main container
    def create_main_container(self):
        self.main_container = tk.Frame(self.root, bg="#2E2E2E")
        self.main_container.pack(fill=tk.BOTH, expand=True)

    # input area -- area for code entry
    def create_input_area(self):
        self.input_frame = tk.Frame(self.main_container, bg="#2E2E2E")
        self.input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.input_frame.pack_propagate(False)

        # line numbers for the input area
        self.line_numbers = tk.Text(
            self.input_frame, width=4, padx=4, takefocus=0, border=0, 
            highlightthickness=0, state="disabled"
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y) # displayed on the left

        # scroll bar on the right side
        self.text_scrollbar = tk.Scrollbar(self.input_frame, orient=tk.VERTICAL)
        self.text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y) 

        # text area for code entry
        self.text_area = tk.Text(
            self.input_frame, width=80, height=20, wrap="none",
            yscrollcommand=self.on_scroll
        )
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True) # text area fills rest of the space
        self.text_scrollbar.config(command=self.on_scrollbar_scroll) # bind the scrollbar to the text area

        # bind events to update line numbers, handle scrolling, and error highlight clearing
        self.text_area.bind("<KeyRelease>", self.update_line_numbers) # update line numbers on key release
        self.text_area.bind("<ButtonRelease-1>", self.update_line_numbers) # update line numbers on mouse click
        self.text_area.bind("<Key>", self.clear_error_highlight) # clear error highlight on key press

        # context menu for right-click actions
        self.context_menu = tk.Menu(self.text_area, tearoff=0)
        self.context_menu.add_command(label="Cut", command=lambda: self.text_area.event_generate("<<Cut>>"))
        self.context_menu.add_command(label="Copy", command=lambda: self.text_area.event_generate("<<Copy>>"))
        self.context_menu.add_command(label="Paste", command=lambda: self.text_area.event_generate("<<Paste>>"))
        self.text_area.bind("<Button-3>", self.show_context_menu) # bind right-click to show context menu

    # action button area (below the input area)
    def create_button_frame(self):
        self.button_frame = tk.Frame(self.main_container, bg="#2E2E2E")
        self.button_frame.pack(fill=tk.X, padx=10, pady=(0, 10)) # fill the frame horizontally

        # left-side buttons (theme, load, save, default program)
        left_frame = tk.Frame(self.button_frame, bg="#2E2E2E")
        left_frame.pack(side=tk.LEFT)
        self.theme_button = tk.Button(left_frame, text="Toggle Theme", command=self.toggle_theme, bg="#444", fg="white")
        self.theme_button.pack(side=tk.LEFT, padx=5)
        self.load_button = tk.Button(left_frame, text="Load", command=self.load_file, bg="#444", fg="white")
        self.load_button.pack(side=tk.LEFT, padx=5)
        self.save_button = tk.Button(left_frame, text="Save", command=self.save_file, bg="#444", fg="white")
        self.save_button.pack(side=tk.LEFT, padx=5)
        self.run_prog1_button = tk.Button(left_frame, text="Program 1", command=self.run_program1, bg="#444", fg="white")
        self.run_prog1_button.pack(side=tk.LEFT, padx=5)
        self.run_prog2_button = tk.Button(left_frame, text="Program 2", command=self.run_program2, bg="#444", fg="white")
        self.run_prog2_button.pack(side=tk.LEFT, padx=5)

        # right-side buttons (clear, step, interpret, semantics, etc...)
        right_frame = tk.Frame(self.button_frame, bg="#2E2E2E")
        right_frame.pack(side=tk.RIGHT)
        self.clear_button = tk.Button(right_frame, text="Clear", command=self.clear_code, bg="#444", fg="white")
        self.clear_button.pack(side=tk.RIGHT, padx=5)
        self.step_interpreter_button = tk.Button(right_frame, text="Step", command=self.step_interpreter, bg="#444", fg="white")
        self.step_interpreter_button.pack(side=tk.RIGHT, padx=5)
        self.interpret_button = tk.Button(right_frame, text="Interpret", command=self.interpret_code, bg="#444", fg="white")
        self.interpret_button.pack(side=tk.RIGHT, padx=5)
        self.semantic_button = tk.Button(right_frame, text="Semantics", command=self.semantic_check, bg="#444", fg="white")
        self.semantic_button.pack(side=tk.RIGHT, padx=5)
        self.ast_button = tk.Button(right_frame, text="Tree", command=self.show_ast, bg="#444", fg="white")
        self.ast_button.pack(side=tk.RIGHT, padx=5)
        self.parse_button = tk.Button(right_frame, text="Parse", command=self.parse_code, bg="#444", fg="white")
        self.parse_button.pack(side=tk.RIGHT, padx=5)
        self.tokenize_button = tk.Button(right_frame, text="Grammar", command=self.tokenize_code, bg="#444", fg="white")
        self.tokenize_button.pack(side=tk.RIGHT, padx=5)

    # output area -- displays processed output
    def create_output_area(self):
        # define the frame
        self.output_frame = tk.Frame(self.main_container, bg="#2E2E2E", height=200)
        self.output_frame.pack(fill=tk.BOTH, padx=10, pady=(0, 10))
        self.output_frame.pack_propagate(False)

        # create a draggable handle to resize between the input and output frames
        self.drag_handle = DraggableHandle(self.main_container, self.input_frame, self.output_frame) # create the handle
        self.drag_handle.pack(fill=tk.X, padx=10, before=self.output_frame) # bind the handle to the output frame

        # scrollable output area
        self.output_area = scrolledtext.ScrolledText(
            self.output_frame, width=80, height=10, bg="#1E1E1E", fg="white", insertbackground="white"
        )
        self.output_area.pack(fill=tk.BOTH, expand=True)
        
        # different output tags depending on the process
        self.output_area.tag_config("interpret_success", foreground="#00FF00", font=('TkDefaultFont', 10, 'bold'))
        self.output_area.tag_config("interpret_fail", foreground="#FF4500", font=('TkDefaultFont', 10, 'bold'))
        self.output_area.tag_config("current_step", foreground="#FF0000")
        self.output_area.tag_config("parse_error", foreground="#FF0000", font=('TkDefaultFont', 10, 'bold'))
        self.output_area.tag_config("parse_success", foreground="#00FF00", font=('TkDefaultFont', 10, 'bold'))
        self.output_area.tag_config("tree_error", foreground="#FF0000", font=('TkDefaultFont', 10, 'bold'))
        self.output_area.tag_config("semantic_error", foreground="#FF0000", font=('TkDefaultFont', 10, 'bold'))

        # bind the right-click event to the output area
        self.output_context_menu = tk.Menu(self.output_area, tearoff=0)
        self.output_context_menu.add_command(label="Clear Output", command=self.clear_output) # clear the output area
        self.output_area.bind("<Button-3>", self.show_output_context_menu) # bind right-click to show context menu
        
        self.text_area.bind("<KeyRelease>", self.highlight_syntax)
        self.text_area.bind("<ButtonRelease-1>", self.highlight_syntax)

    # setup the window
    def setup_window(self):
        self.root.geometry("800x600")
        self.root.resizable(True, True) # allow it to be resized
        
# helper functions 
    # get the source code
    def get_source_code(self):
        return self.text_area.get("1.0", tk.END).strip() # strip the white-space

    # reset the step interpreter
    def reset_interpreter_state(self):
        self.interpreter_step_gen = None
        self.current_step = 1

    # context menu for right-click events
    def show_context_menu(self, event):
        self.context_menu.tk_popup(event.x_root, event.y_root)

    # theme management
    def toggle_theme(self):
        self.dark_mode = not self.dark_mode # toggle dark mode
        self.set_theme() # update the theme
    
    # highlight syntax in the text area
    def highlight_syntax(self, event=None):
        # for each token type
        for tok_type in self.token_colors:
            self.text_area.tag_remove(tok_type.name, "1.0", tk.END) # remove the previous tag

        # for each token type
        for tok_type, color in self.token_colors.items():
            tag = tok_type.name
            self.text_area.tag_config(tag, foreground=color) # set the font and background color

        source = self.get_source_code() # get the current source code
        lexer  = Lexer(source) # lex it
        tokens = lexer.get_tokens() # get the tokens

        # build the table to map line numbers to character offsets
        lines = source.splitlines(True)
        offsets = []
        running = 0
        # for each line, add the line length to the running total and store the offset
        for ln in lines:
            offsets.append(running)
            running += len(ln)

        # tag each token for syntax highlighting
        for tok in tokens:
            base = offsets[tok.line - 1]
            col  = tok.start - base
            start_index = f"{tok.line}.{col}"
            end_index   = f"{tok.line}.{col + len(tok.lexeme)}"
            self.text_area.tag_add(tok.token_type.name, start_index, end_index)

    # configure the output area syntax tags based on the current token colors        
    def configure_output_syntax_tags(self):
        # for each token type, set the color
        for tok_type, color in self.token_colors.items():
            self.output_area.tag_config(tok_type.name, foreground=color)

    # set the theme of the GUI
    def set_theme(self):
        # dark-mode theme
        if self.dark_mode:
            theme = {
                "bg": "#2E2E2E",
                "txt_bg": "#1E1E1E",
                "txt_fg": "white",
                "btn_bg": "#444",
                "btn_fg": "white",
            }
        else:
            # light-mode theme
            theme = {
                "bg": "#F0F0F0",
                "txt_bg": "#FFFFFF",
                "txt_fg": "black",
                "btn_bg": "#ddd",
                "btn_fg": "black",
            }

        # update main window and all frames
        self.root.configure(bg=theme["bg"])
        self.main_container.configure(bg=theme["bg"])
        self.input_frame.configure(bg=theme["bg"])
        self.button_frame.configure(bg=theme["bg"])
        self.output_frame.configure(bg=theme["bg"])

        self.line_numbers.config(bg=theme["bg"], fg=theme["txt_fg"])
        self.text_area.config(bg=theme["txt_bg"], fg=theme["txt_fg"], insertbackground=theme["txt_fg"])
        self.output_area.config(bg=theme["txt_bg"], fg=theme["txt_fg"], insertbackground=theme["txt_fg"])

        self.drag_handle.configure(bg=theme["btn_bg"])
        
        # update the buttons
        buttons = [self.theme_button, self.load_button, self.save_button, self.run_prog1_button,
                   self.run_prog2_button, self.tokenize_button, self.parse_button, self.clear_button,
                   self.ast_button, self.semantic_button, self.interpret_button, self.step_interpreter_button]
        for btn in buttons:
            btn.config(bg=theme["btn_bg"], fg=theme["btn_fg"])

        # update any children of the button frame
        for child in self.button_frame.winfo_children():
            if isinstance(child, tk.Frame):
                child.configure(bg=theme["bg"])
                
        # swap syntax-highlight map
        self.token_colors = self.DARK_TOKEN_COLORS if self.dark_mode else self.LIGHT_TOKEN_COLORS

        # reprocess syntax highlights
        self.highlight_syntax()
        self.configure_output_syntax_tags()
        
        # set error highlight color based on theme
        error_bg = "#5a1a1a" if self.dark_mode else "#ffcccc"
        self.text_area.tag_config("error", background=error_bg)
                

    # update line numbers in the text area
    def update_line_numbers(self, event=None):
        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", tk.END) # clear previous line numbers
        content = self.get_source_code() # get the current code
        number_of_lines = content.count('\n') + 1 # count the number of lines
        line_numbers_str = "\n".join(str(i) for i in range(1, number_of_lines + 1)) # generate the line numbers string
        self.line_numbers.insert("1.0", line_numbers_str) # insert the line numbers into the line number text area
        self.line_numbers.yview_moveto(self.text_area.yview()[0]) # sync the line numbers with the text area
        self.line_numbers.config(state="disabled") # disallow line numbers to be edited

    # update text area and line numbers when scrolling
    def on_scroll(self, *args):
        self.text_scrollbar.set(*args) # set the scrollbar position to match the text area
        self.line_numbers.yview_moveto(args[0]) # sync the line numbers with the text area
        return True

    # update text area and line numbers when the users scrolls "physically"
    def on_scrollbar_scroll(self, *args):
        self.text_area.yview(*args) # scroll the text area to match the scrollbar position
        self.line_numbers.yview(*args) # sync the line numbers with the text area

    # clear error highlighting
    def clear_error_highlight(self, event):
        self.text_area.tag_remove("error", "1.0", tk.END) # remove previous error highlights
        self.clear_output()
        self.reset_interpreter_state()

    # highlight error line and remove previous highlight (for switching themes)
    def highlight_error_line(self, line_number):
        self.text_area.tag_remove("error", "1.0", tk.END) # clear old error highlight
        self.text_area.tag_add("error", f"{line_number}.0", f"{line_number}.end") # add new error highlight

    # show context menu
    def show_output_context_menu(self, event):
        self.output_context_menu.tk_popup(event.x_root, event.y_root) # at the position of the mouse click
    
    # clear the output area
    def clear_output(self):
        self.output_area.config(state=tk.NORMAL) # allow editing
        self.output_area.delete("1.0", tk.END) # clear it
        self.output_area.config(state=tk.DISABLED) # disable editing
        
    # clear the input area
    def clear_code(self):
        self.text_area.delete("1.0", tk.END) # clear the input area
        self.update_line_numbers() # update line numbers
        self.output_area.config(state=tk.NORMAL) # allow editing of output area
        self.output_area.delete("1.0", tk.END) # clear it as well
        self.output_area.config(state=tk.DISABLED) # disable editing
        self.reset_interpreter_state() # reset the interpreter

    # load a file into the text area
    def load_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert("1.0", content)
            self.update_line_numbers()

    # save the content of the text area to a file
    def save_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(self.get_source_code())


# core stuff
    # grammar generator -- to tokenize the text area and displays the token types in the output
    def tokenize_code(self):
        self.reset_interpreter_state()
        source_code = self.get_source_code() # get the code
        lexer = Lexer(source_code) # lex it
        tokens = lexer.get_tokens() # get tokens
        self.output_area.config(state=tk.NORMAL)
        self.output_area.delete("1.0", tk.END) # clear the output area
        
        # for each token type, set the font color and background color
        for tok_type, color in self.token_colors.items():
            self.output_area.tag_config(tok_type.name, foreground=color)

        # for each token, insert the token type into the output area
        for i, tok in enumerate(tokens):
            self.output_area.insert(tk.END, tok.token_type.name, tok.token_type.name)
            # put a space between the tokens
            if i < len(tokens) - 1:
                self.output_area.insert(tk.END, " ")
        self.output_area.config(state=tk.DISABLED)

    # prase code -- parses code from text area with success or an error message in the output area
    def parse_code(self):
        self.reset_interpreter_state()
        source_code = self.get_source_code()
        lexer = Lexer(source_code)
        tokens = lexer.get_tokens()
        parser = Parser(tokens) # create a parser instance with the tokens
        
        # try to parse the source code and display the result in the output area
        try:
            result = parser.parse()
            self.output_area.config(state=tk.NORMAL)
            self.output_area.delete("1.0", tk.END) # clear output area
            self.output_area.insert(tk.END, result, "parse_success") # insert success message
            
        # if parsing fails... we get an exceptions
        except Exception as e:
            error_message = f"Parsing Error: {e}" # store the error message
            import re # import regex module to search for line numbers in the error message
            match = re.search(r"at line (\d+)", error_message) # search for line number in the error message
            # if a line number is found in the error message
            if match:
                line_num = int(match.group(1)) # extract the line number from the match
                # if the error message we were missing a semi
                if "Expecting semicolon" in error_message and line_num > 1:
                    new_line = line_num - 1 # set the line to the previous line
                    self.highlight_error_line(new_line) # highlight the previous line
                    error_message = error_message.replace(f"at line {line_num}", f"at line {new_line}") # update the error message with line number
                # else highlight the line where the error occurred
                else:
                    self.highlight_error_line(line_num)
            self.output_area.config(state=tk.NORMAL)
            self.output_area.delete("1.0", tk.END) # clear the output area
            self.output_area.insert(tk.END, error_message, "parse_error") # insert the error message
        finally:
            self.output_area.config(state=tk.DISABLED)

    # generate an AST of the code in the text-area
    def show_ast(self):
        self.reset_interpreter_state()
        source_code = self.get_source_code() # get the code
        lexer = Lexer(source_code) # lex it
        tokens = lexer.get_tokens() # get the tokens
        parser = ASTParser(tokens, source_code) # create the AST parser instance
        original_stdout = sys.stdout # save the original so we can restore it later
        ast_output = StringIO() # create a StringIO object to capture the AST output
        sys.stdout = ast_output # redirect stdout to the object
        
        # try to parse the source code and generate the AST
        try:
            ast_tree = parser.parse()
            print_tree(ast_tree) # print the AST to the StringIO object
            ast_str = ast_output.getvalue() # get the string value
            self.output_area.config(state=tk.NORMAL)
            self.output_area.delete("1.0", tk.END) # clear the output area
            self.output_area.insert(tk.END, ast_str) # insert the AST string into the output area
        # if parsing fails we land here
        except Exception as e:
            error_message = f"Parsing Error: {e}"
            import re # import regex module to search for line numbers in the error message
            match = re.search(r"at line (\d+)", error_message) # search for line number in the error message
            if match:
                line_num = int(match.group(1)) # if a line number is found, extract it
                self.highlight_error_line(line_num) # highlight the line where the error occurred
            self.output_area.config(state=tk.NORMAL)
            self.output_area.delete("1.0", tk.END) # clear the output area
            self.output_area.insert(tk.END, error_message, "tree_error") # insert the error message
        finally:
            sys.stdout = original_stdout # restore the original stdout
            ast_output.close() # close the StringIO object
        self.output_area.config(state=tk.DISABLED) 

    # semantic analysis of code
    def semantic_check(self):
        self.reset_interpreter_state()
        source_code = self.get_source_code()
        lexer = Lexer(source_code)
        tokens = lexer.get_tokens()
        parser = ASTParser(tokens, source_code) # create AST instance with tokens and source code
        try:
            ast = parser.parse() # try to parse the source code and generate the AST
            analyzer = SemanticAnalyzer() # create a semantic analyzer instance
            analyzer.analyze(ast) # perform semantic analysis on the AST
            self.output_area.config(state=tk.NORMAL)
            self.output_area.delete("1.0", tk.END) # clear the output area
            
            # display results if successful
            self.output_area.tag_config("success_header", foreground="#00FF00", font=('TkDefaultFont', 10, 'bold'))
            self.output_area.tag_config("warning_header", foreground="#FF8C00", font=('TkDefaultFont', 10, 'bold'))
            self.output_area.tag_config("warning", foreground="#FF8C00")
            self.output_area.insert(tk.END, "Semantic Analysis Successful!\n\n", "success_header")
            self.output_area.tag_config("symbol_header", foreground="green", font=('TkDefaultFont', 10, 'bold'))
            self.output_area.insert(tk.END, "Symbol Table:\n", "symbol_header")
            max_var_len = max((len(var) for var in analyzer.symbol_table.keys()), default=0)
            
            # go through the table to display the variable names, types, assignment counts, and usage counts
            for var, meta in analyzer.symbol_table.items():
                formatted = (f"{var.ljust(max_var_len)} : type = {meta['type']:<4}  "
                             f"assignments = {meta['assignment_count']:<2}  usages = {meta['usage_count']:<2}")
                self.output_area.insert(tk.END, formatted + "\n")
                
            # if we generate any warnings, display them
            if analyzer.warnings:
                self.output_area.insert(tk.END, "\nWarnings:\n", "warning_header")
                used_before = [w for w in analyzer.warnings if "used before assignment" in w]
                assigned_never = [w for w in analyzer.warnings if "assigned but never used" in w]
                
                # display warnings
                for warning in used_before:
                    self.output_area.insert(tk.END, f"- {warning}\n", "warning")
                    
                # format the warnings
                if used_before and assigned_never:
                    self.output_area.insert(tk.END, "\n")
                    
                # display warnings
                for warning in assigned_never:
                    self.output_area.insert(tk.END, f"- {warning}\n", "warning")
                    
        # if semantic analysis fails -- we land here
        except Exception as e:
            error_message = str(e) # store the error message
            import re
            match = re.search(r"at line (\d+)", error_message) # search for line number in the error message
            if match:
                line_num = int(match.group(1)) # extract the line number from the match
                self.highlight_error_line(line_num) # highlight the line where the error occurred
            self.output_area.config(state=tk.NORMAL)
            self.output_area.delete("1.0", tk.END) # clear the output area
            self.output_area.insert(tk.END, f"Semantic Error: {error_message}", "semantic_error") # insert the error message
        finally:
            self.output_area.config(state=tk.DISABLED)

    # interpret the source code
    def interpret_code(self):
        self.reset_interpreter_state() 
        source_code = self.get_source_code()
        lexer = Lexer(source_code)
        tokens = lexer.get_tokens()
        parser = ASTParser(tokens, source_code) # create an AST instance
        try:
            ast = parser.parse() # try to parse code and generate the AST
            analyzer = SemanticAnalyzer() # create a semantic analyzer instance
            analyzer.analyze(ast) # perform semantic analysis on the AST
            interpreter = Interpreter() # create an interpreter instance
            status, output_list, variables = interpreter.interpret(ast) # interpret the AST
            self.output_area.config(state=tk.NORMAL)
            self.output_area.delete("1.0", tk.END) # clear the output area
            self.output_area.tag_config("warning_header", foreground="#FF8C00", font=('TkDefaultFont', 10, 'bold'), underline=True)
            self.output_area.tag_config("warning", foreground="#FF8C00")
            
            # if there is output from the interpretation, display it
            if status.startswith("success"):
                self.output_area.insert(tk.END, "Interpretation Successful!\n", "interpret_success")
                # if there are any warnings, display them
                if output_list:
                    self.output_area.tag_config("output_header", foreground="green", font=('TkDefaultFont', 10, 'bold'))
                    self.output_area.insert(tk.END, "\nOutput:\n", "output_header")
                    # insert each line of output
                    for line in output_list:
                        self.output_area.insert(tk.END, f"{line}\n")
            # else if the interpretation fails, display the error message
            else:
                self.output_area.insert(tk.END, f"{status}\n", "interpret_fail")
            # if there are variables, get the maximum length of variable names
            if variables:
                max_var_len = max(len(var) for var in variables)
                self.output_area.tag_config("var_states_header", foreground="green", font=('TkDefaultFont', 10, 'bold'))
                self.output_area.insert(tk.END, "\nVariable States:\n", "var_states_header") # insert the header for variable states
                # insert each variable and its value
                for var, val in variables.items():
                    self.output_area.insert(tk.END, f"{var.ljust(max_var_len)} : {val}\n")
            # if there are any warnings from semantic analysis, display them
            if analyzer.warnings:
                self.output_area.insert(tk.END, "\nWarnings:\n", "warning_header") # insert the header for warnings
                
                # filter the warnings
                used_before = [w for w in analyzer.warnings if "used before assignment" in w]
                assigned_never = [w for w in analyzer.warnings if "assigned but never used" in w]
                
                # insert each warning
                for warning in used_before:
                    self.output_area.insert(tk.END, f"- {warning}\n", "warning")
                # format the warning
                if used_before and assigned_never:
                    self.output_area.insert(tk.END, "\n")
                # insert each warning
                for warning in assigned_never:
                    self.output_area.insert(tk.END, f"- {warning}\n", "warning")
                    
        # if parsing or semantic analysis fails -- we land here
        except Exception as e:
            error_message = str(e) # store the error message
            import re
            match = re.search(r"at line (\d+)", error_message) # search for line number in the error message
            if match:
                line_num = int(match.group(1)) # if a line number is found, extract it
                self.highlight_error_line(line_num) # highlight the line where the error occurred
            self.output_area.config(state=tk.NORMAL)
            self.output_area.delete("1.0", tk.END) # clear the output area
            self.output_area.insert(tk.END, f"Interpretation Error: {error_message}", "interpret_fail") # insert the error message
        finally:
            self.output_area.config(state=tk.DISABLED)

    # step through interpretation process one step at a time
    def step_interpreter(self):
        # if the interpreter step generator is not initialized, do so
        if not self.interpreter_step_gen:
            source = self.get_source_code()
            lexer = Lexer(source)
            tokens = lexer.get_tokens()
            parser = ASTParser(tokens, source) # create an AST instance
            # try to parse the source code and generate the AST
            try:
                ast = parser.parse()
                parse_error = None # no error if we succeed
                
            # if parsing fails -- we land here, try to create an empty AST node
            except Exception as e:
                parse_error = str(e) # store the error message
                # if there are no tokens, create an empty AST node
                if not tokens:
                    ast = ASTNode('Program', 'program', [])
                # else create a new AST parser instance with the tokens and source code
                else:
                    parser = ASTParser(tokens, source)
                    stmts = [] # create an empty list for statements
                    
                    # if there are tokens, try generate the AST
                    if parser.current_token:
                        # try to match the PROGRAM token
                        try:
                            parser.match(TokenType.PROGRAM)
                            # while there are tokens and the current token is not END_P
                            while parser.current_token and parser.current_token.token_type != TokenType.END_P:
                                # try to append the statement to the list
                                try:
                                    stmts.append(parser.statement())
                                # on error, break the loop
                                except Exception:
                                    break
                        # if there is an exception in matching the PROGRAM token, pass because we already have an error message
                        except Exception:
                            pass
                    ast = ASTNode('Program', 'program', stmts) # there are valid tokens, so create an AST node with the statements
            self.interpreter_step_gen = Interpreter().interpret_step(ast) # create step-generator with the AST
            self.current_step = 1 # reset the current step counter
            self.output_area.config(state=tk.NORMAL)
            self.output_area.delete("1.0", tk.END) # clear the output area
            
            # if there is a parse error, insert the error message
            if parse_error:
                self.output_area.insert(tk.END, f"Parse Error (will resume until here): {parse_error}\n\n", "parse_error")
            self.output_area.config(state=tk.DISABLED)
        # try to get the next step from the step-generator
        try:
            next_step = next(self.interpreter_step_gen)
            self.output_area.config(state=tk.NORMAL)
            self.output_area.tag_remove("current_step", "1.0", tk.END) # remove the previous current step tag so it doesn't overlap with the new one
            self.output_area.insert("1.0", f"Step {self.current_step}: {next_step}\n", "current_step") # insert the current step into the output and push the other lines down
            self.current_step += 1 # increment the current step
            self.output_area.config(state=tk.DISABLED)
            
        # if there are no more steps -- we land here
        except StopIteration:
            self.output_area.config(state=tk.NORMAL)
            self.output_area.insert(tk.END, "Step-by-step interpretation complete.\n")
            self.output_area.config(state=tk.DISABLED)
            self.interpreter_step_gen = None # reset the step-generator
            
        # if there is a runtime error -- we land here
        except Exception as e:
            self.output_area.config(state=tk.NORMAL)
            self.output_area.insert("1.0", f"Runtime Error: {e}\n", "error")
            self.output_area.config(state=tk.DISABLED)
            self.interpreter_step_gen = None # reset the step-generator

    # -------------- Sample Programs --------------
    def run_program1(self):
        script_path = get_resource_path("program1.txt")
        with open(script_path, "r", encoding="utf-8") as file:
            content = file.read()

        # clear
        self.output_area.config(state=tk.NORMAL)
        self.output_area.delete("1.0", tk.END)
        self.output_area.config(state=tk.DISABLED)
        self.reset_interpreter_state()

        # load the program
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", content)

        # update line numbers and syntax highlight
        self.update_line_numbers()
        self.highlight_syntax()


    def run_program2(self):
        script_path = get_resource_path("program2.txt")
        with open(script_path, "r", encoding="utf-8") as file:
            content = file.read()

        self.output_area.config(state=tk.NORMAL)
        self.output_area.delete("1.0", tk.END)
        self.output_area.config(state=tk.DISABLED)
        self.reset_interpreter_state()

        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", content)
        self.update_line_numbers()
        self.highlight_syntax()


if __name__ == "__main__":
    root = tk.Tk()
    app = LanGU(root)
    root.mainloop()