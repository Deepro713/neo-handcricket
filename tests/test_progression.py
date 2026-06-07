"""Unit tests for career meta-progression + migration (M008)."""
from __future__ import annotations

import json

from neo_handcricket.career import progression as prog


def test_new_progression_defaults() -> None:
    s = prog.new_progression()
    assert s["currency"] == 0
    assert s["unlocks"] == []
    assert s["schema_version"] == prog.PROGRESSION_SCHEMA_VERSION


def test_reward_for_results() -> None:
    assert prog.reward_for(result="win") == prog.REWARD_WIN
    assert prog.reward_for(result="loss") == prog.REWARD_LOSS
    assert prog.reward_for(result="draw") == prog.REWARD_DRAW
    assert prog.reward_for(result="win", tournament_champion=True) == prog.REWARD_WIN + prog.REWARD_TOURNAMENT_BONUS


def test_currency_accrues() -> None:
    s = prog.new_progression()
    s = prog.bank(s, prog.reward_for(result="win"))
    s = prog.bank(s, prog.reward_for(result="loss"))
    assert s["currency"] == prog.REWARD_WIN + prog.REWARD_LOSS
    # negative amounts are ignored.
    assert prog.bank(s, -50)["currency"] == s["currency"]


def test_unlock_gating() -> None:
    s = prog.new_progression()
    uid = "panel_comedy"
    cost = prog.UNLOCKS[uid]["cost"]
    assert not prog.can_unlock(s, uid)            # broke
    s = prog.bank(s, cost)
    assert prog.can_unlock(s, uid)
    s = prog.unlock(s, uid)
    assert prog.is_unlocked(s, uid)
    assert s["currency"] == 0                     # spent
    assert not prog.can_unlock(s, uid)            # already owned
    # unknown id is a no-op.
    assert prog.unlock(s, "does_not_exist") == prog.migrate(s)


def test_unlock_without_funds_is_noop() -> None:
    s = prog.new_progression()
    s2 = prog.unlock(s, "opponent_legends_xi")
    assert s2["unlocks"] == [] and s2["currency"] == 0


def test_available_unlocks_excludes_owned_and_sorts_by_cost() -> None:
    s = prog.bank(prog.new_progression(), 1000)
    s = prog.unlock(s, "panel_comedy")
    avail = prog.available_unlocks(s)
    assert "panel_comedy" not in avail
    costs = [prog.UNLOCKS[u]["cost"] for u in avail]
    assert costs == sorted(costs)


def test_migrate_v1_dict() -> None:
    # An old/implicit-v1 progression dict (no schema_version) migrates cleanly.
    old = {"currency": 120}
    s = prog.migrate(old)
    assert s["schema_version"] == prog.PROGRESSION_SCHEMA_VERSION
    assert s["currency"] == 120
    assert s["unlocks"] == [] and s["tournaments_won"] == 0


def test_persistence_round_trip(tmp_path, monkeypatch) -> None:
    import neo_handcricket.persistence.progression as pp

    monkeypatch.setattr(pp, "PROGRESSION_FILE", tmp_path / "progression.json")
    assert pp.load_progression()["currency"] == 0   # default when missing
    s = prog.bank(prog.new_progression(), 300)
    s = prog.unlock(s, "panel_comedy")
    pp.save_progression(s)
    loaded = pp.load_progression()
    assert loaded["currency"] == s["currency"]
    assert loaded["unlocks"] == s["unlocks"]


def test_persistence_migrates_old_file(tmp_path, monkeypatch) -> None:
    import neo_handcricket.persistence.progression as pp

    f = tmp_path / "progression.json"
    f.write_text(json.dumps({"currency": 75}))   # legacy, no schema_version
    monkeypatch.setattr(pp, "PROGRESSION_FILE", f)
    loaded = pp.load_progression()
    assert loaded["schema_version"] == prog.PROGRESSION_SCHEMA_VERSION
    assert loaded["currency"] == 75
