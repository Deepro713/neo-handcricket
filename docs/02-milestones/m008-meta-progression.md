---
title: M008 — Career & roguelite meta-progression
type: milestone
milestone: M008
status: Todo
state: open
version: v0.8.0
github:
  milestone: 8
---

# M008 — Career & roguelite meta-progression

**Status:** Todo · **Target version:** v0.8.0 · **GitHub milestone:** #8

## Goal
Wrap it in progression (research §4): an offline tournament campaign with banked currency, variety unlocks, achievements and shareable save codes — every session banks something. Single-player/offline.

See [[decision-log]] ADR-0003 (Round 1 direction) and [[2026-06-07-comparable-games]] (research).

## Clusters & issues
### `m008/tournament-core`
- [[m008-tournament-core]] — Offline tournament / campaign core (pure logic)
### `m008/progression`
- [[m008-progression]] — Banked currency, variety unlocks & progression persistence
### `m008/achievements`
- [[m008-achievements]] — Achievements & shareable save codes
### `m008/ui-and-playtest`
- [[m008-campaign-ui]] — Campaign menu, progression dashboard & unlock UI (thin)
- [[m008-playtest-campaign]] — Headless full-tournament playtest invariant

## Definition of done
All issues shipped through the gate (ruff + mypy + pytest + playtest), one ADR per cluster, a
per-milestone status update (ON_TRACK → COMPLETE), README current-state + roadmap + wiki refreshed,
tagged **v0.8.0**.
