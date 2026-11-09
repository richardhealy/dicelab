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


def test_distribution_of_zero_dice_matches_the_roll() -> None:
    dist = client.post("/distribution", json={"expression": "0d6"})
    rolled = client.post("/roll", json={"expression": "0d6", "seed": 7})
    assert dist.status_code == 200 and rolled.status_code == 200
    assert rolled.json()["total"] == 0
    body = dist.json()
    assert body["pmf"] == {"0": 1.0}
    assert body["mean"] == 0.0
