---
title: "Research — comparable games & mechanics (Round 1)"
type: research
date: 2026-06-07
round: 1
---

# Research — hand cricket, cricket sims, turn-based sports & roguelite progression

Survey to seed Round 1 planning (milestones M004–M008). Sources at the bottom.

## 1. What hand cricket *is*, mechanically

Hand cricket is a **repeated simultaneous-move game**: each ball, batter and bowler independently pick
0–6; a **match on a non-zero value = out**, otherwise the batter's number is scored. This is a
**matching-pennies variant** over a 7-value alphabet. Two consequences:

- **There is no optimal pure strategy.** Against a perfect opponent the game-theoretic equilibrium is a
  *mixed* strategy. Any deterministic rule is exploitable in the long run.
- **Real depth comes from opponent modelling.** Humans fall into predictable patterns (favourite
  numbers, Win-Stay-Lose-Shift, anti-repetition). AIs that count opponent frequencies, apply
  **cognitive-hierarchy** reasoning and **Bayesian learning** beat most humans at penny-matching.

Our engine already does the *first rung*: per-archetype distributions over 0–6 plus an adaptation
strength `α` (0 / 0.3 / 0.6 by difficulty) that biases toward the player's most-frequent number. The
research says the obvious next rungs are **WSLS detection, anti-pattern (sequence) modelling, exploit
vs. mix balancing, and exposing the AI's "read" to the player as tells** — depth without leaving the
0–6 core.

## 2. Cricket-sim realism layers (the context modifiers)

Cricket sim/management games (Cricket Director, Cricket-19-class titles, ML match engines) compute
ball outcomes from **player ratings × match situation**, explicitly modelling:

- **Bowler fatigue** — a bowler bowling long spells loses effectiveness; effectiveness is a function of
  overs bowled and rest. Maps directly to the README roadmap item: an over-used bowler gets a *flatter
  base distribution and lower α* (easier to score off, worse at reading the batter).
- **Batsman "settled-ness" / momentum** — an innings is "gradual acceleration": a new batter is tentative
  and accelerates as they settle; a settled batter in a chase plays differently from one building.
  Maps to the roadmap's *batsman match-state shift*.
- **Match situation awareness** — required run-rate, wickets in hand, settled-ness and bowler form feed
  the outcome probabilities. Maps to *match-up-aware bowling rotation*: the captain biases bowler choice
  toward favourable archetype match-ups and toward fresh bowlers.

These are exactly the top unchecked README roadmap items — research confirms they're the standard
levers for making a cricket sim feel real, and they compose cleanly with our pure-logic, seeded-RNG
design.

## 3. Turn-based-sports presentation

The broadcast feel (which we already lean on via the conversational panel) is what separates a "calculator"
from a "game". The cheapest high-impact upgrades: **big-moment commentary** (distinct lines for wickets,
4s/6s, fifties/hundreds, hat-tricks, last-ball finishes) and **context-aware lines** that reference the
new realism state ("the bowler's legs have gone", "he's set now"). This is the roadmap's *more commentary
lines* item and pairs naturally with §2.

## 4. Roguelite / meta-progression (the wrapper)

The dominant lesson from modern roguelites (Hades, Dead Cells, Slay-the-Spire-likes): **persistent
progression between runs makes every session feel productive even when the run resets.** Key design
rules that respect the player:

- Death/loss should **bank something** (currency, unlocks) — never feel wasted.
- Prefer **variety unlocks** (new options into the pool, à la Dead Cells blueprints) over raw stat
  inflation that trivialises content.
- **Respec / low commitment anxiety** — let players experiment.
- **Gradual onboarding** — drip mechanics in over early runs.

For a single-player offline cricket game this points at a **career / tournament campaign**: a run is a
tournament; winning banks currency/reputation that unlocks new opponents, harder difficulties,
cosmetic flavour (commentator panels, kit), and challenge modifiers — all **offline, original-content,
shareable via save codes** (no network/accounts, per our guardrails).

## 5. Implications for Round 1 (M004–M008)

| Milestone | Theme | Seeded by |
|---|---|---|
| **M004** | **Type-debt foundation** — clear ~44 mypy errors, enforce mypy in the gate | dev-runbook (gate), ADR-0002 |
| **M005** | **Cricket realism layer** — bowler fatigue, batsman match-state/momentum, match-up-aware rotation | §2 + README roadmap |
| **M006** | **Strategic AI & opponent modelling** — WSLS/sequence detection, exploit-vs-mix, difficulty depth, tells | §1 + §2 |
| **M007** | **Commentary & presentation depth** — big-moment slots + context-aware lines reflecting M005/M006 state | §3 + README roadmap |
| **M008** | **Career & roguelite meta-progression** — tournament campaign, banked currency, variety unlocks, achievements (offline) | §4 |

Arc: **pay the debt → deepen the simulation → deepen the AI → deepen the presentation → wrap it in
progression.** Each is one minor bump (v0.4.0 → v0.8.0). Foundation first so the gate can enforce
mypy for everything after.

## Sources
- Hand-cricket AI implementations (adaptive frequency bot): https://github.com/ajain1325/AI-Hand-Cricket-Game ·
  https://towardsai.net/p/l/hand-cricket-simulation-using-cnn-and-opencv
- Matching pennies & opponent modelling: https://en.wikipedia.org/wiki/Matching_pennies ·
  https://ar5iv.labs.arxiv.org/html/1909.12701 (cognitive hierarchy + Bayesian learning beats humans) ·
  https://www.numberanalytics.com/blog/algorithmic-mastery-matching-pennies-game-theory
- Cricket simulation engines (ratings × situation, fatigue, momentum): https://cricketdirector.com/ ·
  https://medium.com/@tejalnarkar/cricket-simulation-engine-using-machine-learning-a2758933b0a7
- Roguelite progression design: https://gamerant.com/roguelite-games-with-best-progression-systems/ ·
  https://gamerant.com/roguelites-best-progression-systems-respect-your-free-time/ ·
  https://notes.hamatti.org/gaming/video-games/meta-progression-with-gradual-tutorial-in-roguelike-games
