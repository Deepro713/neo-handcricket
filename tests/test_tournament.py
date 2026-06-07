"""Unit tests for the knockout tournament core (M008)."""
from __future__ import annotations

from neo_handcricket.career import tournament as T


def _top_seed_wins(teams: list[str]):
    """Resolver where the better-seeded (earlier in list) team always wins."""
    rank = {name: i for i, name in enumerate(teams)}
    return lambda home, away: home if rank[home] < rank[away] else away


def test_seed_slots_padding_and_size() -> None:
    slots = T.seed_slots(["A", "B", "C", "D", "E"])  # 5 → padded to 8
    assert len(slots) == 8
    assert slots.count(None) == 3
    assert slots[0] == "A"          # top seed in the first slot
    assert set(s for s in slots if s) == {"A", "B", "C", "D", "E"}


def test_power_of_two_no_byes() -> None:
    slots = T.seed_slots(["A", "B", "C", "D"])
    assert len(slots) == 4 and None not in slots


def test_champion_is_top_seed_when_seed_decides() -> None:
    teams = [f"T{i}" for i in range(8)]
    t = T.play_tournament(teams, _top_seed_wins(teams))
    assert t.champion == "T0"
    # 8 teams → 4 + 2 + 1 = 7 fixtures.
    assert T.total_fixtures(t) == 7
    assert all(fx.winner is not None for r in t.rounds for fx in r)


def test_byes_advance_without_resolution() -> None:
    teams = ["A", "B", "C"]   # padded to 4 with one bye
    calls: list[tuple[str, str]] = []

    def resolve(home: str, away: str) -> str:
        calls.append((home, away))
        return home

    t = T.play_tournament(teams, resolve)
    assert t.champion is not None
    # First round has a bye (3 teams in a 4-bracket) → fewer than 2 played fixtures R1.
    r1 = t.rounds[0]
    assert any(fx.away is None for fx in r1)


def test_single_and_empty_field() -> None:
    assert T.play_tournament(["solo"], lambda h, a: h).champion == "solo"
    assert T.play_tournament([], lambda h, a: h).champion is None


def test_deduplicates_teams() -> None:
    teams = ["A", "A", "B", "C"]
    t = T.play_tournament(teams, _top_seed_wins(["A", "B", "C"]))
    assert t.teams == ["A", "B", "C"]
    assert t.champion == "A"


def test_resolver_only_sees_valid_pairings() -> None:
    teams = [f"T{i}" for i in range(16)]
    seen: list[tuple[str, str]] = []

    def resolve(home: str, away: str) -> str:
        assert home != away
        seen.append((home, away))
        return home

    t = T.play_tournament(teams, resolve)
    assert t.champion == "T0"          # home always wins → top of bracket
    assert T.total_fixtures(t) == 15   # 8+4+2+1
