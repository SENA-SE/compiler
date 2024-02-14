from compiler import ast
from compiler.tokenizer import Token, tokenize

def parse(tokens: list[Token]) -> ast.Expression:
    if not tokens:
        raise ValueError("No tokens to parse.")

    position = 0
    def peek() -> Token:
        nonlocal position
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
        token = consume('int_literal')
        return ast.Literal(value=int(token.text))
    
    def parse_if_expression() -> ast.IfExpression:
        # Assuming 'if' token already consumed
        condition = parse_expression()
        consume(expected_type='keyword', expected_text='then')
        then_branch = parse_expression()

        else_branch = None
        if peek().type == 'keyword' and peek().text == 'else':
            consume(expected_type='keyword', expected_text='else')
            else_branch = parse_expression()

        return ast.IfExpression(condition=condition, then_branch=then_branch, else_branch=else_branch)


    def parse_expression() -> ast.Expression:
        if peek().type == 'keyword' and peek().text == 'if':
            return parse_if_expression()
        left = parse_literal()
        operation_token = consume('operator')
        right = parse_literal()
        
        # Task1: Ensure no garbage at the end
        if position != len(tokens):
            raise Exception("Garbage after expected end of expression")
        return ast.BinaryOperation(left=left, operation=operation_token.text, right=right)
    


    

    return parse_expression()
