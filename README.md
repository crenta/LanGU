# LanGU Programming Language & Interpreter

This project implements a simple interpreter for the **LanGU** programming language. The interpreter is built in Python and is divided into several modules:

- **Lexer:** Tokenizes the source code and the `Tokenizer()` is used to get print the grammar.
- **Parser & AST Tree:** Parses tokens according to the language grammar and builds an Abstract Syntax Tree (AST).
- **Semantic Analysis:** Checks the AST for semantic correctness.
- **Interpreter:** Evaluates the AST and produces the program's output, with support for both direct interpretation and step-by-step execution.


## EBNF Grammar

Below is the EBNF grammar for the LanGU programming language:
```bnf
<program>         ->    "program" <statements> "end_program"

<statements>      ->    { <statement> }
<statement>       ->    <assignment> | <if_statement> | <loop_statement> | <print_statement>

<assignment>      ->    <var> "=" <expr> ";"

<if_statement>    ->    "if" "(" <logic_expr> ")" <statements> "end_if"
<loop_statement>  ->    "loop" "(" <var> "=" (<INT_LIT> | <var>) ":" (<INT_LIT> | <var>) ")" <statements> "end_loop"
<print_statement> ->    "print" "(" <expr> ")" ";"

<logic_expr>      ->    <rel_expr> { ("&&" | "||") <rel_expr> } | "(" <logic_expr> ")"
<rel_expr>        ->    <expr> <rel_op> <expr>
<rel_op>          ->    "==" | "!=" | ">" | "<" | ">=" | "<="

<expr>            ->    <term> { ("+" | "-") <term> }
<term>            ->    <factor> { ("*" | "/" | "%") <factor> }
<factor>          ->    "-" <factor> | <var> | <INT_LIT> | <STRING_LIT> | "(" <expr> ")"
<var>             ->    <IDENT>
```



## Project Structure

- **lexer.py:** Contains token definitions and a lexical analyzer that converts source code into tokens.
- **parser.py:** Implements the grammar rules and builds the AST.
- **AST_Tree.py:** Defines the AST node structure and provides utilities for printing the AST.
- **semantics.py:** Performs semantic analysis on the AST, checking for issues such as undeclared or unused variables.
- **Interpreter.py:** Evaluates the AST to execute the program. It also supports step-by-step interpretation.
- **LanGU.py:** Provides the GUI for the interpreter.
- **program1.txt / program2.txt:** Sample programs for testing the interpreter.


## How to Run

**Requirements**
- Python

## Option 1 - Download the EXE (Windows x64)
    - Download the EXE file

## Option 2 – Using an IDE
1. **Organize Files:**  
   Save all the following files into a single folder:
   - `AST_Tree.py`
   - `Interpreter.py`
   - `LanGU.py`
   - `parser.py`
   - `program1.txt`
   - `program2.txt`
   - `semantics.py`

2. **Open the Project:**  
   Open the `LanGU.py` file in your preferred IDE (e.g., VSCode) or run it directly from the command line.

3. **Use the GUI:**  
   Once the GUI launches, you can:
   - Enter your own code manually.
   - Click the **Program 1** or **Program 2** buttons to load sample programs.
   - Use the other buttons to step through or run the interpretation process.


## Option 3 - Compiling the EXE
**Requirements**
    - Pyinstaller: Download with `<pip install pyinstaller>` in the terminal

1. **Organize Files:**  
   Save all the following files into a single folder:
   - `AST_Tree.py`
   - `Interpreter.py`
   - `LanGU.py`
   - `parser.py`
   - `program1.txt`
   - `program2.txt`
   - `semantics.py`

2. **Compile the EXE**
    Windows     --> open a terminal in the folder, run `<pyinstaller --onefile --windowed --add-data "program1.txt;." --add-data "program2.txt;." LanGU.py>`
    Linux/MacOS --> open a terminal in the folder, run `<pyinstaller --onefile --windowed --add-data "program1.txt:." --add-data "program2.txt:." LanGU.py>`
        - Note: The --windowed flag may hide the console on MacOS

3. **Run the File**
    - Navigate to the dist folder
    - Run LanGU

## License

This project is licensed under the MIT License.


## Thanks

-C
