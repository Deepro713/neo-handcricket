---
title: Headless game adapter (UI-agnostic API)
type: issue
milestone: M011
area: engine
priority: P1
cluster: m011/adapter
labels:
  - enhancement
status: Done
state: closed
github:
  issue: 77
---

# Headless game adapter (UI-agnostic API)

A thin, UI-agnostic façade over the pure engine: start a match from a config, submit a pick, observe structured state/events — no printing, no input. Any front-end (CLI, TUI, future web) drives the same API. Offline.

**Tests:** drive a whole match through the adapter headlessly; state transitions + terminal result are correct and deterministic under seed.
