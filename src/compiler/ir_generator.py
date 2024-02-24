from compiler import ast, ir
from compiler.ir import IRVar, Label

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
    def visit(node: ast.Expression) -> IRVar:
        match node:
            case ast.Literal():
                var = new_var()
                if isinstance(node.value, int):
                    instructions.append(ir.LoadIntConst(node.value, var))
                return var
            
            case ast.BinaryOp():
                if node.operation in ('==','!='):
                    var_left = visit(node.left)
                    var_right = visit(node.right)
                    var_result = new_var()
                    instructions.append(ir.Call(
                    fun=IRVar(node.operation),
                    args=[var_left, var_right],
                    dest=var_result
                    ))
                    return var_result
                elif node.operation in ('and','or'):
                    var_left = visit(node.left)
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
                    var_right = visit(node.right)
                    instructions.append(ir.Copy(source=var_right, dest=var_result))
                    instructions.append(ir.Jump(label=l_end))
                    instructions.append(l_end)
                    return var_result


                else:            
                    var_left = visit(node.left)
                    var_right = visit(node.right)
                    var_result = new_var()
                    instructions.append(ir.Call(
                        fun = IRVar(node.operation),
                        args=[var_left, var_right],
                        dest = var_result
                    ))
                    return var_result
            
            case ast.IfExpression():
                if node.else_branch is not None:
                    l_then = new_label()
                    l_else = new_label()
                    l_end = new_label()
                    # Recursively emit instructions for evaluating the condition.
                    var_condition = visit(node.condition)
                    instructions.append(ir.CondJump(var_condition, l_then, l_else))

                    instructions.append(l_then)
                    var_then = visit(node.then_branch)
                    instructions.append(ir.Jump(l_end))
                    instructions.append(l_else)
                    var_else = visit(node.else_branch)
                    instructions.append(ir.Copy(var_else, var_then))
                    
                    # Emit the label that we jump to when we don't want to go to the "then" branch.
                    instructions.append(l_end)
                    return var_then

            case ast.UnaryOp():
                var_right = visit(node.right)
                var_result = new_var()
                # Prefix unary operator names with 'unary_' to distinguish them
                op_name = f'unary_{node.operation}'
                instructions.append(ir.Call(
                    fun=IRVar(op_name),
                    args=[var_right],
                    dest=var_result
                ))
                return var_result     

            case _:
                raise Exception(f'Unsupported AST node {node}')

    var_result = visit(root_node)
    instructions.append(ir.Call(
        IRVar("print_int"),
        [var_result],
        new_var()
    ))
    return instructions