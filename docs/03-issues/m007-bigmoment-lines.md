---
title: Big-moment commentary line banks
type: issue
milestone: M007
area: commentary
priority: P1
cluster: m007/bigmoment-lines
labels:
  - enhancement
status: Done
state: closed
github:
  issue: 38
---

# Big-moment commentary line banks

Author CC0/original line banks for each event category from [[m007-event-detection]] (`wicket_bowled`, `wicket_lbw`, `ball_run_4`, `ball_run_6`, `milestone_fifty`, `milestone_hundred`, `hat_trick`, `last_ball_finish`, …), wired into the conversational panel so a big moment escalates the exchange.

**Scope:** extend `commentary/lines.py` + `engine.py` selection.

**Tests:** every event category has lines; no within-match duplicate line; all original (no copyrighted text).
