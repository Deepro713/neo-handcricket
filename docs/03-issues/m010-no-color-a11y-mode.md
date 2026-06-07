---
title: Honour NO_COLOR + an --a11y/static no-animation mode
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
  issue: 86
---

# Honour NO_COLOR + an --a11y/static no-animation mode

Respect the `NO_COLOR` env var and add an accessibility mode (config flag + `NHC_A11Y` env): disable the redraw/animation timer bar in favour of static, line-appended output, and drop heavy boxes/ASCII where it aids screen readers.

**Tests:** color disabled under NO_COLOR; a11y mode flips a single source-of-truth flag read by the UI; pure helpers unit-tested.
