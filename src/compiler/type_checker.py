from compiler.parser1 import parse
from compiler.tokenizer import tokenize
import compiler.ast as ast
from compiler.ast import Int, Bool, Unit
SymbolList = {
    '+': (Int, Int, Int),
    '<': (Int, Int, Int),
    'or': (Bool, Bool, Bool),
    'print_int': (Int, Unit),
    'print_bool': (Bool, Unit),
    # and so on...
}


def typecheck(node: ast.Expression, symbol_table: ast.SymTab = ast.SymTab(variables=SymbolList)) -> ast.Type:
    match node:
        case ast.UnaryOp():
            operand_type = typecheck(node.right, symbol_table)
            # Assuming unary minus applies to integers
            if node.operation == '-':
                if operand_type is not Int:
                    raise Exception(f'Unary minus expected an integer but got {operand_type}')
                node.type = Int
                return Int
            # handling boolean negation (not operation)
            elif node.operation == 'not':
                if operand_type is not Bool:
                    raise Exception(f'{node}: Expected a boolean but got {operand_type}')
                node.type = Bool
                return Bool
            else:
                raise Exception(f'Unary operation {node.operation} is not supported')
            
        case ast.BinaryOp():
            t1 = typecheck(node.left)
            t2 = typecheck(node.right)
            if node.operation in ['+','-','*','-','%']:
                if t1 is not Int or t2 is not Int:
                    raise Exception(f'Expected two integer numbers, but got {t1} and {t2}')
                node.type = Int
                return Int
            elif node.operation in ['<','<=','>','>=']:
                if t1 is not Int or t2 is not Int:
                    raise Exception(f'Expected two integer numbers, but got {t1} and {t2}')
                node.type = Bool
                return Bool

            elif node.operation in ['or','and']:
                if t1!=Bool or t2!=Bool:
                    raise Exception(f'Expected two boolean values, but got {t1} and {t2}')
                else:
                    node.type = Bool
                    return Bool
            elif node.operation in ['==','!=']:
                if t1!=t2:
                    raise Exception(f'Expected both to be boolean values or integer numbers, but got {t1} and {t2}')
                node.type = Bool
                return Bool
            else: 
                raise Exception(f'{node.operation} is not a supported operation')
            
        case ast.IfExpression():
            t1 = typecheck(node.condition)
            t2 = typecheck(node.then_branch)
            if t1 is not Bool:
                raise Exception(f'Expected a boolean value but got {t1}')
            if node.else_branch is not None:
                t3 = typecheck(node.else_branch)
                if t2 != t3:
                    raise Exception(f'Expected then and else return the same type, but got {t2} and {t3}')
                node.type = t2
                return t2
            else:
                node.type = Unit
                return Unit
        
        case ast.Literal():
            if type(node.value) is int:
                node.type = Int
                return Int
            elif type(node.value) is bool:
                node.type = Bool
                return Bool
            else:
                raise Exception(f"{node.value} is not an integer")
        
        case ast.Function():
            function_type = symbol_table.variables[node.name]
            arg_types = [typecheck(arg, symbol_table) for arg in node.args]

            for arg_type, required_type in zip(arg_types, function_type[:-1]):
                if arg_type != required_type:
                    raise Exception(f'Expected type {required_type}, but got {arg_type}')
            node.type = function_type[-1]
            return function_type[-1]
        
        case ast.VariableDeclaration():
            assigned_type = typecheck(node.assignment, symbol_table)
            if node.variable_type is not None:
                required_type = node.variable_type
                if required_type != assigned_type:
                    raise Exception(f'Expected {required_type} but got {assigned_type}')
                symbol_table.variables[node.name] = required_type
                node.type = required_type
                return required_type
            else:
                symbol_table.variables[node.name] = assigned_type
                node.type = assigned_type
                return assigned_type


        case _:
            raise Exception(f'{node} is not supported')
        
# def test_type_checker_if_else_unit() -> None:
#     assert typecheck(parse(tokenize('if not true then 1'))) == Unit
# test_type_checker_if_else_unit()
