"""Innings + over + ball state.

The `Innings` object is the single source of truth for what's happened in a side's
turn at bat. `record_ball()` ingests one ball outcome and updates state. The
match driver (in match.py) decides when an innings is complete.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

WicketKind = Literal["bowled", "lbw", "match", "caught", "run-out"]
ExtraKind = Literal["wide", "no-ball", "byes", "leg-byes", "dead-ball"]


@dataclass
class BallEvent:
    over: int                   # 0-indexed
    ball_in_over: int           # 1..6 (legal balls; extras don't increment this until they re-bowl)
    striker_id: int
    bowler_id: int
    runs: int = 0               # runs to the batter
    extras: int = 0             # runs to extras (e.g. wide gives 1 extra)
    wicket: WicketKind | None = None
    extra_kind: ExtraKind | None = None  # type of extras delivered, if any
    timed_out: bool = False     # this ball came from a timer expiry
    counts_toward_over: bool = True  # wides/no-balls don't


@dataclass
class BatterCard:
    player_id: int
    runs: int = 0
    balls: int = 0
    fours: int = 0
    sixes: int = 0
    out_to: WicketKind | None = None
    out_bowler_id: int | None = None
    out_over: str | None = None  # over.ball string built later

    @property
    def strike_rate(self) -> float:
        return (self.runs / self.balls * 100) if self.balls else 0.0


@dataclass
class BowlerCard:
    player_id: int
    balls: int = 0          # legal balls bowled
    runs_conceded: int = 0  # all runs charged (incl. extras for wide/no-ball)
    wickets: int = 0
    maidens: int = 0
    _runs_in_current_over: int = 0
    _balls_in_current_over: int = 0

    @property
    def overs(self) -> str:
        return f"{self.balls // 6}.{self.balls % 6}"

    @property
    def overs_completed(self) -> int:
        return self.balls // 6

    @property
    def economy(self) -> float:
        if self.balls == 0:
            return 0.0
        return (self.runs_conceded * 6.0) / self.balls


@dataclass
class Innings:
    batting_country: str
    bowling_country: str
    batting_xi: list[int]               # 11 player ids in batting order
    bowling_xi: list[int]
    bowling_pool: list[int]             # 5-ish ids who can bowl
    overs_limit: int | None             # None = no over limit (Test/some custom)
    wickets_limit: int                  # usually 10
    target: int | None = None           # set on chase

    # Live state
    runs: int = 0
    extras: int = 0
    wickets: int = 0
    balls: int = 0                      # legal balls bowled
    striker_idx: int = 0                # index into batting_xi (0 = position 1)
    nonstriker_idx: int = 1
    next_batter_idx: int = 2

    declared: bool = False              # captain declared (Test only)

    current_bowler_id: int | None = None
    current_over_balls: int = 0         # legal balls bowled in current over
    current_over_runs: int = 0
    current_over_results: list[str] = field(default_factory=list)  # short tags per ball

    batter_cards: dict[int, BatterCard] = field(default_factory=dict)
    bowler_cards: dict[int, BowlerCard] = field(default_factory=dict)
    ball_log: list[BallEvent] = field(default_factory=list)

    def __post_init__(self) -> None:
        for pid in self.batting_xi:
            self.batter_cards.setdefault(pid, BatterCard(player_id=pid))
        for pid in self.bowling_xi:
            self.bowler_cards.setdefault(pid, BowlerCard(player_id=pid))

    @property
    def overs_string(self) -> str:
        return f"{self.balls // 6}.{self.balls % 6}"

    @property
    def overs_completed(self) -> int:
        return self.balls // 6

    @property
    def striker_id(self) -> int:
        return self.batting_xi[self.striker_idx]

    @property
    def nonstriker_id(self) -> int:
        return self.batting_xi[self.nonstriker_idx]

    @property
    def is_complete(self) -> bool:
        if self.declared:
            return True
        if self.wickets >= self.wickets_limit:
            return True
        if self.overs_limit is not None and self.balls >= self.overs_limit * 6:
            return True
        if self.target is not None and self.runs >= self.target:
            return True
        return False

    @property
    def runs_needed(self) -> int | None:
        if self.target is None:
            return None
        return max(0, self.target - self.runs)

    @property
    def balls_remaining(self) -> int | None:
        if self.overs_limit is None:
            return None
        return self.overs_limit * 6 - self.balls

    def start_over(self, bowler_id: int) -> None:
        self.current_bowler_id = bowler_id
        self.current_over_balls = 0
        self.current_over_runs = 0
        self.current_over_results = []
        self.bowler_cards.setdefault(bowler_id, BowlerCard(player_id=bowler_id))
        self.bowler_cards[bowler_id]._runs_in_current_over = 0
        self.bowler_cards[bowler_id]._balls_in_current_over = 0

    def end_over(self) -> None:
        # Maiden = legal-ball over with 0 runs charged
        b = self.current_bowler_id
        if b is not None:
            card = self.bowler_cards[b]
            if card._balls_in_current_over == 6 and card._runs_in_current_over == 0:
                card.maidens += 1
        # Strike rotation at end of over
        self.striker_idx, self.nonstriker_idx = self.nonstriker_idx, self.striker_idx

    def record_ball(
        self,
        runs: int = 0,
        extras: int = 0,
        wicket: WicketKind | None = None,
        extra_kind: ExtraKind | None = None,
        timed_out: bool = False,
    ) -> BallEvent:
        bowler_id = self.current_bowler_id
        if bowler_id is None:
            raise RuntimeError("No bowler set; call start_over() first")

        striker_id = self.striker_id
        # Determine if this ball counts toward the over
        counts = extra_kind not in {"wide", "no-ball", "dead-ball"}

        # Update score
        self.runs += runs
        self.extras += extras
        self.runs += extras  # extras add to total too
        self.current_over_runs += runs + extras

        # Update bowler card
        bowler_card = self.bowler_cards[bowler_id]
        bowler_card.runs_conceded += runs + extras
        bowler_card._runs_in_current_over += runs + extras
        if counts:
            bowler_card.balls += 1
            bowler_card._balls_in_current_over += 1
            self.balls += 1
            self.current_over_balls += 1

        # Update batter card (only on legal balls — wides don't count balls faced)
        striker_card = self.batter_cards[striker_id]
        if extra_kind != "wide":  # batter faced this ball
            striker_card.balls += 1
        striker_card.runs += runs
        if runs == 4:
            striker_card.fours += 1
        elif runs == 6:
            striker_card.sixes += 1

        # Wicket?
        if wicket is not None:
            self.wickets += 1
            bowler_card.wickets += 1
            striker_card.out_to = wicket
            striker_card.out_bowler_id = bowler_id
            striker_card.out_over = self.overs_string
            # Bring next batter on as striker
            if self.next_batter_idx < len(self.batting_xi):
                self.striker_idx = self.next_batter_idx
                self.next_batter_idx += 1

        # Strike rotation on odd runs (not on extras-only balls, not on wickets)
        if wicket is None and counts and runs % 2 == 1:
            self.striker_idx, self.nonstriker_idx = self.nonstriker_idx, self.striker_idx

        # Build event tag (compact)
        tag = self._build_tag(runs, extras, wicket, extra_kind)
        self.current_over_results.append(tag)

        event = BallEvent(
            over=self.overs_completed,
            ball_in_over=self.current_over_balls if counts else self.current_over_balls + 1,
            striker_id=striker_id,
            bowler_id=bowler_id,
            runs=runs,
            extras=extras,
            wicket=wicket,
            extra_kind=extra_kind,
            timed_out=timed_out,
            counts_toward_over=counts,
        )
        self.ball_log.append(event)
        return event

    @staticmethod
    def _build_tag(runs: int, extras: int, wicket: WicketKind | None, extra_kind: ExtraKind | None) -> str:
        if wicket is not None:
            return "W"
        if extra_kind == "wide":
            return f"wd+{extras}" if extras > 1 else "wd"
        if extra_kind == "no-ball":
            return f"nb+{runs}" if runs > 0 else "nb"
        if extra_kind == "byes":
            return f"b{extras}"
        if extra_kind == "leg-byes":
            return f"lb{extras}"
        if extra_kind == "dead-ball":
            return "•"
        return str(runs)
