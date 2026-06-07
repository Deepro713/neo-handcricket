---
title: Banked currency, variety unlocks & progression persistence
type: issue
milestone: M008
area: persistence
priority: P1
cluster: m008/progression
labels:
  - enhancement
status: Done
state: closed
github:
  issue: 45
---

# Banked currency, variety unlocks & progression persistence

Results bank a currency (reputation/coins); spend it to unlock **variety** (new opponents into the pool, commentator panels, challenge modifiers) rather than raw power. Persist career progression; bump `SAVE_SCHEMA_VERSION` with a migration from v1 saves.

**Scope:** extend `persistence/` with a progression store; an unlock registry.

**Tests:** currency accrues on results; unlocks gate correctly; old saves migrate without loss; round-trips.
