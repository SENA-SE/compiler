from dataclasses import dataclass
import re
from typing import Literal, List, Tuple

TokenType = Literal["int_literal", "identifier", "operator", "parenthesis", "punctuation", "end"]

@dataclass(frozen=True)
class Token:
    type: TokenType
    text: str

def tokenize(source_code: str) -> List[Token]:
    patterns = [
        ('whitespace', r'\s+'),
        ('identifier', r'[a-zA-Z_][a-zA-Z0-9_]*'),
        ('int_literal', r'[0-9]+'),
        ('operator', r'==|<=|>=|!=|[+\-*\/=><%]'),
        ('parenthesis', r'[(){}]'),
        ('punctuation', r'[;,]')
    ]

    result: List[Token] = []
    position = 0

    while position < len(source_code):
        for token_type, pattern in patterns:
            if token_type == 'whitespace':  
                match = re.match(pattern, source_code[position:])
                if match:
                    position += match.end()
                    break
            else:
                regex = re.compile(pattern)
                match = regex.match(source_code, position)
                if match:
                    if token_type != 'whitespace': 
                        result.append(Token(type=token_type, text=match.group()))
                    position = match.end()
                    break
        else:  
            raise Exception(f'Tokenization failed near {source_code[position:(position+10)]}')
    
    return result
