"""FastAPI application factory."""

from __future__ import annotations

from fastapi import FastAPI

from dicelab import __version__
from dicelab.api.logging import configure_logging
from dicelab.api.routes import router


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(
        title="DiceLab",
        version=__version__,
        description="A dice DSL that rolls and reasons: seeded rolls and exact distributions.",
    )
    app.include_router(router)
    return app


app = create_app()
