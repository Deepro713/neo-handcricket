"""Roguelite relics & run modifiers (pure logic).

Relics are run-scoped rule-benders drafted between matches. Each is a small,
composable transform over a neutral **effective-config** dict; `_mult` keys
multiply and the rest add, so distinct relics compose order-independently. A
deterministic, seeded **draft** offers a few relics each round (declining is
allowed); the chosen set persists for the run and feeds the effective config.
All pure — no I/O, no RNG beyond the seeded draft.
"""
from __future__ import annotations

import random
from typing import Any

# The neutral effective-config a run starts from; relics nudge these.
EFFECTIVE_DEFAULTS: dict[str, float] = {
    "boundary_value_bonus": 0.0,   # extra runs awarded on a boundary
    "fatigue_mult": 1.0,           # bowler fatigue accrual multiplier
    "powerplay_overs_bonus": 0.0,  # extra powerplay overs
    "tail_aggression_bonus": 0.0,  # how much braver the lower order bats
    "currency_mult": 1.0,          # career reward multiplier
}

RELICS: dict[str, dict[str, Any]] = {
    "short_rope":    {"label": "Short Rope",    "desc": "Boundaries are worth +1.",            "effect": {"boundary_value_bonus": 1.0}},
    "marathoners":   {"label": "Marathoners",   "desc": "Your bowlers barely tire.",           "effect": {"fatigue_mult": 0.5}},
    "long_powerplay":{"label": "Long Powerplay", "desc": "Two extra powerplay overs.",          "effect": {"powerplay_overs_bonus": 2.0}},
    "brave_tail":    {"label": "Brave Tail",    "desc": "Your tail bats with real intent.",    "effect": {"tail_aggression_bonus": 0.2}},
    "merchant":      {"label": "Merchant",      "desc": "+50% reputation from results.",       "effect": {"currency_mult": 1.5}},
    "big_hitter":    {"label": "Big Hitter",    "desc": "Boundaries are worth +2.",            "effect": {"boundary_value_bonus": 2.0}},
    "fresh_attack":  {"label": "Fresh Attack",  "desc": "Bowlers tire a touch slower.",        "effect": {"fatigue_mult": 0.8}},
}


def relic_label(relic_id: str) -> str:
    spec = RELICS.get(relic_id)
    return str(spec["label"]) if spec else relic_id


def relic_desc(relic_id: str) -> str:
    spec = RELICS.get(relic_id)
    return str(spec["desc"]) if spec else ""


def apply_relics(relic_ids: list[str], base: dict[str, float] | None = None) -> dict[str, float]:
    """Compose relics onto the effective config (``_mult`` multiplies, others add).
    Order-independent for distinct relics."""
    eff: dict[str, float] = dict(base if base is not None else EFFECTIVE_DEFAULTS)
    for rid in relic_ids:
        spec = RELICS.get(rid)
        if not spec:
            continue
        for key, val in spec["effect"].items():
            if key.endswith("_mult"):
                eff[key] = eff.get(key, 1.0) * float(val)
            else:
                eff[key] = eff.get(key, 0.0) + float(val)
    return eff


def draft_offer(seed: int, owned: list[str], *, count: int = 3) -> list[str]:
    """Deterministic seeded offer of up to ``count`` relics not already owned."""
    rng = random.Random(seed)
    pool = sorted(set(RELICS) - set(owned))
    rng.shuffle(pool)
    return pool[: max(0, min(count, len(pool)))]


def choose(owned: list[str], relic_id: str, *, offer: list[str] | None = None) -> list[str]:
    """Add ``relic_id`` to the owned set. A no-op if unknown, already owned, or
    (when an offer is given) not on offer. Declining = simply not calling this."""
    if relic_id not in RELICS or relic_id in owned:
        return list(owned)
    if offer is not None and relic_id not in offer:
        return list(owned)
    return [*owned, relic_id]
