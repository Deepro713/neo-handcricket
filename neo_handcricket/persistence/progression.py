"""Thin persistence for career meta-progression (stats/progression.json)."""
from __future__ import annotations

import json
from typing import Any

from ..career import progression as prog
from ..config import STATS_DIR

PROGRESSION_FILE = STATS_DIR / "progression.json"


def load_progression() -> dict[str, Any]:
    if not PROGRESSION_FILE.exists():
        return prog.new_progression()
    try:
        data = json.loads(PROGRESSION_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return prog.new_progression()
    return prog.migrate(data)


def save_progression(state: dict[str, Any]) -> None:
    STATS_DIR.mkdir(parents=True, exist_ok=True)
    PROGRESSION_FILE.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
