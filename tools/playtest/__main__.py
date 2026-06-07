"""Headless game-sim playtest — the gameplay QA gate (analogous to Streetbound's
driving playtest). Plays full innings across every format + a custom match over
several seeds and country pairings using the pure engine layer (no UI/prompts),
asserting invariants. Exits non-zero on any failure.

    python -m tools.playtest            # run the gate
    python -m tools.playtest --record out.txt   # also write a transcript
"""
from __future__ import annotations

import argparse
import random
import sys

from neo_handcricket.bots import strategy
from neo_handcricket.formats import PRESETS
from neo_handcricket.formats import custom as custom_fmt
from neo_handcricket.innings import Innings
from neo_handcricket.rosters import loader, selector

COUNTRIES = ["india", "england", "australia", "antarctica", "japan", "brazil"]
RESULTS: list[tuple[bool, str, str]] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    RESULTS.append((cond, name, detail))


def _sim_innings(inn: Innings, bowling, *, rng: random.Random, cap: int = 5000) -> None:
    pool = inn.bowling_pool
    bi = 0
    inn.start_over(pool[bi])
    barch = {p.id: (p.bowling_archetype or "pace") for p in bowling.players}
    recent: list[int] = []
    safety = 0
    while not inn.is_complete and safety < cap:
        safety += 1
        if inn.current_over_balls >= 6:
            inn.end_over()
            bi = (bi + 1) % len(pool)
            inn.start_over(pool[bi])
        bot = strategy.pick_number(
            archetype=barch.get(inn.current_bowler_id, "pace"), is_bowler=True,
            recent_user_picks=recent, difficulty="medium",
            over_number=inn.overs_completed, rng=rng,
        )
        pick = rng.randint(0, 6)
        recent.append(pick)
        inn.record_ball(wicket="match") if pick == bot else inn.record_ball(runs=pick)


def _play(fmt, a_id: str, b_id: str, seed: int, lines: list[str]) -> None:
    a, b = loader.load_country(a_id), loader.load_country(b_id)
    rng = random.Random(seed)
    sa = selector.select_xi(a, fmt, rng=rng)
    sb = selector.select_xi(b, fmt, rng=rng)
    inn = Innings(
        batting_country=a.country, bowling_country=b.country,
        batting_xi=[p.id for p in sa.playing_xi], bowling_xi=[p.id for p in sb.playing_xi],
        bowling_pool=[p.id for p in sb.bowling_pool],
        overs_limit=fmt.overs_per_innings, wickets_limit=fmt.wickets_per_innings,
    )
    _sim_innings(inn, b, rng=rng)
    tag = f"{fmt.name} {a_id}v{b_id}#{seed}"
    check(f"{tag}: innings completes", inn.is_complete, f"balls={inn.balls} runs={inn.runs} wkts={inn.wickets}")
    check(f"{tag}: runs non-negative", inn.runs >= 0, f"runs={inn.runs}")
    check(f"{tag}: wickets within limit", inn.wickets <= fmt.wickets_per_innings, f"wkts={inn.wickets}")
    if fmt.overs_per_innings:
        check(f"{tag}: balls within limit", inn.balls <= fmt.overs_per_innings * 6, f"balls={inn.balls}")
    lines.append(f"{tag}: {inn.runs}/{inn.wickets} in {inn.balls} balls")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", metavar="FILE", help="write a transcript of the sessions")
    args = ap.parse_args()
    lines: list[str] = []
    for fmt_name in ("T10", "T20", "ODI"):
        fmt = PRESETS[fmt_name]
        for seed in (1, 7, 42):
            a, b = COUNTRIES[seed % len(COUNTRIES)], COUNTRIES[(seed + 2) % len(COUNTRIES)]
            try:
                _play(fmt, a, b, seed, lines)
            except Exception as e:  # noqa: BLE001 — a crash IS a failed check
                check(f"{fmt_name} {a}v{b}#{seed}: no crash", False, repr(e))
    # A custom 1v1 match
    try:
        _play(custom_fmt(overs=5, wickets=1, innings_per_team=1, playing_size=2), "england", "antarctica", 99, lines)
    except Exception as e:  # noqa: BLE001
        check("custom 1v1: no crash", False, repr(e))

    if args.record:
        with open(args.record, "w") as f:
            f.write("\n".join(lines) + "\n")

    passed = sum(1 for ok, *_ in RESULTS if ok)
    for ok, name, detail in RESULTS:
        if not ok:
            print(f"[FAIL] {name} — {detail}")
    print(f"\n{passed}/{len(RESULTS)} checks passed; {len(RESULTS) - passed} failure(s).")
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
