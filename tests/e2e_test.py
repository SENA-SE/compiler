from compiler.tokenizer import tokenize
from compiler.type_checker import typecheck
from compiler.parser1 import parse
from compiler.ir_generator import generate_ir
from compiler.assembler import assemble
from compiler.assembly_generator import generate_assembly
import os
import sys
import subprocess
from dataclasses import dataclass


@dataclass
class CaseTest():
    name: str
    code: str
    inputs: list[str]
    expect: list[str]

directory_path = os.path.join(os.path.dirname(__file__), '../test_programs')
test_file_name = "test.txt"
compiled_file_name = "compiled_programs"

def get_cases() -> list[CaseTest]:
    case_list: list[CaseTest] = []
    file_path = os.path.join(directory_path, test_file_name)
    if os.path.isfile(file_path):
        with open(file_path, 'r') as f:
            cases = f.read().split('\n**********\n')
            for i in range(0, len(cases)):
                code = ""
                name = ""
                inputs = []
                expect = []
                for line in cases[i].split("\n"):
                    if line.startswith("# describe: "):
                        name=line[len("# describe: "):]
                    elif line.startswith("input"):
                        inputs.append(line[len("input "):])
                    elif line.startswith("expect"):
                        expect.append(line[len("expect: "):])
                    else:
                        code = code + line + "\n"
                case_list.append(CaseTest(name=name, code=code, inputs=inputs, expect=expect))
    return case_list

def test_all() -> None:
    output_path = os.path.join(directory_path, compiled_file_name)
    if not os.path.exists(output_path):     os.makedirs(output_path)
    cases = get_cases()

    for case in cases:
        def run_test_case(case: CaseTest = case) -> None:
            tokens = tokenize(case.code)
            ast_node = parse(tokens)
            typecheck(ast_node)
            ir_instructions = generate_ir(ast_node)
            asm_code = generate_assembly(ir_instructions)

            assemble(asm_code, f'test_programs/compiled_programs/{case.name}')
            
            process = subprocess.Popen(os.path.join(output_path, case.name), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            for input in case.inputs:
                if process.stdin is not None:
                    process.stdin.write(input.encode())
                    process.stdin.flush()

            output = process.communicate()[0].decode()
            assert output == f'{case.expect[0]}\n'


        sys.modules[__name__].__setattr__(
            f'test_{case.name}',
            run_test_case
        )
        
test_all()