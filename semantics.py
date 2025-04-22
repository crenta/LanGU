from errors import SemanticError
from AST_Tree import ASTNode

# checks for semantic errors such as type mismatches, variable usage before assignment, etc...
class SemanticAnalyzer:
    def __init__(self):
        # each variable maps to a dictionary with its type, assignment count, and usage count
        self.symbol_table = {} # dictionary
        self.warnings = [] # warnings

    # analyze the AST tree
    def analyze(self, node: ASTNode) -> None:
        self.visit(node) # start the from the root
        self.check_unused_variables() # check for unused variables after analysis

    # method to select the appropriate visitor based on the node type
    def visit(self, node: ASTNode):
        method = getattr(self, f"visit_{node.kind}", self.generic_visit) # get the method name or use the generic_visit
        return method(node) # return it.

    # generic visit -- to handle nodes that don't have a specific visitor method
    def generic_visit(self, node: ASTNode):
        for child in getattr(node, "children", []):
            self.visit(child) # visit each child
            

# visitor methods
    # methods for each type of AST node
    
    # visit for the root (PROGRAM) node
    def visit_Program(self, node: ASTNode):
        for child in node.children:
            self.visit(child) # visit each child node.

    # visit for assignment nodes
    def visit_Assign(self, node: ASTNode):
        var_node = node.children[0]
        var_name = var_node.value # get the variable name from the node at index 0
        expr_type = self.visit(node.children[1]) # visit the expression node to get its type
        
        # if the variable is already declared, increment its assignment count
        if var_name in self.symbol_table:
            self.symbol_table[var_name]['assignment_count'] += 1
        # else if the variable is not declared, add it to the symbol table with its type and assignment count
        else:
            self.symbol_table[var_name] = {
                'type': expr_type,
                'assignment_count': 1,
                'usage_count': 0
            }
        return expr_type # return the type of the expression

    # visit variable nodes -- check if they are used before assignment
    def visit_Var(self, node: ASTNode):
        var_name = node.value # get the variable name from the node
        
        # if the variable is not declared, we need to add a warning
        if var_name not in self.symbol_table:
            self.warnings.append(f"Warning: Variable '{var_name}' used before assignment.")
            # update the symbol table
            self.symbol_table[var_name] = {
                'type': 'int',
                'assignment_count': 0,
                'usage_count': 1
            }
        # else if the variable is declared already, simply increment the count
        else:
            self.symbol_table[var_name]['usage_count'] += 1 # increment the usage count of the variable
        return self.symbol_table[var_name]['type'] # return the type of the variable

    # visit string nodes and return the type as string
    def visit_String(self, node: ASTNode):
        return 'string'

    # visit integer nodes and return the type as int
    def visit_Int(self, node: ASTNode):
        return 'int'

    # visit binary operations -- check the types of the operands and make sure they are valid (ie: not int or div by 0)
    def visit_BinOp(self, node: ASTNode):
        left_type = self.visit(node.children[0]) # visit the left operand to get its type
        right_type = self.visit(node.children[1]) # visit the right operand to get its type
        
        # if the left or right operand is not an int
        if left_type != 'int' or right_type != 'int':
            raise SemanticError("Non-integer operands used with arithmetic operator.") # error
        # if we detect division by 0
        if node.value == '/' and node.children[1].kind == 'Int' and int(node.children[1].value) == 0:
            raise SemanticError("Division by zero detected.") # error
        
        return 'int' # return int since it's a binary operation
    
    # visit unary operations -- check the types of the operands are both bool
    def visit_LogicOp(self, node: ASTNode):
        left_type = self.visit(node.children[0])
        right_type = self.visit(node.children[1])
        
        # if either operator is not bool
        if left_type != 'bool' or right_type != 'bool':
            raise SemanticError("Logical operators require boolean operands.") # error
        return 'bool' # return bool
    
    #  NOTE: although this language does not directly use boolean operators, they are still used in and 
    # produced as a by-product of logical and relational operations / if statements.

    # visit relational operation --- check the types of the operands and ensures they are the same
    def visit_RelOp(self, node: ASTNode):
        left_type = self.visit(node.children[0])
        right_type = self.visit(node.children[1])
        
        # if the type are not the same
        if left_type != right_type:
            raise Exception("Semantic Error: Mismatched types in relational operator.") # error
        return 'bool'

    # visit method for if statements, it checks the type of the condition and ensures it is boolean.
    def visit_If(self, node: ASTNode):
        condition_type = self.visit(node.children[0]) # visit the condition to get its type.
        # if the condition of the if() is not boolean, raise an error.
        if condition_type != 'bool':
           raise SemanticError("Condition in IF statement must be boolean.")
        for stmt in node.children[1:]:
            self.visit(stmt) # visit each statement in the body of the if().

    # visit loop --- check loop bound types and make sure they are ints
    def visit_Loop(self, node: ASTNode):
        loop_var = node.children[0].value # get the loop variable name
        start_type = self.visit(node.children[1]) # get the start expression type
        end_type = self.visit(node.children[2]) # get the end expression type
        
        # if either is not an int
        if start_type != 'int' or end_type != 'int':
            raise SemanticError("Loop bounds must be integers.") # error
        
        old_table = self.symbol_table.copy() # create a copy of the current symbol table
        
        # if the loop variable is already declared, increment its count for stats
        if loop_var in self.symbol_table:
            self.symbol_table[loop_var]['assignment_count'] += 1
        # else if its is not declared, add it to the table with its type and count
        else:
            self.symbol_table[loop_var] = {
                'type': 'int',
                'assignment_count': 1,
                'usage_count': 0
            }
        # visit the loop body --- each statement
        for stmt in node.children[3:]:
            self.visit(stmt)
        # if the loop variable is not used (we check the table)
        if self.symbol_table[loop_var]['usage_count'] == 0:
            self.warnings.append(f"Warning: Loop variable '{loop_var}' declared but never used.") # warning
        self.symbol_table = old_table # restore original symbol table -- loop variable is no longer in scope

    # check for unused variables after the analysis
    def check_unused_variables(self):
        # for each variable that is assigned and never used
        for var, meta in self.symbol_table.items():
            if meta['assignment_count'] > 0 and meta['usage_count'] == 0:
                self.warnings.append(f"Warning: Variable '{var}' assigned but never used.") # warning
