---
title: Conventions & Rules
type: reference
---

# neo-handcricket — Conventions & Rules

The operating rules for autonomous, looped development of this project. They mirror the process that
built Streetbound, adapted to a **Python CLI** game. Read this + `dev-runbook.md` + `decision-log.md`
before any work.

## Source of truth & docs
- **The vault (`docs/`) is the source of truth** for plans: `02-milestones/` (one note per milestone),
  `03-issues/` (one note per task), `04-research/` (research syntheses). It opens as an **Obsidian
  vault** (`.obsidian/` at the repo root).
- `docs/00-overview/decision-log.md` records an **ADR per cluster/decision** (newest on top).
- The **GitHub issues + Project board** are generated from the vault via the sync tool — never the
  other way round. Keep them in sync (`make sync` / `scripts/sync.py push`).
- The **wiki** (`wiki/`) auto-publishes to the GitHub wiki on merge to `main`; keep it updated as docs
  change.

## Milestones, versions, branches
- Milestones are zero-padded: `M001`, `M002`, … Each milestone is one **minor** version bump
  (M00N → vX.Y); a headline milestone lands on a `.0`. Clusters within a milestone are **patch** bumps.
- Work happens on a **branch per cluster** (`mNN/<cluster>`), never directly on `main`.
- Every change is a small **PR**, squash-merged. End commit/PR messages with the Co-Authored-By line.

## The QA gate (run before every ship)
1. `ruff check .` (lint) 2. `mypy neo_handcricket` (types) 3. `pytest` (unit) 4. `python -m tools.playtest`
(headless game-sim — the QA harness: plays full games across all formats with seeded RNG and asserts
invariants). **All four must pass.** The playtest is the gameplay gate — it must stay green on every
change, like Streetbound's driving playtest.

## How a cluster is shipped
`scripts/ship-cluster.sh start mNN/<cluster>` → implement (pure logic first + unit tests) → gate →
`scripts/ship-cluster.sh ship "<title>" <issue#...>` (commits, PRs, squash-merges, tags the version,
cuts a GitHub release). One ADR per cluster; one Project status update per milestone (ON_TRACK at
start, flipped to COMPLETE at finish — delete + recreate to re-render the chip, chronological).

## Engineering style
- **Pure logic first:** put rules/scoring/AI in pure, deterministic, unit-tested modules; keep I/O
  (rich UI, prompts, files) thin. Seeded RNG only (reproducible) — no bare `random` in game logic.
- Type-hinted, `from __future__ import annotations`, ruff + mypy clean.
- Match the surrounding code's idiom + comment density.

## Guardrails (unless the owner says otherwise)
- **Single-player / offline only.** No network calls, no telemetry, no accounts. (Async/shareable
  artefacts like share codes or saved transcripts are fine.)
- **CC0 / original content only** — commentary, rosters, names generated/owned, no copyrighted text.
- **No destructive or infra-credential changes**; dev/test deps are fine.
- Spend freely for quality; keep the gate green.

## The perpetual loop
Research (survey comparable games) → plan 5 milestones with detailed issues (vault + GitHub) → implement
cluster-by-cluster under the gate with ADRs + status updates → when they ship, research again and plan
the next five → repeat until the owner says stop. See `dev-runbook.md` for the exact turn checklist.
