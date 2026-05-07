"""Top-level orchestration — pre-match flow + innings loop."""
from __future__ import annotations

import random
import sys
from dataclasses import asdict
from typing import Literal

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .bots import captain as cap_ai
from .bots import strategy
from .commentary.engine import CommentaryEngine
from .config import EXTRAS_BASE_PCT, TIMER_SECONDS
from .formats import Format, custom as custom_fmt
from .innings import Innings
from .match import Match, TeamMeta
from .persistence import save as save_io
from .persistence import stats as stats_io
from .rosters import loader, selector
from .toss import perform_toss, machine_picks_bat_or_bowl
from .ui import cli as ui_cli
from .ui import overlay as ui_overlay
from .ui import prompts as ui_prompts
from .ui import scoreboard as ui_scoreboard
from .ui.input import beep, read_key, read_key_with_timer


# -----------------------------------------------------------------------------
# pre-match flow
# -----------------------------------------------------------------------------

def _team_meta_from_country(c: loader.Country) -> TeamMeta:
    return TeamMeta(
        country=c.country,
        flag=c.flag,
        naming_convention=c.naming_convention,
        players=[asdict_minimal(p) for p in c.players],
        staff=list(c.staff),
    )


def asdict_minimal(p: loader.Player) -> dict:
    return {
        "id": p.id,
        "name": p.name,
        "role": p.role,
        "batting_hand": p.batting_hand,
        "bowling_style": p.bowling_style,
        "batting_archetype": p.batting_archetype,
        "bowling_archetype": p.bowling_archetype,
    }


def _new_match_flow(console: Console) -> Match | None:
    console.clear()
    user_slug = ui_prompts.select_country(console, prompt="Pick YOUR country")
    user_country = loader.load_country(user_slug)
    opp_slug = ui_prompts.select_country(console, prompt="Pick OPPONENT country", exclude=user_slug)
    opp_country = loader.load_country(opp_slug)

    fmt = ui_prompts.select_format(console)
    diff = ui_prompts.select_difficulty(console)

    rng = random.Random()

    # System-pick the playing XI for both
    user_sel = selector.select_xi(user_country, fmt, rng=rng)
    opp_sel = selector.select_xi(opp_country, fmt, rng=rng)

    match = Match(
        user_team=_team_meta_from_country(user_country),
        opponent=_team_meta_from_country(opp_country),
        user_xi=[p.id for p in user_sel.playing_xi],
        opponent_xi=[p.id for p in opp_sel.playing_xi],
        user_bowling_pool=[p.id for p in user_sel.bowling_pool],
        opponent_bowling_pool=[p.id for p in opp_sel.bowling_pool],
        fmt=fmt,
        difficulty=diff,
    )

    # Toss
    _do_toss(console, match)

    return match


def _do_toss(console: Console, match: Match) -> None:
    console.clear()
    console.print(Panel(Text("The Toss", style="bold cyan"), border_style="cyan"))
    console.print("  Call it: [yellow]h[/yellow]eads / [yellow]t[/yellow]ails  (or any key for heads)")
    ch = read_key().lower()
    user_call = "tails" if ch == "t" else "heads"
    console.print(f"  You called: [bold]{user_call}[/bold]")
    console.print("  Press any key to flip the coin...")
    read_key()

    result = perform_toss(user_call)
    for ev in result.events:
        if ev.kind == "retoss":
            console.print(Panel(Text(f"⚠  {ev.excuse}", style="italic yellow"), border_style="yellow"))
            console.print("  Press any key to retoss...")
            read_key()
        elif ev.kind == "fallback":
            console.print(Panel(Text(f"…{ev.excuse}", style="italic"), border_style="dim"))
        else:
            console.print(f"  Coin: [bold]{ev.face}[/bold]")
    if result.user_won:
        console.print("[green]  You won the toss![/green]")
        choice = ui_prompts.choose_bat_or_bowl(console)
        match.user_batting_first = (choice == "bat")
    else:
        console.print("[yellow]  You lost the toss.[/yellow]")
        bot_choice: Literal["bat", "bowl"] = machine_picks_bat_or_bowl()
        console.print(f"  Computer chose to [bold]{bot_choice}[/bold] first.")
        # If bot bats first, user is bowling first — so user_batting_first = False
        match.user_batting_first = (bot_choice == "bowl")
    console.print("  Press any key to start the match...")
    read_key()


# -----------------------------------------------------------------------------
# innings runner
# -----------------------------------------------------------------------------

def _build_innings(
    *,
    match: Match,
    batting_country: TeamMeta,
    bowling_country: TeamMeta,
    batting_xi: list[int],
    bowling_xi: list[int],
    bowling_pool: list[int],
    target: int | None = None,
    overs_override: int | None = None,
    wickets_override: int | None = None,
) -> Innings:
    fmt = match.fmt
    return Innings(
        batting_country=batting_country.country,
        bowling_country=bowling_country.country,
        batting_xi=list(batting_xi),
        bowling_xi=list(bowling_xi),
        bowling_pool=list(bowling_pool),
        overs_limit=overs_override if overs_override is not None else fmt.overs_per_innings,
        wickets_limit=wickets_override if wickets_override is not None else fmt.wickets_per_innings,
        target=target,
    )


def _country_obj_from_meta(meta: TeamMeta) -> loader.Country:
    return loader.Country(
        country=meta.country,
        flag=meta.flag,
        naming_convention=meta.naming_convention,
        players=[loader._player_from_dict(p) for p in meta.players],
        staff=meta.staff,
        slug=meta.country.lower().replace(" ", "-"),
    )


def _bot_archetypes_for_pool(pool: list[int], country: loader.Country) -> dict[int, str]:
    out = {}
    for pid in pool:
        try:
            p = country.player(pid)
            if p.bowling_archetype:
                out[pid] = p.bowling_archetype
        except KeyError:
            pass
    return out


def _user_picks_bowler(console: Console, *, pool: list[int], country: loader.Country, over_counts: dict[int, int], cap: int | None, last_bowler: int | None) -> int:
    """Prompt the user to pick a bowler for this over."""
    console.print(Panel(Text("Pick your bowler for this over", style="bold"), border_style="cyan"))
    eligible = [
        pid for pid in pool
        if (cap is None or over_counts.get(pid, 0) < cap) and pid != last_bowler
    ]
    if not eligible:
        eligible = [pid for pid in pool if cap is None or over_counts.get(pid, 0) < cap]
    if not eligible:
        eligible = pool
    for i, pid in enumerate(eligible, 1):
        try:
            p = country.player(pid)
            cap_str = f"{over_counts.get(pid, 0)}/{cap}" if cap else f"{over_counts.get(pid, 0)} ov"
            console.print(f"  [yellow]{i}[/yellow]  {p.name}  [dim]({p.bowling_style or 'bowls'}, {cap_str})[/dim]")
        except KeyError:
            pass
    while True:
        ch = read_key()
        if ch.isdigit() and 1 <= int(ch) <= len(eligible):
            return eligible[int(ch) - 1]


def _resolve_ball_outcome_bot_bowling(
    *,
    user_pick: int | None,           # None means timeout
    bot_pick: int,                    # bot's chosen number
    bowler_archetype: str,
    rng: random.Random,
) -> dict:
    """Return a dict with: runs, extras, wicket, extra_kind, timed_out."""
    if user_pick is None:
        outcome = strategy.roll_timeout_bot_bowling(rng)
        return _outcome_from_timeout_bot(outcome)

    # 5% (modulated) base extras roll
    is_extra, kind = strategy.pick_extras_outcome(archetype=bowler_archetype, base_pct=EXTRAS_BASE_PCT, rng=rng)
    if is_extra and kind == "wide":
        return {"runs": 0, "extras": 1, "wicket": None, "extra_kind": "wide", "timed_out": False}
    if is_extra and kind == "no-ball":
        return {"runs": user_pick, "extras": 1, "wicket": None, "extra_kind": "no-ball", "timed_out": False}

    # Normal play: match → wicket; else runs = user_pick
    if user_pick == bot_pick:
        return {"runs": 0, "extras": 0, "wicket": "match", "extra_kind": None, "timed_out": False}
    return {"runs": user_pick, "extras": 0, "wicket": None, "extra_kind": None, "timed_out": False}


def _resolve_ball_outcome_user_bowling(
    *,
    user_pick: int | None,           # user's bowling number
    bot_pick: int,                    # bot batsman's number
    bowler_archetype: str,
    rng: random.Random,
) -> dict:
    """Return a dict with the same shape as above."""
    if user_pick is None:
        outcome = strategy.roll_timeout_user_bowling(rng)
        return _outcome_from_timeout_user(outcome)

    is_extra, kind = strategy.pick_extras_outcome(archetype=bowler_archetype, base_pct=EXTRAS_BASE_PCT, rng=rng)
    if is_extra and kind == "wide":
        return {"runs": 0, "extras": 1, "wicket": None, "extra_kind": "wide", "timed_out": False}
    if is_extra and kind == "no-ball":
        return {"runs": bot_pick, "extras": 1, "wicket": None, "extra_kind": "no-ball", "timed_out": False}

    if user_pick == bot_pick:
        return {"runs": 0, "extras": 0, "wicket": "match", "extra_kind": None, "timed_out": False}
    return {"runs": bot_pick, "extras": 0, "wicket": None, "extra_kind": None, "timed_out": False}


def _outcome_from_timeout_bot(outcome: str) -> dict:
    if outcome == "dot":
        return {"runs": 0, "extras": 0, "wicket": None, "extra_kind": None, "timed_out": True}
    if outcome == "wide":
        return {"runs": 0, "extras": 1, "wicket": None, "extra_kind": "wide", "timed_out": True}
    if outcome == "bowled":
        return {"runs": 0, "extras": 0, "wicket": "bowled", "extra_kind": None, "timed_out": True}
    if outcome == "lbw":
        return {"runs": 0, "extras": 0, "wicket": "lbw", "extra_kind": None, "timed_out": True}
    if outcome == "dead-ball":
        return {"runs": 0, "extras": 0, "wicket": None, "extra_kind": "dead-ball", "timed_out": True}
    return {"runs": 0, "extras": 0, "wicket": None, "extra_kind": None, "timed_out": True}


def _outcome_from_timeout_user(outcome: str) -> dict:
    if outcome == "wide":
        return {"runs": 0, "extras": 1, "wicket": None, "extra_kind": "wide", "timed_out": True}
    if outcome == "no-ball":
        return {"runs": 0, "extras": 1, "wicket": None, "extra_kind": "no-ball", "timed_out": True}
    if outcome == "byes":
        return {"runs": 0, "extras": 1, "wicket": None, "extra_kind": "byes", "timed_out": True}
    if outcome == "leg-byes":
        return {"runs": 0, "extras": 1, "wicket": None, "extra_kind": "leg-byes", "timed_out": True}
    if outcome == "dead-ball":
        return {"runs": 0, "extras": 0, "wicket": None, "extra_kind": "dead-ball", "timed_out": True}
    return {"runs": 0, "extras": 0, "wicket": None, "extra_kind": None, "timed_out": True}


def _commentary_ctx(*, match: Match, inn: Innings, runs: int, wicket: str | None, extras: int, extra_kind: str | None, batter_name: str, bowler_name: str) -> dict:
    return {
        "batter": batter_name,
        "bowler": bowler_name,
        "runs": runs,
        "extras": extras,
        "wicket_kind": wicket,
        "extra_kind": extra_kind,
        "score": f"{inn.runs}/{inn.wickets}",
        "wickets": inn.wickets,
        "over": inn.overs_string,
        "over_num": inn.overs_completed,
        "ball_in_over": inn.current_over_balls,
        "country": inn.batting_country,
        "opponent": inn.bowling_country,
        "batting_country": inn.batting_country,
        "bowling_country": inn.bowling_country,
        "striker_id": inn.striker_id,
        "bowler_id": inn.current_bowler_id,
        "batter_runs": inn.batter_cards.get(inn.striker_id).runs if inn.striker_id in inn.batter_cards else 0,
        "result_summary": match.result_summary or "",
    }


def _run_innings(
    console: Console,
    match: Match,
    engine: CommentaryEngine,
    inn: Innings,
    *,
    user_is_batting: bool,
) -> None:
    """Run one innings end-to-end."""
    rng = random.Random()
    user_country_obj = _country_obj_from_meta(match.user_team)
    opp_country_obj = _country_obj_from_meta(match.opponent)

    if user_is_batting:
        bowling_country_obj = opp_country_obj
        batting_country_obj = user_country_obj
    else:
        bowling_country_obj = user_country_obj
        batting_country_obj = opp_country_obj

    over_counts: dict[int, int] = {}
    bowler_economies: dict[int, float] = {}
    last_bowler: int | None = None

    user_recent_bowling_picks: list[int] = []   # user's bowling picks (when user is bowler)
    user_recent_batting_picks: list[int] = []   # user's batting picks (when user is batter)

    fmt = match.fmt
    total_overs = inn.overs_limit

    while not inn.is_complete:
        # Pick bowler
        archetypes = _bot_archetypes_for_pool(inn.bowling_pool, bowling_country_obj)
        if user_is_batting:
            # Bot picks bowler
            bowler_id = cap_ai.pick_next_bowler(
                bowling_pool=inn.bowling_pool,
                archetypes=archetypes,
                over_counts=over_counts,
                economies=bowler_economies,
                last_bowler=last_bowler,
                over_idx=inn.overs_completed,
                total_overs=total_overs,
                fmt=fmt,
                rng=rng,
            )
        else:
            bowler_id = _user_picks_bowler(
                console,
                pool=inn.bowling_pool,
                country=bowling_country_obj,
                over_counts=over_counts,
                cap=fmt.bowler_over_cap,
                last_bowler=last_bowler,
            )

        inn.start_over(bowler_id)
        try:
            bowler = bowling_country_obj.player(bowler_id)
        except KeyError:
            bowler = None
        if bowler:
            ui_overlay.show_bowler_card(console, bowler, inn.overs_completed, bowling_country_obj.country)

        antarctica_on_field = (
            inn.batting_country == "Antarctica" or inn.bowling_country == "Antarctica"
        )

        # Per-ball loop within the over
        while True:
            if inn.is_complete:
                break

            # End-of-over check (legal-ball count)
            if inn.current_over_balls >= 6:
                break

            ui_cli.render_frame(console, match, engine)

            try:
                striker = batting_country_obj.player(inn.striker_id)
            except KeyError:
                striker = None
            try:
                bowler_p = bowling_country_obj.player(inn.current_bowler_id) if inn.current_bowler_id is not None else None
            except KeyError:
                bowler_p = None
            batter_name = striker.name if striker else f"#{inn.striker_id}"
            bowler_name = bowler_p.name if bowler_p else f"#{inn.current_bowler_id}"

            if user_is_batting:
                # Bot bowls (bot picks number, user picks number with timer)
                bowler_arch = bowler_p.bowling_archetype if bowler_p and bowler_p.bowling_archetype else "pace"
                bot_pick = strategy.pick_number(
                    archetype=bowler_arch,
                    is_bowler=True,
                    recent_user_picks=user_recent_batting_picks,
                    difficulty=match.difficulty,
                    over_number=inn.overs_completed,
                    rng=rng,
                )
                # Prompt user
                prompt_text = f"BAT — pick 0–6  ({batter_name})"
                beep()
                user_ch = read_key_with_timer(
                    TIMER_SECONDS,
                    tick=lambda r: ui_cli.update_prompt_line(prompt_text, r),
                )
                ui_cli.newline()
                user_pick: int | None = None
                if user_ch and user_ch.isdigit():
                    n = int(user_ch)
                    if 0 <= n <= 6:
                        user_pick = n
                        user_recent_batting_picks.append(n)
                outcome = _resolve_ball_outcome_bot_bowling(
                    user_pick=user_pick,
                    bot_pick=bot_pick,
                    bowler_archetype=bowler_arch,
                    rng=rng,
                )
            else:
                # User bowls (user picks number, bot batsman picks number)
                bot_arch = "tail-ender"
                if striker and striker.batting_archetype:
                    bot_arch = striker.batting_archetype
                bot_pick = strategy.pick_number(
                    archetype=bot_arch,
                    is_bowler=False,
                    recent_user_picks=user_recent_bowling_picks,
                    difficulty=match.difficulty,
                    over_number=inn.overs_completed,
                    rng=rng,
                )
                prompt_text = f"BOWL — pick 0–6  (vs {batter_name})"
                beep()
                user_ch = read_key_with_timer(
                    TIMER_SECONDS,
                    tick=lambda r: ui_cli.update_prompt_line(prompt_text, r),
                )
                ui_cli.newline()
                user_pick = None
                if user_ch and user_ch.isdigit():
                    n = int(user_ch)
                    if 0 <= n <= 6:
                        user_pick = n
                        user_recent_bowling_picks.append(n)
                # User-team's bowler archetype for extras modifier
                user_bowler_arch = "pace"
                try:
                    user_bowler = user_country_obj.player(bowler_id)
                    if user_bowler.bowling_archetype:
                        user_bowler_arch = user_bowler.bowling_archetype
                except KeyError:
                    pass
                outcome = _resolve_ball_outcome_user_bowling(
                    user_pick=user_pick,
                    bot_pick=bot_pick,
                    bowler_archetype=user_bowler_arch,
                    rng=rng,
                )

            event = inn.record_ball(
                runs=outcome["runs"],
                extras=outcome["extras"],
                wicket=outcome["wicket"],
                extra_kind=outcome["extra_kind"],
                timed_out=outcome["timed_out"],
            )

            # Update bowler economy
            bcard = inn.bowler_cards.get(inn.current_bowler_id)
            if bcard and bcard.balls > 0:
                bowler_economies[inn.current_bowler_id] = bcard.economy

            # Commentary
            from .commentary.lines import situation_for_ball
            situation = situation_for_ball(
                runs=outcome["runs"],
                wicket_kind=outcome["wicket"],
                extra_kind=outcome["extra_kind"],
            )
            ctx = _commentary_ctx(
                match=match,
                inn=inn,
                runs=outcome["runs"],
                wicket=outcome["wicket"],
                extras=outcome["extras"],
                extra_kind=outcome["extra_kind"],
                batter_name=batter_name,
                bowler_name=bowler_name,
            )
            engine.maybe_rotate_pair(inn.overs_completed)
            engine.commentate(situation=situation, ctx=ctx, antarctica_on_field=antarctica_on_field)

            # Milestones
            striker_card = inn.batter_cards.get(event.striker_id)
            if striker_card and striker_card.runs >= 50 and (striker_card.runs - outcome["runs"]) < 50:
                engine.commentate(situation="milestone_50", ctx=ctx, antarctica_on_field=antarctica_on_field)
            elif striker_card and striker_card.runs >= 100 and (striker_card.runs - outcome["runs"]) < 100:
                engine.commentate(situation="milestone_100", ctx=ctx, antarctica_on_field=antarctica_on_field)

        # End of over
        inn.end_over()
        over_counts[bowler_id] = over_counts.get(bowler_id, 0) + 1
        last_bowler = bowler_id

        # Auto-save after every over
        try:
            save_io.save_match(match, name="auto")
        except Exception:
            pass

        if inn.is_complete:
            break

        # End-of-over detailed scorecard + pause for keypress
        ui_cli.render_frame(console, match, engine, show_compact=True)
        ui_scoreboard.render_detailed(console, match, inn)
        console.print(Text("  Press any key for the next over (or 'p' for pause menu)...", style="dim italic"))
        ch = read_key().lower()
        if ch == "p":
            choice = ui_prompts.pause_menu(console)
            if choice == "save":
                name = (sys.stdin.read(0) or "manual").strip()  # placeholder
                save_io.save_match(match, name="manual")
                console.print("[green]  Saved.[/green]")
                read_key()
            elif choice == "quit":
                save_io.save_match(match, name="auto")
                console.print("[yellow]  Auto-saved. Goodbye.[/yellow]")
                sys.exit(0)


# -----------------------------------------------------------------------------
# Player of the match
# -----------------------------------------------------------------------------

def _award_pom(match: Match) -> None:
    """Composite stat: runs + 25 * wickets, tiebreak by SR / inverse economy."""
    candidates: list[tuple[int, str, float, float, int, int]] = []
    # tuple: (player_id, team, score, tiebreak, runs, wickets)
    for inn in match.innings_list:
        for pid, c in inn.batter_cards.items():
            score = c.runs + 25 * 0  # batting only
            tb = c.strike_rate
            team = "user" if inn.batting_country == match.user_team.country else "opponent"
            candidates.append((pid, team, score, tb, c.runs, 0))
        for pid, b in inn.bowler_cards.items():
            score = 25 * b.wickets - 0.5 * b.runs_conceded
            tb = -b.economy
            team = "user" if inn.bowling_country == match.user_team.country else "opponent"
            candidates.append((pid, team, score, tb, 0, b.wickets))
    if not candidates:
        return
    candidates.sort(key=lambda x: (x[2], x[3]), reverse=True)
    top_pid, top_team, *_ = candidates[0]
    match.player_of_the_match = top_pid
    match.pom_team = top_team


# -----------------------------------------------------------------------------
# entry
# -----------------------------------------------------------------------------

def run() -> None:
    console = ui_cli.make_console()
    while True:
        choice = ui_prompts.main_menu(console)
        if choice == "quit":
            console.print("[dim]bye[/dim]")
            return
        if choice == "stats":
            _show_stats(console)
            continue
        if choice == "load":
            saves = save_io.list_saves()
            if not saves:
                console.print("[dim]  No saves yet.[/dim]")
                ui_prompts.confirm_continue(console)
                continue
            for i, s in enumerate(saves, 1):
                console.print(f"  [yellow]{i}[/yellow]  {s['name']}  [dim]{s['mtime']}  {s['meta']}[/dim]")
            ch = read_key()
            if ch.isdigit() and 1 <= int(ch) <= len(saves):
                match = save_io.load_match(saves[int(ch) - 1]["name"])
                _continue_match(console, match)
            continue

        # NEW match
        match = _new_match_flow(console)
        if match is None:
            continue
        _play_match(console, match)


def _continue_match(console: Console, match: Match) -> None:
    engine = CommentaryEngine()
    # Resume into whichever phase the match is in
    if match.phase == "complete":
        ui_scoreboard.render_match_summary(console, match)
        ui_prompts.confirm_continue(console)
        return
    _play_match_innings(console, match, engine)


def _play_match(console: Console, match: Match) -> None:
    engine = CommentaryEngine()
    match.phase = "innings1"
    _play_match_innings(console, match, engine)


def _play_match_innings(console: Console, match: Match, engine: CommentaryEngine) -> None:
    fmt = match.fmt

    user_country_obj = _country_obj_from_meta(match.user_team)
    opp_country_obj = _country_obj_from_meta(match.opponent)

    # Innings 1
    if match.phase == "innings1":
        if match.user_batting_first:
            bat = match.user_team
            bowl = match.opponent
            bat_xi = match.user_xi
            bowl_xi = match.opponent_xi
            bowl_pool = match.opponent_bowling_pool
            user_is_batting = True
        else:
            bat = match.opponent
            bowl = match.user_team
            bat_xi = match.opponent_xi
            bowl_xi = match.user_xi
            bowl_pool = match.user_bowling_pool
            user_is_batting = False
        if not match.innings_list:
            match.add_innings(_build_innings(
                match=match, batting_country=bat, bowling_country=bowl,
                batting_xi=bat_xi, bowling_xi=bowl_xi, bowling_pool=bowl_pool,
            ))
        _run_innings(console, match, engine, match.innings_list[-1], user_is_batting=user_is_batting)
        match.phase = "innings2"

    # End-of-innings detailed scorecard
    ui_scoreboard.render_detailed(console, match, match.innings_list[-1])
    console.print(Text("  Press any key for the second innings...", style="dim italic"))
    read_key()

    # Innings 2
    if match.phase == "innings2":
        first = match.innings_list[0]
        target = first.runs + 1
        if match.user_batting_first:
            # Now the opponent bats
            bat = match.opponent
            bowl = match.user_team
            bat_xi = match.opponent_xi
            bowl_xi = match.user_xi
            bowl_pool = match.user_bowling_pool
            user_is_batting = False
        else:
            bat = match.user_team
            bowl = match.opponent
            bat_xi = match.user_xi
            bowl_xi = match.opponent_xi
            bowl_pool = match.opponent_bowling_pool
            user_is_batting = True
        if len(match.innings_list) < 2:
            match.add_innings(_build_innings(
                match=match, batting_country=bat, bowling_country=bowl,
                batting_xi=bat_xi, bowling_xi=bowl_xi, bowling_pool=bowl_pool,
                target=target,
            ))
        _run_innings(console, match, engine, match.innings_list[-1], user_is_batting=user_is_batting)
        match.set_winner_from_score()
        if match.winner == "tie":
            match.phase = "super-over"
        else:
            match.phase = "complete"

    # Super over loop
    while match.phase == "super-over":
        _run_super_over(console, match, engine)

    # Final
    _award_pom(match)
    ui_cli.render_frame(console, match, engine)
    ui_scoreboard.render_match_summary(console, match)
    ui_scoreboard.render_detailed(console, match, match.innings_list[0])
    if len(match.innings_list) > 1:
        ui_scoreboard.render_detailed(console, match, match.innings_list[1])
    stats_io.record_match(match)
    save_io.save_match(match, name="auto")
    console.print(Text("  Press any key to return to menu...", style="dim italic"))
    read_key()


def _run_super_over(console: Console, match: Match, engine: CommentaryEngine) -> None:
    """1-over super over. User bats first by default."""
    console.print(Panel(Text("⚡ SUPER OVER ⚡", style="bold magenta"), border_style="magenta"))
    # User XI first (or whoever batted first in the regular match — give user the first crack)
    inn1 = _build_innings(
        match=match,
        batting_country=match.user_team,
        bowling_country=match.opponent,
        batting_xi=match.user_xi,
        bowling_xi=match.opponent_xi,
        bowling_pool=match.opponent_bowling_pool,
        overs_override=1,
        wickets_override=2,  # super over: 2-wicket cap
    )
    match.super_over_innings.append(inn1)
    _run_innings(console, match, engine, inn1, user_is_batting=True)

    inn2 = _build_innings(
        match=match,
        batting_country=match.opponent,
        bowling_country=match.user_team,
        batting_xi=match.opponent_xi,
        bowling_xi=match.user_xi,
        bowling_pool=match.user_bowling_pool,
        overs_override=1,
        wickets_override=2,
        target=inn1.runs + 1,
    )
    match.super_over_innings.append(inn2)
    _run_innings(console, match, engine, inn2, user_is_batting=False)

    match.set_super_over_winner()
    if match.winner == "tie":
        # Repeat — clear and try again (super_over_innings keeps growing as a record)
        return
    match.phase = "complete"


def _show_stats(console: Console) -> None:
    data = stats_io.read_stats()
    matches = data.get("matches", [])
    if not matches:
        console.print("[dim]  No matches recorded yet.[/dim]")
        ui_prompts.confirm_continue(console)
        return
    console.print(Panel(Text(f"Career stats — {len(matches)} matches", style="bold"), border_style="cyan"))
    for m in matches[-20:]:
        console.print(f"  {m.get('completed_at', '?')}  {m.get('format')}  {m.get('user_team')} vs {m.get('opponent')}  →  [bold]{m.get('result')}[/bold]")
    ui_prompts.confirm_continue(console)


if __name__ == "__main__":
    run()
