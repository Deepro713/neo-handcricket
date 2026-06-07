"""Bowler rotation captain-AI heuristic.

Picks the next bowler to bowl an over given current match state.

Heuristic:
  - Powerplay (first ~30% of overs): prefer PACE
  - Middle (~30-70%): prefer SPIN
  - Death (last ~30%): prefer best economy among bowlers with overs left
  - Within a phase, bias toward a favourable bowler-vs-batter archetype match-up
    and toward fresher bowlers (M005)
  - Always respect format.bowler_over_cap
  - Never pick the bowler who bowled the previous over (no consecutive overs)
"""
from __future__ import annotations

import random

from ..config import ROTATION_FRESHNESS_WEIGHT, ROTATION_MATCHUP_WEIGHT
from ..formats import Format

PACE_LIKE = {"pace", "swing", "mystery"}
SPIN_LIKE = {"off-spin", "leg-spin"}

# Bowler-archetype × batter-archetype advantage (higher = the bowler is favoured).
# Values roughly in [-0.2, 0.2]. Original/flavourful, not from any external source.
MATCHUP: dict[str, dict[str, float]] = {
    "pace":     {"opener": 0.15, "tail-ender": 0.20, "power-hitter": -0.15, "finisher": -0.05, "all-rounder": 0.05},
    "swing":    {"opener": 0.20, "anchor": 0.10, "tail-ender": 0.15, "power-hitter": -0.10, "finisher": -0.05},
    "off-spin": {"power-hitter": 0.15, "finisher": 0.10, "anchor": -0.10, "opener": -0.05, "tail-ender": 0.10},
    "leg-spin": {"finisher": 0.20, "power-hitter": 0.15, "anchor": -0.05, "opener": -0.10, "tail-ender": 0.15, "all-rounder": 0.10},
    "mystery":  {"tail-ender": 0.20, "all-rounder": 0.10, "anchor": 0.05, "opener": 0.05, "power-hitter": 0.05, "finisher": 0.10},
}


def matchup_advantage(bowler_archetype: str, batter_archetype: str | None) -> float:
    """Advantage (higher favours the bowler) of a bowler archetype vs a batter archetype."""
    if not batter_archetype:
        return 0.0
    return MATCHUP.get(bowler_archetype, {}).get(batter_archetype, 0.0)


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
    batter_archetype: str | None = None,        # current striker's archetype (match-ups)
    fatigues: dict[int, float] | None = None,   # bowler_id -> fatigue 0..1 (freshness)
    rng: random.Random | None = None,
) -> int:
    """Return the player_id of the next bowler. Falls back to a random eligible bowler if no preference matches.

    ``batter_archetype`` and ``fatigues`` (both optional, backward-compatible) bias
    selection toward a favourable match-up and toward fresher bowlers.
    """
    rng = rng if rng is not None else random.Random()
    fatigues = fatigues or {}
    eligible = _eligible(bowling_pool, over_counts, fmt.bowler_over_cap, last_bowler)
    if not eligible:
        # Truly stuck: all overs spent. Caller should have bailed before this.
        return bowling_pool[0]

    phase = _phase(over_idx, total_overs)

    if phase == "death":
        # Prefer lowest economy, then freshest, then fewest overs bowled.
        eligible.sort(key=lambda pid: (
            economies.get(pid, 99.0),
            fatigues.get(pid, 0.0),
            over_counts.get(pid, 0),
        ))
        return eligible[0]

    preferred_kinds = PACE_LIKE if phase == "power" else SPIN_LIKE
    matching = [pid for pid in eligible if archetypes.get(pid) in preferred_kinds]
    pool = matching if matching else eligible

    def _rank(pid: int) -> float:
        # Higher is better: favourable match-up + freshness, penalised by workload.
        matchup = matchup_advantage(archetypes.get(pid, "pace"), batter_archetype)
        freshness = 1.0 - fatigues.get(pid, 0.0)
        return (
            ROTATION_MATCHUP_WEIGHT * matchup
            + ROTATION_FRESHNESS_WEIGHT * freshness
            - float(over_counts.get(pid, 0))
        )

    pool.sort(key=_rank, reverse=True)
    # Slight randomness: pick from the top half of the ranked pool.
    cutoff = max(1, len(pool) // 2)
    return rng.choice(pool[:cutoff])
