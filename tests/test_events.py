"""Unit tests for the big-moment event detector (M007)."""
from __future__ import annotations

from neo_handcricket.commentary import events
from neo_handcricket.innings import Innings


def _innings(overs_limit: int | None = 20, target: int | None = None) -> Innings:
    xi = list(range(1, 12))           # batters 1..11
    bowlers = list(range(101, 106))   # bowlers 101..105
    inn = Innings(
        batting_country="A", bowling_country="B",
        batting_xi=xi, bowling_xi=bowlers, bowling_pool=bowlers,
        overs_limit=overs_limit, wickets_limit=10, target=target,
    )
    inn.start_over(101)
    return inn


def _kinds(inn: Innings) -> list[str]:
    return [e.kind for e in events.detect(inn)]


def test_no_events_before_any_ball() -> None:
    inn = _innings()
    assert events.detect(inn) == []


def test_boundary_four_and_six() -> None:
    inn = _innings()
    inn.record_ball(runs=4)
    evs = events.detect(inn)
    assert any(e.kind == "boundary" and e.subtype == "4" for e in evs)
    inn.record_ball(runs=6)
    evs = events.detect(inn)
    assert any(e.kind == "boundary" and e.subtype == "6" for e in evs)


def test_wicket_carries_kind() -> None:
    inn = _innings()
    inn.record_ball(wicket="bowled")
    evs = events.detect(inn)
    assert any(e.kind == "wicket" and e.subtype == "bowled" for e in evs)


def test_individual_fifty_milestone() -> None:
    inn = _innings()
    # 12 fours = 48 (striker stays on strike on even runs), 13th four → 52 crosses 50.
    for _ in range(12):
        inn.record_ball(runs=4)
    assert "milestone" not in _kinds(inn)
    inn.record_ball(runs=4)
    evs = events.detect(inn)
    assert any(e.kind == "milestone" and e.subtype == "fifty" for e in evs)


def test_hat_trick_on_three_consecutive_wickets() -> None:
    inn = _innings()
    inn.record_ball(wicket="bowled")
    inn.record_ball(wicket="lbw")
    assert "hat_trick" not in _kinds(inn)
    inn.record_ball(wicket="match")
    assert "hat_trick" in _kinds(inn)


def test_collapse_without_hat_trick() -> None:
    inn = _innings()
    inn.record_ball(wicket="bowled")
    inn.record_ball(runs=0)
    inn.record_ball(wicket="lbw")
    inn.record_ball(runs=0)
    inn.record_ball(wicket="caught")
    evs = _kinds(inn)
    assert "collapse" in evs
    assert "hat_trick" not in evs   # spaced out, not three in a row


def test_maiden_over() -> None:
    inn = _innings()
    for _ in range(5):
        inn.record_ball(runs=0)
    assert "maiden" not in _kinds(inn)
    inn.record_ball(runs=0)   # sixth dot completes the over
    assert "maiden" in _kinds(inn)


def test_last_ball_finish() -> None:
    inn = _innings(overs_limit=1, target=2)
    for _ in range(5):
        inn.record_ball(runs=0)
    inn.record_ball(runs=2)   # sealed on the final ball
    assert "last_ball_finish" in _kinds(inn)


def test_fifty_partnership() -> None:
    inn = _innings()
    # 24 twos = 48 (stays on strike), 25th two → 50: partnership crosses 50.
    for _ in range(24):
        inn.record_ball(runs=2)
    assert "partnership" not in _kinds(inn)
    inn.record_ball(runs=2)
    assert "partnership" in _kinds(inn)
