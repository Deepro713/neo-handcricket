"""Offline knockout tournament core (pure logic).

A run = a single-elimination tournament. Teams are seeded by reputation (best
first); the bracket is padded to a power of two with byes using standard seeding
(1-vs-lowest, 2-vs-next, …). Fixture resolution is injected as a callback, so this
module is pure and deterministic — the game passes a resolver that plays a real
match; tests pass a deterministic one.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

# resolve(home, away) -> the winning team name. Never called for byes.
Resolver = Callable[[str, str], str]


@dataclass
class Fixture:
    round_idx: int
    home: str
    away: str | None          # None = bye (home advances)
    winner: str | None = None


@dataclass
class Tournament:
    teams: list[str]
    rounds: list[list[Fixture]] = field(default_factory=list)
    champion: str | None = None


def _next_pow2(n: int) -> int:
    p = 1
    while p < n:
        p *= 2
    return p


def _seed_order(n: int) -> list[int]:
    """Standard bracket seed positions (1-indexed) for a bracket of size n (pow2)."""
    order = [1, 2]
    while len(order) < n:
        size = len(order) * 2
        nxt: list[int] = []
        for s in order:
            nxt.append(s)
            nxt.append(size + 1 - s)
        order = nxt
    return order


def seed_slots(teams: list[str]) -> list[str | None]:
    """Order teams (best-seeded first) into bracket slots, padding with byes (None)."""
    n = _next_pow2(max(1, len(teams)))
    seeds = _seed_order(n)
    return [teams[i - 1] if i - 1 < len(teams) else None for i in seeds]


def _first_round(slots: list[str | None]) -> list[Fixture]:
    fixtures: list[Fixture] = []
    for i in range(0, len(slots), 2):
        home, away = slots[i], slots[i + 1]
        if home is None and away is not None:
            home, away = away, None     # keep the real team as home on a bye
        assert home is not None, "two byes met — bracket built wrong"
        fixtures.append(Fixture(round_idx=0, home=home, away=away))
    return fixtures


def play_tournament(teams: list[str], resolve: Resolver) -> Tournament:
    """Run the whole bracket to a single champion. Deterministic given ``resolve``."""
    unique = list(dict.fromkeys(teams))  # de-dupe, preserve seed order
    t = Tournament(teams=unique)
    if len(unique) <= 1:
        t.champion = unique[0] if unique else None
        return t

    current = _first_round(seed_slots(unique))
    round_idx = 0
    while True:
        winners: list[str] = []
        for fx in current:
            fx.winner = fx.home if fx.away is None else resolve(fx.home, fx.away)
            winners.append(fx.winner)
        t.rounds.append(current)
        if len(winners) == 1:
            t.champion = winners[0]
            return t
        round_idx += 1
        current = [
            Fixture(round_idx=round_idx, home=winners[i], away=winners[i + 1])
            for i in range(0, len(winners), 2)
        ]


def total_fixtures(t: Tournament) -> int:
    return sum(len(r) for r in t.rounds)
