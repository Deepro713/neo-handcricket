---
title: M010 — Accessibility, onboarding & 1.0 polish
type: milestone
milestone: M010
status: Todo
state: open
version: v1.0.0
github:
  milestone: 10
---

# M010 — Accessibility, onboarding & 1.0 polish

**Status:** Todo · **Target version:** v1.0.0 · **GitHub milestone:** #10

## Goal
The v1.0.0 headline (research §2): meet CLI accessibility standards (NO_COLOR, static/no-animation a11y mode, colour-never-alone, configurable/untimed timer) and add an onboarding tutorial + a definitive polish pass. The release that says 'this is done and welcoming'.

See [[decision-log]] ADR-0021 (Round 2 direction) and [[2026-06-07-round2]] (research).

## Clusters & issues
### `m010/a11y-core`
- [[m010-no-color-a11y-mode]] — Honour NO_COLOR + an --a11y/static no-animation mode
- [[m010-colour-not-alone]] — Colour-never-alone: pair every coloured signal with a glyph/text
- [[m010-timer-options]] — Surface the timer + add an untimed option
### `m010/onboarding`
- [[m010-onboarding-tutorial]] — Interactive onboarding tutorial
- [[m010-polish-readme-10]] — 1.0 polish pass + docs

## Definition of done
All issues shipped through the gate (ruff + mypy + pytest + playtest), one ADR per cluster, a
per-milestone status update (ON_TRACK → COMPLETE), README current-state + roadmap + wiki refreshed,
tagged **v1.0.0**.
