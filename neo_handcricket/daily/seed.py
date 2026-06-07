"""Date-seeded daily challenge core (pure logic).

Derives a deterministic seed and a fixed match configuration from a calendar date,
so every player gets the *same* daily challenge. Pure — the date and the country
pool are passed in; nothing is read or printed here.
"""
from __future__ import annotations

import datetime as _dt
import random
from dataclasses import dataclass, field

from . import modifiers as mods

# Daily challenges use the quick limited-overs formats (not multi-day Tests).
DAILY_FORMATS = ("T10", "T20", "ODI")
DAILY_DIFFICULTIES = ("easy", "medium", "hard", "legend")


@dataclass(frozen=True)
class DailyChallenge:
    date_iso: str
    seed: int
    fmt: str                       # format preset name
    team_a: str                    # country slug (user)
    team_b: str                    # country slug (opponent)
    difficulty: str
    modifiers: list[str] = field(default_factory=list)


def daily_seed(date: _dt.date) -> int:
    """A stable integer seed for a calendar date (YYYYMMDD)."""
    return date.year * 10000 + date.month * 100 + date.day


def daily_challenge(date: _dt.date, *, countries: list[str], modifier_count: int = 1) -> DailyChallenge:
    """The deterministic challenge for ``date`` drawn from the given country pool."""
    if len(countries) < 2:
        raise ValueError("need at least two countries for a daily challenge")
    seed = daily_seed(date)
    rng = random.Random(seed)
    fmt = rng.choice(DAILY_FORMATS)
    pool = sorted(countries)  # stable input order regardless of caller ordering
    team_a = rng.choice(pool)
    team_b = rng.choice([c for c in pool if c != team_a])
    difficulty = rng.choice(DAILY_DIFFICULTIES)
    modifier_ids = mods.select_modifiers(seed, modifier_count)
    return DailyChallenge(
        date_iso=date.isoformat(),
        seed=seed,
        fmt=fmt,
        team_a=team_a,
        team_b=team_b,
        difficulty=difficulty,
        modifiers=modifier_ids,
    )


def tunables_for(challenge: DailyChallenge) -> dict[str, float]:
    """The effective tunables after applying the challenge's modifiers."""
    return mods.apply_modifiers(challenge.modifiers)
