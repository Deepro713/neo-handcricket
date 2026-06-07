"""Big-moment event detection (pure logic).

A deterministic detector that turns the *most recent ball* (plus innings state)
into a list of typed commentary events: wickets (+kind), boundaries, batting
milestones, hat-tricks, maidens, 50-run partnerships, collapses and last-ball
finishes. The commentary engine and scoreboard consume these; this module has no
I/O and no RNG.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ..config import (
    COLLAPSE_WICKETS,
    COLLAPSE_WINDOW,
    LAST_BALL_FINISH_BALLS,
    MILESTONE_RUNS,
    PARTNERSHIP_MILESTONE,
)

if TYPE_CHECKING:
    from ..innings import BallEvent, Innings


@dataclass
class Event:
    """A detected big moment. ``kind`` is the category; ``subtype`` qualifies it
    (wicket kind, '4'/'6', 'fifty'/'hundred', …); ``player_id`` is whoever it is
    about (striker or bowler); ``detail`` carries extras."""
    kind: str
    subtype: str = ""
    player_id: int | None = None
    detail: dict[str, Any] = field(default_factory=dict)


def _bowler_hat_trick(ball_log: list[BallEvent], bowler_id: int) -> bool:
    """True if the bowler's last three legal deliveries were all wickets."""
    deliveries = [b for b in ball_log if b.bowler_id == bowler_id and b.counts_toward_over]
    last3 = deliveries[-3:]
    return len(last3) == 3 and all(b.wicket is not None for b in last3)


def _is_collapse(ball_log: list[BallEvent]) -> bool:
    legal = [b for b in ball_log if b.counts_toward_over]
    window = legal[-COLLAPSE_WINDOW:]
    return sum(1 for b in window if b.wicket is not None) >= COLLAPSE_WICKETS


def _partnership_runs(ball_log: list[BallEvent]) -> int:
    """Runs added since the last wicket fell (the current partnership)."""
    total = 0
    for b in reversed(ball_log):
        if b.wicket is not None:
            break
        total += b.runs + b.extras
    return total


def detect(inn: Innings) -> list[Event]:
    """Detect the big-moment events triggered by the most recent ball in ``inn``."""
    if not inn.ball_log:
        return []
    last = inn.ball_log[-1]
    events: list[Event] = []

    if last.wicket is not None:
        events.append(Event("wicket", last.wicket, last.striker_id, {"bowler_id": last.bowler_id}))
        if _bowler_hat_trick(inn.ball_log, last.bowler_id):
            events.append(Event("hat_trick", player_id=last.bowler_id))
        if _is_collapse(inn.ball_log):
            events.append(Event("collapse"))
    elif last.runs in (4, 6):
        events.append(Event("boundary", str(last.runs), last.striker_id))

    # Individual batting milestone (crossed on this ball).
    card = inn.batter_cards.get(last.striker_id)
    if card is not None and last.runs > 0:
        for thresh in sorted(MILESTONE_RUNS, reverse=True):
            if card.runs >= thresh > card.runs - last.runs:
                name = "hundred" if thresh >= 100 else "fifty"
                events.append(Event("milestone", name, last.striker_id, {"runs": card.runs}))
                break

    # 50-run partnership (crossed on this ball, non-wicket).
    if last.wicket is None:
        pr = _partnership_runs(inn.ball_log)
        delta = last.runs + last.extras
        if pr >= PARTNERSHIP_MILESTONE > pr - delta:
            events.append(Event("partnership", "fifty", detail={"runs": pr}))

    # Maiden over (this legal ball completed an over that conceded nothing).
    if last.counts_toward_over and inn.current_over_balls >= 6 and inn.current_over_runs == 0:
        events.append(Event("maiden", player_id=last.bowler_id))

    # Last-ball finish (chase sealed with ≤ N balls to spare).
    if inn.target is not None and inn.runs >= inn.target:
        br = inn.balls_remaining
        if br is not None and br <= LAST_BALL_FINISH_BALLS:
            events.append(Event("last_ball_finish", player_id=last.striker_id))

    return events
