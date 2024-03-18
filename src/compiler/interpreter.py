import copy
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
    'print_int':'',
    'print_bool':'',
    'read_int':'',

    'unary': lambda x: not x if isinstance(x, bool) else -x,
}

library_functions = ['print_int','print_bool','read_int']

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
                current_symbol_table = symbol_table
                # Search for the variable in the current and all parent symbol tables
                while current_symbol_table is not None:
                    if node.left.name in current_symbol_table.variables:
                        current_symbol_table.variables[node.left.name] = interpret(node.right, symbol_table)
                        return None
                    current_symbol_table = getattr(current_symbol_table, 'parent', None)
                
                # If the variable was not found in any scope, raise an exception
                raise Exception(f'Variable {node.left.name} is not defined')

            a = interpret(node.left, symbol_table)
            b = interpret(node.right, symbol_table)
            #while a,b are expressions...
            if isinstance(a, ast.Expression):
                a = interpret(a, symbol_table)
            if isinstance(b, ast.Expression):
                b = interpret(b, symbol_table)

            top_symbol_table = symbol_table

            while isinstance(top_symbol_table, ast.HierarchicalSymTab):
                top_symbol_table = top_symbol_table.parent
            if node.operation in top_symbol_table.variables:
                if node.operation in ['or','and']:
                    operation_function = top_symbol_table.variables[node.operation]
                    return operation_function(node.left, node.right, symbol_table)
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
            if node.name in symbol_table.variables and not isinstance(symbol_table.variables[node.name], ast.Expression): 
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
            if symbol_table.variables.get(node.name) is not None:
                    raise Exception(f"The variable {node.name} has already been declared")
            symbol_table.variables[node.name] = interpret(node.assignment, symbol_table)
            return symbol_table.variables[node.name]
        
        case ast.FunctionCalled():
                for i in range(0, len(node.arg_variables)):
                    symbol_table.variables[node.arg_variables[i].name] = node.arg_variables[i].assignment
                    if isinstance(symbol_table.variables[node.arg_variables[i].name], ast.Literal):
                        symbol_table.variables[node.arg_variables[i].name] = symbol_table.variables[node.arg_variables[i].name].value
                    if isinstance(symbol_table.variables[node.arg_variables[i].name], ast.Identifier):
                        symbol_table.variables[node.arg_variables[i].name] = interpret(symbol_table.variables[node.arg_variables[i].name], symbol_table)
                    if isinstance(symbol_table.variables[node.arg_variables[i].name], ast.Function):
                        symbol_table.variables[node.arg_variables[i].name] = interpret(symbol_table.variables[node.arg_variables[i].name], symbol_table)
                    if isinstance(symbol_table.variables[node.arg_variables[i].name], ast.FunctionCalled):
                        symbol_table.variables[node.arg_variables[i].name] = interpret(symbol_table.variables[node.arg_variables[i].name], symbol_table)

                return interpret(node.body, symbol_table)
        
        case ast.Block():
            variables = ast.HierarchicalSymTab({}, symbol_table)
            # y = node.expressions[len(node.expressions)-1]
            for i in range(0, len(node.expressions)-1):
                result = interpret(node.expressions[i], variables)
                if isinstance(result, ast.FunctionCalled | ast.LibraryFunctionCalled):
                    result = interpret(result, variables)
            if not (isinstance(node.expressions[len(node.expressions)-1], ast.Literal) and getattr(node.expressions[len(node.expressions)-1],'value', None) is None):
                result = interpret(node.expressions[len(node.expressions)-1], variables)
            if isinstance(result, ast.FunctionCalled| ast.LibraryFunctionCalled):
                return interpret(result, variables)
            else:   return result

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
            if isinstance(node.value, ast.Function):
                return interpret(node.value, symbol_table)
            if symbol_table.variables.get(name) is not None:
                return symbol_table.variables[name]
            else:
                return interpret(node.value, symbol_table)
            
        case ast.LibraryFunctionCalled():
                    arg_variables = []
                    for i in range(0, len(node.args)):
                        arg = node.args[i]
                        if getattr(arg, 'value', None) is None:
                            arg = interpret(arg, symbol_table)
                            arg_variables.append(arg)
                        else:
                            arg_variables.append(arg.value)

                    match node.name:
                        case 'print_int':
                                    for i in range(0, len(arg_variables)):
                                        if type(arg_variables[i]) is int :
                                            print(arg_variables[i])
                                        else: raise Exception(f'Expected an integer, but get {arg_variables[i]}')
                        case 'print_bool':
                                    for i in range(0, len(arg_variables)):
                                        if type(arg_variables[i]) is bool :
                                            print(arg_variables[i])
                                        else: raise Exception(f'Expected an boolean value, but get {node.args[0]}')
                    return None
                
        case ast.Function():
            if node.body is not None:
                name = node.name
                body = node.body
                symbol_table.variables[name] = node

                return symbol_table
            else:
                name = node.name
                if node.name in symbol_table.variables: 

                    if name in library_functions:
                        top_symbol_table = symbol_table
                        while isinstance(top_symbol_table, ast.HierarchicalSymTab):
                            top_symbol_table = top_symbol_table.parent
                        if node.name in top_symbol_table.variables:
                                operation_function = top_symbol_table.variables[node.name]
                        operation_function = top_symbol_table.variables[node.name]
                        args = node.args
                        variables = ast.HierarchicalSymTab({}, symbol_table)
                        # interpret(ast.LibraryFunctionCalled(name=name, args=args), variables)
                        return ast.LibraryFunctionCalled(name=name, args=args)

                    else:
                        body = symbol_table.variables[name].body
                        return_type = symbol_table.variables[name].return_type
                        
                        args = node.args
                        arg_variables = symbol_table.variables[name].args
                        new_arg_variables = [copy.deepcopy(arg) for arg in arg_variables]
                        if (len(arg_variables)!= len(args)):
                            raise Exception(f'Expected {len(symbol_table.variables[name].args)} arguments')
                        for i in range(0, len(args)):
                                new_arg_variables[i].assignment = args[i]
                        return ast.FunctionCalled(name=name, body=body, return_type=return_type, arg_variables=new_arg_variables)

                elif isinstance(symbol_table, ast.HierarchicalSymTab):
                    return interpret(node, symbol_table.parent)
                else:
                    raise Exception(f'{node.name} is not defined')
                


        case _:
            raise Exception(f'{node} is not supported')

            

        
