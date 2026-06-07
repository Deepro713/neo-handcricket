---
title: Surface fatigue & settled-state in the UI (thin)
type: issue
milestone: M005
area: ui
priority: P2
cluster: m005/ui-and-playtest
labels:
  - enhancement
status: Done
state: closed
github:
  issue: 31
---

# Surface fatigue & settled-state in the UI (thin)

Thin presentation only: show a bowler **stamina** hint in the over overlay and a batter **settled** indicator on the scoreboard (e.g. a small bar / ★ once set). No logic in the UI layer — read state from the engine.

**Acceptance:** renders cleanly in recorded playtest transcript; no new mypy/ruff issues; toggle-able via config if it clutters.
