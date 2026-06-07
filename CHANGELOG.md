# Changelog

All notable changes to this project will be documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- **History reconstruction** (2026-06-07): retroactive milestones **M001–M003**, closed issues, vault
  notes, backdated tags `v0.1.0`/`v0.2.0`/`v0.3.0` + releases, and a v0.x version scheme reconciliation.
  See `docs/00-overview/decision-log.md` (ADR-0002).
- **Round 1 plan** (M004–M008) + research synthesis (ADR-0003).

## [1.2.0]–[1.2.1] — 2026-06-07 — M012 roguelite draft: relics & run modifiers

### Added
- **Relic registry** (`career/relics.py`): run-scoped rule-benders over a neutral effective-config
  (boundary value, fatigue, powerplay overs, tail aggression, currency), composing order-independently,
  plus a deterministic seeded **draft**. (v1.2.0)
- **Relics in the career** (`career/run.py`): a between-rounds draft wired into the tournament (decline
  allowed); the chosen relics' effective config feeds match resolution. Thin draft/owned UI. (v1.2.1)

## [1.1.0]–[1.1.1] — 2026-06-07 — M011 headless adapter & Textual TUI foundation

### Added
- **Headless game adapter** (`adapter.py`): a UI-agnostic façade — start a match from a config, submit a
  0–6 pick, observe structured state + events; deterministic, no I/O. `bot_bowl_pick` is now the single
  source of truth the CLI also routes through. (v1.1.0)
- **Optional local Textual TUI** (`tui/`, `neo-handcricket-tui`): a richer terminal front-end driving the
  adapter. `textual` is an optional `[tui]` extra — offline, no network; the core CLI/gate never depend
  on it. (v1.1.1)

## [1.0.0]–[1.0.1] — 2026-06-07 — M010 accessibility, onboarding & the 1.0 release 🎉

The **1.0** release: a complete, accessible, welcoming game.

### Added
- **Accessibility** (`a11y.py`): honour `NO_COLOR`; an a11y/static **no-animation** mode (`NHC_A11Y` /
  `config.A11Y_MODE`); an **untimed** option (`NHC_UNTIMED` / a setup prompt); a **colour-never-alone**
  signal map (every signal carries a glyph + word). (v1.0.0)
- **Interactive onboarding tutorial** (`onboarding.py`, "How to play" menu) + a README Accessibility
  section and first-run pointer; recorded-playtest polish review. (v1.0.1)

## [0.9.0]–[0.9.2] — 2026-06-07 — M009 daily-seed & procedural challenges

### Added
- **Daily challenge core** (`daily/seed.py`, `daily/modifiers.py`): a date-seeded, deterministic daily
  match (format, teams, difficulty) + a pool of composable modifiers — identical for everyone on a
  given day. (v0.9.0)
- **Daily scoring + local best-table** (`daily/score.py`, `persistence/daily.py`): a monotonic score and
  a best-per-date table that round-trips through the offline share codes. (v0.9.1)
- **Playable Daily challenge** main-menu entry (seeded match → score → share code) + a reproducibility
  playtest invariant (gate now 60 checks). (v0.9.2)

## [0.8.0]–[0.8.3] — 2026-06-07 — M008 career & roguelite meta-progression

### Added
- **Offline tournament core** (`career/tournament.py`): reputation-seeded single-elimination bracket
  with byes and an injected fixture resolver. (v0.8.0)
- **Progression** (`career/progression.py`): banked currency from results spent on **variety unlocks**
  (opponents/panels/modifiers, not power); persisted to `stats/progression.json`. Bumped
  `SAVE_SCHEMA_VERSION` 1→2 with migration so v1 saves load cleanly. (v0.8.1)
- **Achievements** (`career/achievements.py`) evaluated from the event stream + result, and
  **shareable save codes** (`career/sharecode.py`, offline Base32, corruption-safe). (v0.8.2)
- **Campaign & progression dashboard** (main-menu entry) and a headless full-tournament playtest
  invariant (gate now 57 checks). (v0.8.3)

## [0.7.0]–[0.7.2] — 2026-06-07 — M007 commentary & presentation depth

### Added
- **Big-moment event detector** (`commentary/events.py`): a pure, deterministic detector emitting typed
  events — wickets (+kind), boundaries, fifties/hundreds, hat-tricks, collapses, maidens, 50-run
  partnerships, last-ball finishes. (v0.7.0)
- **Escalating big-moment commentary** (`commentary/lines.py`): original CC0 line banks per event with a
  priority `event_situation` mapping; the engine now adds an accent beat on a big moment and avoids
  within-match line repeats. (v0.7.1)
- **Context-aware asides** (`commentary/context.py`) referencing live fatigue / settledness / AI-reads,
  a `★`/`💯` scoreboard marker for fifties/hundreds, and a **match highlights reel**
  (`commentary/highlights.py`) built from the event stream. (v0.7.2)

## [0.6.0]–[0.6.3] — 2026-06-07 — M006 strategic AI & opponent modelling

### Added
- **Opponent model** (`bots/opponent.py`): predicts your next number by blending recent **frequency**,
  **Win-Stay-Lose-Shift**, and a **bigram/sequence** predictor, then `exploit_mix`es toward the
  matching-pennies equilibrium so the bot exploits patterns without becoming predictable. (v0.6.0)
- **Difficulty tiers** wire it live with per-tier epsilon and a new **Legend** tier; the engine tracks
  per-pick reward signs to power WSLS. (v0.6.1)
- **Offline AI eval harness** (`bots/evaluation.py`) proving the model beats the frequency baseline
  against predictable players (and shows no edge vs a random one); 2 new playtest invariants. (v0.6.2)
- **Optional player-facing "tells"** (`bots/tells.py`, off by default): a coarse, sometimes-bluffing
  zone read on the bowler that never leaks the exact pick. (v0.6.3)

## [0.5.0]–[0.5.3] — 2026-06-07 — M005 cricket realism layer

### Added
- **Bowler fatigue** (`bots/fatigue.py`): a bowler's effectiveness fades over a long spell and recovers
  with rest (pacers tire faster); flattens the bowling distribution and lowers its adaptation. (v0.5.0)
- **Batsman match-state / momentum** (`bots/matchstate.py`): settledness grows with balls faced and a
  chase raises intent, reshaping the batter toward (or away from) boundaries. (v0.5.1)
- **Match-up-aware bowling rotation** (`bots/captain.py`): the captain biases bowler choice by
  bowler-vs-batter archetype advantage and freshness, preserving cap / no-consecutive-over rules. (v0.5.2)
- **Live realism indicators**: a bowler stamina gauge in the over overlay and a settled marker per
  batter on the scoreboard; 9 new playtest invariants (gate now 49 checks). (v0.5.3)

## [0.4.1] — 2026-06-07 — M004 gate-enforcement

### Changed
- **mypy is now enforced** in the QA gate (`ship-cluster.sh`, CI, Makefile) — no longer advisory.
- Fixed `ship-cluster.sh` version map to handle zero-padded `m00N` branch slugs. (ADR-0005)

## [0.4.0] — 2026-06-07 — M004 type-debt foundation

### Fixed
- Cleared all ~44 mypy errors across scoreboard/selector/main/strategy/captain/innings;
  `mypy neo_handcricket` is now **0 errors / 31 files**. No behavioural change. (ADR-0004)

## [0.3.0] — 2026-06-07 — repo polish, docs & autonomous-dev bootstrap

### Added
- **Autonomous-dev scaffolding**: `docs/00-overview/` (conventions-and-rules, dev-runbook,
  decision-log), an Obsidian vault (`docs/` + `.obsidian/`) for milestones/issues/research, a GitHub
  Project board, `scripts/ship-cluster.sh` + `scripts/sync.py`, a headless game-sim QA gate
  (`tools/playtest`), ruff/mypy/pytest config + a `[dev]` extra, a `Makefile` gate, CI + wiki-publish
  workflows, and `wiki/` seed pages.

### Changed
- Removed one-shot data-prep script `tools/generate_remaining_rosters.py`
  (581 lines). The 200 country JSONs are committed; the generator served its
  purpose and is no longer needed at runtime.
- Added `tools/json_to_vault_md.py` — reverse converter that materialises
  vault Markdown files from repo JSON. Lets the vault stay structurally
  uniform with the repo (one MD per country).
- `.gitignore` now excludes `.claude/` (editor-local settings).

### Added
- `LICENSE` (MIT).
- `CHANGELOG.md` (this file).

## [0.2.0] — 2026-05-08 — v1.1 push

### Added
- **All 200 country rosters**: every UN member state + observers + Antarctica.
  18 hand-curated; 182 bulk-generated programmatically using ~30 regional /
  linguistic name pools.
- **Conversational multi-line commentary**: each ball produces 2–3 lines as a
  flowing conversation across a per-match panel of 2 or 3 commentators
  (randomly picked at start with country / gender diversity).
- **10-second inter-ball pacing**: lines stream at 3-second intervals;
  ≥10s minimum gap before next ball; skippable on any keypress.
- **Full Test cricket engine**: 5-day cap (2700 balls), 4 innings, follow-on
  at lead ≥ 200 (user prompt or bot heuristic ≥ 250), declarations at
  end-of-over (user `d` key or bot heuristic at lead ≥ 280), innings-victory
  detection, draw resolution.
- **Career stats dashboard**: aggregate W/L/D by format, top run-scorers and
  wicket-takers, head-to-head per opponent, highest team total / individual
  score, longest winning streak, PoTM count.

### Tests
- 12 smoke tests, all green.

## [0.1.0] — 2026-05-08 — initial CLI v1

### Added
- T10 / T20 / ODI / Custom formats fully playable. Test scaffolded.
- 14 hand-curated country rosters (13 cricket nations + Antarctica).
- 3-second hidden timer per ball with audible BEL beep. Timeout outcomes:
  bot bowling — dot/wide/bowled/LBW/dead-ball at 20% each; user bowling —
  wide/no-ball/byes/leg-byes/dead-ball.
- Adaptive bot AI with per-player profiles. Tunable difficulty: easy / medium
  / hard with α = 0 / 0.3 / 0.6 adaptation strength.
- 20-commentator framework across 5 cricket nations (initial single-line
  output; multi-line came in 0.2.0).
- Toss subsystem with 100 ridiculous retoss excuses; retoss cap = 3.
- Captain-AI bowler rotation (early=pace, middle=spin, death=best
  econ-with-overs-left). User picks own bowlers each over with format caps
  enforced.
- Save / pause / quit at any over boundary. Rolling auto-save per over;
  named manual saves. Career stats JSON.
- Player of the Match award.
- 9 end-to-end smoke tests, all green.
