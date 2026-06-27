from fastapi import FastAPI

from dicelab.api.app import app


def test_module_level_app_is_fastapi() -> None:
    assert isinstance(app, FastAPI)
