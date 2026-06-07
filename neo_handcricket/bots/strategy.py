"""Number selection strategy.

Two modes:
  - "bowl": bot is bowling, picks a number trying to MATCH the user's batting pick
  - "bat": bot is batting, picks a number trying to AVOID matching the user's bowling pick

Adaptation builds an adapted distribution from the user's last N picks. The
final distribution mixes base (the player's archetype) with adapted, weighted
by α (player archetype × difficulty).
"""
from __future__ import annotations

import random
from collections import Counter

from ..config import ADAPTIVE_WINDOW, DIFFICULTY_ALPHA, OPP_WINDOW
from . import fatigue as fatigue_mod
from . import matchstate as matchstate_mod
from . import opponent as opponent_mod
from . import profiles


def _normalize(dist: list[float]) -> list[float]:
    s = sum(dist)
    if s <= 0:
        return [1 / 7] * 7
    return [x / s for x in dist]


def _adapted_for_bowling(recent_user_picks: list[int]) -> list[float]:
    """Bowling = match the user. Bias the distribution TOWARD the user's recent picks."""
    if not recent_user_picks:
        return [1 / 7] * 7
    counts = Counter(recent_user_picks)
    total = sum(counts.values())
    base_smooth = 0.5  # add-half smoothing so unseen numbers still get probability
    dist = [(counts.get(i, 0) + base_smooth) / (total + base_smooth * 7) for i in range(7)]
    return _normalize(dist)


def _adapted_for_batting(recent_user_picks: list[int]) -> list[float]:
    """Batting = avoid matching the user's bowling pick. Bias AWAY from recent user picks."""
    if not recent_user_picks:
        return [1 / 7] * 7
    counts = Counter(recent_user_picks)
    # Inverse: high-frequency picks get LOW probability
    raw = [1.0 / (counts.get(i, 0) + 1) for i in range(7)]  # +1 smoothing
    return _normalize(raw)


def _mystery_drift_seed(over: int) -> int:
    """Return a per-spell seed for mystery-bowler drift, changing each over."""
    return over


def pick_number(
    *,
    archetype: str,
    is_bowler: bool,
    recent_user_picks: list[int],
    difficulty: str = "medium",
    over_number: int = 0,
    fatigue: float = 0.0,
    aggression: float | None = None,
    opponent_outcomes: list[int] | None = None,
    epsilon: float | None = None,
    rng: random.Random | None = None,
) -> int:
    """Pick a 0–6 number for the bot. Pure function; uses rng if provided.

    ``fatigue`` (0=fresh, 1=gassed) only applies when bowling: it flattens the
    bowler's base distribution toward uniform and lowers its effective α.
    ``aggression`` (0=blocking, 0.5=neutral, 1=all-out), when given, only applies
    when batting: it reshapes the batter's base toward (or away from) boundaries.
    ``epsilon`` (0=exploit hard, 1=unexploitable), when given, switches adaptation
    to the richer opponent model (frequency + WSLS + bigram) mixed toward the
    equilibrium; ``opponent_outcomes`` are per-pick reward signs enabling WSLS.
    """
    rng = rng if rng is not None else random.Random()
    diff_alpha = DIFFICULTY_ALPHA.get(difficulty, 0.3)

    if is_bowler:
        base = list(profiles.BOWLER_BASE.get(archetype, profiles.BOWLER_BASE["pace"]))
        a_player = profiles.BOWLER_ALPHA.get(archetype, 0.3)
        if archetype == "mystery":
            # Rotate base each over (drift)
            shift = _mystery_drift_seed(over_number) % 7
            base = base[shift:] + base[:shift]
        if fatigue > 0:
            base, a_player = fatigue_mod.apply_fatigue(base, a_player, fatigue)
        if epsilon is not None:
            # Bowling = match the human: aim at where they are predicted to go.
            pred = opponent_mod.predict_next(recent_user_picks[-OPP_WINDOW:], (opponent_outcomes or [])[-OPP_WINDOW:])
            adapted = opponent_mod.exploit_mix(pred, epsilon)
        else:
            adapted = _adapted_for_bowling(recent_user_picks[-ADAPTIVE_WINDOW:])
    else:
        base = list(profiles.BATSMAN_BASE.get(archetype, profiles.BATSMAN_BASE["tail-ender"]))
        a_player = profiles.BATSMAN_ALPHA.get(archetype, 0.3)
        if aggression is not None:
            base = matchstate_mod.apply_matchstate(base, aggression)
        if epsilon is not None:
            # Batting = avoid the human's bowling pick: go where they are unlikely.
            pred = opponent_mod.predict_next(recent_user_picks[-OPP_WINDOW:], (opponent_outcomes or [])[-OPP_WINDOW:])
            adapted = opponent_mod.exploit_mix(opponent_mod.invert(pred), epsilon)
        else:
            adapted = _adapted_for_batting(recent_user_picks[-ADAPTIVE_WINDOW:])

    alpha = a_player * diff_alpha
    base = _normalize(base)
    final = [(1 - alpha) * b + alpha * a for b, a in zip(base, adapted, strict=False)]
    final = _normalize(final)

    return rng.choices(range(7), weights=final, k=1)[0]


def pick_extras_outcome(
    *,
    archetype: str,
    base_pct: float,
    rng: random.Random | None = None,
) -> tuple[bool, str | None]:
    """Decide whether this ball is an extra (wide/no-ball) before normal play.

    Returns (is_extra, kind). kind is "wide" or "no-ball" if is_extra is True.
    """
    rng = rng if rng is not None else random.Random()
    mod = profiles.BOWLER_EXTRAS_MOD.get(archetype, 1.0)
    if rng.random() >= base_pct * mod:
        return (False, None)
    p_wide, p_noball = profiles.extras_kind_probabilities(archetype)
    r = rng.random()
    if r < p_wide:
        return (True, "wide")
    return (True, "no-ball")


# Timeout outcome rolls
TIMEOUT_BOT_BOWLING = ["dot", "wide", "bowled", "lbw", "dead-ball"]
TIMEOUT_USER_BOWLING = ["wide", "no-ball", "byes", "leg-byes", "dead-ball"]


def roll_timeout_bot_bowling(rng: random.Random | None = None) -> str:
    rng = rng if rng is not None else random.Random()
    return rng.choice(TIMEOUT_BOT_BOWLING)


def roll_timeout_user_bowling(rng: random.Random | None = None) -> str:
    rng = rng if rng is not None else random.Random()
    return rng.choice(TIMEOUT_USER_BOWLING)
