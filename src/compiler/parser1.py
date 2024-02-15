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
        if token.text == 'true':
            consume(token.text)
            return ast.Literal(True)
        if token.text == 'false':
            consume(token.text)
            return ast.Literal(False)
        if peek().type != 'identifier':
            raise Exception(f' expected an identifier')
        else:
            consume()
            next_token = peek()

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
        elif peek().text == 'while':
            return parse_while()
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
    
    def parse_while() -> ast.Expression:
        consume('while')
        condition = parse_expression()
        consume('do')
        body = parse_expression()
        return ast.WhileExpression(condition=condition,do=body)
    
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

    def parse_block()-> ast.Expression:
        consume('{')
        expressions = parse_multiple_expressions()
        block = ast.Block(expressions)
        consume('}')
        return block
    def parse_variable_declaration()-> ast.Expression:
        consume('var')
        if peek().type == 'identifier':
            name = peek().text
            consume()
            consume('=')
            initializer = parse_expression()

            return ast.VariableDeclaration(name=name, assignment=initializer)
        else:
            raise Exception(f'Expected an identifier')
    def parse_multiple_expressions() -> list[ast.Expression]:
        expressions: list[ast.Expression] = []
        result: ast.Expression = ast.Literal(None)

        while peek().type != 'end' and peek().text!='}':
            if peek().text == ';':
                consume(';')# This handles empty statements (just a semicolon)
                continue
            if peek().text == '{':
                block = parse_block()
                if peek().text == ';':
                    consume(';')
                    expressions.append(block)
                elif peek().type != 'end' and peek().text!='}':
                    expressions.append(block)
                else:
                    result = block
                    break
            else:
                if peek().text == 'var':
                    expression = parse_variable_declaration()
                else:
                    expression = parse_expression()
                if peek().type != 'end' and peek().text!='}':

                    if peek().text == ';':
                        consume(';')
                    # elif peek().text != '}' and peek().type != 'end':
                    #     raise Exception(f'{pos}: Expected \';\' after expression within a block')
                    elif peek().text not in ('}', 'end') and not isinstance(expression, ast.IfExpression):
                        # If the expression is not an if-else statement, and we're not at the end or facing a closing brace, expect a semicolon.
                        raise Exception("Expected ';' after expression within a block, unless it's an if-else statement.")

                    expressions.append(expression)
                else:   
                    result = expression
                        

        expressions.append(result)
        # if peek().text != ';':
        #     raise Exception("Expected ';' after expression")
        # consume(';')
        return expressions
    # This is our main parsing function for this example.
    # To parse "integer + integer" expressions,
    # it uses `parse_int_literal` to parse the first integer,
    # then it checks that there's a supported operator,
    # and finally it uses `parse_int_literal` to parse the
    # second integer.
    def parse_expression() -> ast.Expression:

        if peek().text == '{':
            left = parse_block()
        else:
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
    
    def parse_all()-> ast.Expression:
        if peek().type == 'end':
            raise Exception('No input')
        expressions = parse_multiple_expressions()
        if pos!= len(tokens):
            raise Exception(f'Only {pos} tokens were parsed')
        
        if len(expressions) ==1: 
            return expressions[0]
        else:   
            return ast.Block(expressions)
    
    return parse_all()
    # return parse_expression()


# def test_parser_parse_variable_declaration() -> None:
#     assert parse(tokenize('var a = b')) == ast.VariableDeclaration(
#         name='a',
#         initializer=ast.Identifier('b')
#     )
# test_parser_parse_variable_declaration()