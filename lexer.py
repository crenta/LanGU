import re
from enum import Enum, auto
from typing import List, Tuple, Optional
# cSpell:ignore MULT_OP


# Token types & Patterns
class TokenType(Enum):
    PROGRAM = auto()
    END_P = auto()
    IF_STMT = auto()
    END_IF = auto()
    LOOP = auto()
    END_LOOP = auto()
    PRINT = auto()
    IDENT = auto()
    STRING_LIT = auto()
    INT_LIT = auto()
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    SEMI = auto()
    COLON = auto()
    ASSIGN_OP = auto()
    ADD_OP = auto()
    SUB_OP = auto()
    MULT_OP = auto()
    DIV_OP = auto()
    MOD_OP = auto()
    EQUALS = auto()
    NOT_EQUALS = auto()
    GREATER_THAN = auto()
    LESS_THAN = auto()
    GREATER_EQ = auto()
    LESS_EQ = auto()
    LOGICAL_AND = auto()
    LOGICAL_OR = auto()
    COMMENT = auto()
    UNKNOWN = auto()

TOKEN_PATTERNS: List[Tuple[re.Pattern, TokenType]] = [
    (re.compile(r'//.*'), TokenType.COMMENT),
    (re.compile(r'\|\|'), TokenType.LOGICAL_OR),
    (re.compile(r'&&'), TokenType.LOGICAL_AND),
    (re.compile(r'=='), TokenType.EQUALS),
    (re.compile(r'!='), TokenType.NOT_EQUALS),
    (re.compile(r'>='), TokenType.GREATER_EQ),
    (re.compile(r'<='), TokenType.LESS_EQ),
    (re.compile(r'>'), TokenType.GREATER_THAN),
    (re.compile(r'<'), TokenType.LESS_THAN),
    (re.compile(r'\bprogram\b'), TokenType.PROGRAM),
    (re.compile(r'\bend_program\b'), TokenType.END_P),
    (re.compile(r'\bif\b'), TokenType.IF_STMT),
    (re.compile(r'\bend_if\b'), TokenType.END_IF),
    (re.compile(r'\bloop\b'), TokenType.LOOP),
    (re.compile(r'\bend_loop\b'), TokenType.END_LOOP),
    (re.compile(r'\bprint\b'), TokenType.PRINT),
    (re.compile(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'), TokenType.IDENT),
    (re.compile(r'"[^"\n]*"'), TokenType.STRING_LIT),
    (re.compile(r'-?\d+'), TokenType.INT_LIT),
    (re.compile(r'\+'), TokenType.ADD_OP),
    (re.compile(r'-'), TokenType.SUB_OP),
    (re.compile(r'\*'), TokenType.MULT_OP),
    (re.compile(r'/'), TokenType.DIV_OP),
    (re.compile(r'%'), TokenType.MOD_OP),
    (re.compile(r'='), TokenType.ASSIGN_OP),
    (re.compile(r'\('), TokenType.LEFT_PAREN),
    (re.compile(r'\)'), TokenType.RIGHT_PAREN),
    (re.compile(r';'), TokenType.SEMI),
    (re.compile(r':'), TokenType.COLON),
]


# each token has [type, lexeme, line number, starting index]
class Token:
    def __init__(self, token_type: TokenType, lexeme: str, line: int, start: int):
        self.token_type = token_type
        self.lexeme = lexeme # lexeme = the actual text
        self.line = line
        self.start = start

    def __str__(self) -> str:
        return f"{self.token_type.name}({self.lexeme}) at line {self.line}" # DEBUG

    def __repr__(self) -> str:
        return self.__str__() # DEBUG

# lexer to generates tokens
class Lexer:
    def __init__(self, input_string: str):
        self.input = input_string
        self.tokens: List[Token] = []
        self.tokenize()

    # initialization
    def tokenize(self) -> None:
        position = 0
        line = 1

        # while there are characters left to be processed
        while position < len(self.input):
            match: Optional[re.Match] = None # no matches yet
            start_pos = position  # store the tokens starting position

            # for each token try to match it with a pattern
            for regex, token_type in TOKEN_PATTERNS:
                match = regex.match(self.input, position)
                
                # if we find a match
                if match:
                    lexeme = match.group(0) # get the lexeme
                    line += lexeme.count("\n") # update the line number
                    # if its not a comment
                    if token_type != TokenType.COMMENT:
                        token = Token(token_type, lexeme, line, start_pos) # create a token
                        self.tokens.append(token) # add it to the list
                    position += len(lexeme) # increment the position
                    break # if we found a match break

            # if no match was found, check if the character is whitespace and if so, skip it
            if not match:
                # if the character is white-space
                if self.input[position].isspace():
                    # catch he newline
                    if self.input[position] == "\n":
                        line += 1 # increment the line number
                    position += 1 # skip the white-space
                # else, we have an unknown token
                else:
                    self.tokens.append(Token(TokenType.UNKNOWN, self.input[position], line, position))
                    position += 1 # move the position up
                    
    # generate the tokens
    def get_tokens(self) -> List[Token]:
        return self.tokens
