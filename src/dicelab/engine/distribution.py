"""Exact probability distributions over integer outcomes (NumPy-backed)."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass

import numpy as np
import numpy.typing as npt


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
