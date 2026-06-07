---
title: M001 — Core engine
type: milestone
milestone: M001
status: Done
state: closed
version: v0.1.0
github:
  milestone: 1
---

# M001 — Core engine

> **Retroactive milestone** — reconstructed on 2026-06-07 to represent work that shipped before the
> autonomous-dev cycle existed. Dates below are the true historical ship dates; GitHub issue/milestone
> `created_at` timestamps reflect the reconstruction date and cannot be backdated (the platform forbids it).

**Status:** Done · **Version:** v0.1.0 · **Shipped:** 2026-05-08 · **Commits:** `3b1bb01`

## Summary
Initial CLI v1. The complete playable core: five-format scaffolding, innings/match state machine, toss, adaptive bot AI, keystroke timer, rosters, single-line commentary, persistence and UI.

## Issues (all Done)
- [ ] ~~#2 Match formats & format definitions (T10/T20/ODI/Custom)~~ ✅
- [ ] ~~#3 Innings & match state machine~~ ✅
- [ ] ~~#4 Toss subsystem with 100 retoss excuses~~ ✅
- [ ] ~~#5 Adaptive bot AI (profiles, strategy, captain rotation)~~ ✅
- [ ] ~~#6 Hidden 3-second keystroke timer + timeout outcomes~~ ✅
- [ ] ~~#7 Country rosters (14 curated) + loader/validator/selector~~ ✅
- [ ] ~~#8 20-commentator framework (single-line)~~ ✅
- [ ] ~~#9 Persistence: save/pause/quit + career stats~~ ✅
- [ ] ~~#10 Scoreboard / UI + Player of the Match~~ ✅

## Outcome
Tagged **v0.1.0** (backdated annotated tag at the historical commit) with a matching GitHub release.
See [[decision-log]] ADR-0002 for the reconstruction rationale and the chosen v0.x version scheme.
