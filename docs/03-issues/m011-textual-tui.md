---
title: Optional local Textual TUI (foundation)
type: issue
milestone: M011
area: ui
priority: P2
cluster: m011/tui
labels:
  - enhancement
status: Todo
state: open
github:
  issue: 78
---

# Optional local Textual TUI (foundation)

An optional Textual-based TUI driving the adapter: scoreboard pane + commentary pane + pick input. Local only, **no network/telemetry**; `textual` as an optional extra so the core CLI has no new hard dep.

**Acceptance:** launches and plays a match locally; gated behind an optional dependency; CI core gate unaffected.
