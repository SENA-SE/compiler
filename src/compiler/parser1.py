from compiler import ast
from compiler.tokenizer import Token


def parse(tokens: list[Token]) -> ast.Expression:
    position = 0

    def peek() -> Token:
        if position < len(tokens):
            return tokens[position]
        else:
            return Token(type='end', text='')

    def consume() -> Token:
        token = peek()
        nonlocal position
        position += 1
        return token
    
    def parse_literal() -> ast.Literal:
        token = peek()
        if token.type == 'int_literal':
            consume()
            return ast.Literal(int(token.text))
        else:
            raise Exception(f'Expected literal, but found "{token.text}')
    
    def parse_expression() -> ast.Expression:
        left = parse_literal()
        operation_token = consume()
        if operation_token.text not in ['+','-','*','/']:
            raise Exception(f'Expected operator, got "{operation_token.text}"')
        right = parse_literal()
        return ast.BinaryOperation(left=left, operation=operation_token.text, right=right)

    return parse_expression()


