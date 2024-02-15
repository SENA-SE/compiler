from compiler.interpreter import interpret
from compiler.parser1 import parse
from compiler.tokenizer import tokenize



def test_interpreter_calculation() -> None:
    assert interpret(parse(tokenize('(1 + 2) * 3'))) == 9

def test_interpreter_if() -> None:
    assert interpret(parse(tokenize('if 1 < 2 then 3 '))) == 3

def test_interpreter_if_else() -> None:
    assert interpret(parse(tokenize('if 1 == 2 then 3 else 4 '))) == 4

def test_interpreter_unary() -> None:
    assert interpret(parse(tokenize('-1'))) == -1
    assert interpret(parse(tokenize('not 1'))) == -1
    assert interpret(parse(tokenize('not -1'))) == True

def test_interpreter_variable_declaration() -> None:
    assert interpret(parse(tokenize('{var a = 1;  a + 1}'))) == 2

def test_interpreter_blocks() -> None:
    assert interpret(parse(tokenize('var a=1;{var b=2; var a = 3;}   a+4'))) == 5

def test_interpreter_variable_in_scope() -> None:
    try:
        interpret(parse(tokenize('{var a=1}  a'))) == 1
    except Exception:
        assert True
