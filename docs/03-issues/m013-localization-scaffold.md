---
title: Localization scaffold (parallel string tables)
type: issue
milestone: M013
area: commentary
priority: P1
cluster: m013/localization
labels:
  - enhancement
status: Todo
state: open
github:
  issue: 83
---

# Localization scaffold (parallel string tables)

Introduce a locale-keyed structure for user-facing strings / commentary `LINES` (default 'en') with a lookup that falls back to English, so translations can be added without code changes. No translation yet — structure only.

**Tests:** lookup returns en by default; a stub locale overrides + falls back; existing commentary unaffected.
