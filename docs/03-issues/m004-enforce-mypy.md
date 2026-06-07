---
title: Add mypy to the QA gate + flip the 'advisory' note
type: issue
milestone: M004
area: infra
priority: P1
cluster: m004/gate-enforcement
labels:
  - enhancement
  - area:tooling
status: Todo
state: open
github:
  issue: 22
---

# Add mypy to the QA gate + flip the 'advisory' note

Once the package is mypy-clean, make mypy a **hard** gate step:

- `scripts/ship-cluster.sh run_gate`: move `mypy neo_handcricket` out of the advisory `|| true` block.
- `Makefile` `gate` target + `.github/workflows/ci.yml`: include mypy.
- README Development section: change 'mypy is advisory' to 'mypy is enforced'.
- `conventions-and-rules.md` already lists mypy in the gate — verify wording matches.

**Acceptance:** a deliberately-introduced type error fails the gate; all four steps green on a clean tree.
