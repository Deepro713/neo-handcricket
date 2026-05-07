"""Career stats — append-only JSON log of completed matches."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from ..config import STATS_DIR
from ..match import Match


STATS_DIR.mkdir(parents=True, exist_ok=True)
CAREER_FILE = STATS_DIR / "career.json"


def _read_career() -> dict:
    if not CAREER_FILE.exists():
        return {"matches": []}
    try:
        return json.loads(CAREER_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"matches": []}


def _write_career(data: dict) -> None:
    CAREER_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def record_match(match: Match) -> None:
    if match.phase != "complete":
        return
    data = _read_career()
    summary = {
        "completed_at": datetime.now().isoformat(timespec="seconds"),
        "format": match.fmt.name,
        "difficulty": match.difficulty,
        "user_team": match.user_team.country,
        "opponent": match.opponent.country,
        "winner": match.winner,
        "result": match.result_summary,
        "player_of_the_match": match.player_of_the_match,
        "pom_team": match.pom_team,
        "innings": [
            {
                "batting": inn.batting_country,
                "bowling": inn.bowling_country,
                "runs": inn.runs,
                "wickets": inn.wickets,
                "overs": inn.overs_string,
            }
            for inn in match.innings_list
        ],
    }
    data.setdefault("matches", []).append(summary)
    _write_career(data)


def read_stats() -> dict:
    return _read_career()
