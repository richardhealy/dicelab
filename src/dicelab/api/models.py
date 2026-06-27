"""Pydantic v2 request/response models for the HTTP API (camelCase JSON)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from dicelab.engine.result import SuccessLadder


class _CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class RollRequest(_CamelModel):
    expression: str
    seed: int | None = None
    ladder: SuccessLadder | None = None

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        json_schema_extra={"examples": [{"expression": "4d6dl1 + 2", "seed": 42}]},
    )


class DistributionRequest(_CamelModel):
    expression: str
    ladder: SuccessLadder | None = None
    percentiles: list[int] | None = None

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        json_schema_extra={"examples": [{"expression": "4d6dl1"}]},
    )


class ValidateRequest(_CamelModel):
    expression: str


class ValidateResponse(_CamelModel):
    valid: bool
    normalized: str | None
    ast: dict[str, Any] | None
    error: str | None


class HealthResponse(_CamelModel):
    status: str
