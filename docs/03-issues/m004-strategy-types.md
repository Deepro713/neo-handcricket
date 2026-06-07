---
title: Fix mypy errors in bots/strategy.py (9)
type: issue
milestone: M004
area: types
priority: P1
cluster: m004/types-fixes
labels:
  - enhancement
  - area:bots
status: Todo
state: open
github:
  issue: 26
---

# Fix mypy errors in bots/strategy.py (9)

Clear the 9 mypy errors in `neo_handcricket/bots/strategy.py`. Type the distribution lists (`list[float]`) and the pick path precisely. Also remove the dead `sum(counts.values())` no-op in `_adapted_for_batting`.

**Acceptance:** file mypy-clean; gate green; RNG-seeded outputs unchanged.
