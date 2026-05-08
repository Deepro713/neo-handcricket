# Contributing to neo-handcricket

This is a personal hobby project — built for fun, kept honest by tests, maintained by one person in spare time. PRs are welcome but I may be slow to respond. If you're thinking of larger changes, please **open an issue first** so we can talk it through before you write code.

By participating in this project, you agree to abide by the [Code of Conduct](CODE_OF_CONDUCT.md).

## Quick start

```sh
git clone https://github.com/<your-fork>/neo-handcricket.git
cd neo-handcricket
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m tests.test_smoke   # all 12 should pass
python -m neo_handcricket    # play a match
```

## Easy ways to contribute

- **Refine an auto-generated country roster.** 182 of the 200 country rosters are bulk-generated from regional name pools. If you spot one that reads off-rhythm (a Ghanaian name with the wrong family-name structure, an Italian roster missing northern/southern variety, etc.), edit the vault MD and re-run the converter. See [Roster workflow](#roster-workflow) below.
- **Add commentary lines.** `neo_handcricket/commentary/lines.py` has 178 templates across 23 situations. More variety per (situation × trait) makes the commentary feel deeper. Lines are tagged with traits — pick existing tags from [`commentators.py`](neo_handcricket/commentary/commentators.py) so the engine can route them.
- **Fix a bug.** Anything that contradicts the documented behaviour in the vault notes is a bug. Open an issue with steps to reproduce.
- **Improve the README / docs.** Always welcome.

## Larger changes — please open an issue first

These are areas where the design is more opinionated and a heads-up saves us both time:

- New cricket formats or rule changes
- New game features (sound design, GUI port, multiplayer)
- Changes to bot AI distributions or the captain-AI heuristic — see [`bot-profiles.md` in the vault](https://github.com/) (or the equivalent narrative)
- Breaking changes to save-file schema (bump `SAVE_SCHEMA_VERSION` in `config.py` and write a migration)

## Repository layout

```
neo_handcricket/   game source (one module per responsibility)
tests/             smoke tests
tools/             vault ↔ repo roster converters
saves/  stats/     runtime data (gitignored)
```

The `neo_handcricket/` package is structured so each module owns one responsibility — see the table in `README.md`. If you're adding a new feature, prefer extending an existing module before adding a new one.

## Roster workflow

The 200 country rosters live in **two synchronised places**:

- `neo_handcricket/rosters/data/<slug>.json` — what the game loads at runtime.
- `~/personal/10-Projects/neo-handcricket/rosters/<slug>.md` (the maintainer's vault — ignore this path; for contributors, the vault MDs aren't shipped in this repo, only the JSONs).

If you want to refine a roster as a contributor, **edit the JSON directly** in `neo_handcricket/rosters/data/`. Run the smoke tests after editing to confirm the JSON still parses and meets the squad-shape requirements (33 players + 2 staff; 1 captain + 1 vice-captain + 3 keepers; ≥ 4 bowlers).

## Testing

```sh
python -m tests.test_smoke
```

12 smoke tests cover roster loading, validator behaviour, playing-XI selection, full-innings simulation, save/load round-trip, and the multi-line commentary structure. **All tests must pass before a PR is merged.**

If you're adding a feature, add a smoke test that exercises it. The test file is intentionally small and fast — keep it that way. Don't pull in pytest unless you have a strong reason; the runner is plain Python `if __name__ == "__main__":`.

## Code style

- **Python 3.10+ idioms** — `match` statements, union `X | Y` types, `dataclass` over manual `__init__`.
- **Single dependency policy** — runtime depends only on `rich`. New runtime deps need a strong justification in the PR description.
- **Type hints encouraged**, not enforced. Useful where it clarifies intent.
- **No comments restating what code does.** Comments explain *why*, especially around hidden constraints (e.g. the wide/no-ball/dead-ball decision tree in `_resolve_ball_outcome_*`).
- **No formatter is configured.** PEP 8 by default. Don't reformat unrelated code in a feature PR — keeps diffs reviewable.

## Commit messages

- Imperative subject line, ≤ 72 chars: "Add fatigue-decay to bowler profiles" not "added fatigue".
- Body wrapped at 72 chars. Explain *why*, not what — the diff shows what.
- Reference issues with `#NN` if applicable.

## PR process

1. Fork the repo, branch off `main`.
2. Make your change. Add a test if relevant.
3. Run `python -m tests.test_smoke`. All 12 must pass.
4. Open a PR with a clear description. Screenshots / asciicasts welcome for UX changes.
5. Be patient with reviews — this is a hobby project.

## License

By contributing, you agree your work is licensed under the MIT License — see [LICENSE](LICENSE).
