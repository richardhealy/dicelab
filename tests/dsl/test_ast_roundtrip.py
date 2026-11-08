import pytest
from hypothesis import given
from hypothesis import strategies as st

from dicelab.dsl.ast import (
    Advantage,
    BinOp,
    Constant,
    DiceTerm,
    Drop,
    Keep,
    Node,
    UnaryOp,
    unparse,
)
from dicelab.dsl.normalize import normalize
from dicelab.dsl.parser import parse

_dice = st.builds(
    lambda n, s: f"{n}d{s}",
    st.integers(min_value=1, max_value=20),
    st.integers(min_value=2, max_value=100),
)
# Paren-free expressions: parse(s) yields the canonical (precedence-correct,
# left-associative) tree, and unparse re-emits a string that parses back to
# the same tree.
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


# Any tree the parser can produce, including ones that need parentheses
# (a sum under a product, a right-nested difference, a negated sum).
# Constants are non-negative because the parser builds a negative number as
# UnaryOp("-", Constant(n)).
_dice_node: st.SearchStrategy[Node] = st.builds(
    DiceTerm,
    st.integers(min_value=1, max_value=20),
    st.integers(min_value=2, max_value=100),
    st.one_of(
        st.just([]),
        st.builds(
            lambda kind, which, k: [kind(which, k)],
            st.sampled_from([Keep, Drop]),
            st.sampled_from(["h", "l"]),
            st.integers(min_value=0, max_value=5),
        ),
    ),
)
_tree: st.SearchStrategy[Node] = st.recursive(
    _dice_node | st.builds(Constant, st.integers(min_value=0, max_value=99)),
    lambda kids: st.one_of(
        st.builds(BinOp, st.sampled_from(["+", "-", "*"]), kids, kids),
        st.builds(UnaryOp, st.just("-"), kids),
    ),
    max_leaves=10,
)


@given(_tree)
def test_unparse_parses_back_to_the_same_tree(tree: Node) -> None:
    assert parse(unparse(tree)) == tree


def test_normalize_advantage() -> None:
    tree = DiceTerm(1, 20, [Advantage("adv")])
    assert normalize(tree) == DiceTerm(2, 20, [Keep("h", 1)])


def test_normalize_requires_single_die() -> None:
    with pytest.raises(ValueError):
        normalize(DiceTerm(2, 20, [Advantage("adv")]))
