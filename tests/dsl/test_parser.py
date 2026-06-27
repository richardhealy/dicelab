import pytest

from dicelab.dsl.ast import (
    Advantage,
    BinOp,
    Constant,
    DiceTerm,
    Drop,
    Explode,
    Keep,
    Reroll,
    SuccessPool,
    UnaryOp,
)
from dicelab.dsl.parser import ParseError, parse


def test_precedence() -> None:
    # 1 + 2 * 3 -> 1 + (2*3)
    assert parse("1 + 2 * 3") == BinOp("+", Constant(1), BinOp("*", Constant(2), Constant(3)))


def test_dice_binds_tightest() -> None:
    assert parse("2d6 + 3") == BinOp("+", DiceTerm(2, 6, []), Constant(3))


def test_implicit_count() -> None:
    assert parse("d20") == DiceTerm(1, 20, [])


def test_modifiers() -> None:
    assert parse("4d6dl1") == DiceTerm(4, 6, [Drop("l", 1)])
    assert parse("2d20kh") == DiceTerm(2, 20, [Keep("h", 1)])
    assert parse("3d6!") == DiceTerm(3, 6, [Explode()])
    assert parse("1d6r1") == DiceTerm(1, 6, [Reroll(1)])
    assert parse("6d10>=7") == DiceTerm(6, 10, [SuccessPool(">=", 7)])


def test_trailing_advantage() -> None:
    assert parse("1d20+5 adv") == BinOp("+", DiceTerm(1, 20, [Advantage("adv")]), Constant(5))


def test_unary_minus() -> None:
    assert parse("-2d6") == UnaryOp("-", DiceTerm(2, 6, []))


def test_parens() -> None:
    assert parse("2 * (1d6 + 1)") == BinOp(
        "*", Constant(2), BinOp("+", DiceTerm(1, 6, []), Constant(1))
    )


def test_pool_with_keep_is_error() -> None:
    with pytest.raises(ParseError):
        parse("6d10kh3>=7")


def test_trailing_adv_needs_unique_die() -> None:
    with pytest.raises(ParseError):
        parse("2 + 3 adv")
    with pytest.raises(ParseError):
        parse("1d6 + 1d8 adv")


def test_trailing_garbage_is_error() -> None:
    with pytest.raises(ParseError):
        parse("2d6 3")
