---
title: Extend the playtest with realism invariants + recorded review
type: issue
milestone: M005
area: tooling
priority: P1
cluster: m005/ui-and-playtest
labels:
  - enhancement
status: Todo
state: open
github:
  issue: 30
---

# Extend the playtest with realism invariants + recorded review

Add headless playtest checks asserting the new systems behave: a bowler kept on for a long spell shows rising economy (fatigue), a settling batter's scoring rate rises, and rotation never violates caps. Run `python -m tools.playtest --record out.txt` and review the transcript for anything broken/ugly.

**Acceptance:** new invariants green; transcript reviewed; any defects filed/fixed.
