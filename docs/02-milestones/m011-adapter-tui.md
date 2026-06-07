---
title: M011 — Headless adapter & Textual TUI foundation
type: milestone
milestone: M011
status: Done
state: closed
version: v1.1.0
github:
  milestone: 11
---

# M011 — Headless adapter & Textual TUI foundation

**Status:** Done · **Target version:** v1.1.0 · **GitHub milestone:** #11

## Goal
Open the engine to new front-ends (research §3): a UI-agnostic headless adapter any UI can drive, the CLI routed through it, and an optional local Textual TUI. Offline only — de-risks a future web/GUI port without adding network/telemetry.

See [[decision-log]] ADR-0021 (Round 2 direction) and [[2026-06-07-round2]] (research).

## Clusters & issues
### `m011/adapter`
- [[m011-headless-adapter]] — Headless game adapter (UI-agnostic API)
- [[m011-adapter-refactor-cli]] — Route the CLI through the adapter (no behaviour change)
### `m011/tui`
- [[m011-textual-tui]] — Optional local Textual TUI (foundation)

## Definition of done
All issues shipped through the gate (ruff + mypy + pytest + playtest), one ADR per cluster, a
per-milestone status update (ON_TRACK → COMPLETE), README current-state + roadmap + wiki refreshed,
tagged **v1.1.0**.
