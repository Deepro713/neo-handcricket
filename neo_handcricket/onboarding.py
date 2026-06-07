"""Interactive onboarding tutorial (pure model).

A small, data-driven set of steps explaining the game, plus a cursor model that the
thin UI drives (advance / back / skip / replay). All content is original. No I/O.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Step:
    title: str
    body: str


TUTORIAL_STEPS: list[Step] = [
    Step(
        "Welcome to neo-handcricket",
        "Hand cricket is the schoolyard game where two players show a number at the same time. "
        "Here it's a full match — formats, country teams, a thinking opponent and live commentary.",
    ),
    Step(
        "The core: pick a number",
        "Every ball, you and the bot each pick 0–6 at the same time. If your numbers MATCH, the "
        "batter is OUT. If they differ, the batter scores their own number as runs.",
    ),
    Step(
        "Batting vs bowling",
        "When you're batting, you want to AVOID matching the bowler's number. When you're bowling, "
        "you want to MATCH the batter's number to take a wicket. The bot learns your habits — keep "
        "it guessing.",
    ),
    Step(
        "Formats",
        "Play T10, T20, ODI or a full 5-day Test (follow-on, declarations, draws), or build a Custom "
        "match. Try the Daily challenge for a seeded match that's the same for everyone that day.",
    ),
    Step(
        "Controls",
        "Press 0–6 to pick. 'p' pauses between overs, 'd' declares in a Test, 'h'/'t' call the toss. "
        "Prefer no time pressure? Choose the Untimed option at match start (great for accessibility).",
    ),
    Step(
        "You're set",
        "Pick your country, your opponent, a format and a difficulty (Easy → Legend) and play. "
        "Bank reputation in the campaign, chase achievements, and share results with offline codes. "
        "Good luck out there.",
    ),
]


@dataclass
class Tutorial:
    """A cursor over the tutorial steps; the UI calls advance/back/skip/replay."""
    index: int = 0
    skipped: bool = False
    steps: list[Step] = field(default_factory=lambda: TUTORIAL_STEPS)

    @property
    def total(self) -> int:
        return len(self.steps)

    @property
    def current(self) -> Step:
        return self.steps[min(self.index, self.total - 1)]

    @property
    def done(self) -> bool:
        return self.skipped or self.index >= self.total

    def advance(self) -> None:
        if self.index < self.total:
            self.index += 1

    def back(self) -> None:
        if self.index > 0:
            self.index -= 1

    def skip(self) -> None:
        self.skipped = True

    def replay(self) -> None:
        self.index = 0
        self.skipped = False
