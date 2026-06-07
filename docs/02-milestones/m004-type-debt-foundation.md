---
title: M004 — Type-debt foundation
type: milestone
milestone: M004
status: Todo
state: open
version: v0.4.0
github:
  milestone: 4
---

# M004 — Type-debt foundation

**Status:** Todo · **Target version:** v0.4.0 · **GitHub milestone:** #4

## Goal
Pay down the ~44 mypy errors and make mypy a hard gate. Foundation first: every later milestone is type-checked. No gameplay change — pure correctness/quality.

See [[decision-log]] ADR-0003 (Round 1 direction) and [[2026-06-07-comparable-games]] (research).

## Clusters & issues
### `m004/types-fixes`
- [[m004-scoreboard-types]] — Fix mypy errors in ui/scoreboard.py (12)
- [[m004-selector-types]] — Fix mypy errors in rosters/selector.py (10)
- [[m004-main-types]] — Fix mypy errors in main.py (10)
- [[m004-strategy-types]] — Fix mypy errors in bots/strategy.py (9)
- [[m004-captain-innings-types]] — Fix mypy errors in bots/captain.py (2) + innings.py (1)
### `m004/gate-enforcement`
- [[m004-enforce-mypy]] — Add mypy to the QA gate + flip the 'advisory' note

## Definition of done
All issues shipped through the gate (ruff + mypy + pytest + playtest), one ADR per cluster, a
per-milestone status update (ON_TRACK → COMPLETE), README current-state + roadmap + wiki refreshed,
tagged **v0.4.0**.
