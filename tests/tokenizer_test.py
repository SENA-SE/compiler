from compiler.tokenizer import Token, tokenize


def test_tokenizer() -> None:
    assert tokenize("hello") == [
        Token(type="identifier", text="hello")
    ]

def test_tokenizer_whitespace() -> None:
    assert tokenize("   \n  whitespaces\n\n\n  ") == [
        Token(type="identifier", text="whitespaces")
    ]

def test_tokenizer_integer() -> None:
    assert tokenize(" hello this is number 1 ") == [
        Token(type="identifier", text="hello"),
        Token(type="identifier", text="this"),
        Token(type="identifier", text="is"),
        Token(type="identifier", text="number"),
        Token(type="int_literal", text="1")
    ]

def test_tokenizer_operator() -> None:
    assert tokenize("3 + -5") == [
        Token(type="int_literal", text="3"),
        Token(type="operator", text="+"),
        Token(type="operator", text="-"),
        Token(type="int_literal", text="5")
    ]

def test_tokenizer_parenthesis() -> None:
    assert tokenize("(3 + 6) * 2") == [
        Token(type="parenthesis", text="("),
        Token(type="int_literal", text="3"),
        Token(type="operator", text="+"),
        Token(type="int_literal", text="6"),
        Token(type="parenthesis", text=")"),
        Token(type="operator", text="*"),
        Token(type="int_literal", text="2")
    ]


def test_tokenizer_punctuation() -> None:
    assert tokenize("if a>=b then int n=1;") == [


        Token(type="keyword", text="if"),
        Token(type="identifier", text="a"),
        Token(type="operator", text=">="),
        Token(type="identifier", text="b"),
        Token(type="keyword", text="then"),
        Token(type="identifier", text="int"),
        Token(type="identifier", text="n"),
        Token(type="operator", text="="),
        Token(type="int_literal", text="1"),
        Token(type="punctuation", text=";")
    ]


def test_tokenizer_comments() -> None:
    # Single-line comments

    assert tokenize("int x = 10; // This is a single-line comment\ny = x + 1;") == [
        Token(type="identifier", text="int"),
        Token(type="identifier", text="x"),
        Token(type="operator", text="="),
        Token(type="int_literal", text="10"),
        Token(type="punctuation", text=";"),
        Token(type="identifier", text="y"),
        Token(type="operator", text="="),
        Token(type="identifier", text="x"),
        Token(type="operator", text="+"),
        Token(type="int_literal", text="1"),
        Token(type="punctuation", text=";")
    ]

    # Multi-line comments
    source_code_multi_line = """
    /* This is a 
       multi-line comment */
    int z = 5;
    /* Another
       multi-line
       comment */
    """
    assert tokenize(source_code_multi_line) == [
        Token(type="identifier", text="int"),
        Token(type="identifier", text="z"),
        Token(type="operator", text="="),
        Token(type="int_literal", text="5"),
        Token(type="punctuation", text=";")
    ]

    # Combined single and multi-line comments
    source_code_combined = """
    // Single-line comment here
    int a = 5; /* Multi-line
    comment */
    // Another single-line
    """
    assert tokenize(source_code_combined) == [
        Token(type="identifier", text="int"),
        Token(type="identifier", text="a"),
        Token(type="operator", text="="),
        Token(type="int_literal", text="5"),
        Token(type="punctuation", text=";")
    ]

