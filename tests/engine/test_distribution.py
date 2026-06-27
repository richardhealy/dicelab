import pytest

from dicelab.engine.distribution import Distribution


def test_uniform_die_mean() -> None:
    d6 = Distribution.uniform_die(6)
    assert d6.mean() == pytest.approx(3.5)
    assert sum(p for _, p in d6.items()) == pytest.approx(1.0)


def test_convolve_two_d6() -> None:
    d6 = Distribution.uniform_die(6)
    two = d6.convolve(d6)
    pmf = dict(two.items())
    assert two.outcomes().start == 2
    assert pmf[7] == pytest.approx(6 / 36)
    assert pmf[2] == pytest.approx(1 / 36)
    assert two.mean() == pytest.approx(7.0)


def test_negate_and_combine() -> None:
    d6 = Distribution.uniform_die(6)
    diff = d6.combine(d6, lambda a, b: a - b)
    assert diff.mean() == pytest.approx(0.0)
    assert dict(diff.items())[0] == pytest.approx(6 / 36)


def test_percentile_and_cdf() -> None:
    d6 = Distribution.uniform_die(6)
    assert d6.percentile(50) in (3, 4)
    cdf = d6.cdf()
    assert cdf[6] == pytest.approx(1.0)
    assert cdf[3] == pytest.approx(0.5)


def test_from_pairs_fills_gaps() -> None:
    d = Distribution.from_pairs({1: 0.5, 3: 0.5})
    assert list(d.outcomes()) == [1, 2, 3]
    assert dict(d.items()) == {1: 0.5, 3: 0.5}
