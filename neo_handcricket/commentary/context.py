"""Context-aware commentary (pure logic).

Occasional flavour lines that reference the live match state introduced in M005/M006:
a gassed bowler, a settled batter, or the bot AI having just read the human. Returns
a single line (or None) — gated on thresholds and a low emit probability so it stays
a garnish, not a flood. All lines original / CC0.
"""
from __future__ import annotations

import random

from ..config import (
    CONTEXT_FATIGUE_THRESHOLD,
    CONTEXT_LINE_PROB,
    CONTEXT_SETTLED_THRESHOLD,
)

FATIGUE_LINES = [
    "The legs have gone there — that was a tired delivery.",
    "You can see the bowler's running on empty now.",
    "Heavy spell catching up with him; the zip's off it.",
]
SETTLED_LINES = [
    "He's set now — looks completely at home out there.",
    "This batter's in; timing it sweetly.",
    "Eye well and truly in — everything's middling.",
]
AI_READ_LINES = [
    "Read that one perfectly — like he knew what was coming.",
    "The bowler had him figured out that ball.",
    "Outthought there; the trap was sprung.",
]


def context_line(
    *,
    bowler_fatigue: float = 0.0,
    batter_settledness: float = 0.0,
    ai_read: bool = False,
    rng: random.Random,
    emit_prob: float = CONTEXT_LINE_PROB,
) -> str | None:
    """An occasional state-referencing line, or None.

    A line is only eligible when its condition holds; among eligible buckets one is
    chosen, and it is emitted with probability ``emit_prob``.
    """
    buckets: list[list[str]] = []
    if ai_read:
        buckets.append(AI_READ_LINES)
    if bowler_fatigue >= CONTEXT_FATIGUE_THRESHOLD:
        buckets.append(FATIGUE_LINES)
    if batter_settledness >= CONTEXT_SETTLED_THRESHOLD:
        buckets.append(SETTLED_LINES)
    if not buckets or rng.random() >= emit_prob:
        return None
    return rng.choice(rng.choice(buckets))
