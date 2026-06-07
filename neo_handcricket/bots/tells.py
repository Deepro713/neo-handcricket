"""Player-facing "tells" (pure logic).

Optional mind-games: before the user bats, the bot bowler can drop a *coarse* hint
about its likely **zone** — low (0-2), middle (3-4) or high (5-6) — derived from
the bowler's archetype (and nudged by fatigue). The hint is only truthful some of
the time (it bluffs otherwise) and never names an exact number, so it adds reads
without breaking the hidden-pick core. Off by default (``config.TELLS_ENABLED``).

All CC0/original lines. Pure and deterministic given the rng.
"""
from __future__ import annotations

import random

from ..config import TELLS_TRUTHFUL_PROB
from . import profiles

ZONES = ("low", "mid", "high")
_ZONE_INDICES = {"low": (0, 1, 2), "mid": (3, 4), "high": (5, 6)}

# Original, flavourful hint lines per zone.
TELL_LINES: dict[str, list[str]] = {
    "low": [
        "He's rolling the fingers — looks like he'll keep it low and tidy.",
        "Body's leaning into something full and straight.",
        "Feels like a single's on offer if you nudge it.",
    ],
    "mid": [
        "Back-of-a-length vibe to this one.",
        "He's settling into that nagging middle line.",
        "Looks like he wants you reaching, nothing in your slot.",
    ],
    "high": [
        "He's loading up — could be short and quick.",
        "There's a glint in his eye; smells like a big one.",
        "He's backing himself for the top of the range here.",
    ],
}

# When the bowler is gassed, occasionally telegraph it (a true read either way).
TIRED_LINES = [
    "His shoulders have dropped — there's a tired one in here.",
    "Legs look heavy; this could sit up nicely.",
]


def archetype_zone(archetype: str) -> str:
    """The zone an archetype's base distribution most favours."""
    dist = profiles.BOWLER_BASE.get(archetype, profiles.BOWLER_BASE["pace"])
    best = max(ZONES, key=lambda z: sum(dist[i] for i in _ZONE_INDICES[z]))
    return best


def generate_tell(
    archetype: str,
    fatigue: float = 0.0,
    *,
    rng: random.Random,
    truthful_prob: float = TELLS_TRUTHFUL_PROB,
) -> str:
    """A coarse, sometimes-bluffing zone hint. Never names an exact number."""
    # A clearly gassed bowler sometimes telegraphs fatigue (always a fair read).
    if fatigue >= 0.6 and rng.random() < 0.4:
        return rng.choice(TIRED_LINES)
    true_zone = archetype_zone(archetype)
    if rng.random() < truthful_prob:
        zone = true_zone
    else:
        zone = rng.choice([z for z in ZONES if z != true_zone])  # bluff
    return rng.choice(TELL_LINES[zone])
