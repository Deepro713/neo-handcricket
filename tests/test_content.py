"""Tests for M013 content: curated rosters + expanded commentary breadth."""
from __future__ import annotations

from neo_handcricket.commentary.lines import LINES
from neo_handcricket.formats import PRESETS
from neo_handcricket.rosters import loader, selector, validator


def test_curated_rosters_load_validate_select() -> None:
    for slug in ("iceland", "mongolia"):
        c = loader.load_country(slug)
        assert validator.validate(c, playing_size=11).ok
        sel = selector.select_xi(c, PRESETS["T20"])
        assert len(sel.playing_xi) == 11
        assert all(p.name.strip() for p in c.players)


def test_curated_names_are_distinct_and_onrhythm() -> None:
    ice = [p.name for p in loader.load_country("iceland").players]
    # Icelandic patronymics end in -son (fictional/original).
    assert sum(1 for n in ice if n.endswith("son")) >= 20
    assert len(set(ice)) == len(ice)   # no duplicate names


def test_every_commentary_category_has_lines() -> None:
    for sit, turns in LINES.items():
        assert turns, sit
        assert any(turns.get(t) for t in ("opener", "analysis", "quip")), sit


def test_thin_categories_were_expanded() -> None:
    # Categories topped up in M013 now carry several opener lines.
    for sit in ("ball_run_2", "milestone_100", "partnership_50", "ball_run_5"):
        assert len(LINES[sit].get("opener", [])) >= 2, sit
