"""Match highlights reel (pure logic).

Turns an accumulated stream of detected :class:`Event`s into an ordered list of
short, human-readable highlight strings for the match summary. Pure: takes the
events plus a name-resolver callback. The most newsworthy moments are kept.
"""
from __future__ import annotations

from collections.abc import Callable, Iterable

from .events import Event

# Kinds worth putting in a highlights reel, with a formatter. Boundaries/dots are
# too frequent to list individually; collapses, milestones and finishes are not.
_NOTEWORTHY = {
    "milestone",
    "hat_trick",
    "last_ball_finish",
    "collapse",
    "partnership",
    "maiden",
}


def _format(ev: Event, name_of: Callable[[int], str]) -> str | None:
    who = name_of(ev.player_id) if ev.player_id is not None else ""
    if ev.kind == "milestone":
        runs = ev.detail.get("runs")
        label = "century" if ev.subtype == "hundred" else "fifty"
        tail = f" ({runs})" if runs else ""
        return f"💯 {who} brought up a {label}{tail}" if ev.subtype == "hundred" else f"⭐ {who} brought up a {label}{tail}"
    if ev.kind == "hat_trick":
        return f"🎩 {who} took a hat-trick"
    if ev.kind == "last_ball_finish":
        return "🔥 Sealed at the death — a last-ball finish"
    if ev.kind == "collapse":
        return "📉 A dramatic collapse"
    if ev.kind == "partnership":
        runs = ev.detail.get("runs", 50)
        return f"🤝 A {runs}-run partnership"
    if ev.kind == "maiden":
        return f"🧱 {who} bowled a maiden"
    return None


def build_highlights(events: Iterable[Event], name_of: Callable[[int], str], *, limit: int = 8) -> list[str]:
    """Ordered, de-duplicated highlight lines from the event stream (most recent kept
    when over ``limit``)."""
    out: list[str] = []
    seen: set[str] = set()
    for ev in events:
        if ev.kind not in _NOTEWORTHY:
            continue
        line = _format(ev, name_of)
        if line and line not in seen:
            seen.add(line)
            out.append(line)
    return out[-limit:]
