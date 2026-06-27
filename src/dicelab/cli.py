"""Typer + Rich CLI over the dice engine (no server required)."""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from dicelab.dsl.ast import Node, unparse
from dicelab.dsl.lexer import LexError
from dicelab.dsl.parser import ParseError, parse
from dicelab.engine.distribution import distribute as engine_distribute
from dicelab.engine.roll import roll as engine_roll

app = typer.Typer(help="DiceLab: roll dice and compute exact distributions.")
console = Console()


def _parse_or_exit(expression: str) -> Node:
    try:
        return parse(expression)
    except (ParseError, LexError) as exc:
        console.print(f"[red]Invalid expression:[/red] {exc}")
        raise typer.Exit(code=1) from exc


@app.command()
def roll(
    expression: Annotated[str, typer.Argument(metavar="EXPRESSION")],
    seed: Annotated[int | None, typer.Option("--seed")] = None,
) -> None:
    """Roll an expression."""
    result = engine_roll(_parse_or_exit(expression), seed=seed)
    table = Table(title=f"Roll: {result.expression}")
    table.add_column("Kept")
    table.add_column("Dropped")
    table.add_row(str(result.kept_rolls), str(result.dropped_rolls))
    console.print(table)
    console.print(f"[bold]Total[/bold]: {result.total}")
    if result.outcome is not None:
        console.print(f"[bold]Outcome[/bold]: {result.outcome}")


@app.command()
def distribution(
    expression: Annotated[str, typer.Argument(metavar="EXPRESSION")],
) -> None:
    """Show the exact distribution of an expression."""
    result = engine_distribute(_parse_or_exit(expression))
    console.print(f"[bold]{result.expression}[/bold]  (method: {result.method})")
    console.print(f"mean={result.mean:.4f}  stddev={result.stddev:.4f}")
    peak = max(result.pmf.values())
    for outcome in sorted(result.pmf):
        prob = result.pmf[outcome]
        bar = "█" * max(1, round(prob / peak * 40))
        console.print(f"{outcome:>4} {bar} {prob * 100:5.2f}%")


@app.command()
def validate(
    expression: Annotated[str, typer.Argument(metavar="EXPRESSION")],
) -> None:
    """Validate (parse) an expression without evaluating it."""
    node = _parse_or_exit(expression)
    console.print(f"[green]valid[/green]: {unparse(node)}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
