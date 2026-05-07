"""Match-format definitions."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Format:
    name: str
    overs_per_innings: int | None       # None = "no over cap" (Test/some custom)
    wickets_per_innings: int
    innings_per_team: int
    bowler_over_cap: int | None         # None = "no per-bowler cap"
    min_bowlers_in_xi: int
    min_spinners: int
    min_pacers: int
    playing_size: int = 11              # custom can shrink this


T10 = Format(
    name="T10",
    overs_per_innings=10,
    wickets_per_innings=10,
    innings_per_team=1,
    bowler_over_cap=2,
    min_bowlers_in_xi=4,
    min_spinners=0,
    min_pacers=0,
)

T20 = Format(
    name="T20",
    overs_per_innings=20,
    wickets_per_innings=10,
    innings_per_team=1,
    bowler_over_cap=4,
    min_bowlers_in_xi=4,
    min_spinners=0,
    min_pacers=0,
)

ODI = Format(
    name="ODI",
    overs_per_innings=50,
    wickets_per_innings=10,
    innings_per_team=1,
    bowler_over_cap=10,
    min_bowlers_in_xi=5,
    min_spinners=1,
    min_pacers=1,
)

TEST = Format(
    name="Test",
    overs_per_innings=None,
    wickets_per_innings=10,
    innings_per_team=2,
    bowler_over_cap=None,
    min_bowlers_in_xi=5,
    min_spinners=2,
    min_pacers=2,
)

PRESETS: dict[str, Format] = {
    "T10": T10,
    "T20": T20,
    "ODI": ODI,
    "Test": TEST,
}


def custom(
    *,
    overs: int | None,
    wickets: int,
    innings_per_team: int,
    playing_size: int = 11,
    bowler_over_cap: int | None = None,
) -> Format:
    """Build a custom format. `overs=None` means no over cap.

    For tiny custom games (playing_size < 11), the role-mix mins relax to 0.
    """
    if playing_size < 11:
        min_bowlers, min_spin, min_pace = 0, 0, 0
    else:
        # Reasonable defaults that scale with overs
        if overs is None or overs >= 50:
            min_bowlers, min_spin, min_pace = 5, 1, 1
        elif overs >= 20:
            min_bowlers, min_spin, min_pace = 4, 0, 0
        else:
            min_bowlers, min_spin, min_pace = 4, 0, 0
    if bowler_over_cap is None and overs is not None and playing_size >= 11:
        # Sensible default cap: ceil(overs / 5)
        bowler_over_cap = max(1, -(-overs // 5))
    return Format(
        name="Custom",
        overs_per_innings=overs,
        wickets_per_innings=wickets,
        innings_per_team=innings_per_team,
        bowler_over_cap=bowler_over_cap,
        min_bowlers_in_xi=min_bowlers,
        min_spinners=min_spin,
        min_pacers=min_pace,
        playing_size=playing_size,
    )
