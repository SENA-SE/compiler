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


        Token(type="identifier", text="if"),
        Token(type="identifier", text="a"),
        Token(type="operator", text=">="),
        Token(type="identifier", text="b"),
        Token(type="identifier", text="then"),
        Token(type="identifier", text="int"),
        Token(type="identifier", text="n"),
        Token(type="operator", text="="),
        Token(type="int_literal", text="1"),
        Token(type="punctuation", text=";")
    ]


# def test_tokenizer_skips_comment() -> None:
#     assert tokenize("// this is comment \n int a;") == [
#         Token(type="identifier", text="int"),
#         Token(type="identifier", text="a"),
#         Token(type="punctuation", text=";")
#     ]