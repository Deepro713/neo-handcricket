"""Offline AI evaluation harness (pure logic).

Plays the bot (bowling, trying to MATCH the batter = dismiss) against a battery of
scripted human-like batting patterns and measures the dismissal (match) rate. Used
to prove the M006 opponent model beats the frequency-only baseline against
predictable players, while neither does better than chance against a uniform random
player. No I/O; deterministic under a seed.
"""
from __future__ import annotations

import random
from collections.abc import Callable

from . import strategy

# A pattern maps (rng, past_picks, past_outcomes) -> next batting pick in 0..6.
# ``past_outcomes[i]`` is +1 if that batting pick scored (bot missed), -1 if matched.
Pattern = Callable[[random.Random, list[int], list[int]], int]


def uniform_pattern(rng: random.Random, picks: list[int], outcomes: list[int]) -> int:
    return rng.randint(0, 6)


def favourite_pattern(number: int = 4) -> Pattern:
    def pat(rng: random.Random, picks: list[int], outcomes: list[int]) -> int:
        return number
    return pat


def wsls_pattern(rng: random.Random, picks: list[int], outcomes: list[int]) -> int:
    """Win-Stay-Lose-Shift batter: repeat after a good ball, shift after a bad one."""
    if not picks:
        return rng.randint(0, 6)
    if outcomes[-1] > 0:
        return picks[-1]
    return (picks[-1] + 1 + rng.randint(0, 5)) % 7


def sequence_pattern(rng: random.Random, picks: list[int], outcomes: list[int]) -> int:
    """Cycles through a fixed run of numbers."""
    cycle = [1, 2, 3, 4, 5]
    return cycle[len(picks) % len(cycle)]


PATTERNS: dict[str, Pattern] = {
    "uniform": uniform_pattern,
    "favourite": favourite_pattern(4),
    "wsls": wsls_pattern,
    "sequence": sequence_pattern,
}


def simulate_match_rate(
    pattern: Pattern, *, epsilon: float | None, n_balls: int = 800, seed: int = 0
) -> float:
    """Fraction of balls on which the bot bowler matches (dismisses) the scripted
    batter. ``epsilon=None`` uses the legacy frequency baseline; a float uses the
    opponent model at that exploit level.
    """
    rng_bot = random.Random(seed)
    rng_bat = random.Random(seed + 9973)
    picks: list[int] = []
    outcomes: list[int] = []
    matches = 0
    for _ in range(n_balls):
        bot = strategy.pick_number(
            archetype="pace", is_bowler=True, recent_user_picks=picks,
            difficulty="hard", epsilon=epsilon, opponent_outcomes=outcomes, rng=rng_bot,
        )
        bat = pattern(rng_bat, picks, outcomes)
        matched = bot == bat
        if matched:
            matches += 1
        picks.append(bat)
        outcomes.append(-1 if matched else 1)  # batter is "rewarded" when NOT matched
    return matches / n_balls


def evaluate(*, model_epsilon: float = 0.08, n_balls: int = 800, seed: int = 0) -> dict[str, dict[str, float]]:
    """For each pattern, the bot's match rate with the opponent model vs the
    frequency-only baseline. Returns ``{pattern: {"model": r, "baseline": r}}``."""
    out: dict[str, dict[str, float]] = {}
    for name, pat in PATTERNS.items():
        out[name] = {
            "model": simulate_match_rate(pat, epsilon=model_epsilon, n_balls=n_balls, seed=seed),
            "baseline": simulate_match_rate(pat, epsilon=None, n_balls=n_balls, seed=seed),
        }
    return out
