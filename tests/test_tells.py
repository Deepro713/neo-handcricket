"""Unit tests for player-facing tells (M006)."""
from __future__ import annotations

import random

from neo_handcricket.bots import tells
from neo_handcricket.config import TELLS_ENABLED


def test_disabled_by_default() -> None:
    assert TELLS_ENABLED is False


def test_archetype_zone_matches_distribution() -> None:
    # off-spin favours the low end; pace the high end.
    assert tells.archetype_zone("off-spin") == "low"
    assert tells.archetype_zone("pace") == "high"


def test_generate_tell_returns_a_known_line() -> None:
    rng = random.Random(0)
    all_lines = {ln for lines in tells.TELL_LINES.values() for ln in lines} | set(tells.TIRED_LINES)
    for _ in range(50):
        t = tells.generate_tell("leg-spin", 0.2, rng=rng)
        assert t in all_lines


def test_tell_never_contains_a_digit() -> None:
    # A tell must never leak an exact number.
    rng = random.Random(3)
    for _ in range(200):
        t = tells.generate_tell("mystery", rng.random(), rng=rng)
        assert not any(ch.isdigit() for ch in t)


def test_truthful_prob_controls_accuracy() -> None:
    # With truthful_prob=1 (and no fatigue telegraph), the tell always points at the
    # archetype's true zone; with 0 it always bluffs to a different zone.
    rng = random.Random(7)
    true_zone = tells.archetype_zone("off-spin")
    true_lines = set(tells.TELL_LINES[true_zone])
    always_true = [tells.generate_tell("off-spin", 0.0, rng=rng, truthful_prob=1.0) for _ in range(40)]
    assert all(t in true_lines for t in always_true)
    always_bluff = [tells.generate_tell("off-spin", 0.0, rng=rng, truthful_prob=0.0) for _ in range(40)]
    assert all(t not in true_lines for t in always_bluff)


def test_tired_bowler_can_telegraph() -> None:
    # A gassed bowler sometimes drops a fatigue tell.
    rng = random.Random(1)
    seen = {tells.generate_tell("pace", 0.95, rng=rng) for _ in range(200)}
    assert seen & set(tells.TIRED_LINES)
