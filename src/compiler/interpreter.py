from typing import Any
from compiler import ast
from compiler.parser1 import parse
from compiler.tokenizer import tokenize
Value = int | bool | None
SymbolList = {
    '+': lambda x, y: x + y,
    '-': lambda x, y: x - y,
    '*': lambda x, y: x * y,
    '/': lambda x, y: x // y,
    '%': lambda x, y: x % y,
    '<': lambda x, y: x < y,
    '<=': lambda x, y: x <= y,
    '>': lambda x, y: x > y,
    '>=': lambda x, y: x >= y,
    '==': lambda x, y: x == y,
    '!=': lambda x, y: x != y,
    '+=': lambda x, y: x + y,
    '-=': lambda x, y: x - y,
    'or': lambda x, y, st: or_operation(x,y,st),
    'and': lambda x, y,st: and_operation(x,y,st),


    'unary': lambda x: not x if isinstance(x, bool) else -x,
}

def or_operation(a,b,symbol_table:ast.SymTab) -> bool:
    if interpret(a, symbol_table) == False:
        if isinstance(interpret(b, symbol_table), bool):    
            return interpret(b, symbol_table)
    else:
        return True
    
    return False

def and_operation(a,b,symbol_table:ast.SymTab)-> bool:
    if interpret(a, symbol_table) == True:
        if isinstance(interpret(b, symbol_table), bool):    
            return interpret(b, symbol_table)
    else:
        return False
    
    return False

class BreakException(Exception):
    pass

class ContinueException(Exception):
    pass

def interpret(node: ast.Expression, symbol_table: ast.SymTab = ast.SymTab(variables=SymbolList)) -> Value:
    match node:
        case ast.Break():
            raise BreakException
        case ast.Continue():
            raise ContinueException

        
        case ast.BinaryOp():
            if isinstance(node.left, ast.Identifier) and node.operation in ['=']:
                if isinstance(symbol_table.variables, dict) and node.left.name in symbol_table.variables:
                    symbol_table.variables[node.left.name] = interpret(node.right, symbol_table)
                    return None
                elif isinstance(symbol_table, ast.HierarchicalSymTab):
                    return interpret(node, symbol_table.parent)
                else:   raise Exception

            a: Any = interpret(node.left, symbol_table)
            b: Any = interpret(node.right, symbol_table)
            top_symbol_table = symbol_table

            while isinstance(top_symbol_table, ast.HierarchicalSymTab):
                top_symbol_table = top_symbol_table.parent
            if node.operation in top_symbol_table.variables:
                if node.operation in ['or','and']:
                    operation_function = top_symbol_table.variables[node.operation]
                    return operation_function(node.left, node.right, symbol_table)
                # elif node.operation in ['+=','-=']:
                #     # operation_function = top_symbol_table.variables[node.operation]
                #     # symbol_table.variables[node.left.name] = operation_function(a,b)
                #     # Ensure 'a' is the current value of the variable
                #     current_value = symbol_table.variables.get(node.left.name, 0)
                #     operation_function = top_symbol_table.variables[node.operation]
                #     # Calculate new value and update directly in the symbol table
                #     new_value = operation_function(current_value, b)
                #     symbol_table.variables[node.left.name] = new_value
                #     return None
                else:
                    operation_function = top_symbol_table.variables[node.operation]
                    return operation_function(a,b)
            else:
                raise Exception(f'operation {node.operation} does not exist')



        case ast.IfExpression():
            if interpret(node.condition, symbol_table):
                return interpret(node.then_branch, symbol_table)
            elif node.else_branch is not None:
                return interpret(node.else_branch, symbol_table)
        
        case ast.Literal():
            if isinstance(node.value, bool):
                return node.value == True
            return node.value
        
        case ast.Identifier():
            if node.name in symbol_table.variables: 
                return symbol_table.variables[node.name]
            elif isinstance(symbol_table, ast.HierarchicalSymTab):
                return interpret(node, symbol_table.parent)
            else:
                raise Exception(f'{node.name} is not defined')
            
        case ast.UnaryOp():
            a: Any = interpret(node.right, symbol_table)
            top_symbol_table = symbol_table
            while isinstance(top_symbol_table, ast.HierarchicalSymTab):
                top_symbol_table = top_symbol_table.parent
            if 'unary' in top_symbol_table.variables:
                operation_function = top_symbol_table.variables['unary']
                return operation_function(a)
            else:
                raise Exception("Expected an unary operator")


        case ast.VariableDeclaration():
            # top_symbol_table = symbol_table
            # while isinstance(top_symbol_table, ast.HierarchicalSymTab):
            #     top_symbol_table = top_symbol_table.parent
            if symbol_table.variables.get(node.name) is not None:
                    raise Exception(f"The variable {node.name} has already been declared")
            symbol_table.variables[node.name] = interpret(node.assignment, symbol_table)

        case ast.Block():
            variables = ast.HierarchicalSymTab({}, symbol_table)
            for i in range(0, len(node.expressions)-1):
                interpret(node.expressions[i], variables)
            y=interpret(node.expressions[len(node.expressions)-1], variables)
            return y
        
        case ast.WhileExpression():
            condition = node.condition
            counter = 0
            if condition == True:
                raise Exception('infinited loop')
            while interpret(condition, symbol_table) == True:
                if counter > 500 : raise Exception('loop is stopped manually')
                counter+=1
                try:
                    interpret(node.do, symbol_table)
                except ContinueException:
                    continue
                except BreakException:
                    break
            return None
        
        case ast.Return():
            name = getattr(node.value, 'name', None)
            if symbol_table.variables.get(name) is not None:
                return symbol_table.variables[name]
            else:
                return interpret(node.value, symbol_table)



        case _:
            raise Exception(f'{node} is not supported')

            

def test_interpreter_variable_context() -> None:
        assert interpret(parse(tokenize('var a=1; {var a=2; a=a+1;} return a+1'))) == 2
test_interpreter_variable_context()
        



