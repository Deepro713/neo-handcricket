"""Unit tests for match-up-aware bowling rotation (M005)."""
from __future__ import annotations

import random

from neo_handcricket.bots import captain
from neo_handcricket.formats import PRESETS


def _t20():
    return PRESETS["T20"]


def test_matchup_advantage_lookup() -> None:
    assert captain.matchup_advantage("pace", "power-hitter") < 0  # pace struggles vs power
    assert captain.matchup_advantage("swing", "opener") > 0       # swing strong vs opener
    assert captain.matchup_advantage("pace", None) == 0.0         # unknown batter → neutral
    assert captain.matchup_advantage("unknown", "anchor") == 0.0  # unknown bowler → neutral


def test_respects_no_consecutive_over() -> None:
    pool = [1, 2, 3, 4]
    arch = {1: "pace", 2: "pace", 3: "off-spin", 4: "leg-spin"}
    pick = captain.pick_next_bowler(
        bowling_pool=pool, archetypes=arch, over_counts={}, economies={},
        last_bowler=1, over_idx=0, total_overs=20, fmt=_t20(), rng=random.Random(0),
    )
    assert pick != 1


def test_respects_over_cap() -> None:
    pool = [1, 2, 3, 4]
    arch = {1: "pace", 2: "pace", 3: "off-spin", 4: "leg-spin"}
    fmt = _t20()
    cap = fmt.bowler_over_cap
    assert cap is not None
    over_counts = {1: cap, 2: cap}  # 1 and 2 are maxed out
    for seed in range(20):
        pick = captain.pick_next_bowler(
            bowling_pool=pool, archetypes=arch, over_counts=dict(over_counts),
            economies={}, last_bowler=None, over_idx=2, total_overs=20, fmt=fmt,
            rng=random.Random(seed),
        )
        assert pick in (3, 4)


def test_matchup_bias_prefers_advantaged_bowler() -> None:
    # Middle phase, two spinners; one (leg-spin) is strongly advantaged vs a finisher.
    pool = [10, 11]
    arch = {10: "off-spin", 11: "leg-spin"}
    picks = {
        captain.pick_next_bowler(
            bowling_pool=pool, archetypes=arch, over_counts={}, economies={},
            last_bowler=None, over_idx=10, total_overs=20, fmt=_t20(),
            batter_archetype="finisher", rng=random.Random(seed),
        )
        for seed in range(30)
    }
    # leg-spin (0.20 vs finisher) should be the deterministic top pick of the 2-pool.
    assert picks == {11}


def test_freshness_breaks_toward_rested_bowler() -> None:
    # Two identical pace bowlers in the powerplay; one is gassed.
    pool = [5, 6]
    arch = {5: "pace", 6: "pace"}
    picks = {
        captain.pick_next_bowler(
            bowling_pool=pool, archetypes=arch, over_counts={}, economies={},
            last_bowler=None, over_idx=0, total_overs=20, fmt=_t20(),
            fatigues={5: 0.9, 6: 0.0}, rng=random.Random(seed),
        )
        for seed in range(30)
    }
    assert picks == {6}  # the fresh bowler wins the 2-pool every time


def test_death_phase_prefers_economy() -> None:
    pool = [7, 8, 9]
    arch = {7: "pace", 8: "swing", 9: "leg-spin"}
    econ = {7: 9.5, 8: 5.0, 9: 7.0}
    pick = captain.pick_next_bowler(
        bowling_pool=pool, archetypes=arch, over_counts={}, economies=econ,
        last_bowler=None, over_idx=18, total_overs=20, fmt=_t20(), rng=random.Random(3),
    )
    assert pick == 8  # lowest economy at the death
