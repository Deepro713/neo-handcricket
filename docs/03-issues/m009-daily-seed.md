---
title: Date-seeded daily challenge core (pure)
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
  issue: 70
---

# Date-seeded daily challenge core (pure)

A pure module `neo_handcricket/daily/seed.py`: derive a deterministic seed + fixed match config (format, both teams, toss, difficulty) from a calendar date, so every player gets the *same* daily match. Pure, no I/O (date passed in).

**Tests:** same date → identical config; different dates → different; config is always valid/playable.
