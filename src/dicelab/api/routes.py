"""HTTP routes: thin adapters over the engine."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from dicelab.api.models import (
    DistributionRequest,
    HealthResponse,
    RollRequest,
    ValidateRequest,
    ValidateResponse,
)
from dicelab.constants import DEFAULT_PERCENTILES
from dicelab.dsl.ast import Node, ast_to_dict, unparse
from dicelab.dsl.lexer import LexError
from dicelab.dsl.parser import ParseError, parse
from dicelab.engine.distribution import distribute
from dicelab.engine.result import DistributionResult, RollResult
from dicelab.engine.roll import roll

router = APIRouter()


def _parse_or_422(expression: str) -> Node:
    try:
        return parse(expression)
    except (ParseError, LexError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/healthz", response_model=HealthResponse)
def healthz() -> HealthResponse:
    return HealthResponse(status="ok")


@router.post("/validate", response_model=ValidateResponse)
def validate(req: ValidateRequest) -> ValidateResponse:
    try:
        node = parse(req.expression)
    except (ParseError, LexError) as exc:
        return ValidateResponse(valid=False, normalized=None, ast=None, error=str(exc))
    return ValidateResponse(
        valid=True, normalized=unparse(node), ast=ast_to_dict(node), error=None
    )


@router.post("/roll", response_model=RollResult)
def roll_endpoint(req: RollRequest) -> RollResult:
    node = _parse_or_422(req.expression)
    return roll(node, seed=req.seed, ladder=req.ladder)


@router.post("/distribution", response_model=DistributionResult)
def distribution_endpoint(req: DistributionRequest) -> DistributionResult:
    node = _parse_or_422(req.expression)
    percentiles = tuple(req.percentiles) if req.percentiles else DEFAULT_PERCENTILES
    return distribute(node, ladder=req.ladder, percentiles=percentiles)
