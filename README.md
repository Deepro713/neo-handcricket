# neo-handcricket

A single-player CLI hand cricket game with proper match-format scaffolding.

Each ball, you and the computer simultaneously reveal a number 0–6: matching numbers = wicket, otherwise the batter scores their value. Pick a country, pick the opponent, pick a format, play.

## Highlights

- **5 formats:** T10, T20, ODI (50 overs), Test (5 days, 90 ov/day cap, follow-on, declarations, draw possible), Custom (your overs / wickets / innings / playing-size — 1-vs-1 valid).
- **200 country rosters** — every UN member + observers + Antarctica (the penguins). 18 hand-curated, 182 auto-generated from regional / linguistic name pools.
- **Hidden 3-second timer** per ball with audible BEL beep. Miss the timer and one of five outcomes rolls at 20% each.
- **Adaptive bot AI** with per-player archetype profiles. Tunable difficulty (easy / medium / hard).
- **Conversational commentary** — every ball produces 2–3 lines as a flowing conversation across a per-match panel of 2 or 3 commentators (20 personalities total across 5 cricket nations × 2M+2F).
- **10-second inter-ball pacing** so you can absorb each ball; skippable on any keypress.
- **Toss with personality** — hidden 0–6 RNG, parity → heads/tails, rolling 0 triggers a randomly drawn ridiculous excuse and a retoss (cap: 3 consecutive 0s).
- **Save / pause / quit** at any over boundary. Rolling auto-save + named manual saves. Career stats with aggregate dashboard (W/L/D by format, head-to-head, top scorers, longest winning streak, PoTM count).

## Install

Requires Python 3.10+.

```sh
git clone <this-repo>
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

## Tools

The `tools/` scripts maintain the vault ↔ repo roster sync. Hand-curated vault MDs are at `~/personal/10-Projects/neo-handcricket/rosters/`. To refine a country's roster:

1. Edit the vault MD directly.
2. Run `python tools/convert_rosters.py` to overwrite the corresponding JSON.
3. Run `python -m tests.test_smoke` to confirm the JSON still parses.

## License

MIT — see [LICENSE](LICENSE).

## Changelog

See [CHANGELOG.md](CHANGELOG.md).
