"""Bowler rotation captain-AI heuristic.

Picks the next bowler to bowl an over given current match state.

Heuristic:
  - Powerplay (first ~30% of overs): prefer PACE
  - Middle (~30-70%): prefer SPIN
  - Death (last ~30%): prefer best economy among bowlers with overs left
  - Always respect format.bowler_over_cap
  - Never pick the bowler who bowled the previous over (no consecutive overs)
"""
from __future__ import annotations

import random

from ..formats import Format

PACE_LIKE = {"pace", "swing", "mystery"}
SPIN_LIKE = {"off-spin", "leg-spin"}


def _phase(over_idx: int, total_overs: int | None) -> str:
    if total_overs is None:
        # Test/no-cap → cycle between phases by over number
        if over_idx % 30 < 10:
            return "power"
        if over_idx % 30 < 20:
            return "middle"
        return "death"
    frac = over_idx / max(1, total_overs)
    if frac < 0.30:
        return "power"
    if frac < 0.70:
        return "middle"
    return "death"


def _eligible(
    bowling_pool: list[int],
    over_counts: dict[int, int],
    bowler_over_cap: int | None,
    last_bowler: int | None,
) -> list[int]:
    out = []
    for pid in bowling_pool:
        if pid == last_bowler:
            continue
        if bowler_over_cap is not None and over_counts.get(pid, 0) >= bowler_over_cap:
            continue
        out.append(pid)
    if not out:
        # Allow last bowler if everyone else is capped/excluded
        out = [
            pid for pid in bowling_pool
            if bowler_over_cap is None or over_counts.get(pid, 0) < bowler_over_cap
        ]
    return out


def pick_next_bowler(
    *,
    bowling_pool: list[int],
    archetypes: dict[int, str],     # bowler_id -> bowling_archetype
    over_counts: dict[int, int],
    economies: dict[int, float],
    last_bowler: int | None,
    over_idx: int,
    total_overs: int | None,
    fmt: Format,
    rng: random.Random | None = None,
) -> int:
    """Return the player_id of the next bowler. Falls back to a random eligible bowler if no preference matches."""
    rng = rng if rng is not None else random.Random()
    eligible = _eligible(bowling_pool, over_counts, fmt.bowler_over_cap, last_bowler)
    if not eligible:
        # Truly stuck: all overs spent. Caller should have bailed before this.
        return bowling_pool[0]

    phase = _phase(over_idx, total_overs)

    if phase == "death":
        # Prefer lowest economy among eligible
        eligible.sort(key=lambda pid: (economies.get(pid, 99.0), over_counts.get(pid, 0)))
        return eligible[0]

    preferred_kinds = PACE_LIKE if phase == "power" else SPIN_LIKE
    matching = [pid for pid in eligible if archetypes.get(pid) in preferred_kinds]

    pool = matching if matching else eligible
    # Prefer those with fewer overs bowled so far (rotation)
    pool.sort(key=lambda pid: (over_counts.get(pid, 0), economies.get(pid, 99.0)))
    # Slight randomness: pick from top half
    cutoff = max(1, len(pool) // 2)
    return rng.choice(pool[:cutoff])
