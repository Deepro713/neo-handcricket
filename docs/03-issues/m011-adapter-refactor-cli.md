---
title: Route the CLI through the adapter (no behaviour change)
type: issue
milestone: M011
area: ui
priority: P2
cluster: m011/adapter
labels:
  - enhancement
status: Todo
state: open
github:
  issue: 76
---

# Route the CLI through the adapter (no behaviour change)

Refactor the CLI ball-loop to consume the headless adapter where practical, proving the API is sufficient and keeping a single source of truth. No gameplay change.

**Acceptance:** playtest + smoke green; recorded transcript unchanged in substance.
