"""Smoke tests for the thin campaign UI (M008) — renders without error, no logic."""
from __future__ import annotations

from rich.console import Console

from neo_handcricket.career import progression as prog
from neo_handcricket.ui import campaign


def _console() -> Console:
    return Console(file=open("/dev/null", "w"), force_terminal=False)


def test_dashboard_renders_empty_state() -> None:
    campaign.render_dashboard(_console(), prog.new_progression(), set())


def test_dashboard_renders_with_unlocks_and_achievements() -> None:
    state = prog.bank(prog.new_progression(), 500)
    state = prog.unlock(state, "panel_comedy")
    campaign.render_dashboard(_console(), state, {"hat_trick", "century"})


def test_unlock_toast_renders() -> None:
    campaign.unlock_toast(_console(), "Legends XI (bonus opponent)")
