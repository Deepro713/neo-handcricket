"""Pure view-model for the TUI — turns adapter state into display strings.

No Textual dependency, no I/O: just formats the structured state from
``adapter.GameAdapter.state()`` so the (optional) Textual app stays a thin shell.
"""
from __future__ import annotations

from typing import Any


def scoreboard_lines(state: dict[str, Any]) -> list[str]:
    lines = [f"{state['batting']}  {state['runs']}/{state['wickets']}  ({state['overs']} ov)"]
    if state.get("target") is not None:
        need, balls = state.get("runs_needed"), state.get("balls_remaining")
        lines.append(f"Target {state['target']}" + (f" — need {need} off {balls}" if need and balls else ""))
    over = " ".join(state.get("this_over") or []) or "—"
    lines.append(f"This over: {over}")
    return lines


def prompt_text(state: dict[str, Any]) -> str:
    if state.get("complete"):
        return f"Innings complete — {state['runs']}/{state['wickets']}"
    return "Pick a number 0–6"


def event_line(events: list[tuple[str, str]]) -> str:
    """A short human line for the ball's detected events (or empty)."""
    if not events:
        return ""
    labels = {
        "wicket": "WICKET", "boundary": "boundary", "milestone": "milestone",
        "hat_trick": "HAT-TRICK!", "last_ball_finish": "last-ball finish!",
        "collapse": "collapse", "maiden": "maiden over", "partnership": "50 partnership",
    }
    kinds = [labels.get(k, k) for k, _ in events]
    return " · ".join(dict.fromkeys(kinds))  # de-duped, order-preserving
