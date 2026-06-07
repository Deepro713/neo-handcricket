"""Batsman match-state / momentum model (pure logic).

A new batter is tentative and accelerates as they settle; a chase raises intent as
the required run-rate climbs. Both feed a single ``aggression`` scalar in [0, 1]
(0 = blocking, 0.5 = neutral, 1 = all-out) which reshapes the batsman's base
distribution toward boundaries — or away from them, when tentative.

All functions are pure and deterministic; no RNG. Tunables live in ``config``.
"""
from __future__ import annotations

from ..config import (
    AGGRO_BASE,
    AGGRO_INTENT_WEIGHT,
    AGGRO_SETTLE_WEIGHT,
    AGGRO_TILT,
    SETTLE_BALLS_K,
)


def settledness(balls_faced: int) -> float:
    """How "in" the batter is, in [0, 1). 0 at the first ball, asymptotes to 1.

    Reaches 0.5 after ``SETTLE_BALLS_K`` balls.
    """
    b = max(0, balls_faced)
    return b / (b + SETTLE_BALLS_K)


def chase_intent(runs_needed: int | None, balls_remaining: int | None) -> float:
    """Chase pressure in [0, 1] from the required run-rate.

    Returns 0 when not chasing (no target / no balls left). One run/ball maps to
    ~0.5; two+ runs/ball saturates to 1.
    """
    if not runs_needed or not balls_remaining or balls_remaining <= 0 or runs_needed <= 0:
        return 0.0
    required_per_ball = runs_needed / balls_remaining
    return max(0.0, min(1.0, required_per_ball / 2.0))


def aggression(settled: float, intent: float) -> float:
    """Combine settledness and chase intent into an aggression scalar in [0, 1]."""
    a = AGGRO_BASE + AGGRO_SETTLE_WEIGHT * settled + AGGRO_INTENT_WEIGHT * intent
    return max(0.0, min(1.0, a))


# Per-index tilt by run value (0..6): negative favours safe low scores, positive
# favours boundaries. Centred so index 3 is neutral.
_TILT = [(i - 3) / 3.0 for i in range(7)]


def apply_matchstate(base: list[float], aggression_level: float) -> list[float]:
    """Reshape a batsman base distribution by aggression in [0, 1].

    At 0.5 the (normalised) base is unchanged. Below 0.5 mass shifts toward low
    scores (tentative); above 0.5 it shifts toward 4/6 (attacking). Always returns
    a valid probability distribution.
    """
    a = max(0.0, min(1.0, aggression_level))
    t = (a - 0.5) * 2.0  # [-1, 1]
    s = sum(base)
    n = len(base) or 1
    norm = [b / s for b in base] if s > 0 else [1.0 / n] * n
    weighted = [max(0.0, p * (1.0 + t * _TILT[i] * AGGRO_TILT)) for i, p in enumerate(norm)]
    ws = sum(weighted)
    if ws <= 0:
        return [1.0 / n] * n
    return [w / ws for w in weighted]
