---
title: Fix mypy errors in ui/scoreboard.py (12)
type: issue
milestone: M004
area: types
priority: P1
cluster: m004/types-fixes
labels:
  - enhancement
status: Done
state: closed
github:
  issue: 24
---

# Fix mypy errors in ui/scoreboard.py (12)

Clear the 12 `union-attr`/`assignment` mypy errors in `neo_handcricket/ui/scoreboard.py` (the single biggest cluster). Most are `Optional[...]` values dereferenced without a guard.

**Acceptance:** `mypy neo_handcricket/ui/scoreboard.py` clean; no behavioural change; ruff + pytest + playtest still green. Prefer real guards / narrowing over `# type: ignore`.
