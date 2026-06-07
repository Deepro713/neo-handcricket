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

from neo_handcricket.bots import captain, evaluation, fatigue, matchstate, strategy
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


def _realism_invariants(lines: list[str]) -> None:
    """M005 realism-layer invariants: fatigue, batsman match-state, rotation."""
    # --- Bowler fatigue ---
    fs = [fatigue.fatigue_factor(o, 0, "pace") for o in range(8)]
    check("fatigue: rises within a spell", all(b >= a for a, b in zip(fs, fs[1:], strict=False)))
    check("fatigue: rest reduces it", fatigue.fatigue_factor(6, 4, "pace") < fatigue.fatigue_factor(6, 0, "pace"))
    check("fatigue: pace tires faster than spin",
          fatigue.fatigue_factor(5, 0, "pace") > fatigue.fatigue_factor(5, 0, "off-spin"))
    # A gassed bowler matches a predictable batter less than a fresh one.
    rng = random.Random(11)
    recent = [4] * 5
    fresh_hits = sum(
        strategy.pick_number(archetype="pace", is_bowler=True, recent_user_picks=recent,
                             difficulty="hard", fatigue=0.0, rng=rng) == 4
        for _ in range(400)
    )
    tired_hits = sum(
        strategy.pick_number(archetype="pace", is_bowler=True, recent_user_picks=recent,
                             difficulty="hard", fatigue=0.9, rng=rng) == 4
        for _ in range(400)
    )
    check("fatigue: tired bowler matches predictable batter less", fresh_hits > tired_hits,
          f"fresh={fresh_hits} tired={tired_hits}")

    # --- Batsman match-state / momentum ---
    ss = [matchstate.settledness(b) for b in range(12)]
    check("matchstate: settledness monotonic from 0", ss[0] == 0.0 and all(b >= a for a, b in zip(ss, ss[1:], strict=False)))
    check("matchstate: chase raises intent", matchstate.aggression(1.0, 1.0) > matchstate.aggression(0.0, 0.0))
    rng = random.Random(22)
    tentative_big = sum(
        strategy.pick_number(archetype="anchor", is_bowler=False, recent_user_picks=[],
                             difficulty="medium", aggression=0.1, rng=rng) in (4, 6)
        for _ in range(400)
    )
    aggressive_big = sum(
        strategy.pick_number(archetype="anchor", is_bowler=False, recent_user_picks=[],
                             difficulty="medium", aggression=0.95, rng=rng) in (4, 6)
        for _ in range(400)
    )
    check("matchstate: aggressive batter hits more boundaries", aggressive_big > tentative_big,
          f"tentative={tentative_big} aggressive={aggressive_big}")

    # --- Match-up-aware rotation: invariants over a full T20 innings ---
    rng = random.Random(5)
    pool = [1, 2, 3, 4, 5]
    arch = {1: "pace", 2: "swing", 3: "off-spin", 4: "leg-spin", 5: "mystery"}
    fmt = PRESETS["T20"]
    over_counts: dict[int, int] = {}
    last: int | None = None
    no_consecutive = True
    cap_ok = True
    for ov in range(fmt.overs_per_innings or 20):
        b = captain.pick_next_bowler(
            bowling_pool=pool, archetypes=arch, over_counts=over_counts, economies={},
            last_bowler=last, over_idx=ov, total_overs=fmt.overs_per_innings, fmt=fmt,
            batter_archetype="anchor",
            fatigues={pid: fatigue.fatigue_factor(over_counts.get(pid, 0), 0, arch[pid]) for pid in pool},
            rng=rng,
        )
        if b == last:
            no_consecutive = False
        over_counts[b] = over_counts.get(b, 0) + 1
        if fmt.bowler_over_cap is not None and over_counts[b] > fmt.bowler_over_cap:
            cap_ok = False
        last = b
    check("rotation: no consecutive overs across an innings", no_consecutive)
    check("rotation: respects per-bowler over cap", cap_ok, f"counts={over_counts}")
    lines.append(f"realism: fatigue fresh/tired matches={fresh_hits}/{tired_hits}; "
                 f"boundaries tentative/aggressive={tentative_big}/{aggressive_big}; rotation={over_counts}")

    # --- Strategic AI: opponent model beats the frequency baseline (M006) ---
    model_sum = base_sum = 0.0
    for seed in (0, 1, 2):
        res = evaluation.evaluate(n_balls=400, seed=seed)
        for name in ("favourite", "wsls", "sequence"):
            model_sum += res[name]["model"]
            base_sum += res[name]["baseline"]
    check("ai-eval: opponent model beats frequency baseline vs predictable players",
          model_sum > base_sum, f"model={model_sum:.3f} baseline={base_sum:.3f}")
    fav = evaluation.simulate_match_rate(evaluation.favourite_pattern(4), epsilon=0.08, n_balls=600, seed=1)
    check("ai-eval: favourite-number player exploited above chance", fav > 0.18, f"rate={fav:.3f}")
    lines.append(f"ai-eval: predictable model/baseline={model_sum:.3f}/{base_sum:.3f}; favourite={fav:.3f}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", metavar="FILE", help="write a transcript of the sessions")
    args = ap.parse_args()
    lines: list[str] = []
    _realism_invariants(lines)
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
