from dicelab.engine.result import (
    LadderRung,
    RollResult,
    SuccessLadder,
    SystemRules,
    derive_outcome,
)


def test_camelcase_serialization() -> None:
    r = RollResult(
        expression="4d6dl1",
        total=12,
        kept_rolls=[4, 4, 4],
        dropped_rolls=[1],
        rolls=[],
        seed=7,
        outcome=None,
        system_rules=SystemRules(),
    )
    data = r.model_dump(by_alias=True)
    assert data["keptRolls"] == [4, 4, 4]
    assert data["droppedRolls"] == [1]
    assert data["systemRules"] == {"successLadder": None}


def test_derive_outcome_first_match_wins() -> None:
    ladder = SuccessLadder(
        rungs=[
            LadderRung(compare=">=", threshold=3, outcome="success"),
            LadderRung(compare="==", threshold=0, outcome="botch"),
        ],
        default="failure",
    )
    assert derive_outcome(5, ladder) == "success"
    assert derive_outcome(0, ladder) == "botch"
    assert derive_outcome(1, ladder) == "failure"
    assert derive_outcome(1, None) is None
