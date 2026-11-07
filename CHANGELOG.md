# Changelog

## 2026-10-06

### Fixed

- `/roll` and `/distribution` disagreed on some keep/drop terms, so the exact
  distribution described a different roll from the one the service made. Each
  engine had its own keep/drop code, and both used `[-k:]` slices that go wrong
  when `k` is 0 or larger than the number of dice:
  - `4d6dh0` rolled 0 (every die dropped) while its distribution had a mean of 14.
  - `4d6kh0` kept all four dice in both engines instead of none.
  - `4d6dh5` rolled 0 while its distribution kept three dice (mean 8.76).
  - Chained modifiers such as `4d6dh1dh1` or `4d6kh3kl1` were applied left to
    right by the distribution engine but all against the original dice by the
    roll engine, so `4d6dh1dh1` rolled totals up to 18 that the distribution
    gave zero probability.

  Both engines now call one function, `dicelab.engine.keepdrop.kept_indices`.
  Modifiers apply left to right, each to the dice the previous one kept, and
  `k` is clamped to the dice still in play. Seeded results for single-modifier
  terms with `1 <= k <= count` (such as `4d6dl1` or advantage) are unchanged.

### Added

- `tests/engine/test_keep_drop.py`: the keep/drop rules for `k = 0`, `k` larger
  than the pool and chained modifiers; roll/distribution agreement on those
  cases; and a Hypothesis test that checks the exact keep/drop distribution
  against a brute-force enumeration of every face tuple through the roll engine.
- `PROGRESS.md` and this changelog.
