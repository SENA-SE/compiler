from compiler.tokenizer import Location, Token, tokenize


def test_tokenizer() -> None:
    assert tokenize("hello") == [
        Token(type="identifier", text="hello",location=Location(line=1, pos=1))
    ]

def test_tokenizer_whitespace() -> None:
    assert tokenize("   \n  whitespaces\n\n\n  ") == [
        Token(type='identifier', text='whitespaces', location=Location(line=1, pos=1))
    ]

def test_tokenizer_integer() -> None:
    assert tokenize(" hello this is number 1 ") == [
    Token(type='identifier', text='hello', location=Location(line=1, pos=1)),
    Token(type='identifier', text='this', location=Location(line=1, pos=6)),
    Token(type='identifier', text='is', location=Location(line=1, pos=10)),
    Token(type='identifier', text='number', location=Location(line=1, pos=12)),
    Token(type='int_literal', text='1', location=Location(line=1, pos=18))
    ]

def test_tokenizer_operator() -> None:
    assert tokenize("3 + -5") == [
    Token(type='int_literal', text='3', location=Location(line=1, pos=1)),
    Token(type='operator', text='+', location=Location(line=1, pos=2)),
    Token(type='operator', text='-', location=Location(line=1, pos=3)),
    Token(type='int_literal', text='5', location=Location(line=1, pos=4))
    ]

def test_tokenizer_parenthesis() -> None:
    assert tokenize("(3 + 6) * 2") == [
    Token(type='parenthesis', text='(', location=Location(line=1, pos=1)),
    Token(type='int_literal', text='3', location=Location(line=1, pos=2)),
    Token(type='operator', text='+', location=Location(line=1, pos=3)),
    Token(type='int_literal', text='6', location=Location(line=1, pos=4)),
    Token(type='parenthesis', text=')', location=Location(line=1, pos=5)),
    Token(type='operator', text='*', location=Location(line=1, pos=6)),
    Token(type='int_literal', text='2', location=Location(line=1, pos=7))
    ]


def test_tokenizer_punctuation() -> None:
    assert tokenize("if a>=b then int n=1;") == [
    Token(type='keyword', text='if', location=Location(line=1, pos=1)),
    Token(type='identifier', text='a', location=Location(line=1, pos=3)),
    Token(type='operator', text='>=', location=Location(line=1, pos=4)),
    Token(type='identifier', text='b', location=Location(line=1, pos=6)),
    Token(type='keyword', text='then', location=Location(line=1, pos=7)),
    Token(type='identifier', text='int', location=Location(line=1, pos=11)),
    Token(type='identifier', text='n', location=Location(line=1, pos=14)),
    Token(type='operator', text='=', location=Location(line=1, pos=15)),
    Token(type='int_literal', text='1', location=Location(line=1, pos=16)),
    Token(type='punctuation', text=';', location=Location(line=1, pos=17))
    ]


def test_tokenizer_comments() -> None:
    # Single-line comments

    assert tokenize("int x = 10; // This is a single-line comment\ny = x + 1;") == [Token(type='identifier', text='int', location=Location(line=1, pos=1)),
    Token(type='identifier', text='x', location=Location(line=1, pos=4)),
    Token(type='operator', text='=', location=Location(line=1, pos=5)),
    Token(type='int_literal', text='10', location=Location(line=1, pos=6)),
    Token(type='punctuation', text=';', location=Location(line=1, pos=8)),
    Token(type='identifier', text='y', location=Location(line=2, pos=1)),
    Token(type='operator', text='=', location=Location(line=2, pos=2)),
    Token(type='identifier', text='x', location=Location(line=2, pos=3)),
    Token(type='operator', text='+', location=Location(line=2, pos=4)),
    Token(type='int_literal', text='1', location=Location(line=2, pos=5)),
    Token(type='punctuation', text=';', location=Location(line=2, pos=6))]

    # Multi-line comments
    source_code_multi_line = """/* This is a 
       multi-line comment */
    int z = 5;
    /* Another
       multi-line
       comment */
    """
    assert tokenize(source_code_multi_line) == [Token(type='identifier', text='int', location=Location(line=2, pos=1)), 
     Token(type='identifier', text='z', location=Location(line=2, pos=4)), 
     Token(type='operator', text='=', location=Location(line=2, pos=5)), 
     Token(type='int_literal', text='5', location=Location(line=2, pos=6)), 
     Token(type='punctuation', text=';', location=Location(line=2, pos=7))]

    


    # Combined single and multi-line comments
    source_code_combined = """
    // Single-line comment here
    int a = 5; /* Multi-line
    comment */
    // Another single-line
    """
    assert tokenize(source_code_combined) == [Token(type='identifier', text='int', location=Location(line=3, pos=1)), 
     Token(type='identifier', text='a', location=Location(line=3, pos=4)), 
     Token(type='operator', text='=', location=Location(line=3, pos=5)), 
     Token(type='int_literal', text='5', location=Location(line=3, pos=6)), 
     Token(type='punctuation', text=';', location=Location(line=3, pos=7))]

