---
title: M005 — Cricket realism layer
type: milestone
milestone: M005
status: Done
state: closed
version: v0.5.0
github:
  milestone: 5
---

# M005 — Cricket realism layer

**Status:** Done · **Target version:** v0.5.0 · **GitHub milestone:** #5

## Goal
Deepen the simulation with the standard cricket-sim levers (research §2): bowler fatigue, batsman match-state/momentum, match-up-aware rotation. Pure-logic, seeded, unit-tested; playtest invariants extended.

See [[decision-log]] ADR-0003 (Round 1 direction) and [[2026-06-07-comparable-games]] (research).

## Clusters & issues
### `m005/fatigue`
- [[m005-bowler-fatigue]] — Bowler fatigue model (pure logic)
### `m005/matchstate`
- [[m005-batsman-matchstate]] — Batsman match-state / momentum model (pure logic)
### `m005/rotation`
- [[m005-matchup-rotation]] — Match-up-aware bowling rotation (captain AI)
### `m005/ui-and-playtest`
- [[m005-realism-ui]] — Surface fatigue & settled-state in the UI (thin)
- [[m005-playtest-invariants]] — Extend the playtest with realism invariants + recorded review

## Definition of done
All issues shipped through the gate (ruff + mypy + pytest + playtest), one ADR per cluster, a
per-milestone status update (ON_TRACK → COMPLETE), README current-state + roadmap + wiki refreshed,
tagged **v0.5.0**.
