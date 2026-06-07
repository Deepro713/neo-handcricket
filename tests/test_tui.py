"""Unit tests for the optional TUI's pure view-model + import guard (M011)."""
from __future__ import annotations

from neo_handcricket.tui import app, viewmodel

SAMPLE = {
    "batting": "India", "bowling": "Australia", "runs": 84, "wickets": 3,
    "overs": "9.2", "striker_id": 1, "bowler_id": 101, "this_over": ["4", "1", "W"],
    "target": None, "runs_needed": None, "balls_remaining": None, "complete": False,
}


def test_scoreboard_lines() -> None:
    lines = viewmodel.scoreboard_lines(SAMPLE)
    assert any("India" in line and "84/3" in line for line in lines)
    assert any("This over" in line for line in lines)


def test_scoreboard_shows_chase() -> None:
    state = {**SAMPLE, "target": 150, "runs_needed": 66, "balls_remaining": 40}
    lines = viewmodel.scoreboard_lines(state)
    assert any("Target 150" in line and "need 66 off 40" in line for line in lines)


def test_prompt_text() -> None:
    assert "0" in viewmodel.prompt_text(SAMPLE)
    assert "complete" in viewmodel.prompt_text({**SAMPLE, "complete": True}).lower()


def test_event_line_dedupes_and_labels() -> None:
    assert viewmodel.event_line([]) == ""
    line = viewmodel.event_line([("wicket", "bowled"), ("hat_trick", ""), ("wicket", "lbw")])
    assert "WICKET" in line and "HAT-TRICK!" in line
    assert line.count("WICKET") == 1   # de-duped


def test_is_available_returns_bool() -> None:
    assert isinstance(app.is_available(), bool)


def test_run_without_textual_raises_cleanly(monkeypatch) -> None:
    # When Textual is absent, run() must raise a clear error, not crash on import.
    monkeypatch.setattr(app, "is_available", lambda: False)
    import pytest

    from neo_handcricket.adapter import AdapterConfig
    with pytest.raises(RuntimeError, match="Textual"):
        app.run(AdapterConfig(batting="india", bowling="australia"))
