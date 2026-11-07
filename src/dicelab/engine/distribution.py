"""Exact probability distributions over integer outcomes (NumPy-backed)."""

from __future__ import annotations

import operator
from collections import Counter
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from itertools import combinations_with_replacement
from math import comb, factorial, prod
from typing import Literal

import numpy as np
import numpy.typing as npt

from dicelab.constants import DEFAULT_PERCENTILES, EXPLODE_EPSILON
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
from dicelab.engine.keepdrop import kept_indices
from dicelab.engine.result import (
    DistributionResult,
    SuccessLadder,
    SystemRules,
    derive_outcome,
)

_KEEPDROP_COMBO_CAP = 200_000


@dataclass(frozen=True)
class Distribution:
    offset: int
    probs: npt.NDArray[np.float64]

    @classmethod
    def constant(cls, value: int) -> Distribution:
        return cls(value, np.array([1.0], dtype=np.float64))

    @classmethod
    def uniform_die(cls, sides: int) -> Distribution:
        if sides < 1:
            raise ValueError("dice must have >= 1 side")
        return cls(1, np.full(sides, 1.0 / sides, dtype=np.float64))

    @classmethod
    def from_pairs(cls, pairs: dict[int, float]) -> Distribution:
        if not pairs:
            raise ValueError("empty distribution")
        lo, hi = min(pairs), max(pairs)
        probs = np.zeros(hi - lo + 1, dtype=np.float64)
        for outcome, prob in pairs.items():
            probs[outcome - lo] += prob
        return cls(lo, probs).normalized()

    def normalized(self) -> Distribution:
        total = float(self.probs.sum())
        if total <= 0:
            raise ValueError("distribution has no probability mass")
        return Distribution(self.offset, self.probs / total)

    def outcomes(self) -> range:
        return range(self.offset, self.offset + len(self.probs))

    def items(self) -> Iterator[tuple[int, float]]:
        for outcome, prob in zip(self.outcomes(), self.probs, strict=True):
            if prob > 0.0:
                yield outcome, float(prob)

    def mean(self) -> float:
        return float(np.dot(np.asarray(self.outcomes(), dtype=np.float64), self.probs))

    def variance(self) -> float:
        xs = np.asarray(self.outcomes(), dtype=np.float64)
        mean = float(np.dot(xs, self.probs))
        return float(np.dot((xs - mean) ** 2, self.probs))

    def stddev(self) -> float:
        return float(np.sqrt(self.variance()))

    def cdf(self) -> dict[int, float]:
        cumulative = np.cumsum(self.probs)
        return {outcome: float(c) for outcome, c in zip(self.outcomes(), cumulative, strict=True)}

    def percentile(self, p: int) -> int:
        target = p / 100.0
        cumulative = np.cumsum(self.probs)
        idx = int(np.searchsorted(cumulative, target, side="left"))
        idx = min(idx, len(self.probs) - 1)
        return self.offset + idx

    def convolve(self, other: Distribution) -> Distribution:
        probs = np.convolve(self.probs, other.probs)
        return Distribution(self.offset + other.offset, probs)

    def negate(self) -> Distribution:
        return Distribution(-(self.offset + len(self.probs) - 1), self.probs[::-1].copy())

    def combine(self, other: Distribution, op: Callable[[int, int], int]) -> Distribution:
        pairs: dict[int, float] = {}
        for oa, pa in self.items():
            for ob, pb in other.items():
                key = op(oa, ob)
                pairs[key] = pairs.get(key, 0.0) + pa * pb
        return Distribution.from_pairs(pairs)


class _Intractable(Exception):
    """Raised when exact enumeration would be too large; triggers sampling."""


def _single_die_pmf(sides: int, reroll: set[int], explode: bool) -> dict[int, float]:
    base = {face: 1.0 / sides for face in range(1, sides + 1)}
    if reroll:
        reroll_mass = sum(base[f] for f in range(1, sides + 1) if f in reroll)
        base = {
            face: (0.0 if face in reroll else base[face]) + reroll_mass * (1.0 / sides)
            for face in range(1, sides + 1)
        }
    if explode and sides >= 2:
        base = _explode_pmf(base, sides)
    return base


def _explode_pmf(face_pmf: dict[int, float], sides: int) -> dict[int, float]:
    p_max = face_pmf[sides]
    pmf: dict[int, float] = {}
    carry = 1.0
    accumulated = 0
    while carry >= EXPLODE_EPSILON:
        for face, prob in face_pmf.items():
            if face != sides:
                pmf[accumulated + face] = pmf.get(accumulated + face, 0.0) + carry * prob
        accumulated += sides
        carry *= p_max
        if p_max == 0.0:
            break
    pmf[accumulated] = pmf.get(accumulated, 0.0) + carry
    return pmf


def _pool_hit(face: int, pool: SuccessPool) -> bool:
    return face >= pool.threshold if pool.compare == ">=" else face <= pool.threshold


def _term_distribution(term: DiceTerm) -> Distribution:
    reroll = {m.value for m in term.modifiers if isinstance(m, Reroll)}
    explode = any(isinstance(m, Explode) for m in term.modifiers)
    face_pmf = _single_die_pmf(term.sides, reroll, explode)

    pool = next((m for m in term.modifiers if isinstance(m, SuccessPool)), None)
    if pool is not None:
        p = sum(prob for face, prob in face_pmf.items() if _pool_hit(face, pool))
        n = term.count
        pairs = {k: comb(n, k) * (p**k) * ((1 - p) ** (n - k)) for k in range(n + 1)}
        return Distribution.from_pairs(pairs)

    if any(isinstance(m, (Keep, Drop)) for m in term.modifiers):
        return _keep_drop_distribution(term, face_pmf)

    single = Distribution.from_pairs(face_pmf)
    result = single
    for _ in range(term.count - 1):
        result = result.convolve(single)
    return result


def _keep_drop_distribution(term: DiceTerm, face_pmf: dict[int, float]) -> Distribution:
    faces = sorted(face_pmf)
    support = len(faces)
    if comb(term.count + support - 1, term.count) > _KEEPDROP_COMBO_CAP:
        raise _Intractable
    pairs: dict[int, float] = {}
    fact_n = factorial(term.count)
    for combo in combinations_with_replacement(faces, term.count):
        counts = Counter(combo)
        multiplicity = fact_n
        for c in counts.values():
            multiplicity //= factorial(c)
        prob = multiplicity * prod(face_pmf[f] ** c for f, c in counts.items())
        kept_sum = sum(combo[i] for i in kept_indices(combo, term.modifiers))
        pairs[kept_sum] = pairs.get(kept_sum, 0.0) + prob
    return Distribution.from_pairs(pairs)


def _dist(node: Node) -> Distribution:
    match node:
        case Constant(value):
            return Distribution.constant(value)
        case DiceTerm():
            return _term_distribution(node)
        case UnaryOp(_, operand):
            return _dist(operand).negate()
        case BinOp(op, left, right):
            ld = _dist(left)
            rd = _dist(right)
            if op == "+":
                return ld.convolve(rd)
            if op == "-":
                return ld.convolve(rd.negate())
            return ld.combine(rd, operator.mul)


def _sample(node: Node, samples: int, seed: int) -> Distribution:
    from dicelab.engine.roll import roll

    counts: dict[int, float] = {}
    for i in range(samples):
        total = roll(node, seed=seed + i).total
        counts[total] = counts.get(total, 0.0) + 1.0
    return Distribution.from_pairs(counts)


def _outcome_probabilities(
    dist: Distribution, ladder: SuccessLadder | None
) -> dict[str, float] | None:
    if ladder is None:
        return None
    buckets: dict[str, float] = {}
    for outcome, prob in dist.items():
        label = derive_outcome(outcome, ladder)
        if label is not None:
            buckets[label] = buckets.get(label, 0.0) + prob
    return buckets


def distribute(
    node: Node,
    ladder: SuccessLadder | None = None,
    percentiles: tuple[int, ...] = DEFAULT_PERCENTILES,
    samples: int = 100_000,
    seed: int = 0,
) -> DistributionResult:
    normalized = normalize(node)
    method: Literal["exact", "sampled"]
    try:
        dist = _dist(normalized).normalized()
        method = "exact"
    except _Intractable:
        dist = _sample(normalized, samples, seed)
        method = "sampled"
    return DistributionResult(
        expression=unparse(node),
        method=method,
        mean=dist.mean(),
        variance=dist.variance(),
        stddev=dist.stddev(),
        pmf=dict(dist.items()),
        cdf=dist.cdf(),
        percentiles={p: dist.percentile(p) for p in percentiles},
        outcome_probabilities=_outcome_probabilities(dist, ladder),
        system_rules=SystemRules(success_ladder=ladder),
    )
