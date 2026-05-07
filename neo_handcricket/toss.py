"""Toss subsystem.

Hidden 0–6 RNG. Parity → heads/tails. 0 → retoss with a ridiculous excuse.
After RETOSS_CAP consecutive 0s, fall back to a fair flip with a meta-line.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Literal

from .config import RETOSS_CAP
from .excuses import FALLBACK_LINE, random_excuse


CoinFace = Literal["heads", "tails"]


@dataclass
class TossEvent:
    kind: Literal["call", "retoss", "fallback"]
    excuse: str | None = None
    face: CoinFace | None = None
    raw: int | None = None


@dataclass
class TossResult:
    face: CoinFace
    user_call: CoinFace
    user_won: bool
    events: list[TossEvent] = field(default_factory=list)


def parity_to_face(n: int) -> CoinFace:
    return "heads" if n % 2 == 1 else "tails"


def roll_coin() -> int:
    return random.randint(0, 6)


def perform_toss(user_call: CoinFace) -> TossResult:
    """Perform a toss start-to-finish. Returns the full event sequence so the UI can pace it."""
    events: list[TossEvent] = []
    seen_excuses: set[str] = set()
    consecutive_zeros = 0

    while True:
        n = roll_coin()
        if n == 0:
            consecutive_zeros += 1
            if consecutive_zeros >= RETOSS_CAP:
                # Fair flip fallback
                fair = random.choice([1, 2])  # 1=heads, 2=tails
                face = parity_to_face(fair)
                events.append(TossEvent(kind="fallback", excuse=FALLBACK_LINE, face=face, raw=fair))
                user_won = (face == user_call)
                return TossResult(face=face, user_call=user_call, user_won=user_won, events=events)
            excuse = random_excuse(seen=seen_excuses)
            seen_excuses.add(excuse)
            events.append(TossEvent(kind="retoss", excuse=excuse))
            continue
        face = parity_to_face(n)
        events.append(TossEvent(kind="call", face=face, raw=n))
        user_won = (face == user_call)
        return TossResult(face=face, user_call=user_call, user_won=user_won, events=events)


def machine_picks_bat_or_bowl() -> Literal["bat", "bowl"]:
    return random.choice(["bat", "bowl"])
