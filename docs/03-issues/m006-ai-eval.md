---
title: Offline AI eval harness + playtest hook
type: issue
milestone: M006
area: tooling
priority: P1
cluster: m006/eval
labels:
  - enhancement
status: Todo
state: open
github:
  issue: 32
---

# Offline AI eval harness + playtest hook

An offline harness that plays the smarter bot against a battery of **scripted player patterns** (uniform, favourite-number, WSLS, sequence) over many seeded balls and asserts the new model beats the frequency-only baseline on match-rate / runs-conceded. Hook a smoke version into the playtest.

**Acceptance:** harness runs fast and deterministically; baseline-beating margins asserted; CI-friendly.
