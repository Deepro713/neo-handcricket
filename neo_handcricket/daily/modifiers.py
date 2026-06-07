"""Daily-challenge modifiers (pure logic).

A small pool of rule-bending modifiers, selected deterministically from the daily
seed. Each modifier nudges a dict of neutral *tunables*; `_mult` keys multiply and
`_bonus` keys add, so distinct modifiers compose order-independently. No I/O / RNG
beyond the seeded selection.
"""
from __future__ import annotations

import random
from typing import Any

# Neutral baseline the modifiers transform.
DEFAULT_TUNABLES: dict[str, float] = {
    "boundary_bonus": 0.0,    # extra value/likelihood of boundaries
    "fatigue_mult": 1.0,      # bowler fatigue accrual multiplier
    "wicket_bonus": 0.0,      # extra wicket likelihood (a "minefield")
    "scoring_mult": 1.0,      # general run multiplier (a "flat track")
    "aggression_bonus": 0.0,  # batter aggression nudge
}

MODIFIERS: dict[str, dict[str, Any]] = {
    "short_boundaries": {
        "label": "Short Boundaries — the rope is in, boundaries come easier",
        "tunables": {"boundary_bonus": 1.0},
    },
    "tired_legs": {
        "label": "Tired Legs — bowlers fatigue faster",
        "tunables": {"fatigue_mult": 1.5},
    },
    "minefield": {
        "label": "Minefield — a spicy pitch, wickets fall easier",
        "tunables": {"wicket_bonus": 1.0},
    },
    "flat_track": {
        "label": "Flat Track — a road, runs flow freely",
        "tunables": {"scoring_mult": 1.2},
    },
    "powerplay_plus": {
        "label": "Powerplay Plus — everyone comes out swinging",
        "tunables": {"aggression_bonus": 0.15},
    },
    "fresh_legs": {
        "label": "Fresh Legs — bowlers barely tire",
        "tunables": {"fatigue_mult": 0.5},
    },
}


def select_modifiers(seed: int, count: int) -> list[str]:
    """Deterministically pick ``count`` distinct modifier ids from ``seed``."""
    rng = random.Random(seed ^ 0x9E3779B9)
    ids = sorted(MODIFIERS)
    rng.shuffle(ids)
    n = max(0, min(count, len(ids)))
    return sorted(ids[:n])


def apply_modifiers(modifier_ids: list[str], base: dict[str, float] | None = None) -> dict[str, float]:
    """Compose a list of modifiers onto the tunables. ``_mult`` keys multiply,
    others add — so distinct modifiers compose order-independently."""
    t: dict[str, float] = dict(base if base is not None else DEFAULT_TUNABLES)
    for mid in modifier_ids:
        spec = MODIFIERS.get(mid)
        if not spec:
            continue
        for key, val in spec["tunables"].items():
            if key.endswith("_mult"):
                t[key] = t.get(key, 1.0) * float(val)
            else:
                t[key] = t.get(key, 0.0) + float(val)
    return t


def label(modifier_id: str) -> str:
    spec = MODIFIERS.get(modifier_id)
    return str(spec["label"]) if spec else modifier_id
