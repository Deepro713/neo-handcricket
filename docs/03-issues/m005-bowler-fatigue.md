---
title: Bowler fatigue model (pure logic)
type: issue
milestone: M005
area: bots
priority: P1
cluster: m005/fatigue
labels:
  - enhancement
status: Done
state: closed
github:
  issue: 28
---

# Bowler fatigue model (pure logic)

A bowler's effectiveness decays the longer they bowl in a spell and recovers with rest. Effectiveness modulates two things from `bots/profiles.py`: **flatten the base distribution** (toward uniform => easier to score off / harder to take wickets) and **lower the effective α** (worse at reading the batter).

**Scope:** new pure module `neo_handcricket/bots/fatigue.py` with a `fatigue_factor(overs_in_spell, overs_rested, archetype) -> float` (0..1) and a helper that applies it to a base distribution + α. Config tunables in `config.py` (decay rate, recovery rate, spin vs pace stamina). Wire through `strategy.pick_number`.

**Tests:** monotonic decay within a spell; recovery after rest; pacers tire faster than spinners; factor stays in [0,1]; seeded outputs reproducible.
