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

def test_interpreter_variable_operation_in_scope() -> None:
        assert interpret(parse(tokenize('var a=1; {var a=2; a=a+1;} a'))) == 1


def test_interpreter_variable_context() -> None:
        assert interpret(parse(tokenize('var a=1; {a=2; a=a+1;} a'))) == 3

def test_interpreter_double_declaration() -> None:
    try:
        interpret(parse(tokenize('var a=1; {var a=2; a=a+1;} a'))) == 3
    except Exception:
        assert True


def test_intepreter_and_or_operations() -> None:
    assert interpret(parse(tokenize('1==1 and 1<2 '))) == True
    assert interpret(parse(tokenize('1==1 or 1<2 '))) == True
    assert interpret(parse(tokenize('1!=1 or 1<2 '))) == True
    assert interpret(parse(tokenize('1!=1 and 1<2 '))) == False

def test_interpreter_while_expression() -> None:
    assert interpret(parse(tokenize('var a = -1; while a<2 do a=a+1; a'))) == 2
    # assert interpret(parse(tokenize('var a = -1; while a < 2 do a += 1; a'))) == 1
    # assert interpret(parse(tokenize('var a = -1; while a < 2 do {a += 1; a}'))) == None

def test_interpreter_infinite_loop() -> None:
    try:
        interpret(parse(tokenize('while a < 2 do a += 1; a'))) == 1
    except Exception:
        assert True

def test_break_in_loop():
    program = """
    var x = 0;
    while (x < 10) do{
        x = x + 1;
        if (x == 5) then break;
    }
    x
    """
    # x should be 5 because the loop breaks when x reaches 5
    assert interpret(parse(tokenize(program))) == 5

def test_continue_in_loop():
    program = """
    var x = 0;
    var y = 0;
    while (x < 5) do{
        x = x + 1;
        if (x == 3) then continue;
        y = y + 1;
    }
    y
    """
    # y should be 4 because the increment of y is skipped when x is 3
    assert interpret(parse(tokenize(program))) == 4