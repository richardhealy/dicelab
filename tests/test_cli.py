from typer.testing import CliRunner

from dicelab.cli import app

runner = CliRunner()


def test_cli_roll_deterministic() -> None:
    a = runner.invoke(app, ["roll", "4d6dl1", "--seed", "42"])
    b = runner.invoke(app, ["roll", "4d6dl1", "--seed", "42"])
    assert a.exit_code == 0
    assert a.stdout == b.stdout
    assert "Total" in a.stdout


def test_cli_distribution() -> None:
    result = runner.invoke(app, ["distribution", "2d6"])
    assert result.exit_code == 0
    assert "mean" in result.stdout.lower()


def test_cli_validate_bad() -> None:
    result = runner.invoke(app, ["validate", "2d6 @"])
    assert result.exit_code == 1
    assert "invalid" in result.stdout.lower()
