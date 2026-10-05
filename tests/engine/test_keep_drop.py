"""Keep/drop semantics, and agreement between the roll and distribution engines."""

from collections import Counter
from itertools import product

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from dicelab.dsl.ast import DiceTerm, Drop, Keep, Modifier
from dicelab.dsl.parser import parse
from dicelab.engine.distribution import distribute
from dicelab.engine.roll import _apply_keep_drop, roll

_FACES = [3, 1, 4, 1, 5]


@pytest.mark.parametrize(
    ("modifiers", "expected_kept"),
    [
        ([Keep("h", 2)], [4, 5]),
        ([Drop("l", 1)], [3, 4, 1, 5]),
        # k = 0 keeps nothing / drops nothing
        ([Keep("h", 0)], []),
        ([Keep("l", 0)], []),
        ([Drop("h", 0)], _FACES),
        ([Drop("l", 0)], _FACES),
        # k larger than the pool keeps everything / drops everything
        ([Keep("h", 9)], _FACES),
        ([Keep("l", 9)], _FACES),
        ([Drop("h", 9)], []),
        ([Drop("l", 9)], []),
        # modifiers apply left to right, each to the dice the previous one kept
        ([Keep("h", 3), Keep("l", 1)], [3]),
        ([Drop("h", 1), Drop("h", 1)], [3, 1, 1]),
        ([Drop("l", 1), Keep("h", 2)], [4, 5]),
    ],
)
def test_keep_drop_semantics(modifiers: list[Modifier], expected_kept: list[int]) -> None:
    kept, dropped = _apply_keep_drop(_FACES, DiceTerm(len(_FACES), 6, modifiers))
    assert Counter(kept) == Counter(expected_kept)
    assert Counter(kept + dropped) == Counter(_FACES)


@pytest.mark.parametrize(
    ("expression", "kept_count"),
    [("4d6dh0", 4), ("4d6kh0", 0), ("4d6dh5", 0), ("4d6kh5", 4), ("4d6dh1dh1", 2)],
)
def test_roll_and_distribution_agree_on_edge_counts(expression: str, kept_count: int) -> None:
    support = set(distribute(parse(expression)).pmf)
    for seed in range(50):
        r = roll(parse(expression), seed=seed)
        assert len(r.kept_rolls) == kept_count
        assert r.total in support


def _brute_force_pmf(term: DiceTerm) -> dict[int, float]:
    """Exact PMF by enumerating every ordered face tuple through the roll engine."""
    pmf: dict[int, float] = {}
    p_each = (1.0 / term.sides) ** term.count
    for faces in product(range(1, term.sides + 1), repeat=term.count):
        kept, _ = _apply_keep_drop(list(faces), term)
        total = sum(kept)
        pmf[total] = pmf.get(total, 0.0) + p_each
    return pmf


@st.composite
def _keep_drop_terms(draw: st.DrawFn) -> DiceTerm:
    count = draw(st.integers(min_value=1, max_value=4))
    sides = draw(st.integers(min_value=2, max_value=6))
    modifier = st.builds(
        lambda kind, which, k: Keep(which, k) if kind == "keep" else Drop(which, k),
        st.sampled_from(["keep", "drop"]),
        st.sampled_from(["h", "l"]),
        st.integers(min_value=0, max_value=count + 1),
    )
    modifiers = draw(st.lists(modifier, min_size=1, max_size=2))
    return DiceTerm(count, sides, modifiers)


@settings(max_examples=150, deadline=None)
@given(_keep_drop_terms())
def test_distribution_matches_brute_force_rolls(term: DiceTerm) -> None:
    expected = _brute_force_pmf(term)
    actual = distribute(term).pmf
    assert set(actual) == {total for total, p in expected.items() if p > 0}
    for total, p in expected.items():
        assert actual[total] == pytest.approx(p, abs=1e-9)
