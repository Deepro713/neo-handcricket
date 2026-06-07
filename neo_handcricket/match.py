"""Match orchestration: state machine across innings, super over, result."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

from .formats import Format
from .innings import Innings

MatchPhase = Literal["pre", "innings1", "innings2", "innings3", "innings4", "super-over", "complete"]


@dataclass
class TeamMeta:
    country: str
    flag: str
    naming_convention: str
    players: list[dict]  # raw player dicts from JSON
    staff: list[dict]


@dataclass
class Match:
    user_team: TeamMeta
    opponent: TeamMeta
    user_xi: list[int]
    opponent_xi: list[int]
    user_bowling_pool: list[int]
    opponent_bowling_pool: list[int]
    fmt: Format
    difficulty: str = "medium"
    user_batting_first: bool = True

    # State
    phase: MatchPhase = "pre"
    innings_list: list[Innings] = field(default_factory=list)
    schema_version: int = 1
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    # Super over fallback
    super_over_innings: list[Innings] = field(default_factory=list)

    # Result
    winner: str | None = None              # "user" | "opponent" | "tie" | "draw"
    result_summary: str | None = None
    player_of_the_match: int | None = None
    pom_team: str | None = None            # "user" | "opponent"

    @property
    def current_innings(self) -> Innings | None:
        if self.innings_list:
            return self.innings_list[-1]
        return None

    def add_innings(self, innings: Innings) -> None:
        self.innings_list.append(innings)

    def set_winner_from_score(self) -> None:
        """Determine winner after both innings complete (T10/T20/ODI/Custom 1-innings each)."""
        if len(self.innings_list) < 2:
            return
        a, b = self.innings_list[0], self.innings_list[1]
        if a.runs > b.runs:
            self.winner = "user" if a.batting_country == self.user_team.country else "opponent"
            margin = a.runs - b.runs
            self.result_summary = f"{a.batting_country} won by {margin} runs"
        elif b.runs > a.runs:
            self.winner = "user" if b.batting_country == self.user_team.country else "opponent"
            wickets_left = b.wickets_limit - b.wickets
            self.result_summary = f"{b.batting_country} won by {wickets_left} wickets"
        else:
            self.winner = "tie"
            self.result_summary = "Match tied — super over"

    def set_super_over_winner(self) -> None:
        if len(self.super_over_innings) < 2:
            return
        a, b = self.super_over_innings[0], self.super_over_innings[1]
        if a.runs > b.runs:
            self.winner = "user" if a.batting_country == self.user_team.country else "opponent"
            self.result_summary = f"{a.batting_country} won the super over by {a.runs - b.runs} runs"
        elif b.runs > a.runs:
            self.winner = "user" if b.batting_country == self.user_team.country else "opponent"
            wickets_left = b.wickets_limit - b.wickets
            self.result_summary = f"{b.batting_country} won the super over by {wickets_left} wickets"
        else:
            self.winner = "tie"
            self.result_summary = "Super over tied — repeat super over"
