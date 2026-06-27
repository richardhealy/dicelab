"""Typed AST for the dice DSL."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

KeepWhich = Literal["h", "l"]
Compare = Literal[">=", "<="]
AdvKind = Literal["adv", "dis"]


@dataclass(frozen=True)
class Keep:
    which: KeepWhich
    k: int = 1


@dataclass(frozen=True)
class Drop:
    which: KeepWhich
    k: int = 1


@dataclass(frozen=True)
class Explode:
    pass


@dataclass(frozen=True)
class Reroll:
    value: int


@dataclass(frozen=True)
class SuccessPool:
    compare: Compare
    threshold: int


@dataclass(frozen=True)
class Advantage:
    kind: AdvKind


Modifier = Keep | Drop | Explode | Reroll | SuccessPool | Advantage


@dataclass(frozen=True)
class Constant:
    value: int


@dataclass(frozen=True)
class DiceTerm:
    count: int
    sides: int
    modifiers: list[Modifier] = field(default_factory=list)


@dataclass(frozen=True)
class BinOp:
    op: Literal["+", "-", "*"]
    left: Node
    right: Node


@dataclass(frozen=True)
class UnaryOp:
    op: Literal["-"]
    operand: Node


Node = Constant | DiceTerm | BinOp | UnaryOp


def _unparse_modifier(m: Modifier) -> str:
    match m:
        case Keep(which, k):
            return f"k{which}{k}"
        case Drop(which, k):
            return f"d{which}{k}"
        case Explode():
            return "!"
        case Reroll(value):
            return f"r{value}"
        case SuccessPool(compare, threshold):
            return f"{compare}{threshold}"
        case Advantage(kind):
            return kind


def unparse(node: Node) -> str:
    match node:
        case Constant(value):
            return str(value)
        case DiceTerm(count, sides, modifiers):
            mods = "".join(_unparse_modifier(m) for m in modifiers)
            return f"{count}d{sides}{mods}"
        case BinOp(op, left, right):
            return f"{unparse(left)} {op} {unparse(right)}"
        case UnaryOp(op, operand):
            return f"{op}{unparse(operand)}"


def _modifier_to_dict(m: Modifier) -> dict[str, Any]:
    match m:
        case Keep(which, k):
            return {"type": "keep", "which": which, "k": k}
        case Drop(which, k):
            return {"type": "drop", "which": which, "k": k}
        case Explode():
            return {"type": "explode"}
        case Reroll(value):
            return {"type": "reroll", "value": value}
        case SuccessPool(compare, threshold):
            return {"type": "pool", "compare": compare, "threshold": threshold}
        case Advantage(kind):
            return {"type": "advantage", "kind": kind}


def ast_to_dict(node: Node) -> dict[str, Any]:
    match node:
        case Constant(value):
            return {"type": "constant", "value": value}
        case DiceTerm(count, sides, modifiers):
            return {
                "type": "dice",
                "count": count,
                "sides": sides,
                "modifiers": [_modifier_to_dict(m) for m in modifiers],
            }
        case BinOp(op, left, right):
            return {
                "type": "binop",
                "op": op,
                "left": ast_to_dict(left),
                "right": ast_to_dict(right),
            }
        case UnaryOp(op, operand):
            return {"type": "unaryop", "op": op, "operand": ast_to_dict(operand)}
