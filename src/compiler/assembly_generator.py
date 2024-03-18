import dataclasses
from compiler import ir
from compiler.intrinsics import IntrinsicArgs, all_intrinsics



def generate_assembly(instructions: list[ir.Instruction]) -> str:
    assembly_code_lines = []
    def emit(line: str) -> None: assembly_code_lines.append(line)

    locals = Locals(get_all_ir_variables(instructions))
    function_table = {}
    flag_definition = False

    emit('.global main')
    emit('.type main, @function')
    emit('.extern print_int')
    emit('.extern print_bool')
    emit('.extern read_int')
    
    emit('.section .text')
    emit('main:')
    emit('pushq %rbp')
    emit('movq %rsp, %rbp')
    emit(f'subq ${locals.stack_used()}, %rsp')

    for insn in instructions:
        emit('# ' + str(insn))
        match insn:
            case ir.Label():
                emit(f'.L{insn.name}:')

            case ir.FunctionDefinition():
                # emit(f'.L{insn.label.name}:')
                emit(f'{insn.name}:')
                function_table[insn.name] = insn.label.name
                flag_definition = True

            case ir.LoadIntConst():
                if -2**31 <= insn.value<2**31:
                    emit(f'movq ${insn.value}, {locals.get_ref(insn.dest)}')
                else:
                    emit(f'movabsq ${insn.value}, %rax')
                    emit(f'movq %rax, {locals.get_ref(insn.dest)}')

            case ir.LoadBoolConst():        
                if insn.value:  
                    value = 1
                else:
                    value = 0
                emit(f'movq ${value}, {locals.get_ref(insn.dest)}')

            case ir.Copy():
                emit(f'movq {locals.get_ref(insn.source)}, %rax')
                emit(f'movq %rax, {locals.get_ref(insn.dest)}')

            case ir.Call():
                if (intrinsic := all_intrinsics.get(insn.fun.name)) is not None:
                    args = IntrinsicArgs(
                        arg_refs=[locals.get_ref(a) for a in insn.args],
                        result_register='%rax',
                        emit=emit
                    )
                    intrinsic(args)
                    emit(f'movq %rax, {locals.get_ref(insn.dest)}')
                    if flag_definition:
                        emit('ret')
                        flag_definition = False
                elif insn.fun.name in function_table:
                    for arg, reg in zip(insn.args, ['%rdi', '%rsi']):  # Extend for more arguments as needed
                        emit(f'movq {locals.get_ref(arg)}, {reg}')
                    emit(f'call {insn.fun.name}')
                    emit(f'movq %rax, {locals.get_ref(insn.dest)}')

                elif insn.fun.name in ['print_int', 'print_bool','read_int']:
                     if len(insn.args) == 0:
                         emit(f'call read_int')
                         emit(f'movq %rax, {locals.get_ref(insn.dest)}')
                     elif len(insn.args) == 1:     # read_int
                        emit(f'movq {locals.get_ref(insn.args[0])}, %rdi')
                        emit(f'call {insn.fun.name}')


            case ir.Jump():
                emit(f'jmp .L{insn.label.name}')

            case ir.CondJump():
                emit(f'cmpq $0, {locals.get_ref(insn.condition)}')
                emit(f'jne .L{insn.then_label.name}')
                emit(f'jmp .L{insn.else_label.name}')
            
            
            
            case _:
                raise Exception(f'Unknow instruction:{type(insn)}')

    emit('movq $0, %rax')
    emit('movq %rbp, %rsp')
    emit('popq %rbp')
    emit('ret')
    emit('')

    return "\n".join(assembly_code_lines)


class Locals:
    """Knows the memory location of every local variable."""
    _var_to_location: dict[ir.IRVar, str]
    _stack_used: int

    def __init__(self, variables: list[ir.IRVar]) -> None:
        self._var_to_location = {}
        self._stack_used = 8
        for v in variables:
            if v not in self._var_to_location:
                self._var_to_location[v] = f'-{self._stack_used}(%rbp)'
                self._stack_used += 8

    def get_ref(self, v: ir.IRVar) -> str:
        """Returns an Assembly reference like `-24(%rbp)`
        for the memory location that stores the given variable"""
        return self._var_to_location[v]

    def stack_used(self) -> int:
        """Returns the number of bytes of stack space needed for the local variables."""
        return self._stack_used
    
def get_all_ir_variables(instructions: list[ir.Instruction]) -> list[ir.IRVar]:
    result_list: list[ir.IRVar] = []
    result_set: set[ir.IRVar] = set()

    def add(v: ir.IRVar) -> None:
        if v not in result_set:
            result_list.append(v)
            result_set.add(v)

    for insn in instructions:
        for field in dataclasses.fields(insn):
            value = getattr(insn, field.name)
            if isinstance(value, ir.IRVar):
                add(value)
            elif isinstance(value, list):
                for v in value:
                    if isinstance(v, ir.IRVar):
                        add(v)
    return result_list