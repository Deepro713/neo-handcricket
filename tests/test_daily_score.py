"""Unit tests for daily scoring + best-table + persistence (M009)."""
from __future__ import annotations

from neo_handcricket.career import sharecode
from neo_handcricket.daily import score


def test_win_beats_loss() -> None:
    win = score.score_result(won=True, runs_margin=10)
    loss = score.score_result(won=False, runs_margin=10)
    assert win > loss


def test_score_monotonic_in_each_input() -> None:
    base = score.score_result(won=True)
    assert score.score_result(won=True, runs_margin=20) > base
    assert score.score_result(won=True, wickets_margin=5) > base
    assert score.score_result(won=True, balls_to_spare=10) > base
    assert score.score_result(won=True, wickets_in_hand=4) > base


def test_negative_inputs_clamped() -> None:
    assert score.score_result(won=True, runs_margin=-50) == score.score_result(won=True)


def test_update_best_keeps_higher() -> None:
    table: dict = {}
    e1 = score.make_entry("2026-06-07", 20260607, 1200)
    e2 = score.make_entry("2026-06-07", 20260607, 1500)
    e3 = score.make_entry("2026-06-07", 20260607, 900)
    table = score.update_best(table, e1)
    table = score.update_best(table, e2)
    table = score.update_best(table, e3)   # lower → ignored
    assert score.best_for(table, "2026-06-07")["score"] == 1500


def test_update_best_is_per_date() -> None:
    table: dict = {}
    table = score.update_best(table, score.make_entry("2026-06-07", 1, 100))
    table = score.update_best(table, score.make_entry("2026-06-08", 2, 50))
    assert score.best_for(table, "2026-06-07")["score"] == 100
    assert score.best_for(table, "2026-06-08")["score"] == 50
    assert score.best_for(table, "2026-06-09") is None


def test_entry_round_trips_through_sharecode() -> None:
    entry = score.make_entry("2026-06-07", 20260607, 1330, summary="won by 7 wkts")
    code = sharecode.encode(entry)
    assert sharecode.decode(code) == entry


def test_persistence_round_trip(tmp_path, monkeypatch) -> None:
    import neo_handcricket.persistence.daily as pd

    monkeypatch.setattr(pd, "DAILY_FILE", tmp_path / "daily.json")
    assert pd.load_best_table() == {}
    table = score.update_best({}, score.make_entry("2026-06-07", 20260607, 1410))
    pd.save_best_table(table)
    assert pd.load_best_table() == table
