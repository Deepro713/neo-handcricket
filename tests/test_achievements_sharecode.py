"""Unit tests for achievements + shareable save codes (M008)."""
from __future__ import annotations

from neo_handcricket.career import achievements as ach
from neo_handcricket.career import sharecode
from neo_handcricket.commentary.events import Event


def test_hat_trick_and_century_fire() -> None:
    events = [Event("hat_trick", player_id=9), Event("milestone", "hundred", 1, {"runs": 101})]
    earned = ach.evaluate(events, {})
    assert "hat_trick" in earned
    assert "century" in earned
    assert "half_century" not in earned


def test_last_ball_requires_win() -> None:
    events = [Event("last_ball_finish")]
    assert "last_ball_thriller" not in ach.evaluate(events, {"won": False})
    assert "last_ball_thriller" in ach.evaluate(events, {"won": True})


def test_win_test_by_innings() -> None:
    s = {"won": True, "format": "Test", "won_by_innings": True}
    assert "win_test_by_innings" in ach.evaluate([], s)
    assert "win_test_by_innings" not in ach.evaluate([], {"won": True, "format": "T20", "won_by_innings": True})


def test_big_chase_threshold() -> None:
    assert "big_chase" in ach.evaluate([], {"won": True, "chase_target": 200})
    assert "big_chase" not in ach.evaluate([], {"won": True, "chase_target": 199})
    assert "big_chase" not in ach.evaluate([], {"won": False, "chase_target": 250})


def test_no_achievements_for_empty_match() -> None:
    assert ach.evaluate([], {}) == set()


def test_label_lookup() -> None:
    assert "hat-trick" in ach.label("hat_trick").lower()
    assert ach.label("unknown_id") == "unknown_id"


def test_sharecode_round_trip() -> None:
    data = {"result": "win", "seed": 4242, "format": "T20", "margin": "7 wkts"}
    code = sharecode.encode(data)
    assert code.startswith("NHC1-")
    assert sharecode.decode(code) == data


def test_sharecode_is_case_insensitive_and_trims() -> None:
    code = sharecode.encode({"a": 1, "b": [1, 2, 3]})
    assert sharecode.decode("  " + code.lower() + "  ") == {"a": 1, "b": [1, 2, 3]}


def test_sharecode_corruption_returns_none() -> None:
    assert sharecode.decode("not a real code !!!") is None
    assert sharecode.decode("NHC1-AAAAAAAA") is None   # valid b32 but not valid zlib
    assert sharecode.decode("") is None


def test_sharecode_compact() -> None:
    code = sharecode.encode({"result": "win", "seed": 12345})
    # Comfortably copy-pasteable.
    assert len(code) < 120
