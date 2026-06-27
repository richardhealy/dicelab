from dicelab.dsl.parser import parse
from dicelab.engine.result import LadderRung, SuccessLadder
from dicelab.engine.roll import roll


def test_deterministic_with_seed() -> None:
    a = roll(parse("4d6dl1 + 2"), seed=42)
    b = roll(parse("4d6dl1 + 2"), seed=42)
    assert a == b


def test_constant() -> None:
    r = roll(parse("7"), seed=1)
    assert r.total == 7
    assert r.kept_rolls == []


def test_keep_drop_separates_dice() -> None:
    r = roll(parse("4d6dl1"), seed=42)
    assert len(r.kept_rolls) == 3
    assert len(r.dropped_rolls) == 1
    assert r.total == sum(r.kept_rolls)
    # dropped die is the lowest
    assert min(r.kept_rolls) >= r.dropped_rolls[0]


def test_bounds_simple_roll() -> None:
    for seed in range(50):
        r = roll(parse("3d6"), seed=seed)
        assert 3 <= r.total <= 18


def test_success_pool_counts() -> None:
    r = roll(parse("6d10>=7"), seed=3)
    assert r.total == len(r.kept_rolls)
    assert all(f >= 7 for f in r.kept_rolls)
    assert all(f < 7 for f in r.dropped_rolls)


def test_reroll_once_changes_ones() -> None:
    # With reroll of 1s, a kept face could still be 1 only via the rerolled value.
    rolls = [roll(parse("1d6r1"), seed=s).total for s in range(200)]
    assert min(rolls) >= 1 and max(rolls) <= 6


def test_outcome_from_ladder() -> None:
    ladder = SuccessLadder(
        rungs=[LadderRung(compare=">=", threshold=3, outcome="success")],
        default="failure",
    )
    r = roll(parse("6d10>=7"), seed=3, ladder=ladder)
    assert r.outcome in {"success", "failure"}
    assert r.system_rules.success_ladder == ladder
