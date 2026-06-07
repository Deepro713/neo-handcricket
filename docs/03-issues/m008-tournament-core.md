---
title: Offline tournament / campaign core (pure logic)
type: issue
milestone: M008
area: engine
priority: P1
cluster: m008/tournament-core
labels:
  - enhancement
status: Done
state: closed
github:
  issue: 46
---

# Offline tournament / campaign core (pure logic)

A run = a tournament. Pure-logic structures for a bracket (knockout) and/or a league table, fixture generation, seeding by reputation, progression and elimination — all offline and seeded.

**Scope:** `neo_handcricket/career/tournament.py` (pure). Drives a series of matches via the existing match engine.

**Tests:** bracket advances correctly; league points/NRR ordering; deterministic under seed; a full tournament resolves to one winner.
