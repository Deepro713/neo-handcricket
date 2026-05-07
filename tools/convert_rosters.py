"""
Convert vault roster Markdown files to JSON for the game.

Reads from: ~/personal/10-Projects/neo-handcricket/rosters/*.md
Writes to:  neo_handcricket/rosters/data/*.json

Usage:
    python tools/convert_rosters.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

VAULT_ROSTERS = Path.home() / "personal/10-Projects/neo-handcricket/rosters"
REPO_DATA = Path(__file__).resolve().parent.parent / "neo_handcricket/rosters/data"

# Player line: "1. **Name** — Role · field · field · ..."
PLAYER_RE = re.compile(r"^\s*(\d+)\.\s+\*\*([^*]+)\*\*\s+—\s+(.+?)\s*$")
STAFF_RE = re.compile(r"^\s*-\s+\*\*([^:]+):\*\*\s+(.+?)\s*$")
FRONTMATTER_RE = re.compile(r"^---\s*$\n(.*?)\n---\s*$", re.MULTILINE | re.DOTALL)

ROLE_MAP = {
    "Captain": "captain",
    "Vice-captain": "vice-captain",
    "Wicketkeeper": "keeper",
    "Wicketkeeper (reserve)": "keeper-reserve",
    "Batsman": "batsman",
    "All-rounder": "all-rounder",
    "Bowler": "bowler",
}

BATTING_ARCHETYPES = {"opener", "anchor", "power-hitter", "finisher", "tail-ender", "all-rounder"}
BOWLING_ARCHETYPES = {"pace", "swing", "off-spin", "leg-spin", "mystery"}


def parse_frontmatter(text: str) -> dict:
    m = FRONTMATTER_RE.search(text)
    if not m:
        return {}
    out = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def classify_field(field: str) -> tuple[str, str | None]:
    """Return (kind, value) where kind is one of:
    'batting_hand' | 'bowling_style' | 'batting_archetype' | 'bowling_archetype' | 'unknown'.
    Bowling fields produce both 'bowling_style' (full text) and 'bowling_archetype' (root).
    """
    f = field.strip()
    if f in ("RH", "LH"):
        return ("batting_hand", f)
    if f in ("RH bat", "LH bat"):
        return ("batting_hand", f[:2])
    if f.startswith("RA ") or f.startswith("LA "):
        # e.g. "RA pace", "LA off-spin", "RA mystery"
        for arch in BOWLING_ARCHETYPES:
            if arch in f:
                return ("bowling_style+archetype", (f, arch))  # type: ignore
        return ("bowling_style", f)
    if f in BATTING_ARCHETYPES:
        return ("batting_archetype", f)
    return ("unknown", f)


def parse_player_line(line: str) -> dict | None:
    m = PLAYER_RE.match(line)
    if not m:
        return None
    num, name, rest = m.group(1), m.group(2).strip(), m.group(3).strip()
    fields = [x.strip() for x in rest.split("·")]
    role_text = fields[0].strip()
    role = ROLE_MAP.get(role_text, role_text.lower())

    player = {
        "id": int(num),
        "name": name,
        "role": role,
        "batting_hand": None,
        "bowling_style": None,
        "batting_archetype": None,
        "bowling_archetype": None,
    }
    for f in fields[1:]:
        kind, value = classify_field(f)
        if kind == "batting_hand":
            player["batting_hand"] = value
        elif kind == "bowling_style":
            player["bowling_style"] = value
        elif kind == "bowling_style+archetype":
            assert isinstance(value, tuple)
            player["bowling_style"] = value[0]
            player["bowling_archetype"] = value[1]
        elif kind == "batting_archetype":
            player["batting_archetype"] = value
    return player


def parse_staff_line(line: str) -> dict | None:
    m = STAFF_RE.match(line)
    if not m:
        return None
    role_text = m.group(1).strip()
    name = m.group(2).strip()
    role = "coach" if role_text.lower() == "coach" else (
        "assistant_coach" if "assistant" in role_text.lower() else role_text.lower().replace(" ", "_")
    )
    return {"role": role, "name": name}


def parse_roster_md(text: str) -> dict:
    fm = parse_frontmatter(text)
    players: list[dict] = []
    staff: list[dict] = []
    in_squad = False
    in_staff = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("## squad"):
            in_squad = True
            in_staff = False
            continue
        if stripped.lower().startswith("## staff"):
            in_squad = False
            in_staff = True
            continue
        if stripped.startswith("##"):
            in_squad = False
            in_staff = False
            continue
        if in_squad:
            p = parse_player_line(line)
            if p:
                players.append(p)
        elif in_staff:
            s = parse_staff_line(line)
            if s:
                staff.append(s)
    return {
        "country": fm.get("country", ""),
        "flag": fm.get("flag", ""),
        "naming_convention": fm.get("naming_convention", "given-family"),
        "players": players,
        "staff": staff,
    }


def main() -> None:
    REPO_DATA.mkdir(parents=True, exist_ok=True)
    md_files = sorted(VAULT_ROSTERS.glob("*.md"))
    for md_path in md_files:
        if md_path.name.lower() == "readme.md":
            continue
        slug = md_path.stem
        text = md_path.read_text(encoding="utf-8")
        roster = parse_roster_md(text)
        if len(roster["players"]) != 33:
            print(f"WARN  {slug}: expected 33 players, parsed {len(roster['players'])}")
        if len(roster["staff"]) != 2:
            print(f"WARN  {slug}: expected 2 staff, parsed {len(roster['staff'])}")
        out_path = REPO_DATA / f"{slug}.json"
        out_path.write_text(json.dumps(roster, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"OK    {slug}.json  ({len(roster['players'])} players, {len(roster['staff'])} staff)")


if __name__ == "__main__":
    main()
