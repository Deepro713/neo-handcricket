"""Unit tests for difficulty tiers wiring the opponent model (M006)."""
from __future__ import annotations

import random

from neo_handcricket.bots import strategy
from neo_handcricket.config import DIFFICULTY_ALPHA, DIFFICULTY_EPSILON


def test_all_tiers_defined() -> None:
    for tier in ("easy", "medium", "hard", "legend"):
        assert tier in DIFFICULTY_ALPHA
        assert tier in DIFFICULTY_EPSILON
    # Epsilon decreases (more exploitation) as difficulty rises.
    assert (
        DIFFICULTY_EPSILON["easy"]
        > DIFFICULTY_EPSILON["medium"]
        > DIFFICULTY_EPSILON["hard"]
        > DIFFICULTY_EPSILON["legend"]
    )


def _match_rate_vs_predictable_batter(difficulty: str, seed: int) -> int:
    """How often the bot (bowling) matches a batter who always plays 4."""
    recent = [4] * 12
    rng = random.Random(seed)
    return sum(
        strategy.pick_number(
            archetype="pace", is_bowler=True, recent_user_picks=recent,
            difficulty=difficulty, epsilon=DIFFICULTY_EPSILON[difficulty], rng=rng,
        ) == 4
        for _ in range(600)
    )


def test_harder_tiers_exploit_more() -> None:
    easy = _match_rate_vs_predictable_batter("easy", 13)
    hard = _match_rate_vs_predictable_batter("hard", 13)
    legend = _match_rate_vs_predictable_batter("legend", 13)
    # A predictable batter is matched (dismissed) more often as difficulty rises.
    assert legend > hard > easy
