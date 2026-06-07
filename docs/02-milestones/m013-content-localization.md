---
title: M013 — Content & localization scaffold
type: milestone
milestone: M013
status: Todo
state: open
version: v1.3.0
github:
  milestone: 13
---

# M013 — Content & localization scaffold

**Status:** Todo · **Target version:** v1.3.0 · **GitHub milestone:** #13

## Goal
Broaden reach (research §5): more hand-curated rosters and commentary, plus a parallel string-table structure so the English-only commentary can be localized later. CC0/original.

See [[decision-log]] ADR-0021 (Round 2 direction) and [[2026-06-07-round2]] (research).

## Clusters & issues
### `m013/localization`
- [[m013-localization-scaffold]] — Localization scaffold (parallel string tables)
### `m013/content`
- [[m013-curated-rosters]] — Hand-curate more rosters
- [[m013-more-commentary]] — Expand commentary breadth

## Definition of done
All issues shipped through the gate (ruff + mypy + pytest + playtest), one ADR per cluster, a
per-milestone status update (ON_TRACK → COMPLETE), README current-state + roadmap + wiki refreshed,
tagged **v1.3.0**.
