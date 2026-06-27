import pytest

from dicelab.dsl.lexer import LexError, tokenize
from dicelab.dsl.tokens import TokenType


def types(text: str) -> list[TokenType]:
    return [t.type for t in tokenize(text)]


def test_simple_dice() -> None:
    assert types("2d6") == [
        TokenType.NUMBER,
        TokenType.D,
        TokenType.NUMBER,
        TokenType.EOF,
    ]


def test_keywords_before_d() -> None:
    # 'dh', 'dl', 'dis' must not be split into D + ...
    assert types("4d6dl1") == [
        TokenType.NUMBER, TokenType.D, TokenType.NUMBER,
        TokenType.DL, TokenType.NUMBER, TokenType.EOF,
    ]
    assert types("1d20 dis") == [
        TokenType.NUMBER, TokenType.D, TokenType.NUMBER,
        TokenType.DIS, TokenType.EOF,
    ]


def test_comparisons_and_ops() -> None:
    assert types("6d10>=7") == [
        TokenType.NUMBER, TokenType.D, TokenType.NUMBER,
        TokenType.GE, TokenType.NUMBER, TokenType.EOF,
    ]
    assert types("1d6 + 2 * 3") == [
        TokenType.NUMBER, TokenType.D, TokenType.NUMBER,
        TokenType.PLUS, TokenType.NUMBER, TokenType.STAR,
        TokenType.NUMBER, TokenType.EOF,
    ]


def test_bad_char_raises() -> None:
    with pytest.raises(LexError):
        tokenize("2d6 @ 1")
