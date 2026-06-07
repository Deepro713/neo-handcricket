---
title: Daily score function + local best-table
type: issue
milestone: M009
area: persistence
priority: P1
cluster: m009/leaderboard
labels:
  - enhancement
status: Done
state: closed
github:
  issue: 73
---

# Daily score function + local best-table

A pure score for a completed daily attempt (margin, balls to spare, wickets, etc.) and a local best-table persisted under `stats/` (one entry per date, keep best). Results encodable to a `sharecode` for offline comparison.

**Tests:** score monotonic in the right directions; best-table keeps the best per date; round-trips.
