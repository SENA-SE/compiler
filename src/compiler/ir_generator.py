from compiler import ast, ir
from compiler.ir import IRVar, Label
from compiler import ast
from compiler.parser1 import parse
from compiler.tokenizer import tokenize
from compiler.type_checker import typecheck
from compiler.assembler import assemble
from compiler.assembly_generator import generate_assembly

SymbolList = {}

def generate_ir(root_node: ast.Expression) -> list[ir.Instruction]:
    next_var_num = 1
    next_label_num = 1
    loop_labels = []    # stack to keep track of loop labels
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
                if type(node.value) is int:
                    instructions.append(ir.LoadIntConst(node.value, var))
                elif type(node.value) is bool:
                    instructions.append(ir.LoadBoolConst(node.value, var))
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
                var_right = getattr(node.assignment,'value', None)
                if var_right is not None:
                    var = new_var()
                    var_result = new_var()
                    if type(var_right) is int:
                        instructions.append(ir.LoadIntConst(var_right, var))
                    if type(var_right) is bool:
                        instructions.append(ir.LoadBoolConst(var_right, var))
                else:
                    if isinstance(node.assignment, ast.Expression):
                        var = visit(node.assignment, symbol_table)
                    var_result = new_var()
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
                    var_result = new_var()
                    instructions.append(ir.Copy(var_then, var_result))
                    instructions.append(ir.Jump(l_end))

                    instructions.append(l_else)
                    var_else = visit(node.else_branch, symbol_table)
                    instructions.append(ir.Copy(var_else, var_then))
                    
                    # Emit the label that we jump to when we don't want to go to the "then" branch.
                    instructions.append(l_end)
                    return var_then
                else:
                    l_then = new_label()
                    l_end = new_label()

                    var_condition = visit(node.condition, symbol_table)
                    instructions.append(ir.CondJump(var_condition, l_then, l_end))
                    instructions.append(l_then)

                    var_result = visit(node.then_branch, symbol_table)
                    instructions.append(l_end)
                    return var_result
            case ast.WhileExpression():
                l_start = new_label()
                l_do = new_label()
                l_end = new_label()

                # Push the current loop's start and end labels onto the stack
                loop_labels.append((l_start, l_end))

                instructions.append(l_start)
                condition = visit(node.condition, symbol_table)
                instructions.append(ir.CondJump(condition=condition, then_label=l_do, else_label=l_end))

                instructions.append(l_do)
                var_result = visit(node.do, symbol_table)
                instructions.append(ir.Jump(l_start))

                instructions.append(l_end)
                loop_labels.pop()
                return var_result
                

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
                else:
                    return Exception(f'{node.name} is not defined')
                
            case ast.Return():
                return visit(node.value, symbol_table)
            
            case ast.Function():
                if node.name in ['print_int','print_bool','read_int']:
                    match node.name:
                        case 'print_int':
                            var_result = new_var()
                            var_args = visit(node.args[0], symbol_table)
                            instructions.append(ir.Call(
                                fun=IRVar(node.name),
                                args=[var_args],
                                dest=var_result
                            ))
                            return var_result
                        case 'print_bool':
                            var_result = new_var()
                            var_args = visit(node.args[0], symbol_table)
                            instructions.append(ir.Call(
                                fun=IRVar(node.name),
                                args=[var_args],
                                dest=var_result
                            ))
                            return var_result
                        case 'read_int':
                            var_result = new_var()
                            instructions.append(ir.Call(
                                fun=IRVar(node.name),
                                args=[],
                                dest=var_result
                            ))
                            return var_result
                elif node.body is not None: # define a function
                    fun_label = new_label()
                    instructions.append(ir.FunctionDefinition(name=node.name,label=fun_label))

                    symbol_table.variables[node.name] = fun_label

                    fun_symbol_table = ast.SymTab(variables={})

                    for arg in node.args:
                        var = new_var()
                        fun_symbol_table.variables[arg.name] = var
                
                    for expression in node.body.expressions:
                        visit(expression, fun_symbol_table)

                else:   # call a function
                    args_vars = [visit(arg, symbol_table) for arg in node.args]
                
                    result_var = new_var()

                    instructions.append(ir.Call(
                        fun=IRVar(node.name),
                        args=args_vars,
                        dest=result_var
                    ))

                    return result_var


            case _:
                raise Exception(f'Unsupported AST node {node}')
            

    var_result = visit(root_node)

    return instructions
