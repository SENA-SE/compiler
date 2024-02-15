from compiler.interpreter import interpret
from compiler.parser1 import parse
from compiler.tokenizer import tokenize



def test_interpreter_calculation() -> None:
    assert interpret(parse(tokenize('(1 + 2) * 3'))) == 9

def test_interpreter_if() -> None:
    assert interpret(parse(tokenize('if 1 < 2 then 3 '))) == 3

def test_interpreter_if_else() -> None:
    assert interpret(parse(tokenize('if 1 == 2 then 3 else 4 '))) == 4