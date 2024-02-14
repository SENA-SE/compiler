
from compiler import ast
from compiler.parser1 import parse
from compiler.tokenizer import tokenize


def test_parser() -> None:
    tokens = tokenize("1+1")
    parsed_expression = parse(tokens)
    assert parsed_expression == ast.BinaryOperation(
        left=ast.Literal(value=1),  
        operation="+",
        right=ast.Literal(value=1)  
    )

def test_parser_empty_input() -> None:
    try:
        parse([])
        assert False
    except ValueError as e:
        assert str(e) == "No tokens to parse."

def test_parser_garbage_at_end() -> None:
    tokens = tokenize("1 + 2 xyz")
    try:
        parse(tokens)
        assert False
    except Exception as e:
        assert "Garbage after expected end of expression" in str(e)

def test_parser_unexpected_token_type() -> None:
    tokens = tokenize("1 2")
    try:
        parse(tokens)
        assert False
    except Exception as e:
        assert "Expected token type" in str(e)

