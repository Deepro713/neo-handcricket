"""Top-level orchestration — pre-match flow + innings loop."""
from __future__ import annotations

import random
import sys
import time
from functools import partial
from typing import Literal

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from . import a11y, adapter, config, i18n
from .bots import captain as cap_ai
from .bots import fatigue as fatigue_mod
from .bots import matchstate as matchstate_mod
from .bots import strategy
from .bots import tells as tells_mod
from .commentary import context as context_mod
from .commentary import events as events_mod
from .commentary import lines as lines_mod
from .commentary.engine import CommentaryEngine
from .config import (
    COMMENTARY_LINE_GAP_SECONDS,
    DIFFICULTY_EPSILON,
    EXTRAS_BASE_PCT,
    INTER_BALL_GAP_SECONDS,
    TELLS_ENABLED,
    TEST_BALL_CAP,
    TEST_BOT_DECLARE_LEAD,
    TEST_BOT_FOLLOW_ON_LEAD,
    TEST_FOLLOW_ON_THRESHOLD,
)
from .innings import Innings
from .match import Match, TeamMeta
from .persistence import save as save_io
from .persistence import stats as stats_io
from .rosters import loader, selector
from .toss import machine_picks_bat_or_bowl, perform_toss
from .ui import cli as ui_cli
from .ui import overlay as ui_overlay
from .ui import prompts as ui_prompts
from .ui import scoreboard as ui_scoreboard
from .ui.input import beep, read_key, read_key_with_timer

# -----------------------------------------------------------------------------
# pre-match flow
# -----------------------------------------------------------------------------

def _read_timed(prompt_text: str) -> str | None:
    """Read the user's pick, honouring the untimed option + a11y (no-animation) mode."""
    secs = a11y.timer_seconds()
    if secs is None:                       # untimed — block until a key is pressed
        ui_cli.update_prompt_line(prompt_text)
        return read_key()
    if a11y.animations_enabled():
        return read_key_with_timer(secs, tick=partial(ui_cli.update_prompt_line, prompt_text))
    ui_cli.update_prompt_line(prompt_text)  # static prompt, no redraw bar
    return read_key_with_timer(secs)


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
    config.TIMER_UNTIMED = ui_prompts.select_timer(console)  # session timer preference

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
    user_call: Literal["heads", "tails"] = "tails" if ch == "t" else "heads"
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


def _check_declaration(console: Console, match: Match, inn: Innings, *, user_is_batting: bool) -> bool:
    """At end of an over in Test, decide whether the batting side declares."""
    # Heuristic — only meaningful in innings 3 (extending lead). Or innings 1 if very late.
    innings_idx = len(match.innings_list)  # 1-indexed: 1, 2, 3, 4
    if innings_idx == 4:
        return False  # 4th innings is a chase / follow-on — never declare
    if user_is_batting:
        # Prompt user if not in 4th innings
        if innings_idx in (1, 2, 3):
            console.print(Text("  Press [bold]d[/bold] to declare, any other key to continue.", style="dim italic"))
            ch = read_key().lower()
            return ch == "d"
        return False
    # Bot batting: heuristic based on innings + lead
    if innings_idx == 3:
        # Lead = current_innings.runs + (innings_1 - innings_2) [for the side that batted first]
        # Compute lead simply: total bot runs - total opponent runs across all innings
        bot_country = inn.batting_country
        runs_for_bot = sum(i.runs for i in match.innings_list if i.batting_country == bot_country)
        runs_against = sum(i.runs for i in match.innings_list if i.batting_country != bot_country)
        if runs_for_bot - runs_against >= TEST_BOT_DECLARE_LEAD:
            return True
    return False


def _deliver_commentary_paced(
    console: Console,
    engine: CommentaryEngine,
    *,
    situation: str,
    ctx: dict,
    antarctica_on_field: bool,
    min_total_seconds: float = INTER_BALL_GAP_SECONDS,
    line_gap: float = COMMENTARY_LINE_GAP_SECONDS,
) -> None:
    """Generate the multi-line conversational commentary for this event,
    print each line incrementally with a pause between, and ensure at least
    `min_total_seconds` elapses before returning. User can press any key to
    skip the wait at any point."""
    start = time.monotonic()
    entries = engine.commentate(situation=situation, ctx=ctx, antarctica_on_field=antarctica_on_field)
    skipped = False
    for i, entry in enumerate(entries):
        console.print(f"  ▸ {entry.line}  [dim]({entry.commentator})[/dim]")
        if skipped:
            continue
        if i < len(entries) - 1:
            ch = read_key_with_timer(line_gap)
            if ch is not None:
                # Skip the rest of the line gaps — but still print remaining lines instantly
                skipped = True
    if skipped:
        return
    elapsed = time.monotonic() - start
    remaining = max(0.0, min_total_seconds - elapsed)
    if remaining > 0:
        read_key_with_timer(remaining)


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
        "batter_runs": inn.batter_cards[inn.striker_id].runs if inn.striker_id in inn.batter_cards else 0,
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
    last_over_by_bowler: dict[int, int] = {}  # bowler_id → over index of their last spell (fatigue)
    last_bowler: int | None = None

    user_recent_bowling_picks: list[int] = []   # user's bowling picks (when user is bowler)
    user_recent_batting_picks: list[int] = []   # user's batting picks (when user is batter)
    user_batting_outcomes: list[int] = []       # reward sign per batting pick (opponent model / WSLS)
    user_bowling_outcomes: list[int] = []        # reward sign per bowling pick (opponent model / WSLS)

    fmt = match.fmt
    total_overs = inn.overs_limit

    while not inn.is_complete:
        # Pick bowler
        archetypes = _bot_archetypes_for_pool(inn.bowling_pool, bowling_country_obj)
        if user_is_batting:
            # Bot picks bowler — bias by match-up vs the current striker + freshness.
            try:
                striker_arch = batting_country_obj.player(inn.striker_id).batting_archetype
            except KeyError:
                striker_arch = None
            pool_fatigues = {
                pid: fatigue_mod.fatigue_factor(
                    over_counts.get(pid, 0),
                    inn.overs_completed - last_over_by_bowler.get(pid, inn.overs_completed),
                    archetypes.get(pid, "pace"),
                )
                for pid in inn.bowling_pool
            }
            bowler_id = cap_ai.pick_next_bowler(
                bowling_pool=inn.bowling_pool,
                archetypes=archetypes,
                over_counts=over_counts,
                economies=bowler_economies,
                last_bowler=last_bowler,
                over_idx=inn.overs_completed,
                total_overs=total_overs,
                fmt=fmt,
                batter_archetype=striker_arch,
                fatigues=pool_fatigues,
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
            cur_fatigue = fatigue_mod.fatigue_factor(
                over_counts.get(bowler_id, 0),
                inn.overs_completed - last_over_by_bowler.get(bowler_id, inn.overs_completed),
                archetypes.get(bowler_id, "pace"),
            )
            ui_overlay.show_bowler_card(
                console, bowler, inn.overs_completed, bowling_country_obj.country, fatigue=cur_fatigue
            )

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
            bot_fatigue = 0.0  # set in the bot-bowling branch; used for context lines

            if user_is_batting:
                # Bot bowls (bot picks number, user picks number with timer)
                bowler_arch = bowler_p.bowling_archetype if bowler_p and bowler_p.bowling_archetype else "pace"
                last_ov = last_over_by_bowler.get(bowler_id)
                overs_rested = (inn.overs_completed - last_ov) if last_ov is not None else inn.overs_completed
                bot_fatigue = fatigue_mod.fatigue_factor(
                    over_counts.get(bowler_id, 0), overs_rested, bowler_arch
                )
                # Route the bot's bowling pick through the shared headless adapter
                # helper (single source of truth for the CLI, TUI and any front-end).
                bot_pick = adapter.bot_bowl_pick(
                    bowler_archetype=bowler_arch,
                    recent_user_batting_picks=user_recent_batting_picks,
                    difficulty=match.difficulty,
                    over_number=inn.overs_completed,
                    fatigue=bot_fatigue,
                    batting_outcomes=user_batting_outcomes,
                    rng=rng,
                )
                if TELLS_ENABLED:
                    ui_overlay.show_tell(console, tells_mod.generate_tell(bowler_arch, bot_fatigue, rng=rng))
                # Prompt user
                prompt_text = f"BAT — pick 0–6  ({batter_name})"
                beep()
                user_ch = _read_timed(prompt_text)
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
                striker_balls = inn.batter_cards[inn.striker_id].balls if inn.striker_id in inn.batter_cards else 0
                bot_aggression = matchstate_mod.aggression(
                    matchstate_mod.settledness(striker_balls),
                    matchstate_mod.chase_intent(inn.runs_needed, inn.balls_remaining),
                )
                bot_pick = strategy.pick_number(
                    archetype=bot_arch,
                    is_bowler=False,
                    recent_user_picks=user_recent_bowling_picks,
                    difficulty=match.difficulty,
                    over_number=inn.overs_completed,
                    aggression=bot_aggression,
                    opponent_outcomes=user_bowling_outcomes,
                    epsilon=DIFFICULTY_EPSILON.get(match.difficulty),
                    rng=rng,
                )
                prompt_text = f"BOWL — pick 0–6  (vs {batter_name})"
                beep()
                user_ch = _read_timed(prompt_text)
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

            inn.record_ball(
                runs=outcome["runs"],
                extras=outcome["extras"],
                wicket=outcome["wicket"],
                extra_kind=outcome["extra_kind"],
                timed_out=outcome["timed_out"],
            )

            # Opponent-model outcome tracking (M006): reward sign for the user's pick,
            # kept aligned with the corresponding picks list (appended only when the
            # user actually picked a number).
            if user_pick is not None:
                if user_is_batting:
                    rewarded = outcome["wicket"] is None and outcome["runs"] > 0
                    user_batting_outcomes.append(1 if rewarded else -1)
                else:
                    rewarded = outcome["wicket"] is not None or outcome["runs"] <= 1
                    user_bowling_outcomes.append(1 if rewarded else -1)

            # Update bowler economy
            bid = inn.current_bowler_id
            if bid is not None:
                bcard = inn.bowler_cards.get(bid)
                if bcard and bcard.balls > 0:
                    bowler_economies[bid] = bcard.economy

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
            _deliver_commentary_paced(
                console, engine,
                situation=situation, ctx=ctx, antarctica_on_field=antarctica_on_field,
            )

            # Big-moment escalation, driven by the pure event detector (M007):
            # fifties/hundreds, hat-tricks, maidens, last-ball finishes, collapses,
            # 50-partnerships. Wickets/boundaries are already in the ball conversation.
            detected = events_mod.detect(inn)
            match.highlight_events.extend(detected)
            accent = lines_mod.event_situation(detected)
            if accent:
                _deliver_commentary_paced(
                    console, engine,
                    situation=accent, ctx=ctx, antarctica_on_field=antarctica_on_field,
                    min_total_seconds=0.0,
                )

            # Context-aware aside referencing live fatigue / settledness / AI-read.
            faced_card = inn.batter_cards.get(inn.ball_log[-1].striker_id) if inn.ball_log else None
            ctx_line = context_mod.context_line(
                bowler_fatigue=bot_fatigue if user_is_batting else 0.0,
                batter_settledness=matchstate_mod.settledness(faced_card.balls) if faced_card else 0.0,
                ai_read=user_is_batting and outcome["wicket"] == "match",
                rng=rng,
            )
            if ctx_line:
                ui_overlay.show_tell(console, ctx_line)

        # End of over
        inn.end_over()
        last_over_by_bowler[bowler_id] = inn.overs_completed  # for fatigue rest-tracking
        over_counts[bowler_id] = over_counts.get(bowler_id, 0) + 1
        last_bowler = bowler_id

        # Auto-save after every over
        try:
            save_io.save_match(match, name="auto")
        except Exception:
            pass

        # Test cricket: total-overs cap (force draw if reached)
        if match.fmt.name == "Test":
            total_balls_bowled = sum(i.balls for i in match.innings_list)
            if total_balls_bowled >= TEST_BALL_CAP:
                inn.declared = True  # signal innings end via declared flag (treated like end)
                console.print(Text("  ⏰ 5 days exhausted — match heading to a draw.", style="yellow bold"))
                break

        # Test cricket: declaration check at end of over
        if match.fmt.name == "Test" and not inn.is_complete:
            declared = _check_declaration(console, match, inn, user_is_batting=user_is_batting)
            if declared:
                inn.declared = True
                console.print(Text(f"  📣 {inn.batting_country} declares at {inn.runs}/{inn.wickets}.", style="bold magenta"))
                break

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
                (sys.stdin.read(0) or "manual").strip()  # placeholder
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
            score: float = c.runs + 25 * 0  # batting only
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


def _daily_flow(console: Console) -> None:
    """Show today's deterministic daily challenge and, on request, play it."""
    import datetime as _dt

    from .career import sharecode
    from .daily import score as daily_score
    from .daily import seed as daily_seed_mod
    from .formats import PRESETS
    from .persistence import daily as daily_io
    from .ui import daily as ui_daily

    challenge = daily_seed_mod.daily_challenge(_dt.date.today(), countries=loader.list_countries())
    table = daily_io.load_best_table()
    ui_daily.render_daily(console, challenge, daily_score.best_for(table, challenge.date_iso))
    console.print("\n  [yellow]p[/yellow] play today's challenge   ·   any other key to go back")
    if read_key().lower() != "p":
        return

    rng = random.Random(challenge.seed)
    user_country = loader.load_country(challenge.team_a)
    opp_country = loader.load_country(challenge.team_b)
    fmt = PRESETS[challenge.fmt]
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
        difficulty=challenge.difficulty,
    )
    _do_toss(console, match)
    _play_match(console, match)

    won = match.winner == "user"
    totals = [inn.runs for inn in match.innings_list]
    margin = abs(totals[0] - totals[1]) if len(totals) >= 2 else 0
    score_val = daily_score.score_result(won=won, runs_margin=margin)
    entry = daily_score.make_entry(challenge.date_iso, challenge.seed, score_val, summary=match.result_summary or "")
    table = daily_score.update_best(table, entry)
    daily_io.save_best_table(table)
    ui_daily.render_result(console, score_val, sharecode.encode(entry))
    ui_prompts.confirm_continue(console)


# -----------------------------------------------------------------------------
# entry
# -----------------------------------------------------------------------------

def run() -> None:
    console = ui_cli.make_console()
    while True:
        choice = ui_prompts.main_menu(console)
        if choice == "quit":
            console.print(f"[dim]{i18n.t('common.bye')}[/dim]")
            return
        if choice == "stats":
            _show_stats(console)
            continue
        if choice == "career":
            from .persistence import progression as prog_io
            from .ui import campaign as ui_campaign
            state = prog_io.load_progression()
            ui_campaign.render_dashboard(console, state, set(state.get("achievements", [])))
            ui_prompts.confirm_continue(console)
            continue
        if choice == "daily":
            _daily_flow(console)
            continue
        if choice == "tutorial":
            from .ui import tutorial as ui_tutorial
            ui_tutorial.run_tutorial(console)
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
        new_match = _new_match_flow(console)
        if new_match is None:
            continue
        _play_match(console, new_match)


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

    # Test cricket has its own 4-innings flow with follow-on / declarations / draw
    if fmt.name == "Test":
        _play_test_match(console, match, engine)
        return

    _country_obj_from_meta(match.user_team)
    _country_obj_from_meta(match.opponent)

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


def _play_test_match(console: Console, match: Match, engine: CommentaryEngine) -> None:
    """Orchestrate a Test match — 4 innings, ≤ 450 overs total, follow-on, declarations, draw possible.

    Innings order:
        1: Team A bats
        2: Team B bats
        After 2: A leads by ≥ TEST_FOLLOW_ON_THRESHOLD → A captain decides on follow-on.
        3: Team B (if follow-on) or Team A bats
        4: The other team bats, chasing if necessary.
    """
    def total_balls_bowled() -> int:
        return sum(i.balls for i in match.innings_list)

    def cap_reached() -> bool:
        return total_balls_bowled() >= TEST_BALL_CAP

    user_first = match.user_batting_first
    teams_first_to_second = [
        (match.user_team, match.opponent, match.user_xi, match.opponent_xi, match.opponent_bowling_pool, True),
        (match.opponent, match.user_team, match.opponent_xi, match.user_xi, match.user_bowling_pool, False),
    ] if user_first else [
        (match.opponent, match.user_team, match.opponent_xi, match.user_xi, match.user_bowling_pool, False),
        (match.user_team, match.opponent, match.user_xi, match.opponent_xi, match.opponent_bowling_pool, True),
    ]

    def end_of_innings_pause(label: str) -> None:
        ui_scoreboard.render_detailed(console, match, match.innings_list[-1])
        console.print(Text(f"  Press any key to begin {label}...", style="dim italic"))
        read_key()

    # --- Innings 1 ---
    bat, bowl, bat_xi, bowl_xi, bowl_pool, user_is_batting = teams_first_to_second[0]
    inn1 = _build_innings(match=match, batting_country=bat, bowling_country=bowl,
                          batting_xi=bat_xi, bowling_xi=bowl_xi, bowling_pool=bowl_pool)
    match.add_innings(inn1)
    _run_innings(console, match, engine, inn1, user_is_batting=user_is_batting)
    if cap_reached():
        match.winner = "draw"
        match.result_summary = "Match drawn — 5 days exhausted"
        match.phase = "complete"
        _finalise_test(console, match, engine)
        return
    end_of_innings_pause("the second innings")

    # --- Innings 2 ---
    bat, bowl, bat_xi, bowl_xi, bowl_pool, user_is_batting = teams_first_to_second[1]
    inn2 = _build_innings(match=match, batting_country=bat, bowling_country=bowl,
                          batting_xi=bat_xi, bowling_xi=bowl_xi, bowling_pool=bowl_pool)
    match.add_innings(inn2)
    _run_innings(console, match, engine, inn2, user_is_batting=user_is_batting)
    if cap_reached():
        match.winner = "draw"
        match.result_summary = "Match drawn — 5 days exhausted"
        match.phase = "complete"
        _finalise_test(console, match, engine)
        return

    # --- Follow-on decision ---
    inn1_runs = match.innings_list[0].runs
    inn2_runs = match.innings_list[1].runs
    lead_after_2 = inn1_runs - inn2_runs   # positive = team A (batted first) leads

    follow_on = False
    if lead_after_2 >= TEST_FOLLOW_ON_THRESHOLD:
        # Team A (batted first) has the option
        team_a_country = match.innings_list[0].batting_country
        team_a_is_user = (team_a_country == match.user_team.country)
        if team_a_is_user:
            console.print(Panel(
                Text(f"You lead by {lead_after_2}. Enforce follow-on? [y]es / [n]o", style="bold cyan"),
                border_style="cyan",
            ))
            ch = read_key().lower()
            follow_on = (ch == "y")
        else:
            # Bot heuristic
            follow_on = lead_after_2 >= TEST_BOT_FOLLOW_ON_LEAD
            if follow_on:
                console.print(Panel(Text(f"  {team_a_country} has enforced the follow-on (lead: {lead_after_2}).", style="bold yellow"), border_style="yellow"))
            else:
                console.print(Panel(Text(f"  {team_a_country} declined the follow-on (lead: {lead_after_2}).", style="bold yellow"), border_style="yellow"))

    end_of_innings_pause("the third innings")

    # --- Innings 3 ---
    if follow_on:
        # Team B bats again (same xi/pool as inn2)
        bat_country = match.innings_list[1].batting_country
        b3_meta = match.opponent if bat_country == match.opponent.country else match.user_team
        bowl_meta = match.user_team if bat_country == match.opponent.country else match.opponent
        bat_xi = match.opponent_xi if bat_country == match.opponent.country else match.user_xi
        bowl_xi = match.user_xi if bat_country == match.opponent.country else match.opponent_xi
        bowl_pool = match.user_bowling_pool if bat_country == match.opponent.country else match.opponent_bowling_pool
        user_is_batting = (bat_country == match.user_team.country)
    else:
        # Normal: Team A bats again (same xi/pool as inn1)
        bat_country = match.innings_list[0].batting_country
        b3_meta = match.user_team if bat_country == match.user_team.country else match.opponent
        bowl_meta = match.opponent if bat_country == match.user_team.country else match.user_team
        bat_xi = match.user_xi if bat_country == match.user_team.country else match.opponent_xi
        bowl_xi = match.opponent_xi if bat_country == match.user_team.country else match.user_xi
        bowl_pool = match.opponent_bowling_pool if bat_country == match.user_team.country else match.user_bowling_pool
        user_is_batting = (bat_country == match.user_team.country)

    inn3 = _build_innings(match=match, batting_country=b3_meta, bowling_country=bowl_meta,
                          batting_xi=bat_xi, bowling_xi=bowl_xi, bowling_pool=bowl_pool)
    match.add_innings(inn3)
    _run_innings(console, match, engine, inn3, user_is_batting=user_is_batting)

    # Check innings victory between 3 and 4 (only meaningful in follow-on path)
    if follow_on:
        # Team B has now batted twice. If their combined < Team A's first innings, A wins by innings.
        team_a_country = match.innings_list[0].batting_country
        team_b_country = match.innings_list[1].batting_country
        a_runs = match.innings_list[0].runs
        b_total = match.innings_list[1].runs + match.innings_list[2].runs
        if b_total < a_runs:
            margin = a_runs - b_total
            match.winner = "user" if team_a_country == match.user_team.country else "opponent"
            match.result_summary = f"{team_a_country} won by an innings and {margin} runs"
            match.phase = "complete"
            _finalise_test(console, match, engine)
            return
        # B took the lead — A bats 4th to chase
        target = b_total - a_runs + 1  # runs A needs in 4th innings
        if cap_reached():
            match.winner = "draw"
            match.result_summary = "Match drawn — 5 days exhausted"
            match.phase = "complete"
            _finalise_test(console, match, engine)
            return
        end_of_innings_pause("the fourth innings (chase)")

        # --- Innings 4 (A chases) ---
        bat_country = team_a_country
        b4_meta = match.user_team if bat_country == match.user_team.country else match.opponent
        bowl_meta4 = match.opponent if bat_country == match.user_team.country else match.user_team
        bat_xi4 = match.user_xi if bat_country == match.user_team.country else match.opponent_xi
        bowl_xi4 = match.opponent_xi if bat_country == match.user_team.country else match.user_xi
        bowl_pool4 = match.opponent_bowling_pool if bat_country == match.user_team.country else match.user_bowling_pool
        user_batting4 = (bat_country == match.user_team.country)
        inn4 = _build_innings(match=match, batting_country=b4_meta, bowling_country=bowl_meta4,
                              batting_xi=bat_xi4, bowling_xi=bowl_xi4, bowling_pool=bowl_pool4,
                              target=target)
        match.add_innings(inn4)
        _run_innings(console, match, engine, inn4, user_is_batting=user_batting4)
        _resolve_test_result(match)
    else:
        # Normal path: A bats 3rd and sets a target. B bats 4th.
        if cap_reached():
            match.winner = "draw"
            match.result_summary = "Match drawn — 5 days exhausted"
            match.phase = "complete"
            _finalise_test(console, match, engine)
            return
        team_a_country = match.innings_list[0].batting_country
        team_b_country = match.innings_list[1].batting_country
        a_total = match.innings_list[0].runs + match.innings_list[2].runs
        b_so_far = match.innings_list[1].runs
        target = a_total - b_so_far + 1
        end_of_innings_pause("the fourth innings (chase)")

        # --- Innings 4 (B chases) ---
        bat_country = team_b_country
        b4_meta = match.opponent if bat_country == match.opponent.country else match.user_team
        bowl_meta4 = match.user_team if bat_country == match.opponent.country else match.opponent
        bat_xi4 = match.opponent_xi if bat_country == match.opponent.country else match.user_xi
        bowl_xi4 = match.user_xi if bat_country == match.opponent.country else match.opponent_xi
        bowl_pool4 = match.user_bowling_pool if bat_country == match.opponent.country else match.opponent_bowling_pool
        user_batting4 = (bat_country == match.user_team.country)
        inn4 = _build_innings(match=match, batting_country=b4_meta, bowling_country=bowl_meta4,
                              batting_xi=bat_xi4, bowling_xi=bowl_xi4, bowling_pool=bowl_pool4,
                              target=target)
        match.add_innings(inn4)
        _run_innings(console, match, engine, inn4, user_is_batting=user_batting4)
        _resolve_test_result(match)

    _finalise_test(console, match, engine)


def _resolve_test_result(match: Match) -> None:
    """Determine Test result after innings 4 completes (chase / bowl out / draw)."""
    inn4 = match.innings_list[-1]
    target = inn4.target or 0
    if inn4.runs >= target:
        # Chase complete
        wickets_left = inn4.wickets_limit - inn4.wickets
        match.winner = "user" if inn4.batting_country == match.user_team.country else "opponent"
        match.result_summary = f"{inn4.batting_country} won by {wickets_left} wickets"
    elif inn4.wickets >= inn4.wickets_limit:
        # Bowled out short
        margin = target - 1 - inn4.runs
        match.winner = "user" if inn4.bowling_country == match.user_team.country else "opponent"
        match.result_summary = f"{inn4.bowling_country} won by {margin} runs"
    else:
        # Time/balls exhausted
        match.winner = "draw"
        match.result_summary = "Match drawn"
    match.phase = "complete"


def _finalise_test(console: Console, match: Match, engine: CommentaryEngine) -> None:
    _award_pom(match)
    ui_cli.render_frame(console, match, engine)
    ui_scoreboard.render_match_summary(console, match)
    for inn in match.innings_list:
        ui_scoreboard.render_detailed(console, match, inn)
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
    agg = stats_io.aggregate()
    console.print(Panel(Text(f"Career stats — {agg['total_matches']} matches", style="bold cyan"), border_style="cyan"))
    console.print(f"  W [green]{agg['wins']}[/green]  ·  L [red]{agg['losses']}[/red]  ·  T {agg['ties']}  ·  Draw {agg['draws']}  ·  PoTM × {agg['pom_count']}  ·  Best streak: {agg['longest_winning_streak']}")

    if agg["by_format"]:
        console.print()
        console.print(Text("By format:", style="bold"))
        for fmt, row in agg["by_format"].items():
            console.print(f"  [yellow]{fmt:6}[/yellow]  {row['played']} pld   {row['wins']}w  {row['losses']}l  {row['draws']}d  {row['ties']}t")

    if agg["highest_team_total"]:
        runs, country, fmt = agg["highest_team_total"]
        console.print()
        console.print(f"  Highest team total: [bold]{runs}[/bold] by {country} ({fmt})")
    if agg["highest_individual"]:
        runs, pid, country, fmt = agg["highest_individual"]
        console.print(f"  Highest individual: [bold]{runs}[/bold] by player #{pid} ({country}, {fmt})")

    if agg["head_to_head"]:
        console.print()
        console.print(Text("Head-to-head (top 10):", style="bold"))
        h2h_sorted = sorted(agg["head_to_head"].items(), key=lambda kv: -(kv[1]["wins"] + kv[1]["losses"]))[:10]
        for opp, row in h2h_sorted:
            console.print(f"  vs {opp:24} {row['wins']}w  {row['losses']}l  {row['draws']}d  {row['ties']}t")

    if agg["top_run_scorers"]:
        console.print()
        console.print(Text("Top run-scorers (your team):", style="bold"))
        for entry in agg["top_run_scorers"][:5]:
            console.print(f"  player #{entry['player_id']} ({entry['country']}) — {entry['runs']} runs in {entry['matches']} matches")
    if agg["top_wicket_takers"]:
        console.print(Text("Top wicket-takers (your team):", style="bold"))
        for entry in agg["top_wicket_takers"][:5]:
            console.print(f"  player #{entry['player_id']} ({entry['country']}) — {entry['wickets']} wickets in {entry['matches']} matches")

    console.print()
    console.print(Text("Recent matches:", style="bold"))
    for m in matches[-10:]:
        console.print(f"  {m.get('completed_at', '?')}  [yellow]{m.get('format'):6}[/yellow]  {m.get('user_team')} vs {m.get('opponent')}  →  [bold]{m.get('result')}[/bold]")
    ui_prompts.confirm_continue(console)


if __name__ == "__main__":
    run()
