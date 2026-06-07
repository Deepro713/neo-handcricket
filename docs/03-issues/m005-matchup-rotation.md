---
title: Match-up-aware bowling rotation (captain AI)
type: issue
milestone: M005
area: bots
priority: P1
cluster: m005/rotation
labels:
  - enhancement
status: Todo
state: open
github:
  issue: 29
---

# Match-up-aware bowling rotation (captain AI)

Extend `bots/captain.py` so the captain biases bowler choice toward favourable **archetype match-ups** against the current batter and toward **fresher** bowlers (integrating the M005 fatigue model). Keep the existing phase logic (power/middle/death) and over-cap / no-consecutive-overs rules.

**Scope:** a match-up advantage table (bowler archetype × batter archetype), combined with fatigue and phase into a score; pick the best eligible. Pure, seeded tie-breaks.

**Tests:** prefers advantaged archetype when phase/fatigue tie; avoids the gassed bowler; never breaks cap / consecutive-over invariants (existing playtest checks stay green).
