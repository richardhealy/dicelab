# Progress

Last updated: 2026-10-06

## Milestones

| #  | Milestone               | Status | Notes |
|----|-------------------------|--------|-------|
| M0 | Project scaffold        | Done   | uv, `src/` layout, ruff, `mypy --strict`, pre-commit, GitHub Actions CI |
| M1 | Lexer + parser          | Done   | Typed AST, round-trip property test (paren-free expressions only, see known issues) |
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

- 2026-10-06: keep/drop now behaves the same in the roll and distribution
  engines (one shared implementation). See CHANGELOG.md.

## Known issues

Found on 2026-10-06 and not yet fixed:

- `unparse` drops parentheses, so the `expression` echoed by `/roll` and
  `/distribution`, and `normalized` from `/validate`, can mean something else.
  `(1d6+2)*3` comes back as `1d6 + 2 * 3`, and `2-(3-4)` as `2 - 3 - 4`. The
  totals are right (the AST is right); re-submitting the echoed string is not.
- `0d6` rolls 0 but its distribution is that of `1d6` (mean 3.5), because the
  convolution loop starts from one die.
- `1d0` returns HTTP 500 from `/roll` and `/distribution` instead of a 422.
  `/validate` accepts it.

## Next

- Fix the three known issues above, each with a regression test.
- Tag a first release (M7).
- Stretch goals from the spec: a `compare` endpoint, distribution caching,
  publishing the engine to PyPI.
