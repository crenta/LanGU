# errors.py

# base error class
class LanGUError(Exception):
    pass

# parsing errors
class ParserError(LanGUError):
    def __init__(self, message, line=None, column=None, lexeme=None):
        error_msg = f"Syntax error"
        if line is not None:
            error_msg += f" at line {line}"
        if column is not None:
            error_msg += f", column {column}"
        if lexeme is not None:
            error_msg += f": found '{lexeme}'"
        error_msg += f": {message}"
        super().__init__(error_msg)

# semantic errors
class SemanticError(LanGUError):
    pass

# interpreter errors
class InterpreterError(LanGUError):
    pass
