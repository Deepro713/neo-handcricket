# Roadmap

Milestones are planned in `docs/02-milestones/` and tracked on the GitHub Project board. This page is
refreshed at each release.

## Round 1 — M004–M008 (in progress)
Arc: pay type-debt → deepen the simulation → deepen the AI → deepen the presentation → wrap in
progression. (See `docs/00-overview/decision-log.md` ADR-0003 and the Round 1 research note.)

- ✅ **M004 — Type-debt foundation** (v0.4.x) — mypy clean + enforced in the gate. **Done.**
- ✅ **M005 — Cricket realism layer** (v0.5.x) — bowler fatigue, batsman match-state/momentum,
  match-up-aware bowling rotation, live indicators. **Done.**
- ✅ **M006 — Strategic AI & opponent modelling** (v0.6.x) — opponent model (frequency + WSLS + bigram),
  exploit-vs-mix, Legend tier, eval harness, optional tells. **Done.**
- ✅ **M007 — Commentary & presentation depth** (v0.7.x) — big-moment event detector + escalating line
  banks, context-aware asides, scoreboard milestones + highlights reel. **Done.**
- ✅ **M008 — Career & roguelite meta-progression** (v0.8.x) — offline tournament campaign, banked
  currency, variety unlocks, achievements, shareable save codes. **Done.**

**Round 1 (M004–M008) is complete.**

## Round 2 — M009–M013 (COMPLETE)
Arc: retain → polish to **1.0** → open up → deepen → broaden. (ADR-0021 + the Round 2 research note.)

- ✅ **M009 — Daily-seed & procedural challenges** (v0.9.x) — deterministic daily match + modifiers,
  score + local best-table, offline share codes. **Done.**
- ✅ **M010 — Accessibility, onboarding & 1.0 polish** (**v1.0.0** 🎉) — NO_COLOR + static a11y mode,
  colour-never-alone, untimed timer, onboarding tutorial. **Done — neo-handcricket is 1.0.**
- ✅ **M011 — Headless adapter & Textual TUI foundation** (v1.1.x) — UI-agnostic engine adapter + optional
  local Textual TUI. **Done.**
- ✅ **M012 — Roguelite draft: relics & run modifiers** (v1.2.x) — relic registry + between-rounds draft in the career. **Done.**
- ✅ **M013 — Content & localization scaffold** (v1.3.x) — localization scaffold + curated rosters + commentary breadth. **Done.**

**v1.0.0** lands at **M010**.
