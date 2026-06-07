---
title: Context-aware lines referencing fatigue / momentum / reads
type: issue
milestone: M007
area: commentary
priority: P2
cluster: m007/context-and-polish
labels:
  - enhancement
status: Todo
state: open
github:
  issue: 39
---

# Context-aware lines referencing fatigue / momentum / reads

Lines that reference the M005/M006 state: 'the bowler's legs have gone' (fatigue), 'he's set now and milking it' (settled), 'the bowler read that perfectly' (AI exploit hit). Selection conditioned on engine state.

**Tests:** context lines only fire when the state holds; fall back gracefully; reproducible.
