
from compiler.ast import BinaryOp, IfExpression, Literal, Identifier, Function, UnaryOp
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

def test_parser_unary_operation() -> None:
    assert parse(tokenize('-1')) == UnaryOp(
        operation='-',
        right=Literal(1)
    )

def test_parser_unary_not() -> None:
    assert parse(tokenize('not a')) == UnaryOp(
        operation='not',
        right=Identifier(name='a')
    )

def test_parser_comparison_with_calculation() -> None:
    assert parse(tokenize('3 > 1+2')) == BinaryOp(
        left=Literal(3),
        operation='>',
        right=BinaryOp(
            left=Literal(1),
            operation='+',
            right=Literal(2)
        )
    )
def test_parser_euqal() -> None:
    assert parse(tokenize('1 == 1')) == BinaryOp(
        left=Literal(1),
        operation='==',
        right=Literal(1)
    )

def test_parser_greater_than_or_equal() -> None:
    assert parse(tokenize('3 >= 1+2')) == BinaryOp(
        left=Literal(3),
        operation='>=',
        right=BinaryOp(
            left=Literal(1),
            operation='+',
            right=Literal(2)
        )
    )

def test_parser_reminder() -> None:
    assert parse(tokenize('16 % a')) == BinaryOp(
        left=Literal(16),
        operation='%',
        right=Identifier(name='a')
    )



def test_parser_or() -> None:
    assert parse(tokenize('if 1 or 2 then 3')) == IfExpression(
        condition=BinaryOp(
            left=Literal(1),
            operation='or',
            right=Literal(2)
        ),
        then_branch=Literal(3),
        else_branch=None
    )

def test_parser_and() -> None:
    assert parse(tokenize('if a < b and a < c then 1')) == IfExpression(
        condition=BinaryOp(
            left=BinaryOp(
                left=Identifier('a'),
                operation='<',
                right=Identifier('b')
            ),
            operation='and',
            right=BinaryOp(
                left=Identifier('a'),
                operation='<',
                right=Identifier('c')
            ),
        ),
        then_branch=Literal(1),
        else_branch=None
    )