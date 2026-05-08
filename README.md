# neo-handcricket

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-12%20passing-brightgreen.svg)](tests/test_smoke.py)
[![Status: v0.2.0](https://img.shields.io/badge/status-v0.2.0-informational.svg)](CHANGELOG.md)

A single-player CLI hand cricket game with proper match-format scaffolding.

Each ball, you and the computer simultaneously reveal a number 0–6: matching numbers = wicket, otherwise the batter scores their value. Pick a country, pick the opponent, pick a format, play.

> 200 country rosters · 5 match formats · 20-commentator conversational engine · the full Test cricket experience · and yes, the penguins.

## Highlights

- **5 formats:** T10, T20, ODI (50 overs), Test (5 days, 90 ov/day cap, follow-on, declarations, draw possible), Custom (your overs / wickets / innings / playing-size — 1-vs-1 valid).
- **200 country rosters** — every UN member + observers + Antarctica (the penguins). 18 hand-curated, 182 auto-generated from regional / linguistic name pools.
- **Hidden 3-second timer** per ball with audible BEL beep. Miss the timer and one of five outcomes rolls at 20% each.
- **Adaptive bot AI** with per-player archetype profiles. Tunable difficulty (easy / medium / hard).
- **Conversational commentary** — every ball produces 2–3 lines as a flowing conversation across a per-match panel of 2 or 3 commentators (20 personalities total across 5 cricket nations × 2M+2F).
- **10-second inter-ball pacing** so you can absorb each ball; skippable on any keypress.
- **Toss with personality** — hidden 0–6 RNG, parity → heads/tails, rolling 0 triggers a randomly drawn ridiculous excuse and a retoss (cap: 3 consecutive 0s).
- **Save / pause / quit** at any over boundary. Rolling auto-save + named manual saves. Career stats with aggregate dashboard.

## Screenshots

> _The CLI is best seen in motion — drop your captures into [`docs/`](docs/) and link them here._

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

## Install

Requires Python 3.10+.

```sh
git clone https://github.com/Deepro713/neo-handcricket.git
cd neo-handcricket
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```sh
python -m neo_handcricket
```

Run the smoke tests:

```sh
python -m tests.test_smoke
```

## Controls

- **Number entry:** single keystroke `0`–`6`. No Enter required.
- **3-second timer:** starts when the bowler is announced (BEL beep + visual countdown).
- **Pause menu:** press `p` between overs to save / resume / quit.
- **Test declaration:** press `d` between overs while batting (innings 2 or 3).
- **Skip commentary:** any keypress fast-forwards through the inter-ball pause.

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
Edit `neo_handcricket/rosters/data/<slug>.json` directly, or hand-curate a richer narrative in the maintainer's vault and round-trip via `python tools/convert_rosters.py`. Run the smoke tests after editing to confirm the JSON still parses (`python -m tests.test_smoke`).

**Why is the timer so short?**
3 seconds is intentionally tight — it forces you to commit to a number rather than overthink it, which is closer to the schoolyard feel of real hand cricket. Tune via `TIMER_SECONDS` in `neo_handcricket/config.py` if you want more thinking time.

**Why are there penguins in Antarctica's roster?**
Because Antarctica doesn't have a national cricket team but the brief said "every country in the world." When you play against Antarctica, the commentary engine flips into comic mode and the herrings come out. Don't ask.

**Can I play head-to-head against another human?**
Not in v1. The game is single-player vs. computer. Multiplayer is on the roadmap.

**Does this work on Windows?**
The raw-input path uses Unix `termios` / `tty` / `select`. Windows isn't supported in v1 — WSL works fine. A `msvcrt`-based fallback for native Windows is doable; PRs welcome.

**Why a CLI? Will there be a GUI?**
CLI was the fastest path to a complete game. A GUI / web port is on the roadmap — `stats/career.json` and the save format are structured to support it.

**Is this game legal? You used real-sounding cricket names.**
Names are *fictional* — composed from common given/family name elements per culture. No real current or recent international cricketer's full name is used (deliberately — see `tools/generate_remaining_rosters.py`'s pool design and the hand-curated rosters' naming guidelines).

**Where do save files live?**
`saves/auto.json` (rolling, replaced each over) and `saves/<name>.json` (manual). Career stats are at `stats/career.json`. Both directories are gitignored.

## Roadmap

Loose order, biggest impact first:

- **GUI / web port** — Reuse the engine layer; render with React or Tauri. `career.json` already structured for this.
- **Sound design** — Beyond the BEL beep. Crowd ambient, bat-on-ball, wicket-fall stings.
- **Bowler fatigue model** — Over-used bowler gets a flatter base and lower α. Currently profiles are static across the spell.
- **Batsman match-state shift** — Anchor in a chase plays differently than anchor in a steady innings. Wire match-state through `pick_number` ctx.
- **Match-up-aware bowling rotation** — Captain biases toward bowler/batter archetype matchups (spinner vs power-hitter, LA pace vs RH bat).
- **More commentary lines** — 178 templates across 23 situations is enough to feel alive but not exhaustive. Big-moment slots (`wicket_*`, `ball_run_4/6`, `milestone_*`) are the priority.
- **Hand-curated rosters** for less-known nations where the auto-generator's name pools read off-rhythm.
- **Multiplayer** — Local hot-seat first; networked second.
- **Localization** — English-only commentary; parallel `LINES` dicts for other languages.
- **Native Windows** — `msvcrt`-based input fallback so the game runs without WSL.

## Contributing

This is a personal hobby project. PRs welcome — see [CONTRIBUTING.md](CONTRIBUTING.md). All participants must follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## License

[MIT](LICENSE) — © 2026 Deepro Mallick.

## Changelog

See [CHANGELOG.md](CHANGELOG.md).
