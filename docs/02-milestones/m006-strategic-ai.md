---
title: M006 — Strategic AI & opponent modelling
type: milestone
milestone: M006
status: Done
state: closed
version: v0.6.0
github:
  milestone: 6
---

# M006 — Strategic AI & opponent modelling

**Status:** Done · **Target version:** v0.6.0 · **GitHub milestone:** #6

## Goal
Make the bot a real opponent (research §1): WSLS + n-gram detection, exploit-vs-mix balancing, richer difficulty, optional tells, and an offline eval harness proving it beats the frequency-only baseline.

See [[decision-log]] ADR-0003 (Round 1 direction) and [[2026-06-07-comparable-games]] (research).

## Clusters & issues
### `m006/opponent-model`
- [[m006-wsls-detection]] — Win-Stay-Lose-Shift detection + counter
- [[m006-sequence-model]] — Sequence (n-gram) / anti-repetition modelling
- [[m006-exploit-vs-mix]] — Exploit-vs-mix balancing (stay unpredictable)
### `m006/difficulty`
- [[m006-difficulty-depth]] — Richer difficulty tiers wiring the new models
### `m006/tells`
- [[m006-tells]] — Optional player-facing 'tells'
### `m006/eval`
- [[m006-ai-eval]] — Offline AI eval harness + playtest hook

## Definition of done
All issues shipped through the gate (ruff + mypy + pytest + playtest), one ADR per cluster, a
per-milestone status update (ON_TRACK → COMPLETE), README current-state + roadmap + wiki refreshed,
tagged **v0.6.0**.
