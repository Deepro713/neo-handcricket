"""Playing XI selection from a 33-player squad.

Rules (Q11 — accepted proposal):
  - Always in: captain, vice-captain, 2 of 3 keepers (gloveman + fielder).
  - Remaining slots filled to satisfy format role-mix constraints:
      T10 / T20: ≥ 4 bowlers
      ODI:       ≥ 5 bowlers, ≥ 1 spinner, ≥ 1 pacer
      Test:      ≥ 5 bowlers, ≥ 2 spinners, ≥ 2 pacers
  - For Custom playing_size < 11, just take the first N from the squad.

Returns:
  - playing_xi: list[Player] in batting order (cap, VC, keepers, batsmen, all-rounders, bowlers tail)
  - bowling_pool: list[Player] (~5) — the bowlers + all-rounders from the XI
"""
from __future__ import annotations

import random
from dataclasses import dataclass

from ..formats import Format
from .loader import Country, Player

PACE_LIKE = {"pace", "swing", "mystery"}
SPIN_LIKE = {"off-spin", "leg-spin"}


@dataclass
class Selection:
    playing_xi: list[Player]
    bowling_pool: list[Player]
    gloveman_id: int                 # the keeper actually keeping
    fielder_keeper_id: int | None    # second keeper playing as a fielder/batsman
    reserve_keeper_id: int | None    # third keeper not in XI


def _is_pacer(p: Player) -> bool:
    return p.bowling_archetype in PACE_LIKE

def _is_spinner(p: Player) -> bool:
    return p.bowling_archetype in SPIN_LIKE


def select_xi(country: Country, fmt: Format, rng: random.Random | None = None) -> Selection:
    rng = rng or random
    if fmt.playing_size < 11 or len(country.players) < 11:
        # Custom small squad — take first N players, treat first as captain by convention
        size = min(fmt.playing_size, len(country.players))
        xi = country.players[:size]
        bowlers_in_xi = [p for p in xi if p.can_bowl] or xi[-2:]  # fallback
        keeper_ids = [p.id for p in xi if p.role in ("keeper", "keeper-reserve")]
        gloveman = keeper_ids[0] if keeper_ids else xi[0].id
        return Selection(
            playing_xi=xi,
            bowling_pool=bowlers_in_xi[:5],
            gloveman_id=gloveman,
            fielder_keeper_id=None,
            reserve_keeper_id=None,
        )

    chosen: list[Player] = []
    chosen_ids: set[int] = set()

    # Captain + VC always in
    cap = country.captain
    vc = country.vice_captain
    chosen.append(cap)
    chosen_ids.add(cap.id)
    chosen.append(vc)
    chosen_ids.add(vc.id)

    # Two keepers — first listed becomes gloveman, second plays as fielder/batsman
    keepers = country.keepers[:3]
    if len(keepers) < 3:
        # Pad with whatever we have
        keepers = keepers + [k for k in country.players if k.role.startswith("keeper") and k not in keepers]
    gloveman = keepers[0]
    fielder_keeper = keepers[1] if len(keepers) > 1 else None
    reserve_keeper = keepers[2] if len(keepers) > 2 else None
    chosen.append(gloveman)
    chosen_ids.add(gloveman.id)
    if fielder_keeper:
        chosen.append(fielder_keeper)
        chosen_ids.add(fielder_keeper.id)

    remaining_slots = 11 - len(chosen)
    candidates = [p for p in country.players if p.id not in chosen_ids]

    # Step 1: enforce min_pacers + min_spinners + min_bowlers via greedy fill
    bowlers_in_chosen = sum(1 for p in chosen if p.can_bowl)
    pacers_in_chosen = sum(1 for p in chosen if _is_pacer(p))
    spinners_in_chosen = sum(1 for p in chosen if _is_spinner(p))

    needed_pacers = max(0, fmt.min_pacers - pacers_in_chosen)
    needed_spinners = max(0, fmt.min_spinners - spinners_in_chosen)
    needed_bowlers = max(0, fmt.min_bowlers_in_xi - bowlers_in_chosen)

    # Pull pacers
    pacer_pool = [p for p in candidates if _is_pacer(p)]
    rng.shuffle(pacer_pool)
    for _ in range(min(needed_pacers, remaining_slots)):
        if not pacer_pool:
            break
        p = pacer_pool.pop(0)
        chosen.append(p)
        chosen_ids.add(p.id)
        remaining_slots -= 1

    # Pull spinners
    spinner_pool = [p for p in candidates if _is_spinner(p) and p.id not in chosen_ids]
    rng.shuffle(spinner_pool)
    for _ in range(min(needed_spinners, remaining_slots)):
        if not spinner_pool:
            break
        p = spinner_pool.pop(0)
        chosen.append(p)
        chosen_ids.add(p.id)
        remaining_slots -= 1

    # Top up to min bowlers (any kind)
    bowlers_now = sum(1 for p in chosen if p.can_bowl)
    deficit = max(0, fmt.min_bowlers_in_xi - bowlers_now)
    bowler_pool = [p for p in candidates if p.can_bowl and p.id not in chosen_ids]
    rng.shuffle(bowler_pool)
    for _ in range(min(deficit, remaining_slots)):
        if not bowler_pool:
            break
        p = bowler_pool.pop(0)
        chosen.append(p)
        chosen_ids.add(p.id)
        remaining_slots -= 1

    # Step 2: fill remaining slots with batting depth (specialist batsmen + remaining all-rounders)
    bat_pool = [p for p in candidates if p.id not in chosen_ids and p.role in ("batsman", "all-rounder")]
    rng.shuffle(bat_pool)
    while remaining_slots > 0 and bat_pool:
        chosen.append(bat_pool.pop(0))
        remaining_slots -= 1

    # Step 3: still slots? grab anyone left
    leftovers = [p for p in candidates if p.id not in chosen_ids]
    rng.shuffle(leftovers)
    while remaining_slots > 0 and leftovers:
        chosen.append(leftovers.pop(0))
        remaining_slots -= 1

    # Sort into a sensible batting order: cap → VC → batsmen (by archetype priority) → all-rounders → keeper-bat → bowlers (tail)
    order_priority = {
        "captain": 0,
        "vice-captain": 0,
        "batsman": 1,
        "keeper": 2,
        "keeper-reserve": 2,
        "all-rounder": 3,
        "bowler": 4,
    }
    archetype_priority = {
        "opener": 0,
        "anchor": 1,
        "power-hitter": 2,
        "finisher": 3,
        "all-rounder": 4,
        "tail-ender": 5,
        None: 6,
    }
    chosen.sort(key=lambda p: (order_priority.get(p.role, 5), archetype_priority.get(p.batting_archetype, 6)))

    bowling_pool = [p for p in chosen if p.can_bowl][:5]
    if len(bowling_pool) < min(5, fmt.min_bowlers_in_xi):
        # Pad with anyone in chosen who has bowling_archetype set
        extras = [p for p in chosen if p.can_bowl and p not in bowling_pool]
        bowling_pool.extend(extras)
    return Selection(
        playing_xi=chosen,
        bowling_pool=bowling_pool[:5],
        gloveman_id=gloveman.id,
        fielder_keeper_id=fielder_keeper.id if fielder_keeper else None,
        reserve_keeper_id=reserve_keeper.id if reserve_keeper else None,
    )
