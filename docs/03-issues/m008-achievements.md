---
title: Achievements & shareable save codes
type: issue
milestone: M008
area: persistence
priority: P2
cluster: m008/achievements
labels:
  - enhancement
status: Done
state: closed
github:
  issue: 42
---

# Achievements & shareable save codes

An offline achievement/challenge system (e.g. 'win a Test by an innings', 'chase 200+', 'hat-trick') evaluated from the event stream + career stats, plus **shareable save codes** (a compact, offline, copy-pasteable encoding of a result/seed — no network).

**Tests:** achievements fire on their exact criteria; save-code round-trips (encode→decode→identical); codes are self-contained (no external lookup).
