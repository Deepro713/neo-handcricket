# neo-handcricket

A single-player CLI hand cricket game with proper match-format scaffolding.

Each ball, you and the computer simultaneously reveal a number 0–6. Match → wicket; mismatch → batsman scores their value. Pick a format (T10 / T20 / ODI / Test / Custom), pick your country, pick your opponent — play a match.

## Highlights

- **Formats:** T10, T20, ODI (50 overs), Test (scaffolded), Custom (your overs / wickets / innings).
- **0–6 throw range** with a hidden 3-second timer per ball; if you miss the timer the bot's bowler rolls one of five outcomes (dot, wide, bowled, LBW, dead-ball at 20% each).
- **14 country rosters** built in: India, England, Australia, Pakistan, South Africa, New Zealand, Sri Lanka, Bangladesh, Zimbabwe, Afghanistan, Ireland, West Indies, Japan, **Antarctica** (yes, the penguins).
- **Adaptive bot** with per-player profiles. Tunable difficulty (easy / medium / hard).
- **20-commentator system** (5 cricket nations × 2M + 2F) with trait-based personalities and match-log callbacks.
- **Toss** is a flavoured 0–6 RNG; rolling 0 triggers a randomly-drawn ridiculous excuse and a retoss (cap: 3 consecutive 0s, then fair flip).
- **Save / pause / quit** at any moment. Rolling auto-save per over; named manual saves.

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

## Controls

- **Number entry:** single keystroke, `0`–`6`. No Enter required.
- **3-second timer:** starts when the bowler is announced. A `BEL` audible beep + visual countdown.
- **Pause menu:** press `p` at any prompt to save / pause / quit.
- **Continue at end-of-over:** press any key.

## Project layout

```
neo_handcricket/
  main.py            # CLI entry
  match.py           # match orchestration
  innings.py         # innings + over + ball loop
  toss.py
  formats.py
  excuses.py
  bots/
    profiles.py
    strategy.py
    captain.py
  rosters/
    loader.py
    validator.py
    selector.py
    data/            # 14 country JSON rosters
  ui/
    cli.py
    input.py
    scoreboard.py
    overlay.py
    prompts.py
  commentary/
    commentators.py  # 20 personalities
    engine.py
    log.py
    lines.py
  persistence/
    save.py
    stats.py
saves/   # rolling auto-save + manual saves
stats/   # career stats JSON
```

## Status

v1 — works for T10 / T20 / ODI / Custom. Test cricket is scaffolded but the full 5-day / 4-innings logic ships in v1.1.
