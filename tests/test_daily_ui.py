"""Smoke tests for the thin daily-challenge UI (M009)."""
from __future__ import annotations

import datetime as dt

from rich.console import Console

from neo_handcricket.daily import score
from neo_handcricket.daily.seed import daily_challenge
from neo_handcricket.ui import daily as ui_daily

POOL = ["india", "australia", "england", "japan", "brazil", "nepal"]


def _console() -> Console:
    return Console(file=open("/dev/null", "w"), force_terminal=False)


def test_render_daily_without_best() -> None:
    c = daily_challenge(dt.date(2026, 6, 7), countries=POOL)
    ui_daily.render_daily(_console(), c, None)


def test_render_daily_with_best() -> None:
    c = daily_challenge(dt.date(2026, 6, 7), countries=POOL)
    best = score.make_entry(c.date_iso, c.seed, 1340, summary="won by 5 wkts")
    ui_daily.render_daily(_console(), c, best)


def test_render_result() -> None:
    ui_daily.render_result(_console(), 1340, "NHC1-EXAMPLECODE")
