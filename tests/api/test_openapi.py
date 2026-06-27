from fastapi.testclient import TestClient

from dicelab.api.app import create_app

app = create_app()
client = TestClient(app)


def test_openapi_generates() -> None:
    schema = app.openapi()
    assert schema["info"]["title"] == "DiceLab"
    for path in ("/roll", "/distribution", "/validate", "/healthz"):
        assert path in schema["paths"]


def test_docs_served() -> None:
    assert client.get("/openapi.json").status_code == 200
    assert client.get("/docs").status_code == 200


def test_roll_request_has_example() -> None:
    schema = app.openapi()
    roll_schema = schema["components"]["schemas"]["RollRequest"]
    assert "examples" in roll_schema or "example" in roll_schema
