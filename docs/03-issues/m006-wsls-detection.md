---
title: Win-Stay-Lose-Shift detection + counter
type: issue
milestone: M006
area: bots
priority: P1
cluster: m006/opponent-model
labels:
  - enhancement
status: Todo
state: open
github:
  issue: 37
---

# Win-Stay-Lose-Shift detection + counter

Humans frequently play WSLS (repeat a number that 'worked', change after a bad ball). Detect the user's WSLS tendency online and fold it into the bowling-match prediction.

**Scope:** extend the opponent model in `bots/strategy.py` (or a new `bots/opponent.py`) to track stay/shift transitions conditioned on previous outcome; blend into the adapted distribution. Pure, seeded.

**Tests:** against a scripted pure-WSLS player the model's match-rate beats frequency-only baseline by a margin; degrades gracefully vs a random player.
