---
title: Decision Log (ADRs)
type: reference
---

# neo-handcricket — Decision Log

Architecture Decision Records, newest first. One per cluster/significant decision.

## ADR-0003 — Round 1 direction: realism → AI → presentation → progression
**Date:** 2026-06-07 · **Status:** accepted

**Context.** Research ([[2026-06-07-comparable-games]]) framed hand cricket as a repeated
simultaneous-move (matching-pennies) game whose depth comes from **opponent modelling** plus
**cricket-context modifiers** (bowler fatigue, batsman settled-ness/momentum, match-up awareness), and
showed that **roguelite meta-progression** is the standard wrapper that makes single-player sessions
feel productive. These line up almost exactly with the existing README roadmap.

**Decision.** Round 1 = milestones **M004–M008**, in this order:
1. **M004 — Type-debt foundation:** clear the ~44 mypy errors and **add mypy to the QA gate** so every
   subsequent milestone is type-checked. Foundation first, by design.
2. **M005 — Cricket realism layer:** bowler fatigue, batsman match-state/momentum, match-up-aware
   bowling rotation — pure-logic, seeded, unit-tested; playtest invariants extended.
3. **M006 — Strategic AI & opponent modelling:** WSLS/sequence detection, exploit-vs-mix balancing,
   deeper difficulty, optional "tells" surfaced to the player.
4. **M007 — Commentary & presentation depth:** big-moment slots (wickets, boundaries, milestones,
   finishes) + context-aware lines that reference M005/M006 state.
5. **M008 — Career & roguelite meta-progression:** offline tournament campaign with banked currency,
   variety unlocks, achievements, shareable save codes (no network/accounts).

Each is one minor bump (v0.4.0 → v0.8.0); M010 remains the v1.0.0 target.

**Consequences.** A coherent arc (pay debt → deepen sim → deepen AI → deepen presentation → wrap in
progression). mypy enforcement from M005 onward raises the floor permanently. Guardrails preserved:
single-player/offline, CC0/original content.

## ADR-0002 — Reconstruct pre-cycle history & fix the v0.x version scheme
**Date:** 2026-06-07 · **Status:** accepted

**Context.** Before the autonomous-dev cycle (ADR-0001 / PR #1), neo-handcricket was already a
feature-complete CLI game built across five commits (`3b1bb01` … `517e3f0`, all 2026-05-08) with no
milestones, issues, tags or releases — only the bootstrap PR #1 (`5d6af9c`, 2026-06-07) was tracked.
The commit messages used an informal "v1 / v1.1" marketing label, but `CHANGELOG.md` had already
rationalised these to semver `0.1.0` (initial build) and `0.2.0` (the content drop).

**Decision.**
1. **Group the history into three retroactive milestones** and represent each properly:
   - **M001 — Core engine** (`3b1bb01`) → **v0.1.0**
   - **M002 — Rosters, conversational commentary & Test cricket** (`f2a3b5a`) → **v0.2.0**
   - **M003 — Repo polish, docs & autonomous-dev bootstrap** (`125bfd7`, `186d958`, `517e3f0`,
     `5d6af9c`/PR #1) → **v0.3.0**
2. For each: a closed GitHub milestone (with `due_on` set to the real commit date), a vault milestone
   note + per-feature vault issue notes (`status: Done`, `state: closed`), closed GitHub issues whose
   bodies cite the delivering commit SHAs (and PR #1), all added to the Project board as **Done**.
3. **Backdate where the platform allows:** annotated git tags `v0.1.0`/`v0.2.0`/`v0.3.0` created at the
   historical commits via `GIT_AUTHOR_DATE`/`GIT_COMMITTER_DATE`, pushed, with matching GitHub releases.
   GitHub does **not** permit changing issue/PR/release `created_at`, so the true dates are recorded in
   the note/issue/release **bodies** instead.
4. **Version scheme.** Adopt the **v0.x baseline already encoded** in `CHANGELOG.md` and in the
   `ship-cluster.sh` map (`M00N → v0.N`, `M010 → v1.0`). This is monotonic and forward-sensible: the
   pre-cycle state is v0.3.0, so the first forward milestone **M004 ships v0.4.0**, reaching **v1.0.0
   at M010**. `pyproject.version` is set to **0.3.0** to match the current tree. The informal "v1.1"
   label is retired in favour of this scheme.

**Consequences.** History now reads coherently (milestones ↔ issues ↔ commits/PR #1 ↔ board ↔ tags ↔
releases). Forward releases continue cleanly from v0.3.0. The mypy type-debt (~44 errors) remains; the
first forward milestone (M004) is dedicated to clearing it so the gate can enforce mypy afterward
(see Round 1 planning).

## ADR-0001 — Adopt the looped autonomous-dev process
**Date:** 2026-06-07 · **Status:** accepted
Adopt the Streetbound-style process for neo-handcricket: the vault (`docs/`) as source of truth,
milestones (zero-padded, one minor bump each) shipped as small per-cluster PRs through a four-part QA
gate (ruff + mypy + pytest + a headless game-sim playtest), an ADR per cluster, a GitHub Project board
with per-milestone status updates, an auto-published wiki, and a perpetual research→plan→build loop
driven by `/loop` in a dedicated terminal. Guardrails: single-player/offline, CC0/original content,
no infra-credential changes. See `conventions-and-rules.md` + `dev-runbook.md`.
