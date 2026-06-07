---
title: Pure-logic big-moment event detector
type: issue
milestone: M007
area: commentary
priority: P1
cluster: m007/event-detection
labels:
  - enhancement
status: Todo
state: open
github:
  issue: 40
---

# Pure-logic big-moment event detector

A deterministic detector that turns ball/innings state into **events** for commentary: wicket (+type), boundary (4/6), fifty/hundred/milestone, hat-trick, maiden, partnership-50, last-ball finish, collapse. Pure module feeding the commentary engine and scoreboard.

**Scope:** `neo_handcricket/commentary/events.py` consuming innings state; emits typed events.

**Tests:** each event fires exactly on its trigger and not otherwise; hat-trick across overs; milestone boundaries exact; reproducible.
