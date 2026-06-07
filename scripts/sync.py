#!/usr/bin/env python3
"""Vault -> GitHub sync. The vault (docs/03-issues/*.md) is the source of truth;
this creates a GitHub issue for any note that lacks one, attaches it to the
Project board, and writes the issue number back into the note.

    python scripts/sync.py push

Frontmatter expected (see docs/03-issues/*.md):
    title, type: issue, milestone: M0NN, cluster, priority, labels (list), state: open
Adds a `github:\n  issue: N` block once created.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO = "Deepro713/neo-handcricket"
PROJECT_OWNER = "Deepro713"
PROJECT_NUMBER = "6"  # neo-handcricket board (PVT_kwHOBh136c4BZ8xm)
ISSUES_DIR = Path(__file__).resolve().parent.parent / "docs" / "03-issues"


def _front(text: str) -> tuple[dict, str]:
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        return {}, text
    raw, body = m.group(1), m.group(2)
    fm: dict = {}
    labels: list[str] = []
    in_labels = False
    for line in raw.splitlines():
        if re.match(r"^\s*-\s", line) and in_labels:
            labels.append(line.split("-", 1)[1].strip().strip("'\""))
            continue
        in_labels = False
        m2 = re.match(r"^([a-zA-Z_]+):\s*(.*)$", line)
        if not m2:
            continue
        k, v = m2.group(1), m2.group(2).strip()
        if k == "labels":
            in_labels = True
            continue
        fm[k] = v.strip("'\"")
    fm["labels"] = labels
    fm["_has_issue"] = "issue:" in raw
    return fm, body


def push() -> int:
    notes = sorted(ISSUES_DIR.glob("*.md")) if ISSUES_DIR.exists() else []
    created = 0
    for path in notes:
        text = path.read_text()
        fm, body = _front(text)
        if fm.get("type") != "issue" or fm.get("_has_issue") or fm.get("state") == "closed":
            continue
        title = fm.get("title", path.stem)
        args = ["gh", "issue", "create", "--repo", REPO, "--title", title, "--body", body.strip() or title]
        if fm.get("milestone"):
            args += ["--milestone", _milestone_title(fm["milestone"])]
        for lab in fm.get("labels", []):
            args += ["--label", lab]
        if fm.get("area"):
            args += ["--label", f"area:{fm['area']}"]
        try:
            url = subprocess.check_output(args, text=True).strip().splitlines()[-1]
        except subprocess.CalledProcessError as e:
            print(f"! failed to create issue for {path.name}: {e}")
            continue
        num = url.rstrip("/").split("/")[-1]
        subprocess.run(["gh", "project", "item-add", PROJECT_NUMBER, "--owner", PROJECT_OWNER, "--url", url],
                       check=False, capture_output=True)
        path.write_text(text.replace("\n---\n", f"\ngithub:\n  issue: {num}\n---\n", 1))
        print(f"+ #{num} {title}")
        created += 1
    print(f"push: {created} created")
    return 0


_MS_CACHE: dict[str, str] = {}


def _milestone_title(key: str) -> str:
    """Map an M0NN key to the full GitHub milestone title (must already exist)."""
    if not _MS_CACHE:
        import json
        out = subprocess.run(["gh", "api", f"repos/{REPO}/milestones?state=all&per_page=100"],
                             capture_output=True, text=True)
        for ms in json.loads(out.stdout or "[]"):
            k = ms["title"].split(" ")[0]
            _MS_CACHE[k] = ms["title"]
    return _MS_CACHE.get(key, key)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "push"
    sys.exit(push() if cmd == "push" else (print("usage: sync.py push") or 1))
