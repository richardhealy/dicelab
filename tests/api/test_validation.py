from fastapi.testclient import TestClient

from dicelab.api.app import create_app

client = TestClient(create_app())


def test_validate_good() -> None:
    resp = client.post("/validate", json={"expression": "4d6dl1 + 2"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["valid"] is True
    assert body["normalized"] == "4d6dl1 + 2"
    assert body["ast"]["type"] == "binop"
    assert body["error"] is None


def test_validate_bad() -> None:
    resp = client.post("/validate", json={"expression": "2d6 @ 1"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["valid"] is False
    assert body["error"] is not None
    assert body["ast"] is None
