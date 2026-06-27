import pytest

from dicelab.dsl.parser import parse
from dicelab.engine.distribution import Distribution, distribute


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


def test_distribute_d6_uniform() -> None:
    res = distribute(parse("1d6"))
    assert res.method == "exact"
    assert sum(res.pmf.values()) == pytest.approx(1.0)
    assert res.mean == pytest.approx(3.5)
    assert all(v == pytest.approx(1 / 6) for v in res.pmf.values())


def test_distribute_2d6_peak() -> None:
    res = distribute(parse("2d6"))
    assert res.pmf[7] == pytest.approx(6 / 36)
    assert res.mean == pytest.approx(7.0)


def test_distribute_keep_drop_sums_to_one() -> None:
    res = distribute(parse("4d6dl1"))
    assert res.method == "exact"
    assert sum(res.pmf.values()) == pytest.approx(1.0)
    assert min(res.pmf) == 3 and max(res.pmf) == 18


def test_distribute_pool_binomial() -> None:
    res = distribute(parse("2d6>=5"))  # p = 2/6 per die
    assert res.pmf[0] == pytest.approx((4 / 6) ** 2)
    assert res.pmf[2] == pytest.approx((2 / 6) ** 2)
    assert sum(res.pmf.values()) == pytest.approx(1.0)


def test_distribute_explode_sums_to_one() -> None:
    res = distribute(parse("1d6!"))
    assert res.method == "exact"
    assert sum(res.pmf.values()) == pytest.approx(1.0, abs=1e-9)
    # mean of an exploding d6 = 3.5 * 6/5 = 4.2
    assert res.mean == pytest.approx(4.2, abs=1e-6)


def test_distribute_reroll_once() -> None:
    res = distribute(parse("1d6r1"))
    # P(1) = (1/6)*(1/6); P(2..6) = 1/6 + (1/6)(1/6)
    assert res.pmf[1] == pytest.approx(1 / 36)
    assert res.pmf[2] == pytest.approx(1 / 6 + 1 / 36)
    assert sum(res.pmf.values()) == pytest.approx(1.0)
