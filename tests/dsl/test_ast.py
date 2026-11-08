import pytest

from dicelab.dsl.ast import (
    Advantage,
    BinOp,
    Constant,
    DiceTerm,
    Keep,
    SuccessPool,
    unparse,
)
from dicelab.dsl.parser import parse


def test_unparse_simple() -> None:
    node = BinOp("+", DiceTerm(1, 20, []), Constant(5))
    assert unparse(node) == "1d20 + 5"


def test_unparse_keep_and_pool() -> None:
    assert unparse(DiceTerm(4, 6, [Keep("l", 1)])) == "4d6kl1"
    assert unparse(DiceTerm(6, 10, [SuccessPool(">=", 7)])) == "6d10>=7"


def test_unparse_advantage() -> None:
    assert unparse(DiceTerm(1, 20, [Advantage("adv")])) == "1d20adv"


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        # Parentheses that change the meaning are kept.
        ("(1d6+2)*3", "(1d6 + 2) * 3"),
        ("3*(1d6+2)", "3 * (1d6 + 2)"),
        ("2-(3-4)", "2 - (3 - 4)"),
        ("2*(3*4)", "2 * (3 * 4)"),
        ("1d20-(1d4+1)", "1d20 - (1d4 + 1)"),
        ("-(1d6+2)", "-(1d6 + 2)"),
        ("-(2*3)", "-(2 * 3)"),
        # Parentheses that change nothing are dropped.
        ("(1d6*2)+3", "1d6 * 2 + 3"),
        ("(2-3)-4", "2 - 3 - 4"),
        ("((4d6dl1))", "4d6dl1"),
        ("2*-3", "2 * -3"),
        ("-3*2", "-3 * 2"),
        ("-(-3)", "--3"),
    ],
)
def test_unparse_parentheses(expression: str, expected: str) -> None:
    assert unparse(parse(expression)) == expected
