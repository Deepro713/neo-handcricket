"""
Reverse converter: repo JSON → vault Markdown.

For every roster JSON in `neo_handcricket/rosters/data/`, ensure a matching
Markdown file exists in `~/personal/10-Projects/neo-handcricket/rosters/`.
By default, existing vault MD files are NOT overwritten — pass `--force` to
re-render every country.

Use cases:
  - Materialise vault MDs for bulk-generated countries (so the vault has one
    file per country, matching the repo).
  - Re-render every country's MD from JSON after a schema change.

Companion tool: `tools/convert_rosters.py` runs the reverse direction
(vault MD → repo JSON) and is the canonical workflow when hand-editing a
roster.

Usage:
    python tools/json_to_vault_md.py            # generate only missing MDs
    python tools/json_to_vault_md.py --force    # rewrite every country MD
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

REPO_DATA = Path(__file__).resolve().parent.parent / "neo_handcricket/rosters/data"
VAULT_ROSTERS = Path.home() / "personal/10-Projects/neo-handcricket/rosters"

ROLE_LABEL = {
    "captain":         "Captain",
    "vice-captain":    "Vice-captain",
    "keeper":          "Wicketkeeper",
    "keeper-reserve":  "Wicketkeeper (reserve)",
    "batsman":         "Batsman",
    "all-rounder":     "All-rounder",
    "bowler":          "Bowler",
}


def _player_line(idx: int, p: dict) -> str:
    """Format one numbered player line, matching the convention used in
    hand-curated MDs (so re-running convert_rosters.py round-trips cleanly)."""
    role = p.get("role", "")
    label = ROLE_LABEL.get(role, role.title())
    bat = p.get("batting_hand")
    bowl = p.get("bowling_style")
    bat_arch = p.get("batting_archetype")

    if role in ("captain", "vice-captain", "keeper", "keeper-reserve"):
        bat_field = f"{bat} bat" if bat else ""
        fields = [label, bat_field, bat_arch or ""]
    elif role == "batsman":
        fields = [label, bat or "", bat_arch or ""]
    elif role == "all-rounder":
        bat_field = f"{bat} bat" if bat else ""
        fields = [label, bat_field, bowl or ""]
    elif role == "bowler":
        fields = [label, bowl or "", bat_arch or ""]
    else:
        # Unknown role: best-effort formatting
        parts = [label]
        if bat:
            parts.append(f"{bat} bat")
        if bowl:
            parts.append(bowl)
        if bat_arch:
            parts.append(bat_arch)
        return f"{idx}. **{p['name']}** — " + " · ".join(parts)

    body = " · ".join(f for f in fields if f)
    return f"{idx}. **{p['name']}** — {body}"


def _composition(players: list[dict]) -> dict:
    role_counts = Counter(p.get("role") for p in players)
    bat_specialist = role_counts["captain"] + role_counts["vice-captain"] + role_counts["batsman"]
    keepers = role_counts["keeper"] + role_counts["keeper-reserve"]
    all_rounders = role_counts["all-rounder"]
    pace = sum(1 for p in players if p.get("bowling_archetype") in ("pace", "swing", "mystery") and p.get("role") == "bowler")
    spin = sum(1 for p in players if p.get("bowling_archetype") in ("off-spin", "leg-spin") and p.get("role") == "bowler")
    lh = sum(1 for p in players if p.get("batting_hand") == "LH")
    rh = sum(1 for p in players if p.get("batting_hand") == "RH")
    return {
        "specialist_batsmen": bat_specialist,
        "keepers": keepers,
        "all_rounders": all_rounders,
        "pace": pace,
        "spin": spin,
        "lh": lh,
        "rh": rh,
    }


def _staff_lines(staff: list[dict]) -> list[str]:
    out: list[str] = []
    for s in staff:
        role = s.get("role", "").replace("_", " ").title().replace("Assistant Coach", "Assistant coach")
        out.append(f"- **{role}:** {s.get('name', '')}")
    return out


GENERATED_FLAVOR = (
    "Auto-generated squad. Names follow {naming_convention} convention. "
    "Cultural authenticity is best-effort — hand-edit this file and re-run "
    "`python tools/convert_rosters.py` from the repo to refine."
)


def render(country_json: dict, *, slug: str, generated: bool) -> str:
    name = country_json["country"]
    flag = country_json.get("flag", "")
    nc = country_json.get("naming_convention", "given-family")
    players = country_json.get("players", [])
    staff = country_json.get("staff", [])
    comp = _composition(players)

    lines: list[str] = []
    lines.append("---")
    lines.append(f"country: {name}")
    lines.append(f"flag: {flag}")
    lines.append(f"naming_convention: {nc}")
    lines.append("created: 2026-05-08")
    lines.append('parent: "[[../bot-profiles]]"')
    lines.append("type: software")
    lines.append("tags: [project, software, game, roster]")
    lines.append("---")
    lines.append("")
    lines.append(f"# {name}")
    lines.append("")
    if generated:
        lines.append(GENERATED_FLAVOR.format(naming_convention=nc))
        lines.append("")
    lines.append(f"## Squad ({len(players)})")
    lines.append("")
    for i, p in enumerate(players, start=1):
        lines.append(_player_line(i, p))
    lines.append("")
    lines.append(f"## Staff ({len(staff)})")
    lines.append("")
    for s_line in _staff_lines(staff):
        lines.append(s_line)
    lines.append("")
    lines.append("## Composition")
    lines.append("")
    lines.append(f"- Specialist batsmen (incl. cap/VC): {comp['specialist_batsmen']}")
    lines.append(f"- Wicketkeepers: {comp['keepers']}")
    lines.append(f"- All-rounders: {comp['all_rounders']}")
    lines.append(f"- Pace bowlers: {comp['pace']}")
    lines.append(f"- Spinners: {comp['spin']}")
    lines.append(f"- LH/RH split (batting): {comp['lh']} LH / {comp['rh']} RH")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    force = "--force" in sys.argv
    if not VAULT_ROSTERS.exists():
        print(f"vault rosters dir not found: {VAULT_ROSTERS}", file=sys.stderr)
        return 1

    json_files = sorted(REPO_DATA.glob("*.json"))
    written: list[str] = []
    skipped: list[str] = []
    for jp in json_files:
        slug = jp.stem
        md_path = VAULT_ROSTERS / f"{slug}.md"
        if md_path.exists() and not force:
            skipped.append(slug)
            continue
        country_json = json.loads(jp.read_text(encoding="utf-8"))
        # If the vault MD existed before this run, treat as hand-curated and DON'T mark as generated
        # (we only get here if --force, in which case we still want to preserve flavor).
        # Heuristic: a hand-curated MD typically has a flavor paragraph that the
        # auto-generator stamps with the GENERATED_FLAVOR sentence. We can't reliably
        # detect, so the safe behaviour is: with --force, mark as generated.
        generated = True
        md = render(country_json, slug=slug, generated=generated)
        md_path.write_text(md, encoding="utf-8")
        written.append(slug)

    print(f"Wrote {len(written)} MD files; skipped {len(skipped)} existing.")
    if "--verbose" in sys.argv:
        for s in written:
            print(f"  + {s}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
