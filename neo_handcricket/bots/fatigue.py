"""Bowler fatigue model (pure logic).

A bowler's effectiveness decays the more overs they bowl and recovers with rest.
Fatigue is a scalar in [0, 1] (0 = fresh, 1 = exhausted). It modulates two things
the strategy uses when the bot is bowling:

  - **flattens the base distribution** toward uniform — a tired bowler is easier to
    score off / less able to hit a wicket-taking number;
  - **lowers the effective α** — a tired bowler reads the batter less well.

All functions are pure and deterministic; no RNG. Tunables live in ``config``.
"""
from __future__ import annotations

from ..config import (
    FATIGUE_DECAY_PACE,
    FATIGUE_DECAY_SPIN,
    FATIGUE_RECOVERY_PER_OVER,
)

# Archetypes that tire at the faster, "pace" rate. Spinners use the slower rate.
PACE_LIKE = {"pace", "swing", "mystery"}


def _decay_rate(archetype: str) -> float:
    return FATIGUE_DECAY_PACE if archetype in PACE_LIKE else FATIGUE_DECAY_SPIN


def fatigue_factor(overs_bowled: int, overs_rested: int, archetype: str) -> float:
    """Fatigue in [0, 1] for a bowler who has bowled ``overs_bowled`` overs and
    rested ``overs_rested`` overs since their last spell.

    Rises with workload (faster for pace), falls with rest. Clamped to [0, 1].
    """
    workload = max(0, overs_bowled) * _decay_rate(archetype)
    recovery = max(0, overs_rested) * FATIGUE_RECOVERY_PER_OVER
    return max(0.0, min(1.0, workload - recovery))


def apply_fatigue(
    base: list[float], alpha: float, fatigue: float
) -> tuple[list[float], float]:
    """Return ``(flattened_base, reduced_alpha)`` for the given fatigue level.

    ``fatigue`` blends the base distribution toward uniform and scales α down by
    ``(1 - fatigue)``. At fatigue 0 the inputs are returned unchanged (after
    normalisation); at fatigue 1 the base is fully uniform and α is 0.
    """
    f = max(0.0, min(1.0, fatigue))
    n = len(base) or 1
    uniform = 1.0 / n
    s = sum(base)
    norm = [b / s for b in base] if s > 0 else [uniform] * n
    flattened = [(1.0 - f) * b + f * uniform for b in norm]
    return flattened, alpha * (1.0 - f)
