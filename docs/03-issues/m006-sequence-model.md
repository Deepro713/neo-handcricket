---
title: Sequence (n-gram) / anti-repetition modelling
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
  issue: 35
---

# Sequence (n-gram) / anti-repetition modelling

Go beyond pure frequency: model short **n-gram** transitions in the user's pick stream (people avoid immediate repeats, favour runs like 1-2-3). Predict the next pick from the last k picks.

**Scope:** `bots/opponent.py` n-gram predictor (k=1..2) with smoothing; combine with frequency + WSLS via weights. Pure.

**Tests:** beats frequency-only vs scripted sequence patterns; bounded memory; reproducible.
