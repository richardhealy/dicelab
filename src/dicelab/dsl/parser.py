"""Recursive-descent parser: tokens -> typed AST."""

from __future__ import annotations

from dicelab.dsl.ast import (
    Advantage,
    AdvKind,
    BinOp,
    Constant,
    DiceTerm,
    Drop,
    Explode,
    Keep,
    Modifier,
    Node,
    Reroll,
    SuccessPool,
    UnaryOp,
)
from dicelab.dsl.lexer import tokenize
from dicelab.dsl.tokens import Token, TokenType

_KEEP_DROP = {TokenType.KH, TokenType.KL, TokenType.DH, TokenType.DL}


class ParseError(ValueError):
    """Raised on malformed dice notation."""


class _Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self._tokens = tokens
        self._i = 0

    @property
    def _cur(self) -> Token:
        return self._tokens[self._i]

    def _eat(self, ttype: TokenType) -> Token:
        tok = self._cur
        if tok.type is not ttype:
            raise ParseError(f"Expected {ttype.name} at position {tok.pos}, got {tok.type.name}")
        self._i += 1
        return tok

    def _accept(self, ttype: TokenType) -> Token | None:
        if self._cur.type is ttype:
            tok = self._cur
            self._i += 1
            return tok
        return None

    def parse(self) -> Node:
        node = self._expr()
        # adv/dis are handled only as a trailing modifier; for a single-die
        # expression this also covers the postfix form (e.g. "1d20adv").
        if self._cur.type is TokenType.ADV:
            self._i += 1
            node = _apply_trailing_advantage(node, "adv")
        elif self._cur.type is TokenType.DIS:
            self._i += 1
            node = _apply_trailing_advantage(node, "dis")
        if self._cur.type is not TokenType.EOF:
            raise ParseError(f"Unexpected {self._cur.type.name} at position {self._cur.pos}")
        return node

    def _expr(self) -> Node:
        node = self._term()
        while self._cur.type in (TokenType.PLUS, TokenType.MINUS):
            if self._cur.type is TokenType.PLUS:
                self._i += 1
                node = BinOp("+", node, self._term())
            else:
                self._i += 1
                node = BinOp("-", node, self._term())
        return node

    def _term(self) -> Node:
        node = self._factor()
        while self._cur.type is TokenType.STAR:
            self._eat(TokenType.STAR)
            node = BinOp("*", node, self._factor())
        return node

    def _factor(self) -> Node:
        if self._accept(TokenType.MINUS) is not None:
            return UnaryOp("-", self._factor())
        return self._atom()

    def _atom(self) -> Node:
        if self._accept(TokenType.LPAREN) is not None:
            inner = self._expr()
            self._eat(TokenType.RPAREN)
            return inner
        if self._cur.type is TokenType.D:
            return self._dice(count=1)
        num = self._eat(TokenType.NUMBER)
        following = self._cur
        if following.type is TokenType.D:
            return self._dice(count=int(num.value))
        return Constant(int(num.value))

    def _dice(self, count: int) -> DiceTerm:
        self._eat(TokenType.D)
        sides = int(self._eat(TokenType.NUMBER).value)
        modifiers = self._modifiers()
        _validate_modifiers(modifiers)
        return DiceTerm(count, sides, modifiers)

    def _modifiers(self) -> list[Modifier]:
        mods: list[Modifier] = []
        while True:
            tok = self._cur
            if tok.type in _KEEP_DROP:
                self._i += 1
                if self._cur.type is TokenType.NUMBER:
                    k = int(self._cur.value)
                    self._i += 1
                else:
                    k = 1
                if tok.type is TokenType.KH:
                    mods.append(Keep("h", k))
                elif tok.type is TokenType.KL:
                    mods.append(Keep("l", k))
                elif tok.type is TokenType.DH:
                    mods.append(Drop("h", k))
                else:
                    mods.append(Drop("l", k))
            elif tok.type is TokenType.BANG:
                self._i += 1
                mods.append(Explode())
            elif tok.type is TokenType.R:
                self._i += 1
                mods.append(Reroll(int(self._eat(TokenType.NUMBER).value)))
            elif tok.type is TokenType.GE:
                self._i += 1
                mods.append(SuccessPool(">=", int(self._eat(TokenType.NUMBER).value)))
            elif tok.type is TokenType.LE:
                self._i += 1
                mods.append(SuccessPool("<=", int(self._eat(TokenType.NUMBER).value)))
            else:
                return mods


def _validate_modifiers(mods: list[Modifier]) -> None:
    has_pool = any(isinstance(m, SuccessPool) for m in mods)
    has_keepdrop = any(isinstance(m, (Keep, Drop)) for m in mods)
    if has_pool and has_keepdrop:
        raise ParseError("Success pools (>=, <=) cannot be combined with keep/drop")


def _count_dice_terms(node: Node) -> int:
    match node:
        case DiceTerm():
            return 1
        case BinOp(_, left, right):
            return _count_dice_terms(left) + _count_dice_terms(right)
        case UnaryOp(_, operand):
            return _count_dice_terms(operand)
        case Constant():
            return 0


def _apply_trailing_advantage(node: Node, kind: AdvKind) -> Node:
    if _count_dice_terms(node) != 1:
        raise ParseError("Trailing 'adv'/'dis' requires exactly one dice term")
    return _attach_advantage(node, kind)


def _attach_advantage(node: Node, kind: AdvKind) -> Node:
    match node:
        case DiceTerm(count, sides, modifiers):
            return DiceTerm(count, sides, [*modifiers, Advantage(kind)])
        case BinOp(op, left, right):
            if _count_dice_terms(left) == 1:
                return BinOp(op, _attach_advantage(left, kind), right)
            return BinOp(op, left, _attach_advantage(right, kind))
        case UnaryOp(op, operand):
            return UnaryOp(op, _attach_advantage(operand, kind))
        case Constant():
            raise ParseError("Trailing 'adv'/'dis' requires exactly one dice term")


def parse(text: str) -> Node:
    return _Parser(tokenize(text)).parse()
