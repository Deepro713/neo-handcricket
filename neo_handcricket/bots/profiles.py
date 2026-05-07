"""Archetype distributions over 0–6 + per-archetype adaptation strength.

Distributions describe the BASE probabilities (no adaptation). The adaptation
parameter modulates how strongly the player reacts to the user's recent picks.

For BATSMEN (when bot is batting, picks number to avoid matching user's bowl):
  the base distribution captures the batsman's preferred run-types.

For BOWLERS (when bot is bowling, picks number to MATCH user's batting pick):
  the base distribution describes the bowler's "natural" delivery type.

Final pick = (1 − α_player · α_difficulty) · base  +  (α_player · α_difficulty) · adapted
"""
from __future__ import annotations

# All distributions are over 0..6 (length 7).

BATSMAN_BASE: dict[str, list[float]] = {
    # opener: solid 1-3, rare 6
    "opener":       [0.05, 0.20, 0.25, 0.25, 0.15, 0.05, 0.05],
    # anchor: balanced
    "anchor":       [0.08, 0.15, 0.18, 0.20, 0.17, 0.12, 0.10],
    # power-hitter: heavy 4, 6 (riskier — 0/match more likely)
    "power-hitter": [0.04, 0.06, 0.08, 0.10, 0.30, 0.12, 0.30],
    # finisher: late-flair, balanced with 4/6 lean
    "finisher":     [0.05, 0.10, 0.15, 0.15, 0.20, 0.15, 0.20],
    # all-rounder (when batting): middle-balanced
    "all-rounder":  [0.06, 0.12, 0.18, 0.22, 0.20, 0.14, 0.08],
    # tail-ender: predictable, mostly low, rare wild 6
    "tail-ender":   [0.30, 0.30, 0.20, 0.10, 0.05, 0.03, 0.02],
}

BATSMAN_ALPHA: dict[str, float] = {
    "opener":       0.4,
    "anchor":       0.6,
    "power-hitter": 0.2,
    "finisher":     0.5,
    "all-rounder":  0.4,
    "tail-ender":   0.1,
}

BOWLER_BASE: dict[str, list[float]] = {
    # pace: high-end bias (5, 6)
    "pace":     [0.05, 0.08, 0.10, 0.12, 0.18, 0.22, 0.25],
    # swing: middle band (3, 4, 5)
    "swing":    [0.08, 0.10, 0.15, 0.20, 0.20, 0.15, 0.12],
    # off-spin: low end (1, 2, 3)
    "off-spin": [0.10, 0.20, 0.25, 0.20, 0.12, 0.08, 0.05],
    # leg-spin: bimodal — low + occasional 6
    "leg-spin": [0.10, 0.20, 0.22, 0.13, 0.10, 0.10, 0.15],
    # mystery: nearly uniform (drifts over time, see strategy.py)
    "mystery":  [0.13, 0.13, 0.15, 0.16, 0.15, 0.14, 0.14],
}

BOWLER_ALPHA: dict[str, float] = {
    "pace":     0.2,
    "swing":    0.4,
    "off-spin": 0.6,
    "leg-spin": 0.7,
    "mystery":  0.4,
}

# Extras-rate modifier per archetype: multiplied by EXTRAS_BASE_PCT.
# Bowlers more prone to wides/no-balls have a higher modifier.
BOWLER_EXTRAS_MOD: dict[str, float] = {
    "pace":     1.2,   # more no-balls (front-foot fault)
    "swing":    1.0,
    "off-spin": 0.7,
    "leg-spin": 1.0,
    "mystery":  1.5,   # wider, wilder
}

# Probability of a wide vs no-ball given an extra is conceded
# (we don't model byes/leg-byes during normal play; those are timeout-only)
def extras_kind_probabilities(archetype: str) -> tuple[float, float]:
    """Return (P(wide), P(no-ball)) given that an extra is conceded."""
    if archetype == "pace":
        return (0.4, 0.6)
    if archetype == "mystery":
        return (0.7, 0.3)
    return (0.5, 0.5)


def fallback_batsman_archetype() -> str:
    return "tail-ender"


def fallback_bowler_archetype() -> str:
    return "pace"
