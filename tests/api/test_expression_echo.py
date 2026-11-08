"""The expression the API echoes back must mean the same as the one sent."""

import pytest
from fastapi.testclient import TestClient

from dicelab.api.app import create_app

client = TestClient(create_app())

_GROUPED = ["(1d6+2)*3", "2-(3-4)", "-(1d6+2)", "1d20-(1d4+1)"]


@pytest.mark.parametrize("expression", _GROUPED)
def test_validate_normalized_keeps_the_meaning(expression: str) -> None:
    first = client.post("/validate", json={"expression": expression}).json()
    again = client.post("/validate", json={"expression": first["normalized"]}).json()
    assert again["valid"] is True
    assert again["ast"] == first["ast"]


@pytest.mark.parametrize("expression", _GROUPED)
def test_roll_echo_rolls_the_same(expression: str) -> None:
    first = client.post("/roll", json={"expression": expression, "seed": 7}).json()
    again = client.post("/roll", json={"expression": first["expression"], "seed": 7}).json()
    assert again["total"] == first["total"]
    assert again["expression"] == first["expression"]


@pytest.mark.parametrize("expression", _GROUPED)
def test_distribution_echo_has_the_same_distribution(expression: str) -> None:
    first = client.post("/distribution", json={"expression": expression}).json()
    again = client.post("/distribution", json={"expression": first["expression"]}).json()
    assert again["pmf"] == first["pmf"]
    assert again["mean"] == pytest.approx(first["mean"])


def test_distribution_echo_for_a_scaled_sum() -> None:
    body = client.post("/distribution", json={"expression": "(1d6+2)*3"}).json()
    assert body["expression"] == "(1d6 + 2) * 3"
    assert body["mean"] == pytest.approx(16.5)
