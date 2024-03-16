
from compiler.parser1 import parse
from compiler.tokenizer import tokenize
from compiler.type_checker import  typecheck
from compiler.ast import Bool, Int, Unit


def test_type_checker_int() -> None:
    assert typecheck(parse(tokenize('1 + 2'))) == Int

def test_type_checker_bool() -> None:
    assert typecheck(parse(tokenize('1 < 2'))) == Bool
    assert typecheck(parse(tokenize('1>3 or 2<4'))) == Bool

def test_type_checker_comparision() -> None:
    assert typecheck(parse(tokenize('1 == 2'))) == Bool
    assert typecheck(parse(tokenize('1>2 == (3>4)'))) == Bool

def test_type_cheker_comparision_between_different_types() -> None:
    try:
        typecheck(parse(tokenize('1>2 == 3')))
    except Exception:
        assert True

def test_type_checker_calculation_between_different_types() -> None:
    try:
        typecheck(parse(tokenize('1 + (2>3)')))
    except Exception:
        assert True

def test_type_checker_if_else() -> None:
    assert typecheck(parse(tokenize('if 1 < 2 then 3'))) == Unit

def test_type_checker_print_int() -> None:
    assert typecheck(parse(tokenize('print_int(1)'))) == Unit

def test_type_checker_predefined_function_with_wrong_type_argument() -> None:
    try:
         typecheck(parse(tokenize('print_int(True)')))
    except Exception:
        assert True

def test_type_checker_variable_declaration() -> None:
    assert typecheck(parse(tokenize('var x = 1>2'))) == Bool
    assert typecheck(parse(tokenize('var x: Int = 1 + 1'))) == Int

def test_type_checker_assign_invalid_type() -> None:
    try:
         typecheck(parse(tokenize('var x: Int = 1>2')))
    except Exception:
        assert True

def test_type_checker_block_return() -> None:
    assert typecheck(parse(tokenize('{var a=1; return a}'))) == Int

def test_type_checker_function() -> None:
    assert typecheck(parse(tokenize('fun square(x:Int, y:Int):Int{return x*y};  return square(3,4)'))) == Int