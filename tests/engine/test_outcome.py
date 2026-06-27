import pytest

from dicelab.dsl.parser import parse
from dicelab.engine.distribution import distribute
from dicelab.engine.result import LadderRung, SuccessLadder
from dicelab.engine.roll import roll

# A WoD-style ladder: 0 successes = botch, >=1 = success, default failure.
LADDER = SuccessLadder(
    rungs=[
        LadderRung(compare="==", threshold=0, outcome="botch"),
        LadderRung(compare=">=", threshold=3, outcome="critical"),
        LadderRung(compare=">=", threshold=1, outcome="success"),
    ],
    default="failure",
)


def test_pool_roll_maps_successes_to_outcome() -> None:
    r = roll(parse("6d10>=7"), seed=11, ladder=LADDER)
    assert r.outcome in {"botch", "success", "critical"}
    # echo back the ladder under systemRules
    assert r.system_rules.success_ladder == LADDER


def test_outcome_specific_value() -> None:
    # many seeds: every outcome is a valid label
    labels = {roll(parse("6d10>=7"), seed=s, ladder=LADDER).outcome for s in range(100)}
    assert labels <= {"botch", "success", "critical", "failure"}


def test_distribution_outcome_probabilities_sum_to_one() -> None:
    res = distribute(parse("6d10>=7"), ladder=LADDER)
    assert res.outcome_probabilities is not None
    assert sum(res.outcome_probabilities.values()) == pytest.approx(1.0, abs=1e-9)
    assert set(res.outcome_probabilities) <= {"botch", "success", "critical", "failure"}


def test_no_ladder_means_no_outcome() -> None:
    assert roll(parse("6d10>=7"), seed=1).outcome is None
    assert distribute(parse("6d10>=7")).outcome_probabilities is None
