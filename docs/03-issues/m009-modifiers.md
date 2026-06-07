---
title: Daily challenge modifiers (pure)
type: issue
milestone: M009
area: engine
priority: P1
cluster: m009/daily-core
labels:
  - enhancement
status: Todo
state: open
github:
  issue: 72
---

# Daily challenge modifiers (pure)

A small pool of daily modifiers (e.g. 'small boundaries', 'tired bowlers', 'powerplay everywhere') selected deterministically from the daily seed, each adjusting existing config/tunables. Pure.

**Tests:** seed → deterministic modifier set; modifiers compose without breaking invariants.
