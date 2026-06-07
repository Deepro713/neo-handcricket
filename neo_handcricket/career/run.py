"""A relic-aware career run (pure logic).

Wraps the knockout tournament with a between-rounds **relic draft**: before each
round a seeded offer is drawn, a picker chooses one (or declines), and the chosen
relics produce an **effective config** that the resolver sees. Deterministic given
the resolver, seed and picker.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from . import relics, tournament

# resolve(home, away, effective_config) -> winner.
EffResolver = Callable[[str, str, dict[str, float]], str]
# picker(offer, owned) -> a relic id to take, or None to decline.
Picker = Callable[[list[str], list[str]], "str | None"]


@dataclass
class RunResult:
    champion: str | None
    owned: list[str] = field(default_factory=list)
    drafts: list[dict[str, Any]] = field(default_factory=list)
    tournament: tournament.Tournament | None = None

    @property
    def effective(self) -> dict[str, float]:
        return relics.apply_relics(self.owned)


def greedy_first_picker(offer: list[str], owned: list[str]) -> str | None:
    """Default policy: take the first offered relic."""
    return offer[0] if offer else None


def run_with_relics(
    teams: list[str],
    eff_resolve: EffResolver,
    *,
    seed: int = 0,
    picker: Picker = greedy_first_picker,
    draft_count: int = 3,
) -> RunResult:
    owned: list[str] = []
    drafts: list[dict[str, Any]] = []

    def resolve(home: str, away: str) -> str:
        return eff_resolve(home, away, relics.apply_relics(owned))

    def on_round_end(round_idx: int, winners: list[str]) -> None:
        offer = relics.draft_offer(seed + round_idx * 1009, owned, count=draft_count)
        pick = picker(offer, list(owned))
        if pick is not None:
            owned[:] = relics.choose(owned, pick, offer=offer)
        drafts.append({"round": round_idx, "offer": offer, "picked": pick})

    t = tournament.play_tournament(teams, resolve, on_round_end=on_round_end)
    return RunResult(champion=t.champion, owned=list(owned), drafts=drafts, tournament=t)
