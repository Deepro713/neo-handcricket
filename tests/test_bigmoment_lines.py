"""Unit tests for big-moment commentary line banks + event→situation mapping (M007)."""
from __future__ import annotations

import random

from neo_handcricket.commentary import lines as L
from neo_handcricket.commentary.engine import CommentaryEngine
from neo_handcricket.commentary.events import Event

BIG_MOMENT_KEYS = [
    "wicket_caught", "hat_trick", "maiden", "last_ball_finish", "collapse", "partnership_50",
]


def test_every_category_has_at_least_one_opener_line() -> None:
    for key in BIG_MOMENT_KEYS:
        assert key in L.LINES, f"missing line bank: {key}"
        openers = L.LINES[key].get("opener", [])
        assert openers, f"no opener lines for {key}"
        for line in openers:
            assert line["text"].strip()


def test_event_situation_priority() -> None:
    # last-ball finish outranks everything.
    evs = [Event("milestone", "fifty"), Event("last_ball_finish")]
    assert L.event_situation(evs) == "last_ball_finish"
    # hundred outranks fifty.
    assert L.event_situation([Event("milestone", "hundred"), Event("milestone", "fifty")]) == "milestone_100"
    # hat-trick outranks a plain milestone.
    assert L.event_situation([Event("hat_trick"), Event("milestone", "fifty")]) == "hat_trick"
    # partnership and maiden are recognised.
    assert L.event_situation([Event("partnership", "fifty")]) == "partnership_50"
    assert L.event_situation([Event("maiden")]) == "maiden"


def test_event_situation_none_for_plain_ball_events() -> None:
    # Wickets and boundaries are handled by the ball conversation, not an accent.
    assert L.event_situation([Event("wicket", "bowled")]) is None
    assert L.event_situation([Event("boundary", "4")]) is None
    assert L.event_situation([]) is None


def test_caught_maps_to_caught_situation() -> None:
    assert L.situation_for_ball(0, "caught", None) == "wicket_caught"


def test_engine_renders_each_big_moment() -> None:
    for key in BIG_MOMENT_KEYS:
        eng = CommentaryEngine(rng=random.Random(0))
        entries = eng.commentate(situation=key, ctx={"batter": "X", "bowler": "Y"}, antarctica_on_field=False)
        assert entries, f"no commentary produced for {key}"
        assert entries[0].line.strip() not in ("", "...")


def test_no_within_match_duplicate_lines() -> None:
    # Over many balls the engine should not repeat an identical rendered line while
    # fresh templates remain (placeholders make exact dup unlikely, but raw-template
    # dedup is enforced).
    eng = CommentaryEngine(rng=random.Random(1))
    seen: list[str] = []
    for _ in range(40):
        for e in eng.commentate(situation="ball_dot", ctx={"batter": "Z", "bowler": "Q", "score": "10/0"}):
            seen.append(e.line)
    # ball_dot has a finite pool; once exhausted repeats are allowed, but there must
    # be clear variety (more than a handful of distinct lines).
    assert len(set(seen)) >= 6
