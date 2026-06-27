"""Token types for the dice DSL."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    NUMBER = auto()
    D = auto()
    KH = auto()
    KL = auto()
    DH = auto()
    DL = auto()
    BANG = auto()
    R = auto()
    GE = auto()
    LE = auto()
    ADV = auto()
    DIS = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    LPAREN = auto()
    RPAREN = auto()
    EOF = auto()


@dataclass(frozen=True)
class Token:
    type: TokenType
    value: str
    pos: int
