"""Offline achievements / challenges (pure logic).

Achievements are evaluated from a match's detected :class:`Event` stream plus a
small result ``summary`` dict, so they're decoupled from the engine and trivially
testable. ``evaluate`` returns the set of achievement ids earned *this match*.
"""
from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

from ..commentary.events import Event

# A check sees the match's events and a result summary dict with (optional) keys:
#   won: bool, format: str, won_by_innings: bool, chase_target: int|None,
#   team_total: int, opponent: str.
Check = Callable[[list[Event], dict[str, Any]], bool]


def _kinds(events: list[Event]) -> set[tuple[str, str]]:
    return {(e.kind, e.subtype) for e in events}


ACHIEVEMENTS: dict[str, dict[str, Any]] = {
    "hat_trick": {
        "label": "Three in Three — take a hat-trick",
        "check": lambda ev, s: ("hat_trick", "") in _kinds(ev),
    },
    "century": {
        "label": "Ton Up — score a hundred",
        "check": lambda ev, s: ("milestone", "hundred") in _kinds(ev),
    },
    "half_century": {
        "label": "Steady Hand — score a fifty",
        "check": lambda ev, s: ("milestone", "fifty") in _kinds(ev),
    },
    "maiden_over": {
        "label": "Dot to Dot — bowl a maiden over",
        "check": lambda ev, s: ("maiden", "") in _kinds(ev),
    },
    "last_ball_thriller": {
        "label": "Down to the Wire — win off the last ball",
        "check": lambda ev, s: ("last_ball_finish", "") in _kinds(ev) and bool(s.get("won")),
    },
    "win_test_by_innings": {
        "label": "Innings and Plenty — win a Test by an innings",
        "check": lambda ev, s: bool(s.get("won")) and s.get("format") == "Test" and bool(s.get("won_by_innings")),
    },
    "big_chase": {
        "label": "Heist — chase down 200 or more",
        "check": lambda ev, s: bool(s.get("won")) and (s.get("chase_target") or 0) >= 200,
    },
    "survived_collapse": {
        "label": "Phoenix — win after a collapse",
        "check": lambda ev, s: ("collapse", "") in _kinds(ev) and bool(s.get("won")),
    },
}


def evaluate(events: Iterable[Event], summary: dict[str, Any]) -> set[str]:
    """Return the set of achievement ids earned by this match."""
    ev = list(events)
    return {aid for aid, spec in ACHIEVEMENTS.items() if spec["check"](ev, summary)}


def label(achievement_id: str) -> str:
    spec = ACHIEVEMENTS.get(achievement_id)
    return spec["label"] if spec else achievement_id
