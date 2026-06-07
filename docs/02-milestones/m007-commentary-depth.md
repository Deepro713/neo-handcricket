---
title: M007 — Commentary & presentation depth
type: milestone
milestone: M007
status: Done
state: closed
version: v0.7.0
github:
  milestone: 7
---

# M007 — Commentary & presentation depth

**Status:** Done · **Target version:** v0.7.0 · **GitHub milestone:** #7

## Goal
Make every big moment land (research §3): a pure event detector, big-moment line banks, context-aware lines referencing M005/M006 state, and scoreboard/summary polish.

See [[decision-log]] ADR-0003 (Round 1 direction) and [[2026-06-07-comparable-games]] (research).

## Clusters & issues
### `m007/event-detection`
- [[m007-event-detection]] — Pure-logic big-moment event detector
### `m007/bigmoment-lines`
- [[m007-bigmoment-lines]] — Big-moment commentary line banks
### `m007/context-and-polish`
- [[m007-context-lines]] — Context-aware lines referencing fatigue / momentum / reads
- [[m007-presentation-polish]] — Scoreboard & summary polish for milestones

## Definition of done
All issues shipped through the gate (ruff + mypy + pytest + playtest), one ADR per cluster, a
per-milestone status update (ON_TRACK → COMPLETE), README current-state + roadmap + wiki refreshed,
tagged **v0.7.0**.
