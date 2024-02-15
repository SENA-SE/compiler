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
    'or': lambda x, y: True if x else y,
    'and': lambda x, y: False if not x else x and y,


    'unary': lambda x: not x if isinstance(x, bool) else -x,
}
def interpret(node: ast.Expression, symbol_table: ast.SymTab = ast.SymTab(variables=SymbolList)) -> Value:
    match node:

        
        case ast.BinaryOp():
            a: Any = interpret(node.left, symbol_table)
            b: Any = interpret(node.right, symbol_table)
            top_symbol_table = symbol_table
            while isinstance(top_symbol_table, ast.HierarchicalSymTab):
                top_symbol_table = top_symbol_table.parent
            if node.operation in top_symbol_table.variables:
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
            if node.name in symbol_table.variables: return symbol_table.variables[node.name]
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
            symbol_table.variables[node.name] = interpret(node.assignment, symbol_table)

        case ast.Block():
            variables = ast.HierarchicalSymTab({}, symbol_table)
            for i in range(0, len(node.expressions)-1):
                interpret(node.expressions[i], variables)

            return interpret(node.expressions[len(node.expressions)-1], variables)

        case _:
            raise Exception(f'{node} is not supported')

            
