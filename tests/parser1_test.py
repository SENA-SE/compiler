
from compiler.ast import BinaryOp, IfExpression, Literal, Identifier, Function
from compiler.parser1 import parse
from compiler.tokenizer import tokenize


def test_parser() -> None:
    tokens = tokenize("1+1")
    parsed_expression = parse(tokens)
    assert parsed_expression == BinaryOp(
        left=Literal(value=1),  
        operation="+",
        right=Literal(value=1)  
    )
def test_parser_variable_addition() -> None:
    assert parse(tokenize("x + 1")) == BinaryOp(
        left= Identifier(name='x'),
        operation='+',
        right = Literal(1)
    )

def test_parser_multiple_terms_addition() -> None:
    assert parse(tokenize("1 + 2 + 3")) == BinaryOp(
        left = BinaryOp(
            left=Literal(1),
            operation='+',
            right=Literal(2)
        ),
        operation='+',
        right=Literal(3)
    )

def test_parser_left_associate() -> None:
    assert parse(tokenize("(1 + 2 )+ 3")) == BinaryOp(
        left = BinaryOp(
            left=Literal(1),
            operation='+',
            right=Literal(2)
        ),
        operation='+',
        right=Literal(3)
    )

def test_parser_right_associate() -> None:
    assert parse(tokenize("1 + (2 + 3)")) == BinaryOp(
        right = BinaryOp(
            left=Literal(2),
            operation='+',
            right=Literal(3)
        ),
        operation='+',
        left=Literal(1)
    )
def test_parser_multiplication() -> None:
    assert parse(tokenize("(1 + 2)* 3 + 4 / 5")) == BinaryOp(
        left=BinaryOp(
            left=BinaryOp(
                left=Literal(1),
                operation='+',
                right=Literal(2)
            ),
            operation='*',
            right=Literal(3)
        ),
        operation='+',
        right=BinaryOp(
            left=Literal(4),
            operation='/',
            right=Literal(5)
        )
    )


def test_parser_if() -> None:
    assert parse(tokenize('if a then b else c+d')) == IfExpression(
        condition=Identifier(name='a'),
        then_branch=Identifier(name='b'),
        else_branch=BinaryOp(
            left=Identifier(name='c'),
            operation='+',
            right=Identifier(name='d')
        )
    )

def test_parser_if_optional_else() -> None:
    assert parse(tokenize('if a then b')) == IfExpression(
        condition=Identifier(name='a'),
        then_branch=Identifier(name='b'),
        else_branch=None
    )

def test_parser_if_as_part_of_expression() -> None:
    assert parse(tokenize('1 + if 2 then 3 else 4')) == BinaryOp(
        left=Literal(1),
        operation='+',
        right=IfExpression(
            condition=Literal(2),
            then_branch=Literal(3),
            else_branch= Literal(4)
        )
    )

def test_parser_function() -> None:
    assert parse(tokenize('f(x, y+z)')) == Function(
        name='f',
        args=[Identifier(name='x'), BinaryOp(        
        left=Identifier(name='y'),
        operation='+',
        right=Identifier(name='z'))]
    )