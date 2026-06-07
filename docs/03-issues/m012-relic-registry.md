---
title: Relic / run-modifier registry (pure)
type: issue
milestone: M012
area: bots
priority: P1
cluster: m012/relics-core
labels:
  - enhancement
status: Done
state: closed
github:
  issue: 80
---

# Relic / run-modifier registry (pure)

A pure registry of run-scoped relics/modifiers, each a small, composable transform over existing config/tunables (e.g. boundary value, fatigue rate, powerplay length, tail aggression). Apply a set to produce an effective config.

**Tests:** each relic's effect is correct and bounded; relics compose order-independently where claimed; invariants hold.
