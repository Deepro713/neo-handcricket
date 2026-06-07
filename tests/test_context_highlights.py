"""Unit tests for context-aware lines + the highlights reel (M007)."""
from __future__ import annotations

import random

from neo_handcricket.commentary import context
from neo_handcricket.commentary.events import Event
from neo_handcricket.commentary.highlights import build_highlights


def test_context_none_when_no_condition() -> None:
    rng = random.Random(0)
    for _ in range(50):
        assert context.context_line(bowler_fatigue=0.1, batter_settledness=0.1, ai_read=False, rng=rng) is None


def test_context_fatigue_line_emitted() -> None:
    rng = random.Random(1)
    # emit_prob=1 guarantees a line when the condition holds.
    line = context.context_line(bowler_fatigue=0.9, batter_settledness=0.0, rng=rng, emit_prob=1.0)
    assert line in context.FATIGUE_LINES


def test_context_settled_line_emitted() -> None:
    rng = random.Random(2)
    line = context.context_line(batter_settledness=0.8, rng=rng, emit_prob=1.0)
    assert line in context.SETTLED_LINES


def test_context_ai_read_line_emitted() -> None:
    rng = random.Random(3)
    line = context.context_line(ai_read=True, rng=rng, emit_prob=1.0)
    assert line in context.AI_READ_LINES


def test_context_respects_emit_prob() -> None:
    rng = random.Random(4)
    # emit_prob=0 → never emit even when a condition holds.
    assert all(
        context.context_line(bowler_fatigue=0.9, rng=rng, emit_prob=0.0) is None
        for _ in range(50)
    )


def _name(pid: int) -> str:
    return {1: "Ari", 2: "Bo", 101: "Cam"}.get(pid, f"#{pid}")


def test_highlights_keeps_noteworthy_only() -> None:
    events = [
        Event("boundary", "4", 1),               # too frequent — excluded
        Event("milestone", "fifty", 1, {"runs": 52}),
        Event("hat_trick", player_id=101),
        Event("wicket", "bowled", 2),            # excluded from reel
        Event("last_ball_finish"),
    ]
    reel = build_highlights(events, _name)
    joined = " | ".join(reel)
    assert "Ari" in joined and "fifty" in joined
    assert "hat-trick" in joined
    assert "last-ball" in joined
    assert "boundary" not in joined.lower()
    assert len(reel) == 3


def test_highlights_dedupes_and_limits() -> None:
    events = [Event("milestone", "fifty", 1, {"runs": 50}) for _ in range(5)]
    events += [Event("hat_trick", player_id=101) for _ in range(20)]
    reel = build_highlights(events, _name, limit=4)
    assert len(reel) <= 4
    # Identical formatted lines are de-duplicated.
    assert len(reel) == len(set(reel))


def test_century_formats_distinctly() -> None:
    reel = build_highlights([Event("milestone", "hundred", 1, {"runs": 101})], _name)
    assert reel and "century" in reel[0]
