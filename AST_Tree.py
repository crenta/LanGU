from typing import List, Optional
from lexer import Lexer, TokenType
from parser import Parser
# cspell: ignore MULT_OP

# AST node (kind, value, children)
class ASTNode:
    def __init__(self, kind: str, value: Optional[str] = None, children: Optional[List['ASTNode']] = None):
        self.kind: str = kind
        self.value: Optional[str] = value
        self.children: List[ASTNode] = children or []

    # check if the node is a literal (int / string) or an identifier (var)
    def __repr__(self) -> str:
        # if it has a value, return it with the kind or just return kind
        return f"{self.kind}('{self.value}')" if self.value is not None else self.kind

# AST Parser -- parse tokens from the lexer to construct the AST
class ASTParser(Parser):
    # initialize parser with tokens
    def parse(self) -> ASTNode:
        return self.program() # start from program node and return the AST

    # <program> -> program <statements> end_program
    def program(self) -> ASTNode:
        self.match(TokenType.PROGRAM) # match the 'program' keyword
        stmts = self.statements() # parse the statements in the program
        self.match(TokenType.END_P) # match the 'end_program' keyword
        return ASTNode('Program', 'program', stmts) # return the program node with its statements.
    
    # multiple statements
    # <statements> -> <statement> <statements> | <empty>
    def statements(self) -> List[ASTNode]:
        nodes: List[ASTNode] = []
        # while there are more tokens and the current token is not an END_P, END_IF, or END_LOOP
        while self.current_token and self.current_token.token_type not in (TokenType.END_P, TokenType.END_IF, TokenType.END_LOOP):
            nodes.append(self.statement()) # parse a statement and add it to the list of nodes
        return nodes # return the nodes

    # single statement
    # <statement> -> <assignment> | <if_statement> | <loop_statement> | <print_statement>
    def statement(self) -> ASTNode:
        # figure out the type of statement to parse (IF, LOOP, PRINT)
        if self.current_token.token_type == TokenType.IF_STMT:
            return self.if_statement()
        if self.current_token.token_type == TokenType.LOOP:
            return self.loop_statement()
        if self.current_token.token_type == TokenType.PRINT:
            return self.print_statement()
        # or parse an assignment statement
        return self.assignment()

    # <print_statement> -> PRINT '(' <expr> ')' SEMI
    def print_statement(self) -> ASTNode:
        self.match(TokenType.PRINT) # match the PRINT keyword
        self.match(TokenType.LEFT_PAREN) # match the LEFT_PAREN token
        expr_node = self.expr() # parse the expression inside the parentheses
        self.match(TokenType.RIGHT_PAREN) # match the RIGHT_PAREN token
        self.match(TokenType.SEMI) # match the SEMI token
        return ASTNode('Print', "print", [expr_node]) # return the print node & expression

    # <assignment> -> <var> '=' <expr> SEMI
    def assignment(self) -> ASTNode:
        var = ASTNode('Var', self.current_token.lexeme) # create a var node with the current token's lexeme
        self.match(TokenType.IDENT) # match an identifier
        self.match(TokenType.ASSIGN_OP) # match an ASSIGN_OP
        expr_node = self.expr() # parse the expression
        self.match(TokenType.SEMI) # match the SEMI
        return ASTNode('Assign', "=", [var, expr_node]) # return the assignment node with the var and expression

    # <if_statement> -> IF_STMT '(' <logic_expr> ')' <statements> END_IF
    def if_statement(self) -> ASTNode:
        # match tokens, parse expressions/statements
        self.match(TokenType.IF_STMT)
        self.match(TokenType.LEFT_PAREN)
        cond = self.logic_expr()
        self.match(TokenType.RIGHT_PAREN)
        body = self.statements()
        self.match(TokenType.END_IF)
        return ASTNode('If', "if", [cond] + body) # return the if statement node

    # <loop_statement> -> LOOP '(' <var> '=' (<INT_LIT>|<var>) ':' (<INT_LIT>|<var>) ')' <statements> END_LOOP
    def loop_statement(self) -> ASTNode:
        self.match(TokenType.LOOP) # match tokens
        self.match(TokenType.LEFT_PAREN)
        var = ASTNode('Var', self.current_token.lexeme) # create a var with current token's lexeme
        self.match(TokenType.IDENT) # match tokens
        self.match(TokenType.ASSIGN_OP)
        start = (ASTNode('Int', self.current_token.lexeme)
                 if self.current_token.token_type == TokenType.INT_LIT
                 else ASTNode('Var', self.current_token.lexeme)) # create start node with the current token's lexeme
        self.match(self.current_token.token_type) # match the token type (either INT_LIT or variable) -- RANGE 1
        self.match(TokenType.COLON) # match token
        end = (ASTNode('Int', self.current_token.lexeme)
               if self.current_token.token_type == TokenType.INT_LIT
               else ASTNode('Var', self.current_token.lexeme)) # create end node with the current token's lexeme
        self.match(self.current_token.token_type) # match the token type (either INT_LIT or variable) -- RANGE 2
        self.match(TokenType.RIGHT_PAREN) # match token
        body = self.statements() # parse the statements inside the loop
        self.match(TokenType.END_LOOP) # match token
        return ASTNode('Loop', "loop", [var, start, end] + body) # return the loop node

    # <logic_expr> -> <rel_expr> { (LOGICAL_AND | LOGICAL_OR) <rel_expr> } | ( <logic_expr> )
    def logic_expr(self) -> ASTNode:
        # if the current token is a LEFT_PAREN, match it
        if self.current_token.token_type == TokenType.LEFT_PAREN:
            self.match(TokenType.LEFT_PAREN)
            node = self.logic_expr() # parse the logic expression inside
            self.match(TokenType.RIGHT_PAREN) # match the RIGHT_PAREN token
        else:
            node = self.rel_expr() # else just parse a relational expression

        # while there are more tokens and the current token is a logical operator (ie: AND, OR)
        while self.current_token and self.current_token.token_type in (TokenType.LOGICAL_AND, TokenType.LOGICAL_OR):
            op = self.current_token.lexeme # get the current token's lexeme as the operator
            self.advance() # advance to the next token
            right = self.logic_expr() # parse the next logic expression recursively
            node = ASTNode('LogicOp', op, [node, right]) # create the node
        return node # return the node

    # <rel_expr> -> <expr> <rel_op> <expr>
    #   rel_op = (==, !=, >, <, >=, <=)
    def rel_expr(self) -> ASTNode:
        left = self.expr() # parse left
        op = self.current_token.lexeme # get the current token's lexeme as the operator
        self.rel_op() # match token
        right = self.expr() # parse right
        return ASTNode('RelOp', op, [left, right]) # create the node


    # <rel_op> -> == | != | > | < | >= | <=
    def rel_op(self) -> None:
        # check if the current token is a relational operator
        if self.current_token and self.current_token.token_type in (
            TokenType.EQUALS, TokenType.NOT_EQUALS, TokenType.GREATER_THAN,
            TokenType.LESS_THAN, TokenType.GREATER_EQ, TokenType.LESS_EQ
        ):
            self.advance() # advance to next token
        # else -- error
        else:
            self.error("Expecting relational operator")

    # <expr> -> <term> { (ADD_OP | SUB_OP) <term> }
    def expr(self) -> ASTNode:
        node = self.term() # parse term
        # while there are more tokens and the current token is an addition or subtraction operator
        while self.current_token and self.current_token.token_type in (TokenType.ADD_OP, TokenType.SUB_OP):
            op = self.current_token.lexeme # get the current token's lexeme as the operator
            self.advance() # advance
            right = self.term() # parse term
            node = ASTNode('BinOp', op, [node, right]) # create node
        return node # return the node

    # <term> -> <factor> { (MULT_OP | DIV_OP | MOD_OP) <factor> }
    def term(self) -> ASTNode:
        node = self.factor() # parse the node
        # while there are more tokens and the current token is a multiplication, division, or modulo operator
        while self.current_token and self.current_token.token_type in (TokenType.MULT_OP, TokenType.DIV_OP, TokenType.MOD_OP):
            op = self.current_token.lexeme # get the current token's lexeme as the operator
            self.advance() # advance
            right = self.factor() # parse
            node = ASTNode('BinOp', op, [node, right]) # create the node
        return node # return the node

    # <factor> -> <unary> | <var> | <INT_LIT> | <STRING_LIT> | ( <expr> )
    def factor(self) -> ASTNode:
        # parse and operate on tokens
        if self.current_token.token_type == TokenType.SUB_OP:
            self.advance() # advance
            node = self.factor() # parse
            return ASTNode('UnaryOp', '-', [node]) # return the node
        if self.current_token.token_type == TokenType.IDENT:
            node = ASTNode('Var', self.current_token.lexeme)
            self.advance()
            return node
        if self.current_token.token_type == TokenType.STRING_LIT:
            node = ASTNode('String', self.current_token.lexeme[1:-1])
            self.advance()
            return node
        if self.current_token.token_type == TokenType.INT_LIT:
            node = ASTNode('Int', self.current_token.lexeme)
            self.advance()
            return node
        if self.current_token.token_type == TokenType.LEFT_PAREN:
            self.advance()
            node = self.expr()
            self.match(TokenType.RIGHT_PAREN)
            return node
        # else -- error
        self.error("Expecting identifier, integer, unary '-', or '('") # else raise an error

# print the AST tree
def print_tree(node: ASTNode, indent: int = 10) -> None:
    def _print(node: ASTNode, prefix: str = "", is_last: bool = True) -> None:
        connector = "└── " if is_last else "├── "
        print(" " * indent + prefix + connector + repr(node))
        new_prefix = prefix + ("    " if is_last else "│   ")
        for i, child in enumerate(node.children):
            _print(child, new_prefix, i == len(node.children) - 1)
    _print(node)

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print('Usage: python ast_tree.py <source-file>')
        sys.exit(1)
    src = open(sys.argv[1]).read()    # read the source code from the file
    tokens = Lexer(src).get_tokens()  # tokenize the source code
    parser = ASTParser(tokens, src)   # create a parser instance
    # try to parse the tokens and create the AST
    try:
        tree = parser.parse()
        print_tree(tree)
    except Exception as e:
        print(e) # print errors
