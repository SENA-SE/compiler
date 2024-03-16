

from compiler.ast import AddressOf, BinaryOp, Block, Bool, Dereference, IfExpression, Int, Literal, Identifier, Function, PointerType, UnaryOp, Unit, VariableDeclaration, WhileExpression, Return
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

def test_parser_garbage() -> None:
    try:
         parse(tokenize('a + b c'))
    except Exception:
        assert True

def test_parser_empty_input() -> None:
    try:
         parse(tokenize([] ))
    except Exception:
        assert True

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

def test_parser_function_argument_expression() -> None:
    assert parse(tokenize('f(a+b, g(a))')) == Function(
        name='f',
        args=[BinaryOp(        
        left=Identifier(name='a'),
        operation='+',
        right=Identifier(name='b')),
        Function(name='g',args=[Identifier(name='a')])
        ]
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

def test_parser_block() -> None:
    assert parse(tokenize('{ 1 + 2; }')) == Block([
        BinaryOp(
            left=Literal(1),
            operation='+',
            right=Literal(2)
        ),
        Literal(None)
    ])

def test_parser_blocks() -> None:
    assert parse(tokenize('{{ 5 + 4; } { 3 - a }}')) == Block([
        Block([
            BinaryOp(
                left=Literal(5),
                operation='+',
                right=Literal(4)
            ),
            Literal(None)
        ]),
        Block([
            BinaryOp(
                left=Literal(3),
                operation='-',
                right=Identifier('a')
            )
        ])
    ])
    

def test_parser_block_with_if_with_last_semicolun() -> None:
    assert parse(tokenize('{ if a>=b then { a;b; } else { c } d }')) == Block([
        IfExpression(
            condition=BinaryOp(
                left=Identifier('a'),
                operation='>=',
                right=Identifier('b')
            ),
            then_branch=Block([Identifier('a'), Identifier('b'),Literal(None)]),
            else_branch=Block([Identifier('c')])
        ),
        Identifier('d')
    ])

def test_parser_block_with_semicolon() -> None:
    assert parse(tokenize(
        """        
        {
            f(a);
            x+y
        }
        """
    )) == Block([
        Function(name='f', args=[Identifier(name='a')]), 
        BinaryOp(left=Identifier(name='x'), operation='+', right=Identifier(name='y'))
    ])
def test_parser_block_missing_semicolon() -> None:
    try:
         parse(tokenize(
        """        
        {
            f(a)
            x+y
        }
        """
    ))
    except Exception:
        assert True

def test_parser_block_semicolon_tests() -> None:
    passed = False
    try:
         parse(tokenize('{ { a } { b } }'))
         parse(tokenize('{ if true then { a } b }'))
         parse(tokenize('{ if true then { a }; b }'))
         parse(tokenize('{ if true then { a } b; c }'))
         parse(tokenize('{ if true then { a } else { b } 3 }'))
         parse(tokenize('{ { f(a) } { b } }'))

         passed = True
    except Exception:
        pass
        assert passed

def test_parser_block_missing_semicolon_test() -> None:
    try:
         parse(tokenize('{ if true then { a } b c }' ))
    except Exception:
        assert True

def test_parser_variable_declaration() -> None:
    assert parse(tokenize('var a = 1')) == VariableDeclaration(
        name='a',
        assignment=Literal(1)
    )

def test_parser_variable_declaration_with_type() -> None:
    assert parse(tokenize('var a:Int = 1+1')) == VariableDeclaration(
        name='a',
        assignment=BinaryOp(
            left=Literal(1),
            operation='+',
            right=Literal(1)
        ),
        variable_type=Int
    )
    assert parse(tokenize('var a: Bool = true')) == VariableDeclaration(
        name='a',
        assignment=Literal(True),
        variable_type=Bool
    )



def test_parser_assignment() -> None:
    assert parse(tokenize('a = b + c')) == BinaryOp(
        left=Identifier('a'),
        operation='=',
        right=BinaryOp(
            left=Identifier('b'),
            operation='+',
            right=Identifier('c')
        )
    )

def test_parser_boolean() -> None:
    assert parse(tokenize('if false and true then a')) == IfExpression(
        condition=BinaryOp(
            left=Literal(False),
            operation='and',
            right=Literal(True)
        ),
        then_branch=Identifier('a'),
        else_branch=None
    )

def test_parser_while() -> None:
    assert parse(tokenize('while { a } do {b}')) == WhileExpression(
        condition=Block([Identifier('a')]),
        do=Block([Identifier('b')])
    )
    



# def test_parser_pointer_type_annotation():
#     source_code = "var x: Int* = &y"
#     tokens = tokenize(source_code)
#     parsed_expression = parse(tokens)

#     # Assert that the parsed AST matches the expected AST
#     assert parsed_expression == VariableDeclaration(
#         name="x",
#         variable_type=PointerType(base_type=Int),
#         assignment=AddressOf(operand=Identifier(name="y"))
#     )

# def test_parser_pointer_dereference():
#     # Test parsing of a dereference operation
#     source_code = "*p"
#     tokens = tokenize(source_code)
#     parsed_expression = parse(tokens)

#     # Construct the expected AST
#     expected_ast = Dereference(operand=Identifier(name="p"))

#     # Assert that the parsed AST matches the expected AST
#     assert parsed_expression == expected_ast, "Failed to parse pointer dereference operation correctly"
    

def test_parser_parse_function_declaration() -> None:
    assert parse(tokenize('fun square(x:Int, y:Int):Int{return x*x}')) == Function(
        name='square',
        args=[VariableDeclaration(
            name='x',
            variable_type=Int
            ),
        VariableDeclaration(
            name='y',
            variable_type=Int
            )
        ],
        return_type=Int,
        body=Block([
        Return(value=BinaryOp(
            left=Identifier(name='x'),
            operation='*',
            right=Identifier(name='x')
        ))]))

    assert parse(tokenize("""

    fun print_int_twice(x: Int) {
        print_int(x);
    }

    """)) == Function(
            name='print_int_twice',
            args=[VariableDeclaration(
                name='x',
                variable_type=Int
                )],
            return_type=None,
            body=Block([
            Function(
                name='print_int',
                args=[Identifier('x')]
            ),
            Literal(value=None)

        ])

        )



