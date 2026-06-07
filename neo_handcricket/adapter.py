"""Headless game adapter — a UI-agnostic façade over the pure engine.

Drives the primary interactive mode (the user batting, the bot bowling) without
any printing or input: start a match from a config, submit a 0–6 pick, observe a
structured state dict + the big-moment events for that ball. Deterministic under a
seed, so any front-end (CLI, TUI, a future web port) can drive identical games.
No network, no I/O.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any

from .bots import captain as cap_ai
from .bots import fatigue as fatigue_mod
from .bots import strategy
from .commentary import events as events_mod
from .config import DIFFICULTY_EPSILON
from .formats import PRESETS
from .innings import Innings
from .rosters import loader, selector


def bot_bowl_pick(
    *,
    bowler_archetype: str,
    recent_user_batting_picks: list[int],
    difficulty: str,
    over_number: int,
    fatigue: float,
    batting_outcomes: list[int],
    rng: random.Random,
) -> int:
    """The bot's bowling pick — the single source of truth shared by the CLI and
    the adapter (opponent model + fatigue + per-difficulty exploit epsilon)."""
    return strategy.pick_number(
        archetype=bowler_archetype,
        is_bowler=True,
        recent_user_picks=recent_user_batting_picks,
        difficulty=difficulty,
        over_number=over_number,
        fatigue=fatigue,
        opponent_outcomes=batting_outcomes,
        epsilon=DIFFICULTY_EPSILON.get(difficulty),
        rng=rng,
    )


@dataclass
class AdapterConfig:
    batting: str                 # country slug (the user's team, batting)
    bowling: str                 # country slug (the bot's team, bowling)
    fmt: str = "T20"             # format preset name
    difficulty: str = "medium"
    seed: int = 0
    target: int | None = None    # optional chase target


@dataclass
class GameAdapter:
    """A headless driver for one user-batting innings."""
    config: AdapterConfig
    inn: Innings = field(init=False)

    def __post_init__(self) -> None:
        cfg = self.config
        self._rng = random.Random(cfg.seed)
        bat = loader.load_country(cfg.batting)
        bowl = loader.load_country(cfg.bowling)
        fmt = PRESETS[cfg.fmt]
        bat_sel = selector.select_xi(bat, fmt, rng=self._rng)
        bowl_sel = selector.select_xi(bowl, fmt, rng=self._rng)
        self._bowl_country = bowl
        self._bowl_arch = {p.id: (p.bowling_archetype or "pace") for p in bowl.players}
        self.inn = Innings(
            batting_country=bat.country, bowling_country=bowl.country,
            batting_xi=[p.id for p in bat_sel.playing_xi],
            bowling_xi=[p.id for p in bowl_sel.playing_xi],
            bowling_pool=[p.id for p in bowl_sel.bowling_pool],
            overs_limit=fmt.overs_per_innings, wickets_limit=fmt.wickets_per_innings,
            target=cfg.target,
        )
        self._fmt = fmt
        self._recent: list[int] = []
        self._outcomes: list[int] = []
        self._over_counts: dict[int, int] = {}
        self._last_over_by_bowler: dict[int, int] = {}
        self._last_bowler: int | None = None
        self._start_over()

    # --- bowler rotation ---
    def _start_over(self) -> None:
        pool = self.inn.bowling_pool
        if self._last_bowler is None:
            bowler = pool[0]
        else:
            fatigues = {
                pid: fatigue_mod.fatigue_factor(
                    self._over_counts.get(pid, 0),
                    self.inn.overs_completed - self._last_over_by_bowler.get(pid, self.inn.overs_completed),
                    self._bowl_arch.get(pid, "pace"),
                )
                for pid in pool
            }
            bowler = cap_ai.pick_next_bowler(
                bowling_pool=pool, archetypes=self._bowl_arch, over_counts=self._over_counts,
                economies={}, last_bowler=self._last_bowler, over_idx=self.inn.overs_completed,
                total_overs=self._fmt.overs_per_innings, fmt=self._fmt, fatigues=fatigues, rng=self._rng,
            )
        self.inn.start_over(bowler)

    def _bot_fatigue(self, bowler_id: int) -> float:
        last = self._last_over_by_bowler.get(bowler_id)
        rested = (self.inn.overs_completed - last) if last is not None else self.inn.overs_completed
        return fatigue_mod.fatigue_factor(self._over_counts.get(bowler_id, 0), rested, self._bowl_arch.get(bowler_id, "pace"))

    # --- public API ---
    @property
    def is_complete(self) -> bool:
        return self.inn.is_complete

    def state(self) -> dict[str, Any]:
        inn = self.inn
        return {
            "batting": inn.batting_country,
            "bowling": inn.bowling_country,
            "runs": inn.runs,
            "wickets": inn.wickets,
            "balls": inn.balls,
            "overs": inn.overs_string,
            "striker_id": inn.striker_id,
            "bowler_id": inn.current_bowler_id,
            "this_over": list(inn.current_over_results),
            "target": inn.target,
            "runs_needed": inn.runs_needed,
            "balls_remaining": inn.balls_remaining,
            "complete": inn.is_complete,
        }

    def submit_pick(self, n: int) -> dict[str, Any]:
        """Resolve one ball for the user's batting pick ``n`` (0–6). Returns the
        outcome, detected events, and the new state."""
        if self.is_complete:
            return {"outcome": None, "events": [], "state": self.state()}
        if not (0 <= n <= 6):
            raise ValueError("pick must be 0..6")
        inn = self.inn
        bowler_id = inn.current_bowler_id if inn.current_bowler_id is not None else inn.bowling_pool[0]
        arch = self._bowl_arch.get(bowler_id, "pace")
        bot = bot_bowl_pick(
            bowler_archetype=arch, recent_user_batting_picks=self._recent,
            difficulty=self.config.difficulty, over_number=inn.overs_completed,
            fatigue=self._bot_fatigue(bowler_id), batting_outcomes=self._outcomes, rng=self._rng,
        )
        matched = n == bot
        self._recent.append(n)
        if matched:
            inn.record_ball(wicket="match")
            self._outcomes.append(-1)
        else:
            inn.record_ball(runs=n)
            self._outcomes.append(1 if n > 0 else -1)
        events = events_mod.detect(inn)
        # End-of-over rotation.
        if not inn.is_complete and inn.current_over_balls >= 6:
            inn.end_over()
            self._last_over_by_bowler[bowler_id] = inn.overs_completed
            self._over_counts[bowler_id] = self._over_counts.get(bowler_id, 0) + 1
            self._last_bowler = bowler_id
            if not inn.is_complete:
                self._start_over()
        return {
            "outcome": {"user_pick": n, "bot_pick": bot, "wicket": matched, "runs": 0 if matched else n},
            "events": [(e.kind, e.subtype) for e in events],
            "state": self.state(),
        }
