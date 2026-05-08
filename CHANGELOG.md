# Changelog

All notable changes to this project will be documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

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
