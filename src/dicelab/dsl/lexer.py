"""Regex-based tokenizer. Longer/keyword patterns precede 'd'/'r'."""

from __future__ import annotations

import re

from dicelab.dsl.tokens import Token, TokenType

_SPEC: list[tuple[TokenType | None, str]] = [
    (None, r"\s+"),
    (TokenType.NUMBER, r"\d+"),
    (TokenType.GE, r">="),
    (TokenType.LE, r"<="),
    (TokenType.ADV, r"adv"),
    (TokenType.DIS, r"dis"),
    (TokenType.KH, r"kh"),
    (TokenType.KL, r"kl"),
    (TokenType.DH, r"dh"),
    (TokenType.DL, r"dl"),
    (TokenType.D, r"d"),
    (TokenType.R, r"r"),
    (TokenType.BANG, r"!"),
    (TokenType.PLUS, r"\+"),
    (TokenType.MINUS, r"-"),
    (TokenType.STAR, r"\*"),
    (TokenType.LPAREN, r"\("),
    (TokenType.RPAREN, r"\)"),
]
_MASTER = re.compile("|".join(f"(?P<G{i}>{pat})" for i, (_, pat) in enumerate(_SPEC)))


class LexError(ValueError):
    """Raised on an unrecognized character."""


def tokenize(text: str) -> list[Token]:
    tokens: list[Token] = []
    pos = 0
    while pos < len(text):
        match = _MASTER.match(text, pos)
        if match is None:
            raise LexError(f"Unexpected character {text[pos]!r} at position {pos}")
        idx = match.lastgroup
        assert idx is not None
        tok_type = _SPEC[int(idx[1:])][0]
        value = match.group()
        if tok_type is not None:
            tokens.append(Token(tok_type, value, pos))
        pos = match.end()
    tokens.append(Token(TokenType.EOF, "", pos))
    return tokens
