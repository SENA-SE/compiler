from dataclasses import dataclass
import re
from typing import List, Pattern, Literal, Tuple

TokenType = Literal["int_literal", "identifier", "operator", "parenthesis", "punctuation", "end"]

@dataclass(frozen=True)
class Location:
    line: int
    pos: int

    def __str__(self) -> str:
        return f'Location: Line {self.line}, at position {self.pos}'
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Location):
            return True
        return False
@dataclass(frozen=True)
class Token:
    type: TokenType
    text: str
    location: Location = None


def tokenize(source_code: str) -> List[Token]:
    token_patterns = [
        ('single_line_comment', r'\/\/[^\n]*|#.*'),
        ('multi_line_comment', r'\/\*[\s\S]*?\*\/'),
        ('keyword', r'\b(if|then|else|break|continue)\b'), 
        ('identifier', r'[a-zA-Z_][a-zA-Z0-9_]*'),
        ('int_literal', r'\b\d+\b'),
        ('operator', r'==|!=|<=|>=|\+=|\-=|[+\-*/=><%&]'),
        ('parenthesis', r'[(){}]'),
        ('punctuation', r'[;,:]'),
        ('line', r'\n'),
        ('whitespace', r'\s+'),

    ]

    compiled_patterns: List[Tuple[str, Pattern]] = [(name, re.compile(pattern)) for name, pattern in token_patterns]

    result: List[Token] = []
    position = 0
    line_counter = 1
    line_pos_counter = 1

    while position < len(source_code):
        for token_type, regex in compiled_patterns:
            match = regex.match(source_code, position)
            if match:
                if token_type == 'line':
                    line_counter += 1
                    line_pos_counter = 1
                    
                if token_type not in ['whitespace', 'single_line_comment', 'multi_line_comment','line']:
                    result.append(Token(type=token_type, text=match.group(), location=Location(line=line_counter, pos=line_pos_counter)))
                    line_pos_counter += match.end() - match.start()
                position += match.end() - match.start()
                break
        else:
            raise Exception(f"Tokenization failed near '{source_code[position:position+10]}'...")
    
    return result

