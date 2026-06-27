import pytest
from hypothesis import given
from hypothesis import strategies as st

from dicelab.dsl.ast import Advantage, DiceTerm, Keep, unparse
from dicelab.dsl.normalize import normalize
from dicelab.dsl.parser import parse

_dice = st.builds(
    lambda n, s: f"{n}d{s}",
    st.integers(min_value=1, max_value=20),
    st.integers(min_value=2, max_value=100),
)
# Paren-free expressions: parse(s) yields the canonical (precedence-correct,
# left-associative) tree, and unparse re-emits a paren-free string that parses
# back to the same canonical tree.
_expr = st.recursive(
    _dice | st.integers(min_value=0, max_value=99).map(str),
    lambda kids: st.builds(
        lambda a, op, b: f"{a} {op} {b}",
        kids,
        st.sampled_from(["+", "-", "*"]),
        kids,
    ),
    max_leaves=8,
)


@given(_expr)
def test_parse_unparse_roundtrip(expr: str) -> None:
    tree = parse(expr)
    assert parse(unparse(tree)) == tree


def test_normalize_advantage() -> None:
    tree = DiceTerm(1, 20, [Advantage("adv")])
    assert normalize(tree) == DiceTerm(2, 20, [Keep("h", 1)])


def test_normalize_requires_single_die() -> None:
    with pytest.raises(ValueError):
        normalize(DiceTerm(2, 20, [Advantage("adv")]))
