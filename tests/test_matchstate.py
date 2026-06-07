"""Unit tests for the batsman match-state / momentum model (M005)."""
from __future__ import annotations

import random

from neo_handcricket.bots import matchstate, strategy


def test_settledness_monotonic_and_bounded() -> None:
    prev = -1.0
    for b in range(0, 60):
        s = matchstate.settledness(b)
        assert 0.0 <= s < 1.0
        assert s >= prev
        prev = s
    assert matchstate.settledness(0) == 0.0
    # Half-point at SETTLE_BALLS_K balls.
    assert abs(matchstate.settledness(8) - 0.5) < 1e-9


def test_chase_intent_rises_with_required_rate() -> None:
    assert matchstate.chase_intent(None, 60) == 0.0
    assert matchstate.chase_intent(0, 60) == 0.0
    assert matchstate.chase_intent(30, 0) == 0.0
    easy = matchstate.chase_intent(30, 120)   # 0.25/ball
    hard = matchstate.chase_intent(60, 30)    # 2/ball → saturates
    assert easy < hard
    assert 0.0 <= easy <= 1.0
    assert hard == 1.0


def test_aggression_bounds_and_ordering() -> None:
    fresh_calm = matchstate.aggression(0.0, 0.0)
    settled_calm = matchstate.aggression(1.0, 0.0)
    settled_chase = matchstate.aggression(1.0, 1.0)
    assert 0.0 <= fresh_calm <= settled_calm <= settled_chase <= 1.0
    assert fresh_calm < settled_chase


def test_apply_matchstate_neutral_is_identity() -> None:
    base = [0.05, 0.20, 0.25, 0.25, 0.15, 0.05, 0.05]
    out = matchstate.apply_matchstate(base, 0.5)
    norm = [b / sum(base) for b in base]
    assert all(abs(a - b) < 1e-9 for a, b in zip(out, norm, strict=True))


def test_apply_matchstate_tentative_vs_aggressive() -> None:
    base = [0.05, 0.15, 0.18, 0.20, 0.17, 0.12, 0.13]
    tentative = matchstate.apply_matchstate(base, 0.0)
    aggressive = matchstate.apply_matchstate(base, 1.0)
    # Boundary mass (4s + 6s = idx 4 and 6) is higher when aggressive.
    assert aggressive[4] + aggressive[6] > tentative[4] + tentative[6]
    assert aggressive[6] > tentative[6]
    assert tentative[1] > aggressive[1]  # low scores favoured when tentative
    for dist in (tentative, aggressive):
        assert abs(sum(dist) - 1.0) < 1e-9
        assert all(p >= 0 for p in dist)


def test_aggressive_batter_scores_bigger_over_many_balls() -> None:
    """An aggressive batter picks 4/6 more often than a tentative one."""
    base_arch = "anchor"

    def big_shot_rate(aggr: float, seed: int) -> int:
        rng = random.Random(seed)
        big = 0
        for _ in range(500):
            p = strategy.pick_number(
                archetype=base_arch,
                is_bowler=False,
                recent_user_picks=[],
                difficulty="medium",
                aggression=aggr,
                rng=rng,
            )
            if p in (4, 6):
                big += 1
        return big

    tentative = big_shot_rate(0.1, 99)
    aggressive = big_shot_rate(0.95, 99)
    assert aggressive > tentative
