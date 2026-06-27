"""Render the 4d6dl1 probability distribution to docs/4d6dl1.png."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from dicelab.dsl.parser import parse
from dicelab.engine.distribution import distribute


def main() -> None:
    res = distribute(parse("4d6dl1"))
    outcomes = sorted(res.pmf)
    probs = [res.pmf[o] * 100 for o in outcomes]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(outcomes, probs, color="#5b8def")
    ax.set_title(f"4d6dl1  (mean {res.mean:.2f}, exact)")
    ax.set_xlabel("total")
    ax.set_ylabel("probability (%)")
    fig.tight_layout()
    out = Path("docs/4d6dl1.png")
    fig.savefig(out, dpi=120)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
