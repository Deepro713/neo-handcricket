---
title: Batsman match-state / momentum model (pure logic)
type: issue
milestone: M005
area: bots
priority: P1
cluster: m005/matchstate
labels:
  - enhancement
status: Done
state: closed
github:
  issue: 27
---

# Batsman match-state / momentum model (pure logic)

A new batter is tentative and accelerates as they settle (balls faced); the required run-rate / wickets in hand shift intent (a chase plays differently from building an innings). Model a `settledness` (0..1, grows with balls faced) and a `intent` derived from match situation; both reshape the batsman base distribution (early: more 0-2, fewer 6; settled/under-rate-pressure: more 4/6).

**Scope:** `neo_handcricket/bots/matchstate.py` (pure), config tunables, wired into `strategy.pick_number` for the bot-batting path. Needs balls-faced + match-situation inputs threaded from `innings`/`match`.

**Tests:** settledness monotonic in balls faced; chase intent raises aggression as RRR climbs; distributions stay valid; reproducible under seed.
