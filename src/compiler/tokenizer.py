from dataclasses import dataclass
import re
from typing import List, Pattern, Literal, Tuple

TokenType = Literal["int_literal", "identifier", "operator", "parenthesis", "punctuation", "end"]

@dataclass(frozen=True)
class Token:
    type: TokenType
    text: str

def tokenize(source_code: str) -> List[Token]:
    token_patterns = [
        ('whitespace', r'\s+'),
        ('single_line_comment', r'\/\/[^\n]*|#.*'),
        ('multi_line_comment', r'\/\*[\s\S]*?\*\/'),
        ('keyword', r'\b(if|then|else)\b'), 
        ('identifier', r'[a-zA-Z_][a-zA-Z0-9_]*'),
        ('int_literal', r'\b\d+\b'),
        ('operator', r'==|!=|<=|>=|\+=|\-=|[+\-*/=><%]'),
        ('parenthesis', r'[(){}]'),
        ('punctuation', r'[;,:]')
    ]

    compiled_patterns: List[Tuple[str, Pattern]] = [(name, re.compile(pattern)) for name, pattern in token_patterns]

    result: List[Token] = []
    position = 0

    while position < len(source_code):
        for token_type, regex in compiled_patterns:
            match = regex.match(source_code, position)
            if match:
                if token_type not in ['whitespace', 'single_line_comment', 'multi_line_comment']:
                    result.append(Token(type=token_type, text=match.group()))
                position += match.end() - match.start()
                break
        else:
            raise Exception(f"Tokenization failed near '{source_code[position:position+10]}'...")
    
    return result