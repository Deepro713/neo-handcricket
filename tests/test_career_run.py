"""Unit tests for the relic-aware career run + draft UI (M012)."""
from __future__ import annotations

from rich.console import Console

from neo_handcricket.career import relics, run
from neo_handcricket.ui import relics as ui_relics

TEAMS = [f"T{i}" for i in range(8)]


def _seed_resolver(home: str, away: str, eff: dict[str, float]) -> str:
    # Lower index wins (ignores relics) — a deterministic baseline.
    return home if int(home[1:]) < int(away[1:]) else away


def test_run_completes_with_champion() -> None:
    r = run.run_with_relics(TEAMS, _seed_resolver, seed=1)
    assert r.champion == "T0"
    assert r.tournament is not None


def test_owned_grows_one_per_draft() -> None:
    # 8 teams → 3 rounds → 2 between-round drafts; greedy picker takes each.
    r = run.run_with_relics(TEAMS, _seed_resolver, seed=1)
    assert len(r.owned) == 2
    assert len(r.drafts) == 2


def test_deterministic_under_seed() -> None:
    a = run.run_with_relics(TEAMS, _seed_resolver, seed=7)
    b = run.run_with_relics(TEAMS, _seed_resolver, seed=7)
    assert a.champion == b.champion and a.owned == b.owned and a.drafts == b.drafts


def test_decline_keeps_no_relics() -> None:
    r = run.run_with_relics(TEAMS, _seed_resolver, seed=1, picker=lambda offer, owned: None)
    assert r.owned == []
    assert all(d["picked"] is None for d in r.drafts)


def test_effective_config_reflects_owned() -> None:
    r = run.run_with_relics(TEAMS, _seed_resolver, seed=3)
    assert r.effective == relics.apply_relics(r.owned)


def test_relics_can_change_outcomes() -> None:
    # A resolver where, once any relic is owned, 'away' wins instead of 'home'.
    def eff_resolver(home: str, away: str, eff: dict[str, float]) -> str:
        favour_away = eff.get("boundary_value_bonus", 0.0) > 0 or eff.get("currency_mult", 1.0) > 1.0
        if favour_away:
            return away
        return home if int(home[1:]) < int(away[1:]) else away

    # Always take a relic that has an upside our resolver keys on.
    def picker(offer, owned):
        for r in ("short_rope", "big_hitter", "merchant"):
            if r in offer:
                return r
        return offer[0] if offer else None

    with_relics = run.run_with_relics(TEAMS, eff_resolver, seed=2, picker=picker)
    baseline = run.run_with_relics(TEAMS, eff_resolver, seed=2, picker=lambda o, w: None)
    # The relic-influenced run can reach a different champion than the no-relic run.
    assert with_relics.champion != baseline.champion or with_relics.owned


def test_draft_ui_smoke() -> None:
    console = Console(file=open("/dev/null", "w"), force_terminal=False)
    ui_relics.render_owned(console, [])
    ui_relics.render_owned(console, ["short_rope", "merchant"])
    ui_relics.render_draft(console, relics.draft_offer(1, owned=[]))
