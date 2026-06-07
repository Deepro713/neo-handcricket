"""Career stats — append-only JSON log of completed matches."""
from __future__ import annotations

import json
from datetime import datetime

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
    # Per-player batting + bowling rollups for this match (top batter / wicket-taker per innings)
    per_player_batting: list[dict] = []
    per_player_bowling: list[dict] = []
    for inn in match.innings_list:
        for pid, c in inn.batter_cards.items():
            if c.balls == 0 and c.runs == 0 and c.out_to is None:
                continue
            team = "user" if inn.batting_country == match.user_team.country else "opponent"
            per_player_batting.append({
                "player_id": pid,
                "team": team,
                "country": inn.batting_country,
                "runs": c.runs,
                "balls": c.balls,
                "fours": c.fours,
                "sixes": c.sixes,
                "out_to": c.out_to,
            })
        for pid, b in inn.bowler_cards.items():
            if b.balls == 0:
                continue
            team = "user" if inn.bowling_country == match.user_team.country else "opponent"
            per_player_bowling.append({
                "player_id": pid,
                "team": team,
                "country": inn.bowling_country,
                "balls": b.balls,
                "runs_conceded": b.runs_conceded,
                "wickets": b.wickets,
                "maidens": b.maidens,
            })
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
        "per_player_batting": per_player_batting,
        "per_player_bowling": per_player_bowling,
    }
    data.setdefault("matches", []).append(summary)
    _write_career(data)


def read_stats() -> dict:
    return _read_career()


def aggregate() -> dict:
    """Compute career aggregates from the recorded match log."""
    data = _read_career()
    matches = data.get("matches", [])
    out: dict = {
        "total_matches": len(matches),
        "by_format": {},
        "wins": 0, "losses": 0, "draws": 0, "ties": 0,
        "highest_team_total": None,
        "highest_individual": None,
        "top_run_scorers": [],     # user team only
        "top_wicket_takers": [],   # user team only
        "head_to_head": {},
        "pom_count": 0,
        "longest_winning_streak": 0,
    }
    for m in matches:
        fmt = m.get("format", "?")
        out["by_format"].setdefault(fmt, {"played": 0, "wins": 0, "losses": 0, "draws": 0, "ties": 0})
        out["by_format"][fmt]["played"] += 1
        winner = m.get("winner")
        if winner == "user":
            out["wins"] += 1
            out["by_format"][fmt]["wins"] += 1
        elif winner == "opponent":
            out["losses"] += 1
            out["by_format"][fmt]["losses"] += 1
        elif winner == "tie":
            out["ties"] += 1
            out["by_format"][fmt]["ties"] += 1
        elif winner == "draw":
            out["draws"] += 1
            out["by_format"][fmt]["draws"] += 1

        # Highest team total
        for inn in m.get("innings", []):
            cand = (inn.get("runs", 0), inn.get("batting", "?"), m.get("format", "?"))
            if out["highest_team_total"] is None or cand[0] > out["highest_team_total"][0]:
                out["highest_team_total"] = cand

        # Head-to-head
        opp = m.get("opponent", "?")
        h2h = out["head_to_head"].setdefault(opp, {"wins": 0, "losses": 0, "draws": 0, "ties": 0})
        if winner == "user":
            h2h["wins"] += 1
        elif winner == "opponent":
            h2h["losses"] += 1
        elif winner == "tie":
            h2h["ties"] += 1
        elif winner == "draw":
            h2h["draws"] += 1

        if m.get("pom_team") == "user":
            out["pom_count"] += 1

        # Per-player rollup (user team only)
        for entry in m.get("per_player_batting", []):
            if entry.get("team") == "user":
                out_runs = entry.get("runs", 0)
                cand_indiv = (out_runs, entry.get("player_id"), entry.get("country"), m.get("format"))
                if out["highest_individual"] is None or cand_indiv[0] > out["highest_individual"][0]:
                    out["highest_individual"] = cand_indiv

    # Top run-scorers / wicket-takers (cumulative across user-team appearances)
    bat_totals: dict[int, dict] = {}
    bowl_totals: dict[int, dict] = {}
    for m in matches:
        for entry in m.get("per_player_batting", []):
            if entry.get("team") != "user":
                continue
            pid = entry["player_id"]
            agg = bat_totals.setdefault(pid, {"player_id": pid, "country": entry.get("country"), "runs": 0, "balls": 0, "matches": 0})
            agg["runs"] += entry.get("runs", 0)
            agg["balls"] += entry.get("balls", 0)
            agg["matches"] += 1
        for entry in m.get("per_player_bowling", []):
            if entry.get("team") != "user":
                continue
            pid = entry["player_id"]
            agg = bowl_totals.setdefault(pid, {"player_id": pid, "country": entry.get("country"), "wickets": 0, "runs_conceded": 0, "balls": 0, "matches": 0})
            agg["wickets"] += entry.get("wickets", 0)
            agg["runs_conceded"] += entry.get("runs_conceded", 0)
            agg["balls"] += entry.get("balls", 0)
            agg["matches"] += 1
    out["top_run_scorers"] = sorted(bat_totals.values(), key=lambda x: -x["runs"])[:10]
    out["top_wicket_takers"] = sorted(bowl_totals.values(), key=lambda x: -x["wickets"])[:10]

    # Longest winning streak
    streak = best = 0
    for m in matches:
        if m.get("winner") == "user":
            streak += 1
            best = max(best, streak)
        else:
            streak = 0
    out["longest_winning_streak"] = best
    return out
