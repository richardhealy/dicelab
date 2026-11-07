"""Keep/drop selection shared by the roll and distribution engines.

Modifiers apply left to right, each to the dice the previous one kept, so
``4d6kh3kl1`` keeps the lowest of the three highest dice. ``k`` is clamped to
the dice still in play: ``kh0`` keeps nothing, ``dh0`` drops nothing, and a
``k`` larger than the pool keeps (``kh``/``kl``) or drops (``dh``/``dl``) all of
it.
"""

from __future__ import annotations

from collections.abc import Sequence

from dicelab.dsl.ast import Drop, Keep, Modifier


def kept_indices(faces: Sequence[int], modifiers: Sequence[Modifier]) -> set[int]:
    """Indices into ``faces`` that survive the keep/drop modifiers."""
    remaining = sorted(range(len(faces)), key=lambda i: faces[i])  # ascending by value
    for mod in modifiers:
        if not isinstance(mod, (Keep, Drop)):
            continue
        k = min(mod.k, len(remaining))
        split = len(remaining) - k  # remaining[split:] are the k highest
        if isinstance(mod, Keep):
            remaining = remaining[split:] if mod.which == "h" else remaining[:k]
        else:
            remaining = remaining[:split] if mod.which == "h" else remaining[k:]
    return set(remaining)
