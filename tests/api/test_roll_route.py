from fastapi.testclient import TestClient

from dicelab.api.app import create_app

client = TestClient(create_app())


def test_roll_deterministic() -> None:
    payload = {"expression": "4d6dl1", "seed": 42}
    a = client.post("/roll", json=payload).json()
    b = client.post("/roll", json=payload).json()
    assert a == b
    assert len(a["keptRolls"]) == 3
    assert len(a["droppedRolls"]) == 1
    assert a["total"] == sum(a["keptRolls"])


def test_roll_with_ladder() -> None:
    payload = {
        "expression": "6d10>=7",
        "seed": 1,
        "ladder": {
            "rungs": [{"compare": ">=", "threshold": 1, "outcome": "success"}],
            "default": "failure",
        },
    }
    body = client.post("/roll", json=payload).json()
    assert body["outcome"] in {"success", "failure"}
    assert body["systemRules"]["successLadder"]["default"] == "failure"


def test_roll_bad_expression_422() -> None:
    resp = client.post("/roll", json={"expression": "2d6 @"})
    assert resp.status_code == 422
