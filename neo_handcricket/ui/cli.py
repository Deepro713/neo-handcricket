"""Top-level CLI display loop — split-view-ish layout (full-redraw per frame).

Pinned scoreboard at top, scrolling commentary below. We don't use Rich's Live —
each "frame" is a full redraw, which composes cleanly with raw-input mode for
the 3-second timer.
"""
from __future__ import annotations

import sys

from rich.console import Console

from .. import a11y
from ..commentary.engine import CommentaryEngine
from ..match import Match
from . import scoreboard


def make_console() -> Console:
    # Honour NO_COLOR / a11y mode (community-standard accessibility).
    return Console(highlight=False, no_color=not a11y.color_enabled())


def render_frame(
    console: Console,
    match: Match,
    engine: CommentaryEngine,
    *,
    recent_n: int = 8,
    show_compact: bool = True,
    show_detailed: bool = False,
) -> None:
    console.clear()
    if show_compact:
        scoreboard.render_compact(console, match)
    if show_detailed:
        scoreboard.render_detailed(console, match)
    # Scrolling commentary
    console.print()
    for entry in engine.log.recent(recent_n):
        c_label = f"[dim]({entry.commentator})[/dim]"
        console.print(f"  ▸ {entry.line}  {c_label}")
    console.print()


def update_prompt_line(prompt: str, timer_remaining: float | None = None) -> None:
    """Overwrite the bottom line in place — used while the 3-second timer ticks."""
    if timer_remaining is not None:
        bar_len = 12
        filled = int(round(bar_len * (timer_remaining / 3.0)))
        bar = "█" * filled + "·" * (bar_len - filled)
        sys.stdout.write(f"\r\033[K  {prompt}  [{bar}]  {timer_remaining:0.1f}s")
    else:
        sys.stdout.write(f"\r\033[K  {prompt}")
    sys.stdout.flush()


def newline() -> None:
    sys.stdout.write("\n")
    sys.stdout.flush()
