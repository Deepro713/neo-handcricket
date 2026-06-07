"""Unit tests for the daily-seed challenge core + modifiers (M009)."""
from __future__ import annotations

import datetime as dt

from neo_handcricket.daily import modifiers as mods
from neo_handcricket.daily import seed as daily
from neo_handcricket.formats import PRESETS

POOL = ["india", "australia", "england", "japan", "brazil", "nepal", "usa", "antarctica"]


def test_seed_is_stable_yyyymmdd() -> None:
    assert daily.daily_seed(dt.date(2026, 6, 7)) == 20260607


def test_same_date_identical_challenge() -> None:
    d = dt.date(2026, 6, 7)
    a = daily.daily_challenge(d, countries=POOL)
    b = daily.daily_challenge(d, countries=list(reversed(POOL)))  # caller order must not matter
    assert a == b


def test_different_dates_usually_differ() -> None:
    days = [dt.date(2026, 6, n) for n in range(1, 15)]
    challenges = [daily.daily_challenge(d, countries=POOL) for d in days]
    # Not all identical — the daily rotates.
    assert len({(c.fmt, c.team_a, c.team_b, c.difficulty, tuple(c.modifiers)) for c in challenges}) > 1


def test_challenge_is_valid_and_playable() -> None:
    for n in range(1, 29):
        c = daily.daily_challenge(dt.date(2026, 6, n), countries=POOL)
        assert c.fmt in PRESETS
        assert c.team_a in POOL and c.team_b in POOL
        assert c.team_a != c.team_b
        assert c.difficulty in daily.DAILY_DIFFICULTIES
        assert all(m in mods.MODIFIERS for m in c.modifiers)


def test_needs_two_countries() -> None:
    import pytest

    with pytest.raises(ValueError):
        daily.daily_challenge(dt.date(2026, 6, 7), countries=["india"])


def test_modifiers_deterministic_from_seed() -> None:
    assert mods.select_modifiers(20260607, 2) == mods.select_modifiers(20260607, 2)
    chosen = mods.select_modifiers(20260607, 2)
    assert len(chosen) == 2 and len(set(chosen)) == 2


def test_modifiers_compose_order_independently() -> None:
    ids = ["short_boundaries", "tired_legs"]
    a = mods.apply_modifiers(ids)
    b = mods.apply_modifiers(list(reversed(ids)))
    assert a == b


def test_modifier_math() -> None:
    base = mods.DEFAULT_TUNABLES
    t = mods.apply_modifiers(["tired_legs", "fresh_legs"])  # 1.5 * 0.5
    assert abs(t["fatigue_mult"] - 0.75) < 1e-9
    assert mods.apply_modifiers([])["scoring_mult"] == base["scoring_mult"]


def test_tunables_for_challenge() -> None:
    c = daily.daily_challenge(dt.date(2026, 6, 7), countries=POOL, modifier_count=2)
    t = daily.tunables_for(c)
    assert set(t) >= set(mods.DEFAULT_TUNABLES)
