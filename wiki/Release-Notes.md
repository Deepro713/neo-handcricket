# Release Notes

Per-milestone releases (one minor bump each; clusters are patch bumps). Refreshed at every ship.

## Round 2 (in progress)
- **v0.9.2** — M009 `ui-and-playtest`: playable Daily challenge menu + reproducibility gate.
  **Completes M009.**
- **v0.9.1** — M009 `leaderboard`: daily score + local best-table (offline, shareable).
- **v0.9.0** — **M009 Daily-seed & procedural challenges**: deterministic daily match + modifiers.

## Round 1 (forward development) — **COMPLETE (M004–M008)**
- **v0.8.3** — M008 `ui-and-playtest`: campaign dashboard + full-tournament playtest invariant.
  **Completes M008 and Round 1.**
- **v0.8.2** — M008 `achievements`: achievements + offline shareable save codes.
- **v0.8.1** — M008 `progression`: banked currency, variety unlocks, save-schema migration.
- **v0.8.0** — **M008 Career & roguelite meta-progression**: offline knockout tournament core.
- **v0.7.2** — M007 `context-and-polish`: context-aware asides + ★ scoreboard milestones + a match
  highlights reel. **Completes M007.**
- **v0.7.1** — M007 `bigmoment-lines`: escalating big-moment line banks + within-match variety.
- **v0.7.0** — **M007 Commentary & presentation depth**: pure big-moment event detector.
- **v0.6.3** — M006 `tells`: optional, off-by-default player-facing reads on the bowler (never leak the
  pick). **Completes M006.**
- **v0.6.2** — M006 `eval`: offline AI eval harness proving the model beats the frequency baseline
  (gate now 51 checks).
- **v0.6.1** — M006 `difficulty`: opponent model wired live per difficulty + a new **Legend** tier.
- **v0.6.0** — **M006 Strategic AI**: opponent model (frequency + WSLS + bigram) with exploit-vs-mix.
- **v0.5.3** — M005 `ui-and-playtest`: live stamina gauge + settled markers; 9 new playtest invariants
  (gate now 49 checks). **Completes M005.**
- **v0.5.2** — M005 `rotation`: match-up-aware bowling rotation (archetype advantage + freshness).
- **v0.5.1** — M005 `matchstate`: batsman settledness + chase intent reshape the batter's scoring.
- **v0.5.0** — **M005 Cricket realism layer**: bowler fatigue (workload decay + rest recovery).
- **v0.4.1** — M004 `gate-enforcement`: mypy is now a hard QA-gate step (ship-cluster + CI + Makefile);
  ship-cluster version map fixed for zero-padded slugs.
- **v0.4.0** — **M004 Type-debt foundation**: cleared all ~44 mypy errors (`mypy neo_handcricket` =
  0 errors / 31 files). No gameplay change.

## Reconstructed history (pre-cycle work, tagged retroactively)
- **v0.3.0** — **M003 Repo polish, docs & autonomous-dev bootstrap**: LICENSE/CHANGELOG, CONTRIBUTING/
  CoC/README/docs, issue+PR templates, and the autonomous-dev cycle (vault, gate, board, wiki, CI).
- **v0.2.0** — **M002 Rosters, conversational commentary & Test cricket**: all 200 country rosters,
  conversational multi-line commentary, 10s pacing, full Test engine, career dashboard.
- **v0.1.0** — **M001 Core engine**: T10/T20/ODI/Custom formats, innings/match/toss, adaptive bot AI,
  3s keystroke timer, 14 rosters, single-line commentary, persistence, UI, Player of the Match.

_See `docs/00-overview/decision-log.md` (ADR-0002) for the history-reconstruction rationale._
