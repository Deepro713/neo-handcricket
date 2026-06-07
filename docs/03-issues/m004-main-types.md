---
title: Fix mypy errors in main.py (10)
type: issue
milestone: M004
area: types
priority: P1
cluster: m004/types-fixes
labels:
  - enhancement
status: Todo
state: open
github:
  issue: 23
---

# Fix mypy errors in main.py (10)

Clear the 10 mypy errors in `neo_handcricket/main.py`, including the `TeamMeta` vs `str` assignment mismatches around the toss/team-meta path (lines ~880-889). May need a small dataclass/typed-dict tidy.

**Acceptance:** file mypy-clean; gate green; no gameplay change.
