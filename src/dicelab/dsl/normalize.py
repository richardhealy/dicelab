"""Desugar advantage/disadvantage into keep-highest/lowest of two dice."""

from __future__ import annotations

from dicelab.dsl.ast import (
    Advantage,
    BinOp,
    Constant,
    DiceTerm,
    Keep,
    Modifier,
    Node,
    UnaryOp,
)


def normalize(node: Node) -> Node:
    match node:
        case Constant():
            return node
        case DiceTerm(count, sides, modifiers):
            return _normalize_dice(count, sides, modifiers)
        case BinOp(op, left, right):
            return BinOp(op, normalize(left), normalize(right))
        case UnaryOp(op, operand):
            return UnaryOp(op, normalize(operand))


def _normalize_dice(count: int, sides: int, modifiers: list[Modifier]) -> DiceTerm:
    out: list[Modifier] = []
    new_count = count
    for mod in modifiers:
        if isinstance(mod, Advantage):
            if count != 1:
                raise ValueError("adv/dis only applies to a single die (count must be 1)")
            new_count = 2
            out.insert(0, Keep("h", 1) if mod.kind == "adv" else Keep("l", 1))
        else:
            out.append(mod)
    return DiceTerm(new_count, sides, out)
