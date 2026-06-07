"""Unit tests for the opponent model (M006): frequency + WSLS + bigram, exploit-mix."""
from __future__ import annotations

import random

from neo_handcricket.bots import opponent, strategy


def _is_distribution(d: list[float]) -> bool:
    return abs(sum(d) - 1.0) < 1e-9 and all(p >= 0 for p in d) and len(d) == 7


def test_empty_history_is_uniform() -> None:
    assert opponent.predict_next([]) == [1 / 7] * 7


def test_predict_is_distribution() -> None:
    assert _is_distribution(opponent.predict_next([1, 2, 3, 1, 2]))
    assert _is_distribution(opponent.predict_next([4, 4, 4], [1, 1, 1]))


def test_frequency_favours_common_pick() -> None:
    # No outcomes → frequency + bigram. A heavily repeated number scores highest.
    d = opponent.predict_next([5, 5, 5, 5, 2])
    assert d[5] == max(d)


def test_wsls_stay_after_reward() -> None:
    # Last pick 3 was rewarding → predict they STAY on 3.
    d = opponent.predict_next([1, 2, 3], [0, 0, 1])
    assert d[3] == max(d)


def test_wsls_shift_after_failure() -> None:
    # Last pick 3 failed → predict they SHIFT away from 3 (3 should be low).
    d = opponent.predict_next([6, 6, 3], [1, 1, -1])
    assert d[3] < sum(d) / 7  # below average mass


def test_bigram_predicts_follower() -> None:
    # The human always plays 2 after 1; last pick is 1 → predict 2 strongly.
    picks = [1, 2, 1, 2, 1, 2, 1]
    d = opponent.predict_next(picks)
    assert d[2] == max(d)


def test_exploit_mix_endpoints() -> None:
    sharp = [0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0]
    assert opponent.exploit_mix(sharp, 0.0) == sharp                 # exploit fully
    mixed = opponent.exploit_mix(sharp, 1.0)
    assert all(abs(p - 1 / 7) < 1e-9 for p in mixed)                # fully uniform
    half = opponent.exploit_mix(sharp, 0.5)
    assert _is_distribution(half) and half[2] < 1.0 and half[0] > 0  # in between


def test_invert_avoids_likely_pick() -> None:
    pred = [0.0, 0.0, 0.7, 0.0, 0.3, 0.0, 0.0]
    inv = opponent.invert(pred)
    assert _is_distribution(inv)
    assert inv[2] < inv[0]   # avoid the most-likely pick


def test_strategy_exploits_predictable_batter_more_at_low_epsilon() -> None:
    """When bowling, a low-epsilon bot matches a predictable batter more often."""
    batter_pick = 4
    recent = [batter_pick] * 12

    def match_rate(eps: float, seed: int) -> int:
        rng = random.Random(seed)
        return sum(
            strategy.pick_number(
                archetype="pace", is_bowler=True, recent_user_picks=recent,
                difficulty="hard", epsilon=eps, rng=rng,
            ) == batter_pick
            for _ in range(500)
        )

    exploit = match_rate(0.05, 7)
    mix = match_rate(0.9, 7)
    assert exploit > mix


def test_high_epsilon_is_near_uniform_and_unexploitable() -> None:
    # At epsilon ~1 the predicted-adapted component is uniform; the bot is not a
    # deterministic target. Check the adapted distribution directly.
    pred = opponent.predict_next([2, 2, 2, 2, 2])
    near_uniform = opponent.exploit_mix(pred, 1.0)
    assert max(near_uniform) - min(near_uniform) < 1e-9
