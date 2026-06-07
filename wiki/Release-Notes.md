# Release Notes

Per-milestone releases (one minor bump each; clusters are patch bumps). Refreshed at every ship.

## Round 1 (forward development)
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
