---
title: Richer difficulty tiers wiring the new models
type: issue
milestone: M006
area: bots
priority: P2
cluster: m006/difficulty
labels:
  - enhancement
status: Todo
state: open
github:
  issue: 33
---

# Richer difficulty tiers wiring the new models

Wire WSLS + n-gram + exploit-mix behind difficulty. Add a top tier (e.g. `legend`) that uses the full model with low ε; keep `easy/medium/hard` mapped to increasing exploitation. Update `DIFFICULTY_ALPHA` and add a per-difficulty model-weight/ε config.

**Tests:** higher tiers strictly more exploitative in self-play vs scripted patterns; `easy` stays near-random.
