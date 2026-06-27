from dicelab.dsl.ast import (
    Advantage,
    BinOp,
    Constant,
    DiceTerm,
    Keep,
    SuccessPool,
    unparse,
)


def test_unparse_simple() -> None:
    node = BinOp("+", DiceTerm(1, 20, []), Constant(5))
    assert unparse(node) == "1d20 + 5"


def test_unparse_keep_and_pool() -> None:
    assert unparse(DiceTerm(4, 6, [Keep("l", 1)])) == "4d6kl1"
    assert unparse(DiceTerm(6, 10, [SuccessPool(">=", 7)])) == "6d10>=7"


def test_unparse_advantage() -> None:
    assert unparse(DiceTerm(1, 20, [Advantage("adv")])) == "1d20adv"
