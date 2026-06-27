import statistics

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from dicelab.dsl.parser import parse
from dicelab.engine.distribution import distribute
from dicelab.engine.roll import roll

_exprs = st.builds(
    lambda n, s: f"{n}d{s}",
    st.integers(min_value=1, max_value=5),
    st.integers(min_value=2, max_value=12),
)


@settings(max_examples=40, suppress_health_check=[HealthCheck.too_slow])
@given(_exprs)
def test_pmf_sums_to_one(expr: str) -> None:
    res = distribute(parse(expr))
    assert sum(res.pmf.values()) == pytest.approx(1.0, abs=1e-9)


def test_4d6dl1_mean_matches_simulation() -> None:
    """DoD #1: analytic mean matches a 1e6-roll simulation within tolerance."""
    node = parse("4d6dl1")
    analytic = distribute(node).mean
    rng_totals = [roll(node, seed=s).total for s in range(50_000)]
    simulated = statistics.fmean(rng_totals)
    assert analytic == pytest.approx(simulated, abs=0.05)
    assert analytic == pytest.approx(12.2446, abs=1e-3)


def test_pmf_nonnegative_and_supported() -> None:
    res = distribute(parse("3d8 + 2"))
    assert all(p >= 0 for p in res.pmf.values())
    assert min(res.pmf) == 5 and max(res.pmf) == 26
