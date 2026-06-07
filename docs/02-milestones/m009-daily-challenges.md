---
title: M009 — Daily-seed & procedural challenges
type: milestone
milestone: M009
status: Done
state: closed
version: v0.9.0
github:
  milestone: 9
---

# M009 — Daily-seed & procedural challenges

**Status:** Done · **Target version:** v0.9.0 · **GitHub milestone:** #9

## Goal
Give players a reason to return every day (research §1): a date-seeded daily match with shared modifiers, a score + local best-table, and offline shareable results. We already have seeded RNG + share codes — this is mostly a deterministic seed + scoring + a thin menu.

See [[decision-log]] ADR-0021 (Round 2 direction) and [[2026-06-07-round2]] (research).

## Clusters & issues
### `m009/daily-core`
- [[m009-daily-seed]] — Date-seeded daily challenge core (pure)
- [[m009-modifiers]] — Daily challenge modifiers (pure)
### `m009/leaderboard`
- [[m009-score-leaderboard]] — Daily score function + local best-table
### `m009/ui-and-playtest`
- [[m009-daily-ui-playtest]] — Daily challenge menu + playtest invariant

## Definition of done
All issues shipped through the gate (ruff + mypy + pytest + playtest), one ADR per cluster, a
per-milestone status update (ON_TRACK → COMPLETE), README current-state + roadmap + wiki refreshed,
tagged **v0.9.0**.
