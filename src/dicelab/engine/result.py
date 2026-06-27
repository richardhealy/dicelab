"""Serializable result models (camelCase JSON) and outcome derivation."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

Compare3 = Literal[">=", "<=", "=="]


class _CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class LadderRung(_CamelModel):
    compare: Compare3
    threshold: int
    outcome: str


class SuccessLadder(_CamelModel):
    rungs: list[LadderRung]
    default: str | None = None


class SystemRules(_CamelModel):
    success_ladder: SuccessLadder | None = None


class DiceTermResult(_CamelModel):
    notation: str
    faces: list[int]
    kept: list[int]
    dropped: list[int]
    value: int


class RollResult(_CamelModel):
    expression: str
    total: int
    kept_rolls: list[int]
    dropped_rolls: list[int]
    rolls: list[DiceTermResult]
    seed: int | None
    outcome: str | None
    system_rules: SystemRules


class DistributionResult(_CamelModel):
    expression: str
    method: Literal["exact", "sampled"]
    mean: float
    variance: float
    stddev: float
    pmf: dict[int, float]
    cdf: dict[int, float]
    percentiles: dict[int, int]
    outcome_probabilities: dict[str, float] | None
    system_rules: SystemRules


def _matches(score: int, rung: LadderRung) -> bool:
    if rung.compare == ">=":
        return score >= rung.threshold
    if rung.compare == "<=":
        return score <= rung.threshold
    return score == rung.threshold


def derive_outcome(score: int, ladder: SuccessLadder | None) -> str | None:
    if ladder is None:
        return None
    for rung in ladder.rungs:
        if _matches(score, rung):
            return rung.outcome
    return ladder.default
