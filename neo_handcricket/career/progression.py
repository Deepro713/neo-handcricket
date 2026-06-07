"""Career meta-progression (pure logic).

A run banks **currency** (reputation) from results, which is spent on **variety
unlocks** — new opponents, commentary panels and challenge modifiers that widen
the pool rather than inflating power (the roguelite lesson from the research). All
functions operate on a plain dict so they're trivially testable and serialisable;
persistence is a thin layer on top. Offline only.
"""
from __future__ import annotations

from typing import Any

PROGRESSION_SCHEMA_VERSION = 2

# Result rewards.
REWARD_WIN = 100
REWARD_LOSS = 25
REWARD_DRAW = 50
REWARD_TOURNAMENT_BONUS = 250

# Variety unlocks: id -> (cost, kind, label). Kinds are cosmetic/structural, never power.
UNLOCKS: dict[str, dict[str, Any]] = {
    "opponent_legends_xi":   {"cost": 400, "kind": "opponent", "label": "Legends XI (bonus opponent)"},
    "opponent_world_select": {"cost": 350, "kind": "opponent", "label": "World Select XI"},
    "panel_comedy":          {"cost": 150, "kind": "panel",    "label": "Comedy commentary panel"},
    "panel_purist":          {"cost": 150, "kind": "panel",    "label": "Purist commentary panel"},
    "modifier_chase_master": {"cost": 200, "kind": "modifier", "label": "Chase Master challenge"},
    "modifier_minefield":    {"cost": 250, "kind": "modifier", "label": "Minefield (low-scoring) challenge"},
}


def new_progression() -> dict[str, Any]:
    return {
        "schema_version": PROGRESSION_SCHEMA_VERSION,
        "currency": 0,
        "unlocks": [],
        "tournaments_won": 0,
    }


def migrate(state: dict[str, Any]) -> dict[str, Any]:
    """Bring an older/implicit-v1 progression dict up to the current schema."""
    s = dict(state)
    if int(s.get("schema_version", 1)) < PROGRESSION_SCHEMA_VERSION:
        s.setdefault("currency", 0)
        s.setdefault("unlocks", [])
        s.setdefault("tournaments_won", 0)
        s["schema_version"] = PROGRESSION_SCHEMA_VERSION
    return s


def reward_for(*, result: str, tournament_champion: bool = False) -> int:
    """Currency earned for a match ``result`` in {'win','loss','draw','tie'}."""
    base = {"win": REWARD_WIN, "loss": REWARD_LOSS, "draw": REWARD_DRAW, "tie": REWARD_DRAW}.get(result, REWARD_LOSS)
    return base + (REWARD_TOURNAMENT_BONUS if tournament_champion else 0)


def bank(state: dict[str, Any], amount: int) -> dict[str, Any]:
    s = migrate(state)
    s["currency"] = int(s["currency"]) + max(0, int(amount))
    return s


def can_unlock(state: dict[str, Any], unlock_id: str) -> bool:
    if unlock_id not in UNLOCKS or unlock_id in state.get("unlocks", []):
        return False
    return int(state.get("currency", 0)) >= int(UNLOCKS[unlock_id]["cost"])


def unlock(state: dict[str, Any], unlock_id: str) -> dict[str, Any]:
    """Spend currency to unlock ``unlock_id``. Returns the state unchanged if it
    can't be afforded or is already owned / unknown."""
    if not can_unlock(state, unlock_id):
        return migrate(state)
    s = migrate(state)
    s["currency"] = int(s["currency"]) - int(UNLOCKS[unlock_id]["cost"])
    s["unlocks"] = [*s["unlocks"], unlock_id]
    return s


def is_unlocked(state: dict[str, Any], unlock_id: str) -> bool:
    return unlock_id in state.get("unlocks", [])


def available_unlocks(state: dict[str, Any]) -> list[str]:
    """Unlock ids not yet owned, cheapest first."""
    owned = set(state.get("unlocks", []))
    ids = [u for u in UNLOCKS if u not in owned]
    return sorted(ids, key=lambda u: UNLOCKS[u]["cost"])
