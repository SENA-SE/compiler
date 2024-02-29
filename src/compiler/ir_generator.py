from compiler import ast, ir
from compiler.ir import IRVar, Label
from compiler import ast
from compiler.parser1 import parse
from compiler.tokenizer import tokenize
from compiler.type_checker import typecheck

SymbolList = {}

def generate_ir(root_node: ast.Expression) -> list[ir.Instruction]:
    next_var_num = 1
    next_label_num = 1
    def new_var() -> IRVar:
        nonlocal next_var_num
        # print(next_var_num)
        var = IRVar(f'x{next_var_num}')
        next_var_num+=1
        return var
    
    def new_label() -> Label:
        nonlocal next_label_num
        # print(next_label_num)
        label = Label(f'L{next_label_num}')
        next_label_num+=1
        return label
    instructions = []
    def visit(node: ast.Expression, symbol_table: ast.SymTab = ast.SymTab(variables=SymbolList)) -> IRVar:
        match node:
            case ast.Literal():
                var = new_var()
                if isinstance(node.value, int):
                    instructions.append(ir.LoadIntConst(node.value, var))
                return var
            
            case ast.BinaryOp():
                if node.operation in ('==','!='):
                    var_left = visit(node.left, symbol_table)
                    var_right = visit(node.right, symbol_table)
                    var_result = new_var()
                    instructions.append(ir.Call(
                    fun=IRVar(node.operation),
                    args=[var_left, var_right],
                    dest=var_result
                    ))
                    return var_result
                elif node.operation in ('and','or'):
                    var_left = visit(node.left, symbol_table)
                    var_result = new_var()
                    l_skip_right = new_label()
                    l_end = new_label()

                    if node.operation == 'and':
                        # Jump to l_skip_right if var_left is false (0).
                        instructions.append(ir.CondJump(condition=var_left, then_label=l_skip_right, else_label=l_end))
                    else:  # 'or'
                        # Jump to l_end if var_left is true (non-zero).
                        instructions.append(ir.CondJump(condition=var_left, then_label=l_end, else_label=l_skip_right))
                    
                    instructions.append(l_skip_right)
                    var_right = visit(node.right, symbol_table)
                    instructions.append(ir.Copy(source=var_right, dest=var_result))
                    instructions.append(ir.Jump(label=l_end))
                    instructions.append(l_end)
                    return var_result
                elif node.operation == '=':
                    var_source = visit(node.left, symbol_table)
                    new_value = visit(node.right, symbol_table)

                    instructions.append(ir.Copy(source=new_value, dest=var_source))

                else:            
                    var_left = visit(node.left, symbol_table)
                    var_right = visit(node.right, symbol_table)
                    var_result = new_var()
                    instructions.append(ir.Call(
                        fun = IRVar(node.operation),
                        args=[var_left, var_right],
                        dest = var_result
                    ))
                    return var_result
            
            case ast.VariableDeclaration():
                # var_right = visit(node.right)
                var = new_var()
                var_result = new_var()
                var_right = getattr(node.assignment,'value', None)
                if isinstance(var_right, int):
                    instructions.append(ir.LoadIntConst(var_right, var))
                instructions.append(ir.Copy(source=var, dest=var_result))
                symbol_table.variables[node.name] = var_result
                return var_result


            case ast.IfExpression():
                if node.else_branch is not None:
                    l_then = new_label()
                    l_else = new_label()
                    l_end = new_label()
                    # Recursively emit instructions for evaluating the condition.
                    var_condition = visit(node.condition, symbol_table)
                    instructions.append(ir.CondJump(var_condition, l_then, l_else))

                    instructions.append(l_then)
                    var_then = visit(node.then_branch, symbol_table)
                    instructions.append(ir.Jump(l_end))
                    instructions.append(l_else)
                    var_else = visit(node.else_branch, symbol_table)
                    instructions.append(ir.Copy(var_else, var_then))
                    
                    # Emit the label that we jump to when we don't want to go to the "then" branch.
                    instructions.append(l_end)
                    return var_then

            case ast.UnaryOp():
                var_right = visit(node.right, symbol_table)
                var_result = new_var()
                # Prefix unary operator names with 'unary_' to distinguish them
                op_name = f'unary_{node.operation}'
                instructions.append(ir.Call(
                    fun=IRVar(op_name),
                    args=[var_right],
                    dest=var_result
                ))
                return var_result     
            
            case ast.Block():
                symbol_table = ast.HierarchicalSymTab({}, symbol_table)
                for i in range(0,len(node.expressions)):
                    visit(node.expressions[i], symbol_table)

            case ast.Identifier():
                if node.name in symbol_table.variables: 
                    return symbol_table.variables[node.name]
                elif isinstance(symbol_table, ast.HierarchicalSymTab):
                    return visit(node, symbol_table.parent)

            case ast.Return():
                return visit(node.value, symbol_table)
            # case ast.Function():
            #     # Assuming the Function node has a name, args (list of arguments), and a body (an Expression)
            #     # First, create a label for the function entry
            #     fun_label = Label(node.name)
            #     instructions.append(fun_label)

            #     # Create IRVars for each argument
            #     arg_vars = [new_var() for _ in node.args]

            #     # Assuming there's a mechanism to map function arguments to IRVars
            #     # This could be a simple assignment for now, but you might need a more sophisticated approach
            #     # for handling scopes and argument passing
            #     for arg_name, arg_var in zip(node.args, arg_vars):
            #         instructions.append(ir.Copy(source=IRVar(arg_name), dest=arg_var))

            #     # Visit the body of the function
            #     # This assumes the body is a single expression; if it's more complex, additional handling will be needed
            #     body_var = visit(node.body)

            #     # Assuming functions implicitly return the last evaluated expression
            #     instructions.append(ir.Return(value=body_var))

            #     # Return the function label as the result of visiting the function node
            #     # This might be used to reference the function elsewhere
            #     return fun_label

            case _:
                raise Exception(f'Unsupported AST node {node}')
            

    # if end with semicolon
    var_result = visit(root_node)
    instructions.append(ir.Call(
        IRVar("print_int"),
        [var_result],
        new_var()
    ))
    return instructions

tokens = tokenize('var a=1; {var a=2; a=a+1;} return a+1')
ast_node = parse(tokens)
typecheck(ast_node)
ir_instructions = generate_ir(ast_node)
print("\n".join([str(ins) for ins in ir_instructions]))