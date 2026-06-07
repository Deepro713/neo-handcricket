"""Load country rosters from JSON files in data/."""
from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass

from ..config import ROSTERS_DIR


@dataclass
class Player:
    id: int
    name: str
    role: str                        # captain | vice-captain | keeper | keeper-reserve | batsman | all-rounder | bowler
    batting_hand: str | None         # RH | LH
    bowling_style: str | None
    batting_archetype: str | None
    bowling_archetype: str | None

    @property
    def can_bowl(self) -> bool:
        return self.bowling_style is not None and self.bowling_archetype is not None


@dataclass
class Country:
    country: str
    flag: str
    naming_convention: str
    players: list[Player]
    staff: list[dict]
    slug: str = ""

    def player(self, pid: int) -> Player:
        for p in self.players:
            if p.id == pid:
                return p
        raise KeyError(f"player {pid} not in {self.country}")

    @property
    def captain(self) -> Player:
        return next(p for p in self.players if p.role == "captain")

    @property
    def vice_captain(self) -> Player:
        return next(p for p in self.players if p.role == "vice-captain")

    @property
    def keepers(self) -> list[Player]:
        return [p for p in self.players if p.role in ("keeper", "keeper-reserve")]

    @property
    def all_rounders(self) -> list[Player]:
        return [p for p in self.players if p.role == "all-rounder"]

    @property
    def specialist_batsmen(self) -> list[Player]:
        return [p for p in self.players if p.role == "batsman"]

    @property
    def specialist_bowlers(self) -> list[Player]:
        return [p for p in self.players if p.role == "bowler"]


def _player_from_dict(d: dict) -> Player:
    return Player(
        id=d["id"],
        name=d["name"],
        role=d["role"],
        batting_hand=d.get("batting_hand"),
        bowling_style=d.get("bowling_style"),
        batting_archetype=d.get("batting_archetype"),
        bowling_archetype=d.get("bowling_archetype"),
    )


def load_country(slug: str) -> Country:
    path = ROSTERS_DIR / f"{slug}.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    return Country(
        country=raw["country"],
        flag=raw.get("flag", ""),
        naming_convention=raw.get("naming_convention", "given-family"),
        players=[_player_from_dict(p) for p in raw["players"]],
        staff=raw.get("staff", []),
        slug=slug,
    )


def list_countries() -> list[str]:
    return sorted(p.stem for p in ROSTERS_DIR.glob("*.json"))


def load_all() -> dict[str, Country]:
    return {slug: load_country(slug) for slug in list_countries()}


def to_dict(country: Country) -> dict:
    return {
        "country": country.country,
        "flag": country.flag,
        "naming_convention": country.naming_convention,
        "slug": country.slug,
        "players": [
            {
                "id": p.id,
                "name": p.name,
                "role": p.role,
                "batting_hand": p.batting_hand,
                "bowling_style": p.bowling_style,
                "batting_archetype": p.batting_archetype,
                "bowling_archetype": p.bowling_archetype,
            }
            for p in country.players
        ],
        "staff": country.staff,
    }


def find_country_by_name(name: str, countries: Iterable[Country]) -> Country | None:
    """Loose match: lowercased substring of country name or slug."""
    needle = name.lower().strip()
    for c in countries:
        if needle == c.country.lower() or needle == c.slug.lower():
            return c
    for c in countries:
        if needle in c.country.lower() or needle in c.slug.lower():
            return c
    return None
