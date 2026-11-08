# Changelog

## 2026-11-08

### Fixed

- `unparse` dropped every pair of parentheses, so the expression the service
  echoed back could mean something else. The rolled total and the
  distribution were right (the parsed tree was right), but the text was not:
  - `(1d6+2)*3` came back as `1d6 + 2 * 3`. With seed 42, `/roll` gave 24
    for the original and 12 for the echoed text.
  - `2-(3-4)` came back as `2 - 3 - 4` (3 against -5), and `-(1d6+2)` as
    `-1d6 + 2`.

  This affected `expression` from `/roll` and `/distribution`, `normalized`
  from `/validate` and the CLI's `dicelab validate`. `unparse` now adds
  parentheses where the tree needs them: around a looser operation inside a
  tighter one, and around a right operand of the same precedence, because the
  parser groups `+`, `-` and `*` from the left. Expressions that never needed
  parentheses (`4d6dl1 + 2`, `1d20 + 5`) are echoed as before.

### Added

- `tests/dsl/test_ast.py`: unparse cases where parentheses must stay and
  where they should be dropped.
- `tests/dsl/test_ast_roundtrip.py`: a Hypothesis test that generates parsed
  trees (sums, differences, products, negation, dice with keep/drop) and
  checks that `parse(unparse(tree)) == tree`.
- `tests/api/test_expression_echo.py`: sending back the echoed expression
  gives the same AST from `/validate`, the same seeded total from `/roll`
  and the same distribution from `/distribution`.

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
