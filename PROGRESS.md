# Progress

Last updated: 2026-11-09

## Milestones

| #  | Milestone               | Status | Notes |
|----|-------------------------|--------|-------|
| M0 | Project scaffold        | Done   | uv, `src/` layout, ruff, `mypy --strict`, pre-commit, GitHub Actions CI |
| M1 | Lexer + parser          | Done   | Typed AST; round-trip property tests over paren-free strings and over generated trees that need parentheses |
| M2 | Roll evaluator          | Done   | Seeded rolls, kept/dropped dice, `RollResult` |
| M3 | Exact distribution      | Done   | Convolution, keep/drop enumeration, pools, explode, reroll; falls back to sampling with `method: "sampled"` |
| M4 | Outcome + successLadder | Done   | `successLadder` maps a total to an `outcome` |
| M5 | FastAPI surface         | Done   | `/roll`, `/distribution`, `/validate`, `/healthz`, OpenAPI test |
| M6 | CLI                     | Done   | `dicelab roll`, `distribution`, `validate` |
| M7 | Package + ship          | Mostly | Dockerfile and README chart are in; no tagged release yet |

## Definition of done

1. `4d6dl1` PMF sums to 1 and its mean matches a simulation: tested, but the
   simulation is 50,000 seeded rolls rather than the 1e6 the spec mentions.
2. Seeded `/roll` is deterministic and reports kept and dropped dice: tested.
3. `/docs` renders the typed API: tested (`/docs` and `/openapi.json` return 200).
4. ruff, `mypy --strict` and pytest (with Hypothesis) are green in CI.
5. The engine runs from the CLI with no server: tested.

## Recent changes

- 2026-11-09: the exact distribution of a term with no dice is a total of 0,
  as the roll engine already gave, instead of the distribution of one die
  (`0d6` reported mean 3.5). A new property test checks that every seeded
  roll total is an outcome in the distribution. See CHANGELOG.md.
- 2026-11-08: `unparse` keeps the parentheses a tree needs, so the
  `expression` echoed by `/roll` and `/distribution` and `normalized` from
  `/validate` parse back to the expression that was sent. See CHANGELOG.md.
- 2026-10-06: keep/drop now behaves the same in the roll and distribution
  engines (one shared implementation). See CHANGELOG.md.

## Known issues

Not yet fixed:

- (found 2026-10-06) `1d0` returns HTTP 500 from `/roll` and `/distribution`
  instead of a 422. `/validate` accepts it. `0d0` is the same on
  `/distribution` (500), though `/roll` gives a total of 0 (checked
  2026-11-09).
- (found 2026-11-08) Trailing advantage in a longer expression echoes as text
  that does not parse. `1d20+5 adv` is accepted and rolled correctly, but the
  echoed `expression` (and `normalized` from `/validate`) is `1d20adv + 5`,
  and sending that back fails with "Unexpected PLUS". `unparse` writes `adv`
  and `dis` straight after the dice, and the parser only reads them at the end
  of the whole expression. A bare `1d20adv` is fine.

## Next

- Fix the known issues above, each with a regression test.
- Tag a first release (M7).
- Stretch goals from the spec: a `compare` endpoint, distribution caching,
  publishing the engine to PyPI.
