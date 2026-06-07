---
title: Dev Runbook
type: reference
---

# neo-handcricket — Dev Runbook

The concrete checklist for each autonomous turn. Pair with `conventions-and-rules.md`.

## Every turn — FIRST
```bash
git checkout main && git pull --ff-only
gh pr list --state open            # avoid duplicating in-flight work
python -m pip install -q -e ".[dev]"   # ensure dev deps (first turn only)
ruff check . && mypy neo_handcricket && pytest -q && python -m tools.playtest   # baseline gate
```
All green before starting new work.

## Implement a cluster
1. `scripts/ship-cluster.sh start mNN/<cluster>` — branches `mNN/<cluster>`, marks its issues In Progress.
2. Build the feature: **pure logic module(s) in `neo_handcricket/…` + unit tests in `tests/`** first,
   then wire the thin UI/IO.
3. Gate: `ruff check . && mypy neo_handcricket && pytest -q && python -m tools.playtest` — fix until green.
4. ADR: prepend an entry to `docs/00-overview/decision-log.md`.
5. `scripts/ship-cluster.sh ship "<title>" <issue#...>` — commits, opens + squash-merges the PR, tags
   the version, cuts a release.

## Per milestone
- At start: post an **ON_TRACK** Project status update (`scripts/sync.py status ...`).
- At finish: DELETE the on-track update + CREATE a fresh **COMPLETE** one (chips don't re-render on
  edit; recreate in chronological order). Update README current-state + roadmap; refresh `wiki/`.

## Planning a round (every 5 milestones)
1. Research comparable games / mechanics (WebSearch) → `docs/04-research/<dated>.md` + an ADR.
2. Author 5 milestone notes (`docs/02-milestones/`) + many issue notes (`docs/03-issues/`) matching the
   frontmatter schema (see existing notes).
3. `gh api repos/Deepro713/neo-handcricket/milestones -f title="M0NN — …"` for each, then
   `scripts/sync.py push` to create the GitHub issues + board items.
4. ADR + a planning ON_TRACK status update. Then implement.

## Recorded playtest (a fix milestone)
Because this is a CLI, "record + watch" = **transcripts**, not screenshots:
`python -m tools.playtest --record <out.txt>` plays scripted/seeded sessions and writes the full
terminal transcript; review it for anything broken/ugly/abnormal, file issues, fix. (No GPU/visual
caveats — text is ground truth.)

## Keys / commands
- Run the game: `neo-handcricket` (or `python -m neo_handcricket`).
- Gate: `make gate` (or the four commands above).
- Sync vault→GitHub: `scripts/sync.py push`.
