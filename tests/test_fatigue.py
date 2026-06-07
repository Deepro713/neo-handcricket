"""Unit tests for the bowler fatigue model (M005)."""
from __future__ import annotations

import random

from neo_handcricket.bots import fatigue, strategy


def test_factor_bounds() -> None:
    # Always clamped to [0, 1] across a wide range of inputs.
    for ov in range(0, 40):
        for rest in range(0, 40):
            for arch in ("pace", "off-spin", "mystery"):
                f = fatigue.fatigue_factor(ov, rest, arch)
                assert 0.0 <= f <= 1.0


def test_fresh_bowler_has_zero_fatigue() -> None:
    assert fatigue.fatigue_factor(0, 0, "pace") == 0.0


def test_monotonic_increasing_in_workload() -> None:
    prev = -1.0
    for ov in range(0, 12):
        f = fatigue.fatigue_factor(ov, 0, "pace")
        assert f >= prev
        prev = f


def test_rest_reduces_fatigue() -> None:
    worked = fatigue.fatigue_factor(6, 0, "pace")
    rested = fatigue.fatigue_factor(6, 4, "pace")
    assert rested < worked


def test_pace_tires_faster_than_spin() -> None:
    # Same workload, no rest: a pacer is more fatigued than a spinner.
    assert fatigue.fatigue_factor(5, 0, "pace") > fatigue.fatigue_factor(5, 0, "off-spin")


def test_apply_fatigue_flattens_toward_uniform() -> None:
    base = [0.05, 0.08, 0.10, 0.12, 0.18, 0.22, 0.25]
    alpha = 0.4
    # At full fatigue the distribution is uniform and alpha is zero.
    dist, a = fatigue.apply_fatigue(base, alpha, 1.0)
    assert all(abs(p - 1 / 7) < 1e-9 for p in dist)
    assert a == 0.0
    # At zero fatigue the (normalised) base and alpha are preserved.
    dist0, a0 = fatigue.apply_fatigue(base, alpha, 0.0)
    assert abs(sum(dist0) - 1.0) < 1e-9
    assert a0 == alpha
    # Partial fatigue lies between: variance shrinks but isn't uniform.
    half, _ = fatigue.apply_fatigue(base, alpha, 0.5)
    spread_base = max(dist0) - min(dist0)
    spread_half = max(half) - min(half)
    assert spread_half < spread_base


def test_apply_fatigue_output_is_a_distribution() -> None:
    base = [0.10, 0.20, 0.25, 0.20, 0.12, 0.08, 0.05]
    for f in (0.0, 0.25, 0.5, 0.75, 1.0):
        dist, _ = fatigue.apply_fatigue(base, 0.6, f)
        assert abs(sum(dist) - 1.0) < 1e-9
        assert all(p >= 0 for p in dist)


def test_tired_bowler_concedes_more_over_many_balls() -> None:
    """A gassed bowler should match the batter (take wickets / dot) less often,
    i.e. a settled-frequency batter scores more freely against high fatigue."""
    # Simulate a batter who always plays the same number; the bowler tries to match.
    batter_pick = 4
    recent = [batter_pick] * 5

    def matches(fat: float, seed: int) -> int:
        rng = random.Random(seed)
        hits = 0
        for _ in range(400):
            p = strategy.pick_number(
                archetype="pace",
                is_bowler=True,
                recent_user_picks=recent,
                difficulty="hard",
                fatigue=fat,
                rng=rng,
            )
            if p == batter_pick:
                hits += 1
        return hits

    fresh_hits = matches(0.0, 1234)
    tired_hits = matches(0.9, 1234)
    # A fresh bowler reads & matches the predictable batter far more than a tired one.
    assert fresh_hits > tired_hits
