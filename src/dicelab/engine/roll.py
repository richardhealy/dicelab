"""Seeded roll evaluator over the normalized AST."""

from __future__ import annotations

import random

from dicelab.constants import MAX_EXPLODE_DEPTH
from dicelab.dsl.ast import (
    BinOp,
    Constant,
    DiceTerm,
    Drop,
    Explode,
    Keep,
    Node,
    Reroll,
    SuccessPool,
    UnaryOp,
    unparse,
)
from dicelab.dsl.normalize import normalize
from dicelab.engine.result import (
    DiceTermResult,
    RollResult,
    SuccessLadder,
    SystemRules,
    derive_outcome,
)


def roll(node: Node, seed: int | None = None, ladder: SuccessLadder | None = None) -> RollResult:
    rng = random.Random(seed)
    normalized = normalize(node)
    term_results: list[DiceTermResult] = []
    total = _eval(normalized, rng, term_results)
    kept = [f for r in term_results for f in r.kept]
    dropped = [f for r in term_results for f in r.dropped]
    return RollResult(
        expression=unparse(node),
        total=total,
        kept_rolls=kept,
        dropped_rolls=dropped,
        rolls=term_results,
        seed=seed,
        outcome=derive_outcome(total, ladder),
        system_rules=SystemRules(success_ladder=ladder),
    )


def _eval(node: Node, rng: random.Random, sink: list[DiceTermResult]) -> int:
    match node:
        case Constant(value):
            return value
        case DiceTerm():
            result = _roll_term(node, rng)
            sink.append(result)
            return result.value
        case UnaryOp(_, operand):
            return -_eval(operand, rng, sink)
        case BinOp(op, left, right):
            lhs = _eval(left, rng, sink)
            rhs = _eval(right, rng, sink)
            if op == "+":
                return lhs + rhs
            if op == "-":
                return lhs - rhs
            return lhs * rhs


def _roll_one_die(rng: random.Random, sides: int, reroll: set[int], explode: bool) -> int:
    face = rng.randint(1, sides)
    if face in reroll:
        face = rng.randint(1, sides)
    value = face
    if explode and sides >= 2:
        depth = 0
        while face == sides and depth < MAX_EXPLODE_DEPTH:
            face = rng.randint(1, sides)
            value += face
            depth += 1
    return value


def _roll_term(term: DiceTerm, rng: random.Random) -> DiceTermResult:
    reroll = {m.value for m in term.modifiers if isinstance(m, Reroll)}
    explode = any(isinstance(m, Explode) for m in term.modifiers)
    faces = [_roll_one_die(rng, term.sides, reroll, explode) for _ in range(term.count)]

    pool = next((m for m in term.modifiers if isinstance(m, SuccessPool)), None)
    if pool is not None:
        successes = [f for f in faces if _pool_hit(f, pool)]
        failures = [f for f in faces if not _pool_hit(f, pool)]
        return DiceTermResult(
            notation=unparse(term),
            faces=faces,
            kept=successes,
            dropped=failures,
            value=len(successes),
        )

    kept, dropped = _apply_keep_drop(faces, term)
    return DiceTermResult(
        notation=unparse(term), faces=faces, kept=kept, dropped=dropped, value=sum(kept)
    )


def _pool_hit(face: int, pool: SuccessPool) -> bool:
    return face >= pool.threshold if pool.compare == ">=" else face <= pool.threshold


def _apply_keep_drop(faces: list[int], term: DiceTerm) -> tuple[list[int], list[int]]:
    order = sorted(range(len(faces)), key=lambda i: faces[i])  # indices ascending by value
    keep_idx = set(range(len(faces)))
    for mod in term.modifiers:
        if isinstance(mod, Keep):
            chosen = order[-mod.k :] if mod.which == "h" else order[: mod.k]
            keep_idx &= set(chosen)
        elif isinstance(mod, Drop):
            chosen = order[-mod.k :] if mod.which == "h" else order[: mod.k]
            keep_idx -= set(chosen)
    kept = [faces[i] for i in range(len(faces)) if i in keep_idx]
    dropped = [faces[i] for i in range(len(faces)) if i not in keep_idx]
    return kept, dropped
