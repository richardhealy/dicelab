from fastapi.testclient import TestClient

from dicelab.api.app import create_app

client = TestClient(create_app())


def test_distribution_4d6dl1() -> None:
    resp = client.post("/distribution", json={"expression": "4d6dl1"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["method"] == "exact"
    # JSON object keys are strings
    assert abs(sum(body["pmf"].values()) - 1.0) < 1e-9
    assert abs(body["mean"] - 12.2446) < 1e-3


def test_distribution_bad_422() -> None:
    resp = client.post("/distribution", json={"expression": "@@"})
    assert resp.status_code == 422
