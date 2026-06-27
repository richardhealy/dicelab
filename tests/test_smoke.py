from dicelab import __version__
from dicelab.constants import DEFAULT_PERCENTILES, EXPLODE_EPSILON


def test_version_present() -> None:
    assert isinstance(__version__, str)


def test_constants() -> None:
    assert EXPLODE_EPSILON < 1e-6
    assert DEFAULT_PERCENTILES == (5, 25, 50, 75, 95)
