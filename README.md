<div align="center">

# 🏏 neo-handcricket

**Hand cricket — but make it a real fixture.**

A single-player CLI hand cricket game with five formats, 200 country rosters, and a 20-commentator conversational engine.

[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-12%20passing-brightgreen.svg)](tests/test_smoke.py)
[![Status: v0.4.1](https://img.shields.io/badge/status-v0.4.1-informational.svg)](CHANGELOG.md)
[![mypy: clean](https://img.shields.io/badge/mypy-clean-2C9F4A.svg)](pyproject.toml)
[![Code style: PEP 8](https://img.shields.io/badge/code%20style-PEP%208-2C9F4A.svg)](https://peps.python.org/pep-0008/)

</div>

---

## What is this?

Hand cricket is the schoolyard game where two players simultaneously show a number on their fingers, and matching numbers means the batter is **out**. It's been played in classrooms and on the back of school buses for as long as anyone can remember.

This is that game — but with **proper match formats** (T10 / T20 / ODI / Test / Custom), **named country teams** (200 of them), **adaptive bot AI** with archetype-based player profiles, and a **conversational commentary engine** so every ball feels like a real broadcast. It runs in your terminal with a 3-second hidden timer per ball, BEL beeps, Unicode scoreboards, and the kind of personality usually reserved for actual sports games.

Pick a country, pick the opponent, pick a format, play.

```
┌─ T20  🇮🇳 India vs 🐧 Antarctica   Diff: medium ──────────┐
│ India: 38/2  (4.3 / 20 ov)                                 │
└────────────────────────────────────────────────────────────┘
  ► Aryan Bose                23(14)    4s:3   6s:1
    Karan Singh                 8(11)   4s:1   6s:0
  Bowler: Bumble Pugga          0.3 ov   12/0
  This over: 4 1 W .

  ▸ FOUR! Aryan Bose just told the bowler to sit down.   (Rajat Thapliyal)
  ▸ Bumble Pugga gave him room and he didn't miss out.   (Geoffrey Pemberton)
  ▸ That's a six-and-a-half if it's an inch.             (Charlene Dell)

  BAT — pick 0–6  (Aryan Bose)  [█████·······]  2.7s
```

## Highlights

- **🏟️ Five match formats** — T10, T20, ODI (50 ov), full **Test cricket** (5 days, 90 ov/day cap, follow-on, declarations, draws), and Custom (your overs / wickets / innings / playing-size — 1-vs-1 valid).
- **🌍 200 country rosters** — every UN member + observers + **Antarctica** (yes, the penguins). 18 hand-curated, 182 auto-generated from regional / linguistic name pools.
- **⏱️ Hidden 3-second timer** per ball with audible BEL beep. Miss it and one of five outcomes rolls at 20% each.
- **🤖 Adaptive bot AI** with per-player archetype profiles (pace / swing / off-spin / leg-spin / mystery; opener / anchor / power-hitter / finisher / tail-ender). Tunable difficulty.
- **🎙️ Conversational commentary** — every ball, 2–3 lines flow as a conversation across a randomly chosen panel of 2 or 3 commentators. 20 personalities total, each with trait tags and country.
- **🪙 Toss with personality** — hidden 0–6 RNG with parity-based heads/tails, and a 100-line bank of ridiculous excuses for when the coin "rolls into the gutter".
- **💾 Save / pause / quit** at any over boundary. Career stats with aggregate dashboard (W/L/D by format, head-to-head, top scorers, longest streak, PoTM count).

## Install & run

Requires Python 3.10+. Unix-only (macOS / Linux; WSL works on Windows).

```sh
git clone https://github.com/Deepro713/neo-handcricket.git
cd neo-handcricket
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python -m neo_handcricket          # play a match
python -m tests.test_smoke         # run the 12 smoke tests
```

## Controls

| Key | Action |
|---|---|
| `0`–`6` | Pick a number (single keystroke, no Enter) |
| Any key | Skip the inter-ball commentary pause |
| `p` | Pause menu (between overs) — save / resume / quit |
| `d` | Declare innings (Test cricket, while batting) |
| `h` / `t` | Call heads / tails at the toss |

## Project layout

```
neo_handcricket/
  main.py              CLI entry, ball loop, Test orchestrator, super over, PoTM
  config.py            All tunables (timer, retoss cap, gap seconds, Test caps, α)
  formats.py           T10 / T20 / ODI / Test definitions + Custom builder
  excuses.py           100 retoss excuses + sampler
  toss.py              Hidden 0–6 RNG, parity → heads/tails, fair-flip fallback
  innings.py           Live innings state (balls, overs, wickets, batter/bowler cards)
  match.py             Match dataclass + state machine
  bots/
    profiles.py        Archetype distributions over 0–6 + α + extras modifier
    strategy.py        Number selection, extras roll, timeout outcomes
    captain.py         Bot bowler rotation heuristic
  rosters/
    loader.py          JSON → Country/Player dataclasses
    validator.py       Custom-roster validation
    selector.py        Playing-XI picker with format role-mix constraints
    data/              200 country JSON rosters
  ui/
    cli.py             render_frame, update_prompt_line
    input.py           Single-keystroke + 3s timer (cbreak mode)
    scoreboard.py      Compact view + detailed scorecard + match summary
    overlay.py         Bowler-archetype card at start of each over
    prompts.py         Country select, format select, custom wizard, pause menu
  commentary/
    commentators.py    20 personalities across 5 cricket nations
    lines.py           178 templates × {opener, analysis, quip}
    log.py             MatchLog with callback support
    engine.py          Per-match panel of 2–3, conversational generation
  persistence/
    save.py            save_match / load_match / list_saves
    stats.py           record_match / aggregate dashboard

tests/test_smoke.py    12 end-to-end smoke tests
tools/
  convert_rosters.py   vault MD → repo JSON   (use after hand-editing a roster)
  json_to_vault_md.py  repo JSON → vault MD   (materialise missing vault MDs)

saves/                 rolling auto-save + named manual saves (gitignored)
stats/                 career.json (gitignored)
```

## FAQ

**How do I add or improve a country roster?**
Edit `neo_handcricket/rosters/data/<slug>.json` directly. Run the smoke tests after editing to confirm the JSON still parses (`python -m tests.test_smoke`).

**Why is the timer so short?**
3 seconds is intentionally tight — it forces you to commit to a number rather than overthink it, which is closer to the schoolyard feel of real hand cricket. Tune via `TIMER_SECONDS` in `neo_handcricket/config.py` if you want more thinking time.

**Why are there penguins in Antarctica's roster?**
Because Antarctica doesn't have a national cricket team but the brief said "every country in the world." When you play against Antarctica, the commentary engine flips into comic mode and the herrings come out. Don't ask.

**Can I play head-to-head against another human?**
Not in v1. The game is single-player vs. computer. Multiplayer is on the roadmap.

**Does this work on Windows?**
The raw-input path uses Unix `termios` / `tty` / `select`. Native Windows isn't supported in v1 — WSL works fine. A `msvcrt`-based fallback is on the roadmap.

**Why a CLI? Will there be a GUI?**
CLI was the fastest path to a complete game. A GUI / web port is on the roadmap — `stats/career.json` and the save format are structured to support it.

**Are these real cricketer names?**
No. Names are *fictional* — composed from common given/family name elements per culture. No real current or recent international cricketer's full name is used.

**Where do save files live?**
`saves/auto.json` (rolling, replaced each over) and `saves/<name>.json` (manual). Career stats are at `stats/career.json`. Both directories are gitignored.

## Roadmap

Loose order, biggest impact first:

- **GUI / web port** — Reuse the engine; render with React or Tauri.
- **Sound design** — Beyond the BEL beep. Crowd ambient, bat-on-ball, wicket-fall stings.
- **Bowler fatigue model** — Over-used bowler gets a flatter base and lower α.
- **Batsman match-state shift** — Anchor in a chase plays differently than anchor in a steady innings.
- **Match-up-aware bowling rotation** — Captain biases toward bowler/batter archetype matchups.
- **More commentary lines** — Big-moment slots (`wicket_*`, `ball_run_4/6`, `milestone_*`) are the priority.
- **Hand-curated rosters** for less-known nations where the auto-generator's name pools read off-rhythm.
- **Multiplayer** — Local hot-seat first; networked second.
- **Localization** — English-only commentary; parallel `LINES` dicts for other languages.
- **Native Windows** — `msvcrt`-based input fallback so the game runs without WSL.

## Development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"          # rich + pytest + ruff + mypy
make gate                        # ruff + mypy + pytest + tools.playtest  (the QA gate)
neo-handcricket                  # play
```

The **QA gate** that must pass before every change: `ruff check .` · `mypy neo_handcricket` · `pytest` ·
`python -m tools.playtest` (a headless game-sim that plays full matches across every format with seeded
RNG and asserts invariants). All four are **enforced** — the package is mypy-clean as of v0.4.0
(milestone M004).

## Autonomous build

This project is developed by a **looped autonomous-dev cycle** (research → plan milestones → implement
cluster-by-cluster under the gate → repeat), documented in [`docs/00-overview/`](docs/00-overview/):
[conventions-and-rules](docs/00-overview/conventions-and-rules.md) · [dev-runbook](docs/00-overview/dev-runbook.md)
· [decision-log](docs/00-overview/decision-log.md). Plans live in the Obsidian vault under `docs/`
(`02-milestones/`, `03-issues/`, `04-research/`) and are the **source of truth**; the GitHub Project
board + issues are generated from them via [`scripts/sync.py`](scripts/sync.py). Clusters ship through
[`scripts/ship-cluster.sh`](scripts/ship-cluster.sh).

## Contributing

This is a personal hobby project — PRs welcome but I may be slow to respond. See [CONTRIBUTING.md](CONTRIBUTING.md) for the workflow. All participants must follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## License & changelog

[MIT](LICENSE) · [Changelog](CHANGELOG.md) · © 2026 Deepro Mallick.
