"""Daily challenge scoring + local best-table (pure logic).

A completed daily attempt produces a single comparable score (higher = better),
monotonic in the things that should help: winning, a bigger margin, more balls to
spare in a chase, and more wickets in hand. The best-table keeps the highest score
per date; an entry is a plain dict so it round-trips through ``career.sharecode``.
"""
from __future__ import annotations

from typing import Any

SCORE_WIN_BASE = 1000


def score_result(
    *,
    won: bool,
    runs_margin: int = 0,
    wickets_margin: int = 0,
    balls_to_spare: int = 0,
    wickets_in_hand: int = 0,
) -> int:
    """A single comparable score for a daily attempt (higher is better)."""
    base = SCORE_WIN_BASE if won else 0
    return (
        base
        + max(0, runs_margin) * 2
        + max(0, wickets_margin) * 20
        + max(0, balls_to_spare) * 3
        + max(0, wickets_in_hand) * 10
    )


def make_entry(date_iso: str, seed: int, score: int, *, summary: str = "") -> dict[str, Any]:
    return {"date": date_iso, "seed": seed, "score": int(score), "summary": summary}


def update_best(table: dict[str, Any], entry: dict[str, Any]) -> dict[str, Any]:
    """Return a new table keeping the higher score for the entry's date."""
    date_iso = entry["date"]
    cur = table.get(date_iso)
    if cur is None or int(entry["score"]) > int(cur["score"]):
        return {**table, date_iso: entry}
    return dict(table)


def best_for(table: dict[str, Any], date_iso: str) -> dict[str, Any] | None:
    return table.get(date_iso)
