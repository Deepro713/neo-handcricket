---
title: M012 — Roguelite draft: relics & run modifiers
type: milestone
milestone: M012
status: Todo
state: open
version: v1.2.0
github:
  milestone: 12
---

# M012 — Roguelite draft: relics & run modifiers

**Status:** Todo · **Target version:** v1.2.0 · **GitHub milestone:** #12

## Goal
Deepen the roguelite (research §4): run-scoped relics/modifiers drafted between matches with real opportunity cost, composing over the M005/M006 tunables and the M008 career for build variety.

See [[decision-log]] ADR-0021 (Round 2 direction) and [[2026-06-07-round2]] (research).

## Clusters & issues
### `m012/relics-core`
- [[m012-relic-registry]] — Relic / run-modifier registry (pure)
- [[m012-draft]] — Between-match relic draft (pure)
### `m012/career-and-ui`
- [[m012-relics-career-ui]] — Wire relics into the career + draft UI + playtest

## Definition of done
All issues shipped through the gate (ruff + mypy + pytest + playtest), one ADR per cluster, a
per-milestone status update (ON_TRACK → COMPLETE), README current-state + roadmap + wiki refreshed,
tagged **v1.2.0**.
