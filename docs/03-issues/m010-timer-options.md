---
title: Surface the timer + add an untimed option
type: issue
milestone: M010
area: ui
priority: P1
cluster: m010/a11y-core
labels:
  - enhancement
  - area:accessibility
status: Done
state: closed
github:
  issue: 87
---

# Surface the timer + add an untimed option

Expose the per-ball timer length in setup and add an **untimed** mode (the 3s hidden timer is hostile to slower / assistive-tech users). Pure config + a thin setup prompt.

**Tests:** untimed disables the timeout path; configured length is respected.
