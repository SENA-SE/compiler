from compiler import ast
from compiler.tokenizer import Token
from compiler.tokenizer import tokenize



def parse(tokens: list[Token]) -> ast.Expression:
    pos = 0
    # 'peek()' returns the token at 'pos',
    # or a special 'end' token if we're past the end of the token list.
    def peek() -> Token:
        if pos < len(tokens):
            return tokens[pos]
        else:
            return Token(
                type="end",
                text="",
            )

    # 'consume(expected)' returns the token at 'pos' and moves 'pos' forward.
    # If the optional parameter 'expected' is given, it checks that the token being consumed has that text.
    # If 'expected' is a list, then the token must have one of the texts in the list.
    def consume(expected: str | list[str] | None = None) -> Token:
        print(f'expected {expected}')
        nonlocal pos
        token = peek()
        if isinstance(expected, str) and token.text != expected:
            raise Exception(f' expected "{expected}"')
        if isinstance(expected, list) and token.text not in expected:
            comma_separated = ", ".join([f'"{e}"' for e in expected])
            raise Exception(f' expected one of: {comma_separated}')
        pos += 1
        print(f'consumed {token}')
        return token

    # This is the parsing function for integer literals.
    # It checks that we're looking at an integer literal token,
    # moves past it, and returns a 'Literal' AST node containing the integer from the token.
    def parse_int_literal() -> ast.Literal:
        if peek().type != 'int_literal':
            raise Exception(f' expected an integer literal')
        token = consume()
        return ast.Literal(int(token.text))

    def parse_identifier() -> ast.Identifier| ast.Literal| ast.Function:
        token = peek()
        if peek().type != 'identifier':
            raise Exception(f' expected an identifier')
        else:
            consume()
            next_token = peek()
            
            print(f'mmmmmmmmmmtoken: {token}')
            if next_token.text == '(':
                consume('(')
                args = parse_arguments()
                consume(')')
                return ast.Function(name=token.text, args=args)
            else:   # no an if expression
                return ast.Identifier(token.text)
    
    def parse_arguments()-> list[ast.Expression]:
        args:list[ast.Expression] = []
        while peek().text != ')':
            if peek().text == ',':
                consume(',')
            args.append(parse_expression())

        print(f'args{args}')
        return args

    def parse_term() -> ast.Expression:
        left = parse_factor()
        while peek().text in ['*', '/']:
            operator_token = consume()
            operator = operator_token.text
            right = parse_factor()
            left = ast.BinaryOp(
                left,
                operator,
                right
            )
        return left

    # Borrowing from mathematics, we say that
    # "an identifier or an integer literal"
    # is called a "term".
    def parse_factor() -> ast.Expression:
        # print(peek().text,peek().type)
        if peek().text == '(':
            return parse_parenthesized()
        elif peek().text == 'if':
            return parse_if()
        elif peek().text in ['not', '-']:
            return parse_unary()
        elif peek().type == 'int_literal':
            return parse_int_literal()
        elif peek().type == 'identifier':
            return parse_identifier()

        else:
            raise Exception(f'expected an integer literal or an identifier, but got {peek()}')
    
    def parse_parenthesized() -> ast.Expression:
        consume('(')
        # Recursively call the top level parsing function
        # to parse whatever is inside the parentheses.
        expr = parse_expression()
        consume(')')
        return expr  
    
    def parse_if() -> ast.Expression:
        consume('if')
        condition = parse_expression()
        consume('then')
        then_branch = parse_expression()

        if peek().text == 'else':
            consume('else')
            else_branch = parse_expression()
        else:   else_branch = None
        return ast.IfExpression(condition=condition, then_branch=then_branch, else_branch=else_branch)
    def parse_calculation() -> ast.Expression:
        # Parse the first term.
        left = parse_term()
        # While there are more `+` or '-'...
        while peek().text in ['+', '-']:
            # Move past the '+' or '-'.
            operator_token = consume()
            operator = operator_token.text

            # Parse the operator on the right.
            right = parse_term()

            # Combine it with the stuff we've accumulated on the left so far.
            left = ast.BinaryOp(
                left,
                operator,
                right
            )
        
        return left

    def parse_unary()-> ast.Expression:
        operation = peek().text
        consume()
        if peek().text in ['not','-']:
            right = parse_unary()
        else:
            right = parse_expression()
        return ast.UnaryOp(operation=operation, right=right)


    # This is our main parsing function for this example.
    # To parse "integer + integer" expressions,
    # it uses `parse_int_literal` to parse the first integer,
    # then it checks that there's a supported operator,
    # and finally it uses `parse_int_literal` to parse the
    # second integer.
    def parse_expression() -> ast.Expression:

        left = parse_calculation()
        
        if peek().text == '=':
            consume('=')
            operation = '='
            right = parse_expression()
            return ast.BinaryOp(left=left, operation=operation, right=right)
        
        while peek().text in ['==', '!=', '<','<=', '>', '>=','%']:
            operation_token = consume()
            right = parse_calculation()
            left = ast.BinaryOp(left=left, operation=operation_token.text, right=right)
        while peek().text in ['or', 'and']:
            operation_token = consume(peek().text)
            right=parse_expression()
            left = ast.BinaryOp(left=left, operation=operation_token.text, right=right)
        return left
    

    return parse_expression()


# def test_parser_or() -> None:
#     assert parse(tokenize('if 1 or 2 then 3')) == ast.IfExpression(
#         condition=ast.BinaryOp(
#             left=ast.Literal(1),
#             operation='and',
#             right=ast.Literal(2)
#         ),
#         then_branch=ast.Literal(3),
#         else_branch=None
#     )
# test_parser_or()