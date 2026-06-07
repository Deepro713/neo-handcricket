"""Thin persistence for the daily-challenge best-table (stats/daily.json)."""
from __future__ import annotations

import json
from typing import Any

from ..config import STATS_DIR

DAILY_FILE = STATS_DIR / "daily.json"


def load_best_table() -> dict[str, Any]:
    if not DAILY_FILE.exists():
        return {}
    try:
        data = json.loads(DAILY_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def save_best_table(table: dict[str, Any]) -> None:
    STATS_DIR.mkdir(parents=True, exist_ok=True)
    DAILY_FILE.write_text(json.dumps(table, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
