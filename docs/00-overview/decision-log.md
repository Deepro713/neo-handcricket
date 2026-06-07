---
title: Decision Log (ADRs)
type: reference
---

# neo-handcricket — Decision Log

Architecture Decision Records, newest first. One per cluster/significant decision.

## ADR-0018 — M008 cluster `progression`: currency, variety unlocks & save migration
**Date:** 2026-06-07 · **Status:** accepted · **Cluster:** `m008/progression` · **Issues:** #45

**Context.** The roguelite wrapper needs persistent progression that makes every result bank something,
without power-creep, plus a forward-compatible save format.

**Decision.** Pure `career/progression.py` over a plain dict: `reward_for(result, tournament_champion)`
banks currency; `UNLOCKS` is a registry of **variety** items (bonus opponents, commentary panels,
challenge modifiers — never raw power); `bank`/`unlock`/`can_unlock`/`available_unlocks` enforce
affordability and one-time ownership; `migrate()` upgrades an implicit-v1 dict to schema v2. Thin
`persistence/progression.py` round-trips `stats/progression.json` (migrating on load). Bumped
`SAVE_SCHEMA_VERSION` 1→2 and added `_migrate_save` so existing **v1 match saves load cleanly**.

**Consequences.** 9 unit tests (reward table, currency accrual incl. negative-ignore, unlock gating +
no-funds/unknown no-ops, available-sort, v1 migration, persistence round-trip + legacy-file migrate).
Gate green (ruff + mypy 43 files + 94 tests + playtest 54/54). Feeds `m008/achievements` (#42) and the
campaign UI (#43).

## ADR-0017 — M008 cluster `tournament-core`: an injectable knockout bracket
**Date:** 2026-06-07 · **Status:** accepted · **Cluster:** `m008/tournament-core` · **Issues:** #46

**Context.** A roguelite "run" needs a campaign structure. It must be deterministic and unit-testable
without spinning up real matches.

**Decision.** New pure package `neo_handcricket/career/` with `tournament.py`: a single-elimination
bracket seeded by reputation (best first), padded to a power of two with **byes** via standard seeding
(`seed_slots`), and `play_tournament(teams, resolve)` that runs every round to one `champion`. Fixture
resolution is an **injected `Resolver` callback** (`resolve(home, away) -> winner`) — the game passes a
resolver that plays a real match; tests pass a deterministic one. De-dupes teams; handles byes,
single-team and empty fields.

**Consequences.** 7 unit tests (seed/pad sizing, pow2-no-byes, champion-by-seed, byes auto-advance,
dedupe, valid pairings, fixture counts). Decoupling resolution keeps the core pure and lets
`m008/ui-and-playtest` (#44) run a full headless tournament invariant cheaply. Gate green (ruff + mypy
41 files + 85 tests + playtest 54/54). Feeds `m008/progression` (#45) and `m008/achievements` (#42).

## ADR-0016 — M007 cluster `context-and-polish`: state-aware lines + highlights reel
**Date:** 2026-06-07 · **Status:** accepted · **Cluster:** `m007/context-and-polish` · **Issues:** #39, #41

**Context.** The realism (M005) and AI (M006) state was invisible in the commentary, and the match
summary had no recap of the big moments the detector now produces.

**Decision.**
- **Context-aware lines (#39):** pure `commentary/context.py` `context_line(*, bowler_fatigue,
  batter_settledness, ai_read, rng, emit_prob)` returns an occasional original aside when a threshold
  holds (tired bowler / set batter / AI just read the human), gated by `CONTEXT_LINE_PROB`. `main.py`
  computes the live signals after each ball and shows it as a styled aside.
- **Polish (#41):** scoreboard adds a `★`/`💯` marker to batters past 50/100; a new pure
  `commentary/highlights.py` `build_highlights(events, name_of)` turns the accumulated event stream into
  a de-duplicated, capped **highlights reel** rendered in the match summary. `Match` gains a
  `highlight_events` list (TYPE_CHECKING import, excluded from the selective save serializer).

**Consequences.** 8 unit tests (context thresholds/emit-prob; highlights noteworthy-filter, dedupe,
limit, century formatting). Gate green (ruff + mypy 39 files + 78 tests + playtest 54/54). **Completes
M007** — every M005/M006 mechanic now surfaces in commentary or the scoreboard.

## ADR-0015 — M007 cluster `bigmoment-lines`: escalate on the event stream
**Date:** 2026-06-07 · **Status:** accepted · **Cluster:** `m007/bigmoment-lines` · **Issues:** #38

**Context.** The event detector (ADR-0014) produces typed big moments, but the commentary engine only
keyed off the per-ball `situation`. Big moments (hat-tricks, milestones, last-ball finishes) deserve an
extra escalation beat, and lines were repeating within a match.

**Decision.**
- Add **original CC0 line banks** for `wicket_caught`, `hat_trick`, `maiden`, `last_ball_finish`,
  `collapse`, `partnership_50` (via `LINES.update`); `wicket_caught` is a full ball situation, the rest
  are single-line accents. No broadcaster catchphrases.
- `event_situation(events)` maps the **highest-priority** detected event to an accent situation key
  (last-ball finish > hat-trick > hundred > fifty > collapse > partnership > maiden); wickets/boundaries
  stay in the ball conversation (returns None).
- `main.py` replaces the old (buggy 50-vs-100) manual milestone block with one event-driven escalation
  call from `events.detect(inn)`.
- The engine now tracks `_used_lines` and prefers a **not-yet-used template** each pick — within-match
  variety with graceful fallback once a pool is exhausted.

**Consequences.** 6 unit tests (every category has lines, priority mapping, caught→situation, engine
renders each, no-duplicate variety). Fixes the latent caught-wicket-renders-as-dot gap. Gate green
(ruff + mypy 37 files + 70 tests + playtest 54/54). Next: `m007/context-and-polish` (#39/#41).

## ADR-0014 — M007 cluster `event-detection`: a pure big-moment detector
**Date:** 2026-06-07 · **Status:** accepted · **Cluster:** `m007/event-detection` · **Issues:** #40

**Context.** Richer commentary and scoreboard polish both need a single source of truth for "what just
happened". Detection must be deterministic and decoupled from line selection and rendering.

**Decision.** New pure module `neo_handcricket/commentary/events.py`: `detect(inn) -> list[Event]`
inspects the most recent ball plus innings state and emits typed `Event`s —
`wicket` (+kind), `boundary` (4/6), `milestone` (fifty/hundred, crossed on the ball), `hat_trick`
(bowler's last three legal balls all wickets), `collapse` (≥3 wickets in the last 12 legal balls),
`maiden` (over completed conceding 0), `partnership` (50-run stand crossed), and `last_ball_finish`
(chase sealed with ≤1 ball to spare). Thresholds live in `config`; no I/O, no RNG.

**Consequences.** 9 unit tests pin each trigger to its exact boundary (incl. collapse-without-hat-trick
and the milestone off-by-one). 3 playtest invariants added (gate now **54 checks**). Gate green
(ruff + mypy 37 files + 64 tests). Feeds `m007/bigmoment-lines` (#38, line banks per category) and
`m007/context-and-polish` (#39/#41, context lines + scoreboard highlights from the event stream).

## ADR-0013 — M006 cluster `tells`: optional player-facing mind-games
**Date:** 2026-06-07 · **Status:** accepted · **Cluster:** `m006/tells` · **Issues:** #36

**Context.** Add optional reads on the bowler that create mind-games without breaking the hidden-pick
core — they must never leak the actual number.

**Decision.** New pure module `neo_handcricket/bots/tells.py`: `generate_tell(archetype, fatigue, rng,
truthful_prob)` returns a **coarse zone** hint — low (0-2) / middle (3-4) / high (5-6) — drawn from
original CC0 line banks. It points at the archetype's favoured zone only `TELLS_TRUTHFUL_PROB` (0.6) of
the time and **bluffs** otherwise; a gassed bowler sometimes telegraphs fatigue. A zone is three numbers
wide and only sometimes true, so the exact pick never leaks. Gated by `TELLS_ENABLED` (**off by
default**); when on, `main.py` shows a tell before the user bats via `overlay.show_tell`.

**Consequences.** 6 new unit tests including a hard invariant — **a tell never contains a digit** — plus
truthful-vs-bluff control and the fatigue telegraph. Gate green (ruff + mypy 36 files + 55 tests +
playtest 51/51). **Completes M006's build work** (all 6 issues shipped).

## ADR-0012 — M006 cluster `eval`: prove the opponent model works
**Date:** 2026-06-07 · **Status:** accepted · **Cluster:** `m006/eval` · **Issues:** #32

**Context.** The opponent model (ADR-0010/0011) needed an objective check that it actually beats the
frequency baseline and doesn't hurt itself against a random player.

**Decision.** New typed module `neo_handcricket/bots/evaluation.py`: scripted batting patterns
(`uniform`, `favourite`, `wsls`, `sequence`), `simulate_match_rate(pattern, epsilon=…)` (bot bowls to
match/dismiss; `epsilon=None` = frequency baseline, a float = opponent model), and `evaluate()`
returning per-pattern model-vs-baseline dismissal rates. Deterministic under seed.

**Consequences.** Measured (6 seeds): aggregate model **3.33 > baseline 3.14** on predictable players;
favourite-number batters dismissed at ~0.24 vs ~0.143 chance; uniform players ~0.14 for both (no
edge, no self-harm). 5 new unit tests assert the aggregate edge, strong favourite exploitation, and the
uniform no-edge band. Added 2 playtest invariants (gate now **51 checks**) + a transcript line. Gate
green (ruff + mypy 35 files + 49 tests + playtest 51/51). Last build cluster of M006; only `tells`
remains.

## ADR-0011 — M006 cluster `difficulty`: wire the opponent model behind difficulty
**Date:** 2026-06-07 · **Status:** accepted · **Cluster:** `m006/difficulty` · **Issues:** #33

**Context.** ADR-0010 added the opponent model but only the legacy frequency path was active in real games.
Difficulty needs to control exploitation, and the human's pick outcomes must be tracked to power WSLS.

**Decision.**
- Add a **`legend`** tier (`DIFFICULTY_ALPHA["legend"]=0.8`) and a `DIFFICULTY_EPSILON` map
  (easy 0.85 → medium 0.5 → hard 0.25 → legend 0.08): harder = lower epsilon = exploit more.
- `main.py` now passes `epsilon=DIFFICULTY_EPSILON[difficulty]` to every `pick_number` call, so the
  opponent model is the live adaptation in games, and **tracks per-pick reward signs**
  (`user_batting_outcomes`/`user_bowling_outcomes`, kept aligned with the picks lists) to feed WSLS — a
  batting pick is "rewarded" if it scored without getting out; a bowling pick if it took a wicket or
  conceded ≤1.
- The difficulty selector gains **Legend** with reworded, behaviour-accurate descriptions.

**Consequences.** 3 new unit tests (all tiers defined, epsilon strictly decreasing, harder tiers dismiss
a predictable batter more often). Gate green (ruff + mypy 34 files + 44 tests + playtest 49/49). Easy
still ignores reads (α=0); Legend punishes patterns hard while the epsilon floor keeps it non-deterministic.

## ADR-0010 — M006 cluster `opponent-model`: read the human, stay unpredictable
**Date:** 2026-06-07 · **Status:** accepted · **Cluster:** `m006/opponent-model` · **Issues:** #37, #35, #34

**Context.** Hand cricket is a repeated matching-pennies game (research §1): no optimal pure strategy,
so depth = modelling the human while remaining unexploitable. The old adaptation was frequency-only.

**Decision.** New pure module `neo_handcricket/bots/opponent.py`:
- `predict_next(picks, outcomes)` blends three weak models — **frequency** (smoothed recent counts),
  **Win-Stay-Lose-Shift** (after a rewarding pick predict *stay*, else *shift* away; needs per-pick
  reward signs), and a **bigram** sequence predictor (what follows the last pick) — weighted by config.
- `exploit_mix(dist, epsilon)` blends the exploit prediction toward uniform (#34): 0 = exploit hard,
  1 = the equilibrium mixed strategy (unexploitable), so the bot punishes predictable players without
  becoming a deterministic, reverse-engineerable target.
- `invert(dist)` turns "where they'll go" into "where to go to avoid them" (bot batting).

Wired into `strategy.pick_number` via backward-compatible `opponent_outcomes` + `epsilon` kwargs: when
`epsilon` is given, adaptation uses the opponent model (bowling aims at the prediction; batting aims at
its inverse); otherwise the legacy frequency path is unchanged.

**Consequences.** 10 new unit tests (each sub-model's signature behaviour, exploit-mix endpoints,
invert, and an end-to-end "low epsilon matches a predictable batter more than high epsilon"). Gate green
(ruff + mypy 34 files + 42 tests + playtest 49/49). Next: `m006/difficulty` wires epsilon per tier
(incl. a `legend` tier) and threads outcome tracking from `main.py`.

## ADR-0009 — M005 cluster `ui-and-playtest`: surface realism + assert it
**Date:** 2026-06-07 · **Status:** accepted · **Cluster:** `m005/ui-and-playtest` · **Issues:** #31, #30

**Context.** The three M005 realism levers (fatigue, match-state, rotation) were invisible to the player
and unguarded by the playtest gate.

**Decision.**
- **Thin UI (#31), read-only:** `overlay.show_bowler_card` gains an optional `fatigue` arg and renders a
  5-block **stamina gauge**; `scoreboard.render_compact` appends a **settled marker** (`★`/`·`) to each
  batter derived from balls faced via `matchstate.settledness`. `main.py` computes the current bowler's
  fatigue (reusing the rest tracker) and passes it to the overlay. No logic in the UI layer.
- **Playtest invariants (#30):** new `_realism_invariants()` adds 9 checks — fatigue rises/recovers,
  pace tires faster, a tired bowler matches a predictable batter less; settledness monotonic, chase
  raises intent, an aggressive batter hits more boundaries; and a full-innings rotation respects the
  no-consecutive-over and per-bowler-cap invariants. The recorded transcript gains a realism summary
  line.

**Consequences.** Playtest is **49/49** (was 40); recorded transcript reviewed (fresh/tired matches
87/63, boundaries tentative/aggressive 69/148, rotation 4 overs each — all as expected). Gate green
(ruff + mypy 33 files + 32 tests + playtest 49/49). **Completes M005.**

## ADR-0008 — M005 cluster `rotation`: match-up-aware bowling rotation
**Date:** 2026-06-07 · **Status:** accepted · **Cluster:** `m005/rotation` · **Issues:** #29

**Context.** Third realism lever (research §2): the captain should bias bowler selection toward a
favourable bowler-vs-batter archetype match-up and toward fresher bowlers, without breaking the
existing phase logic or the cap / no-consecutive-over invariants.

**Decision.** Extend `bots/captain.py`:
- A `MATCHUP` table (bowler archetype × batter archetype → advantage in ~[-0.2, 0.2], original content)
  and `matchup_advantage(bowler, batter)`.
- `pick_next_bowler` gains two optional, backward-compatible kwargs: `batter_archetype` and
  `fatigues` (bowler_id → fatigue). In the power/middle phases it ranks the preferred-kind pool by
  `ROTATION_MATCHUP_WEIGHT·matchup + ROTATION_FRESHNESS_WEIGHT·freshness − overs_bowled` (then random
  top-half pick). The death phase keeps economy-first, with freshness as a new tie-breaker.

`main.py` computes the striker's archetype and a per-pool fatigue map (reusing `fatigue_factor` with the
`last_over_by_bowler` rest tracker) and passes them in.

**Consequences.** 6 new unit tests (match-up lookup, no-consecutive/cap invariants preserved, match-up
bias, freshness tie-break, death economy). Gate green (ruff + mypy + 32 tests + playtest 40/40). The
three core M005 realism levers (fatigue, match-state, rotation) now compose.

## ADR-0007 — M005 cluster `matchstate`: batsman match-state / momentum
**Date:** 2026-06-07 · **Status:** accepted · **Cluster:** `m005/matchstate` · **Issues:** #27

**Context.** Second realism lever (research §2): a batter should start tentative and accelerate as they
settle, and a chase should sharpen intent as the required rate climbs.

**Decision.** New pure module `neo_handcricket/bots/matchstate.py`:
- `settledness(balls_faced)` → [0,1), `balls/(balls+SETTLE_BALLS_K)` (0.5 at K=8 balls).
- `chase_intent(runs_needed, balls_remaining)` → [0,1] from required-per-ball (1/ball ≈ 0.5, 2+ → 1; 0
  when not chasing).
- `aggression(settled, intent)` → [0,1] = `AGGRO_BASE + w_settle·settled + w_intent·intent`.
- `apply_matchstate(base, aggression)` reshapes the batter base by a boundary **tilt** centred at 0.5
  (neutral = identity; <0.5 favours safe low scores; >0.5 favours 4/6). Always returns a valid pmf.

Wired into `strategy.pick_number` via a backward-compatible `aggression: float | None = None` kwarg
(batting-only; `None` = no change). `main.py` computes it for the bot batter from the striker's balls
faced and the innings chase state (`inn.runs_needed`, `inn.balls_remaining`).

**Consequences.** 6 new unit tests (settledness/intent/aggression bounds+ordering, neutral-identity,
tentative-vs-aggressive reshape, and an end-to-end "aggressive batter hits more 4/6"). Gate green
(ruff + mypy 33 files + 26 tests + playtest 40/40).

## ADR-0006 — M005 cluster `fatigue`: bowler fatigue model
**Date:** 2026-06-07 · **Status:** accepted · **Cluster:** `m005/fatigue` · **Issues:** #28

**Context.** First realism lever (research §2): a bowler should get less effective the longer they
bowl and recover with rest. The game alternates bowlers (no consecutive overs), so the meaningful
signal is **cumulative workload** offset by **rest since last spell**, not strictly-consecutive overs.

**Decision.** New pure module `neo_handcricket/bots/fatigue.py`:
- `fatigue_factor(overs_bowled, overs_rested, archetype) -> float` in [0,1] — workload
  (`overs_bowled × decay_rate`) minus recovery (`overs_rested × recovery`), clamped. Pace/swing/mystery
  decay faster (`FATIGUE_DECAY_PACE=0.12`) than spin (`FATIGUE_DECAY_SPIN=0.07`); recovery 0.05/over.
- `apply_fatigue(base, alpha, fatigue) -> (base', alpha')` — blends the base distribution toward
  uniform by `fatigue` and scales α by `(1-fatigue)`: a tired bowler is easier to score off and reads
  the batter worse.

Wired into `strategy.pick_number` via a new `fatigue: float = 0.0` kwarg (bowling-only,
backward-compatible). `main.py` tracks `last_over_by_bowler` to derive rest, reads `over_counts` for
workload, and passes the computed factor for the bot bowler each over.

**Consequences.** 8 new unit tests (bounds, monotonicity, rest-recovery, pace-vs-spin, distribution
validity, and an end-to-end "tired bowler matches a predictable batter less"). Pure/seeded; gate green
(ruff + mypy 32 files + 20 tests + playtest 40/40). Sets up `m005/rotation` (#29) to factor freshness
into bowler selection and `m005/realism-ui` (#31) to surface stamina.

## ADR-0005 — M004 cluster `gate-enforcement`: make mypy a hard gate + fix the version map
**Date:** 2026-06-07 · **Status:** accepted · **Cluster:** `m004/gate-enforcement` · **Issues:** #22

**Context.** With the package mypy-clean (ADR-0004), mypy can move from advisory to enforced. Separately,
shipping `m004/types-fixes` surfaced a bug: `ship-cluster.sh`'s version-map regex
(`s#^m\([0-9]+\)/…#`) captured the **zero-padded** milestone number (`m004` → `004`), which matched no
`case` label, so the tag/release step was skipped (v0.4.0 had to be tagged by hand).

**Decision.**
- **Enforce mypy everywhere it gates:** move `mypy neo_handcricket` out of the advisory `|| true` block
  in `ship-cluster.sh run_gate`; drop `|| true` in `.github/workflows/ci.yml`; the `Makefile` `gate`
  target already chained `type`. README updated ("all four are enforced; mypy-clean as of v0.4.0").
- **Fix the version map** to strip leading zeros: `s#^m0*\([0-9][0-9]*\)/…#\1#` — now `m4`, `m004`,
  `m010`, `m020` all resolve correctly, honouring the zero-padded `m00N` branch convention.

**Consequences.** A deliberately-introduced type error now fails the gate (verified); future ships from
zero-padded slugs tag + release without manual intervention. mypy enforcement holds for every milestone
from M005 onward.

## ADR-0004 — M004 cluster `types-fixes`: clear the mypy debt (0 errors)
**Date:** 2026-06-07 · **Status:** accepted · **Cluster:** `m004/types-fixes` · **Issues:** #21, #23, #24, #25, #26

**Context.** The package carried ~44 mypy errors across 6 files, so the gate could only treat mypy as
advisory. Three root causes dominated: (a) the `rng = rng or random` idiom assigned the `random`
*module* to a `Random | None` local, poisoning every downstream `rng.<method>` call (23 `union-attr`);
(b) **name collisions** where one local was bound to two unrelated types across mutually-exclusive
branches/loops (`gloveman` int-vs-Player, scoreboard `c` BatterCard-vs-BowlerCard, `bat`
TeamMeta-vs-str, `score` int-vs-float, menu `match` Match-vs-Match|None); (c) `Optional`/`int | None`
values used without narrowing.

**Decision.** Fix at the source, no blanket `# type: ignore`:
- Standardise the RNG idiom on `rng = rng if rng is not None else random.Random()` (behaviourally
  identical — the `None` path is non-deterministic either way; seeded callers are unaffected).
- Resolve collisions by **renaming** the narrower/secondary binding (`gloveman_id`, `bc`, `bat_country`,
  `score: float`, `new_match`) rather than widening types.
- Correct one genuinely-wrong annotation (`BatterCard.out_over: int -> str`, per its own comment).
- Narrow `Optional` before use (`current_bowler_id` guard; subscript instead of `.get()` after an `in`
  check; `Literal["heads","tails"]` for the toss call).
- Replace the per-ball `tick` lambda with `functools.partial(update_prompt_line, prompt_text)` — fixes
  both mypy's "cannot infer lambda" and ruff's B023 loop-binding warning, and drops a dead
  `sum(counts.values())` expression.

**Consequences.** `mypy neo_handcricket` is **0 errors / 31 files**; ruff + 12 tests + playtest (40/40)
green. No behavioural change. Clears the way for cluster `m004/gate-enforcement` (#22) to make mypy a
hard gate step.

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
