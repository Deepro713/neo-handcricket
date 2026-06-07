"""Save / load match state.

Auto-save (rolling) at saves/auto.json — replaced after each over end.
Manual saves at saves/<name>.json — persistent until user deletes.
"""
from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from ..config import SAVE_SCHEMA_VERSION, SAVES_DIR
from ..formats import PRESETS, Format
from ..innings import BallEvent, BatterCard, BowlerCard, Innings
from ..match import Match, TeamMeta

SAVES_DIR.mkdir(parents=True, exist_ok=True)


def _path(name: str) -> Path:
    safe = "".join(c for c in name if c.isalnum() or c in ("-", "_")) or "save"
    return SAVES_DIR / f"{safe}.json"


def list_saves() -> list[dict]:
    """Return [{'name', 'path', 'mtime', 'meta'}, ...]"""
    out = []
    for p in sorted(SAVES_DIR.glob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            meta = {
                "user_team": data.get("user_team", {}).get("country"),
                "opponent": data.get("opponent", {}).get("country"),
                "format": data.get("fmt", {}).get("name"),
                "phase": data.get("phase"),
                "created_at": data.get("created_at"),
            }
        except Exception:
            meta = {}
        out.append({
            "name": p.stem,
            "path": str(p),
            "mtime": datetime.fromtimestamp(p.stat().st_mtime).isoformat(timespec="seconds"),
            "meta": meta,
        })
    return out


def save_match(match: Match, *, name: str = "auto") -> Path:
    data = _serialize_match(match)
    path = _path(name)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def load_match(name: str) -> Match:
    path = _path(name)
    raw = json.loads(path.read_text(encoding="utf-8"))
    return _deserialize_match(raw)


def delete_save(name: str) -> bool:
    path = _path(name)
    if path.exists():
        path.unlink()
        return True
    return False


# ----- (de)serialization -----

def _serialize_match(match: Match) -> dict:
    return {
        "schema_version": SAVE_SCHEMA_VERSION,
        "created_at": match.created_at,
        "user_team": asdict(match.user_team),
        "opponent": asdict(match.opponent),
        "user_xi": list(match.user_xi),
        "opponent_xi": list(match.opponent_xi),
        "user_bowling_pool": list(match.user_bowling_pool),
        "opponent_bowling_pool": list(match.opponent_bowling_pool),
        "fmt": asdict(match.fmt),
        "difficulty": match.difficulty,
        "user_batting_first": match.user_batting_first,
        "phase": match.phase,
        "innings_list": [_serialize_innings(i) for i in match.innings_list],
        "super_over_innings": [_serialize_innings(i) for i in match.super_over_innings],
        "winner": match.winner,
        "result_summary": match.result_summary,
        "player_of_the_match": match.player_of_the_match,
        "pom_team": match.pom_team,
    }


def _serialize_innings(inn: Innings) -> dict:
    d = {
        "batting_country": inn.batting_country,
        "bowling_country": inn.bowling_country,
        "batting_xi": inn.batting_xi,
        "bowling_xi": inn.bowling_xi,
        "bowling_pool": inn.bowling_pool,
        "overs_limit": inn.overs_limit,
        "wickets_limit": inn.wickets_limit,
        "target": inn.target,
        "runs": inn.runs,
        "extras": inn.extras,
        "wickets": inn.wickets,
        "balls": inn.balls,
        "striker_idx": inn.striker_idx,
        "nonstriker_idx": inn.nonstriker_idx,
        "next_batter_idx": inn.next_batter_idx,
        "current_bowler_id": inn.current_bowler_id,
        "current_over_balls": inn.current_over_balls,
        "current_over_runs": inn.current_over_runs,
        "current_over_results": inn.current_over_results,
        "batter_cards": {pid: asdict(c) for pid, c in inn.batter_cards.items()},
        "bowler_cards": {pid: asdict(c) for pid, c in inn.bowler_cards.items()},
        "ball_log": [asdict(e) for e in inn.ball_log],
    }
    return d


def _deserialize_innings(d: dict) -> Innings:
    inn = Innings(
        batting_country=d["batting_country"],
        bowling_country=d["bowling_country"],
        batting_xi=list(d["batting_xi"]),
        bowling_xi=list(d["bowling_xi"]),
        bowling_pool=list(d["bowling_pool"]),
        overs_limit=d["overs_limit"],
        wickets_limit=d["wickets_limit"],
        target=d.get("target"),
        runs=d["runs"],
        extras=d["extras"],
        wickets=d["wickets"],
        balls=d["balls"],
        striker_idx=d["striker_idx"],
        nonstriker_idx=d["nonstriker_idx"],
        next_batter_idx=d["next_batter_idx"],
        current_bowler_id=d.get("current_bowler_id"),
        current_over_balls=d.get("current_over_balls", 0),
        current_over_runs=d.get("current_over_runs", 0),
        current_over_results=list(d.get("current_over_results", [])),
    )
    inn.batter_cards = {int(k): BatterCard(**v) for k, v in d.get("batter_cards", {}).items()}
    inn.bowler_cards = {int(k): BowlerCard(**v) for k, v in d.get("bowler_cards", {}).items()}
    inn.ball_log = [BallEvent(**e) for e in d.get("ball_log", [])]
    return inn


def _deserialize_match(d: dict) -> Match:
    fmt_d = d["fmt"]
    if fmt_d["name"] in PRESETS:
        fmt = PRESETS[fmt_d["name"]]
    else:
        fmt = Format(**fmt_d)

    user_team = TeamMeta(**d["user_team"])
    opp = TeamMeta(**d["opponent"])

    m = Match(
        user_team=user_team,
        opponent=opp,
        user_xi=list(d["user_xi"]),
        opponent_xi=list(d["opponent_xi"]),
        user_bowling_pool=list(d["user_bowling_pool"]),
        opponent_bowling_pool=list(d["opponent_bowling_pool"]),
        fmt=fmt,
        difficulty=d.get("difficulty", "medium"),
        user_batting_first=d["user_batting_first"],
        phase=d["phase"],
        innings_list=[_deserialize_innings(i) for i in d.get("innings_list", [])],
        super_over_innings=[_deserialize_innings(i) for i in d.get("super_over_innings", [])],
        winner=d.get("winner"),
        result_summary=d.get("result_summary"),
        player_of_the_match=d.get("player_of_the_match"),
        pom_team=d.get("pom_team"),
        created_at=d.get("created_at", datetime.now().isoformat(timespec="seconds")),
    )
    return m
