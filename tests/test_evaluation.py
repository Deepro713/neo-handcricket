"""Unit tests for the offline AI eval harness (M006): model beats frequency baseline."""
from __future__ import annotations

import random

from neo_handcricket.bots import evaluation as ev

CHANCE = 1 / 7
PREDICTABLE = ["favourite", "wsls", "sequence"]


def test_patterns_return_valid_picks() -> None:
    rng = random.Random(0)
    for pat in ev.PATTERNS.values():
        picks: list[int] = []
        outcomes: list[int] = []
        for _ in range(30):
            p = pat(rng, picks, outcomes)
            assert 0 <= p <= 6
            picks.append(p)
            outcomes.append(rng.choice((-1, 1)))


def test_match_rate_is_a_fraction() -> None:
    r = ev.simulate_match_rate(ev.uniform_pattern, epsilon=0.08, n_balls=200, seed=3)
    assert 0.0 <= r <= 1.0


def test_model_beats_baseline_on_predictable_players() -> None:
    # Aggregated across predictable patterns and several seeds, the opponent model
    # dismisses more often than the frequency-only baseline.
    model = baseline = 0.0
    for seed in range(6):
        r = ev.evaluate(seed=seed)
        for name in PREDICTABLE:
            model += r[name]["model"]
            baseline += r[name]["baseline"]
    assert model > baseline


def test_favourite_player_is_strongly_exploited() -> None:
    # A batter who always plays the same number is dismissed well above chance.
    rates = [
        ev.simulate_match_rate(ev.favourite_pattern(4), epsilon=0.08, seed=s)
        for s in range(4)
    ]
    assert sum(rates) / len(rates) > 0.20  # chance is ~0.143


def test_uniform_player_has_no_exploitable_edge() -> None:
    # Against a truly random player neither model nor baseline beats chance much,
    # and the model doesn't hurt itself.
    model = [ev.simulate_match_rate(ev.uniform_pattern, epsilon=0.08, seed=s) for s in range(6)]
    mean = sum(model) / len(model)
    assert abs(mean - CHANCE) < 0.04
