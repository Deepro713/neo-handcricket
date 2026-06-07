"""Scoreboard rendering — compact (in-over) and detailed (end-of-over)."""
from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ..bots import matchstate
from ..innings import Innings
from ..match import Match
from ..rosters.loader import Country, Player


def _name_for(country: Country, pid: int) -> str:
    try:
        return country.player(pid).name
    except KeyError:
        return f"#{pid}"


def _settled_marker(balls_faced: int) -> str:
    """A small glyph showing how 'in' a batter is, from balls faced (M005)."""
    s = matchstate.settledness(balls_faced)
    if s >= 0.6:
        return " ★"      # set
    if s >= 0.3:
        return " ·"      # getting in
    return ""            # new at the crease


def render_compact(console: Console, match: Match) -> None:
    inn = match.current_innings
    if inn is None:
        return
    # Determine teams in context
    bat_country = match.user_team if inn.batting_country == match.user_team.country else match.opponent
    bowl_country = match.opponent if bat_country is match.user_team else match.user_team

    bat_country_obj = _country_from_meta(bat_country)
    bowl_country_obj = _country_from_meta(bowl_country)

    # Header
    header = Text()
    header.append(f"{match.fmt.name}  ", style="bold cyan")
    header.append(f"{bat_country.flag} {bat_country.country}", style="bold")
    header.append(" vs ", style="dim")
    header.append(f"{bowl_country.flag} {bowl_country.country}", style="bold")
    header.append(f"   Diff: {match.difficulty}", style="dim")

    # Score line
    score = Text()
    score.append(f"{bat_country.country}: ", style="bold")
    score.append(f"{inn.runs}/{inn.wickets}", style="bold yellow")
    score.append(f"  ({inn.overs_string}", style="dim")
    if inn.overs_limit:
        score.append(f" / {inn.overs_limit}", style="dim")
    score.append(" ov)", style="dim")
    if inn.target is not None:
        needed = inn.runs_needed
        balls_left = inn.balls_remaining
        score.append(f"   Target: {inn.target}", style="green")
        if needed is not None and needed > 0 and balls_left:
            score.append(f"   need {needed} off {balls_left}", style="green")

    # Batsmen on crease
    striker = bat_country_obj.player(inn.striker_id) if inn.striker_id in [p.id for p in bat_country_obj.players] else None
    nonstriker = bat_country_obj.player(inn.nonstriker_id) if inn.nonstriker_id in [p.id for p in bat_country_obj.players] else None
    striker_card = inn.batter_cards.get(inn.striker_id)
    nonstriker_card = inn.batter_cards.get(inn.nonstriker_id)

    bat_table = Table.grid(padding=(0, 2))
    bat_table.add_column()
    bat_table.add_column()
    bat_table.add_column(justify="right", style="dim")
    if striker and striker_card:
        bat_table.add_row(
            Text("► " + striker.name + _settled_marker(striker_card.balls), style="bold"),
            Text(f"{striker_card.runs}({striker_card.balls})", style="yellow"),
            Text(f"4s:{striker_card.fours}  6s:{striker_card.sixes}"),
        )
    if nonstriker and nonstriker_card:
        bat_table.add_row(
            Text("  " + nonstriker.name + _settled_marker(nonstriker_card.balls)),
            Text(f"{nonstriker_card.runs}({nonstriker_card.balls})"),
            Text(f"4s:{nonstriker_card.fours}  6s:{nonstriker_card.sixes}"),
        )

    # Current bowler
    bowler_table = Table.grid(padding=(0, 2))
    bowler_table.add_column()
    bowler_table.add_column(justify="right", style="dim")
    if inn.current_bowler_id is not None:
        bowler = _safe_player(bowl_country_obj, inn.current_bowler_id)
        bcard = inn.bowler_cards.get(inn.current_bowler_id)
        if bowler and bcard:
            bowler_table.add_row(
                Text("Bowler: " + bowler.name, style="bold"),
                Text(f"{bcard.overs} ov   {bcard.runs_conceded}/{bcard.wickets}"),
            )

    # This over
    this_over = " ".join(inn.current_over_results) if inn.current_over_results else "—"
    over_text = Text()
    over_text.append("This over: ", style="dim")
    over_text.append(this_over, style="bold")

    panel_content = Text()
    panel_content.append(score)
    panel_content.append("\n\n")
    console.print(Panel(panel_content, title=header, border_style="cyan", padding=(0, 1)))
    console.print(bat_table)
    if inn.current_bowler_id is not None:
        console.print(bowler_table)
    console.print(over_text)


def render_detailed(console: Console, match: Match, innings: Innings | None = None) -> None:
    """Full scorecard for an innings."""
    inn = innings or match.current_innings
    if inn is None:
        return
    bat_country = match.user_team if inn.batting_country == match.user_team.country else match.opponent
    bowl_country = match.opponent if bat_country is match.user_team else match.user_team
    bat_country_obj = _country_from_meta(bat_country)
    bowl_country_obj = _country_from_meta(bowl_country)

    # Batting card
    bat_t = Table(title=f"{bat_country.flag} {bat_country.country} — {inn.runs}/{inn.wickets} ({inn.overs_string} ov)", show_lines=False)
    bat_t.add_column("Batter")
    bat_t.add_column("Runs", justify="right")
    bat_t.add_column("Balls", justify="right")
    bat_t.add_column("4s", justify="right")
    bat_t.add_column("6s", justify="right")
    bat_t.add_column("SR", justify="right")
    bat_t.add_column("Status", style="dim")

    seen_ids = set()
    for pid in inn.batting_xi:
        if pid in seen_ids:
            continue
        seen_ids.add(pid)
        c = inn.batter_cards.get(pid)
        if c is None:
            continue
        if c.balls == 0 and c.runs == 0 and c.out_to is None:
            status = "did not bat"
        else:
            status = (c.out_to or "not out") if c.out_to else "not out"
        try:
            name = bat_country_obj.player(pid).name
        except KeyError:
            name = f"#{pid}"
        if c.runs >= 100:
            name += " 💯"
        elif c.runs >= 50:
            name += " ★"
        bat_t.add_row(
            name,
            str(c.runs),
            str(c.balls),
            str(c.fours),
            str(c.sixes),
            f"{c.strike_rate:.1f}",
            status,
        )
    extras = inn.extras
    bat_t.add_row("Extras", str(extras), "—", "—", "—", "—", "")
    bat_t.add_row("Total", f"{inn.runs}", "—", "—", "—", "—", f"({inn.wickets} wkts, {inn.overs_string} ov)")

    console.print(bat_t)

    # Bowling card
    bowl_t = Table(title=f"{bowl_country.flag} {bowl_country.country} — bowling", show_lines=False)
    bowl_t.add_column("Bowler")
    bowl_t.add_column("Ov", justify="right")
    bowl_t.add_column("M", justify="right")
    bowl_t.add_column("R", justify="right")
    bowl_t.add_column("W", justify="right")
    bowl_t.add_column("Econ", justify="right")
    for pid, bc in inn.bowler_cards.items():
        if bc.balls == 0:
            continue
        try:
            name = bowl_country_obj.player(pid).name
        except KeyError:
            name = f"#{pid}"
        bowl_t.add_row(
            name,
            bc.overs,
            str(bc.maidens),
            str(bc.runs_conceded),
            str(bc.wickets),
            f"{bc.economy:.2f}",
        )
    console.print(bowl_t)


def render_match_summary(console: Console, match: Match) -> None:
    if not match.result_summary:
        return
    title = Text(match.result_summary, style="bold green" if match.winner == "user" else "bold yellow")
    console.print(Panel(title, border_style="green" if match.winner == "user" else "yellow"))
    if match.player_of_the_match is not None and match.pom_team:
        team = match.user_team if match.pom_team == "user" else match.opponent
        try:
            country = _country_from_meta(team)
            name = country.player(match.player_of_the_match).name
        except KeyError:
            name = f"#{match.player_of_the_match}"
        console.print(Text(f"🏅 Player of the Match: {name} ({team.country})", style="bold magenta"))

    # Highlights reel from the accumulated event stream (M007).
    reel = _match_highlights(match)
    if reel:
        console.print(Text("\n  Highlights", style="bold cyan"))
        for line in reel:
            console.print(Text(f"   • {line}", style="dim"))


def _match_highlights(match: Match) -> list[str]:
    from ..commentary.highlights import build_highlights

    def name_of(pid: int) -> str:
        for meta in (match.user_team, match.opponent):
            try:
                return _country_from_meta(meta).player(pid).name
            except KeyError:
                continue
        return f"#{pid}"

    return build_highlights(match.highlight_events, name_of)


# helpers ----

def _safe_player(country: Country, pid: int) -> Player | None:
    try:
        return country.player(pid)
    except KeyError:
        return None


def _country_from_meta(meta) -> Country:
    """Build a Country object from a TeamMeta (which carries raw dicts)."""
    from ..rosters.loader import _player_from_dict
    return Country(
        country=meta.country,
        flag=meta.flag,
        naming_convention=meta.naming_convention,
        players=[_player_from_dict(p) for p in meta.players],
        staff=meta.staff,
        slug=meta.country.lower().replace(" ", "-"),
    )
