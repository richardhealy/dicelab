"""HTTP routes: thin adapters over the engine."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from dicelab.api.models import HealthResponse
from dicelab.dsl.ast import Node
from dicelab.dsl.lexer import LexError
from dicelab.dsl.parser import ParseError, parse

router = APIRouter()


def _parse_or_422(expression: str) -> Node:
    try:
        return parse(expression)
    except (ParseError, LexError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/healthz", response_model=HealthResponse)
def healthz() -> HealthResponse:
    return HealthResponse(status="ok")
