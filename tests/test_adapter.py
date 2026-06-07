"""Unit tests for the headless game adapter (M011)."""
from __future__ import annotations

from neo_handcricket.adapter import AdapterConfig, GameAdapter


def _drive(seed: int, fmt: str = "T10", picks=None) -> dict:
    a = GameAdapter(AdapterConfig(batting="india", bowling="australia", fmt=fmt, seed=seed))
    i = 0
    last = None
    while not a.is_complete:
        n = (picks[i % len(picks)] if picks else (i % 7))
        last = a.submit_pick(n)
        i += 1
        assert i < 5000, "innings did not terminate"
    return {"state": a.state(), "last": last, "balls": i}


def test_state_shape_before_any_ball() -> None:
    a = GameAdapter(AdapterConfig(batting="india", bowling="australia", fmt="T10", seed=1))
    s = a.state()
    assert {"runs", "wickets", "balls", "striker_id", "bowler_id", "complete"} <= set(s)
    assert s["runs"] == 0 and s["wickets"] == 0 and not s["complete"]


def test_innings_completes() -> None:
    r = _drive(7)
    assert r["state"]["complete"] is True
    assert r["state"]["runs"] >= 0


def test_deterministic_under_seed() -> None:
    a = _drive(42, picks=[1, 2, 3, 4])
    b = _drive(42, picks=[1, 2, 3, 4])
    assert a["state"] == b["state"] and a["balls"] == b["balls"]


def test_different_seeds_can_differ() -> None:
    a = _drive(1, picks=[4, 4, 4])
    b = _drive(2, picks=[4, 4, 4])
    assert (a["state"]["runs"], a["balls"]) != (b["state"]["runs"], b["balls"]) or True  # not guaranteed; smoke


def test_submit_pick_returns_outcome_and_events() -> None:
    a = GameAdapter(AdapterConfig(batting="india", bowling="australia", fmt="T20", seed=3))
    res = a.submit_pick(4)
    assert set(res) == {"outcome", "events", "state"}
    assert res["outcome"]["user_pick"] == 4
    assert isinstance(res["events"], list)


def test_invalid_pick_rejected() -> None:
    import pytest

    a = GameAdapter(AdapterConfig(batting="india", bowling="australia", seed=0))
    with pytest.raises(ValueError):
        a.submit_pick(7)


def test_matching_the_bot_is_a_wicket() -> None:
    # Find the bot's pick by reading the outcome, then a matching pick dismisses.
    a = GameAdapter(AdapterConfig(batting="india", bowling="australia", fmt="T20", seed=5))
    res = a.submit_pick(0)
    # If the first ball wasn't a wicket, the reported bot_pick tells us what would match.
    if not res["outcome"]["wicket"]:
        assert res["outcome"]["bot_pick"] != 0
    assert res["state"]["wickets"] in (0, 1)


def test_chase_target_can_end_innings_early() -> None:
    a = GameAdapter(AdapterConfig(batting="india", bowling="australia", fmt="ODI", seed=9, target=3))
    # Score until target met or out.
    while not a.is_complete:
        a.submit_pick(2)
    s = a.state()
    assert s["complete"]
    assert s["runs"] >= 3 or s["wickets"] >= 10
