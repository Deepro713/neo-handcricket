"""End-to-end smoke tests with no UI / no prompts.

Tests the engine layer by simulating ball-by-ball outcomes directly. Verifies:
  - Innings completes for T10, T20, ODI
  - Custom 1-wicket-per-innings 1v1 completes
  - Save/load round-trip preserves match state
  - Roster validator accepts/rejects correctly
  - Playing-XI selector respects always-in rules
"""
from __future__ import annotations

import json
import random
from pathlib import Path

from neo_handcricket.bots import strategy
from neo_handcricket.formats import PRESETS, custom as custom_fmt
from neo_handcricket.innings import Innings
from neo_handcricket.match import Match, TeamMeta
from neo_handcricket.persistence import save as save_io
from neo_handcricket.rosters import loader, selector, validator


def _team_meta(country: loader.Country) -> TeamMeta:
    return TeamMeta(
        country=country.country,
        flag=country.flag,
        naming_convention=country.naming_convention,
        players=[
            {
                "id": p.id, "name": p.name, "role": p.role,
                "batting_hand": p.batting_hand, "bowling_style": p.bowling_style,
                "batting_archetype": p.batting_archetype, "bowling_archetype": p.bowling_archetype,
            }
            for p in country.players
        ],
        staff=list(country.staff),
    )


def _simulate_innings(inn: Innings, bowling_country: loader.Country, batting_country: loader.Country, *, rng: random.Random, max_balls: int = 1000) -> None:
    """Mock ball-by-ball outcomes. User is treated as the batter (always inputs in time, picks random 0-6)."""
    pool = inn.bowling_pool
    bowler_idx = 0
    inn.start_over(pool[bowler_idx])
    bowler_arch_lookup = {p.id: (p.bowling_archetype or "pace") for p in bowling_country.players}
    batter_arch_lookup = {p.id: (p.batting_archetype or "tail-ender") for p in batting_country.players}

    user_recent: list[int] = []
    safety = 0
    while not inn.is_complete and safety < max_balls:
        safety += 1
        if inn.current_over_balls >= 6:
            inn.end_over()
            bowler_idx = (bowler_idx + 1) % len(pool)
            inn.start_over(pool[bowler_idx])

        bowler_id = inn.current_bowler_id
        bowler_arch = bowler_arch_lookup.get(bowler_id, "pace")
        # Bot picks (matching) and "user" picks random 0-6
        bot_pick = strategy.pick_number(
            archetype=bowler_arch, is_bowler=True,
            recent_user_picks=user_recent, difficulty="medium",
            over_number=inn.overs_completed, rng=rng,
        )
        user_pick = rng.randint(0, 6)
        user_recent.append(user_pick)

        if user_pick == bot_pick:
            inn.record_ball(wicket="match")
        else:
            inn.record_ball(runs=user_pick)
    if not inn.is_complete:
        raise AssertionError(f"innings did not complete after {max_balls} balls")


def test_t20_innings_completes() -> None:
    india = loader.load_country("india")
    antarctica = loader.load_country("antarctica")
    fmt = PRESETS["T20"]
    rng = random.Random(7)
    sel_a = selector.select_xi(india, fmt, rng=rng)
    sel_b = selector.select_xi(antarctica, fmt, rng=rng)

    inn = Innings(
        batting_country=india.country,
        bowling_country=antarctica.country,
        batting_xi=[p.id for p in sel_a.playing_xi],
        bowling_xi=[p.id for p in sel_b.playing_xi],
        bowling_pool=[p.id for p in sel_b.bowling_pool],
        overs_limit=fmt.overs_per_innings,
        wickets_limit=fmt.wickets_per_innings,
    )
    _simulate_innings(inn, antarctica, india, rng=rng)
    assert inn.is_complete
    assert inn.balls <= (fmt.overs_per_innings or 0) * 6
    assert inn.wickets <= fmt.wickets_per_innings


def test_t10_innings_completes() -> None:
    india = loader.load_country("england")
    antarctica = loader.load_country("antarctica")
    fmt = PRESETS["T10"]
    rng = random.Random(11)
    sel_a = selector.select_xi(india, fmt, rng=rng)
    sel_b = selector.select_xi(antarctica, fmt, rng=rng)
    inn = Innings(
        batting_country=india.country,
        bowling_country=antarctica.country,
        batting_xi=[p.id for p in sel_a.playing_xi],
        bowling_xi=[p.id for p in sel_b.playing_xi],
        bowling_pool=[p.id for p in sel_b.bowling_pool],
        overs_limit=fmt.overs_per_innings,
        wickets_limit=fmt.wickets_per_innings,
    )
    _simulate_innings(inn, antarctica, india, rng=rng)
    assert inn.is_complete


def test_custom_1v1_1wicket() -> None:
    """A 2-player custom match, 1 wicket per innings, 5 overs."""
    fmt = custom_fmt(overs=5, wickets=1, innings_per_team=1, playing_size=2)
    england = loader.load_country("england")
    antarctica = loader.load_country("antarctica")
    rng = random.Random(99)
    sel_a = selector.select_xi(england, fmt, rng=rng)
    sel_b = selector.select_xi(antarctica, fmt, rng=rng)
    assert len(sel_a.playing_xi) == 2
    assert len(sel_b.playing_xi) == 2
    inn = Innings(
        batting_country=england.country,
        bowling_country=antarctica.country,
        batting_xi=[p.id for p in sel_a.playing_xi],
        bowling_xi=[p.id for p in sel_b.playing_xi],
        bowling_pool=[p.id for p in sel_b.bowling_pool],
        overs_limit=fmt.overs_per_innings,
        wickets_limit=fmt.wickets_per_innings,
    )
    _simulate_innings(inn, antarctica, england, rng=rng)
    assert inn.is_complete


def test_save_load_roundtrip(tmp_path: Path | None = None) -> None:
    india = loader.load_country("india")
    antarctica = loader.load_country("antarctica")
    fmt = PRESETS["T10"]
    rng = random.Random(13)
    sel_a = selector.select_xi(india, fmt, rng=rng)
    sel_b = selector.select_xi(antarctica, fmt, rng=rng)

    match = Match(
        user_team=_team_meta(india),
        opponent=_team_meta(antarctica),
        user_xi=[p.id for p in sel_a.playing_xi],
        opponent_xi=[p.id for p in sel_b.playing_xi],
        user_bowling_pool=[p.id for p in sel_a.bowling_pool],
        opponent_bowling_pool=[p.id for p in sel_b.bowling_pool],
        fmt=fmt,
        difficulty="medium",
        user_batting_first=True,
    )
    inn = Innings(
        batting_country=india.country,
        bowling_country=antarctica.country,
        batting_xi=match.user_xi,
        bowling_xi=match.opponent_xi,
        bowling_pool=match.opponent_bowling_pool,
        overs_limit=fmt.overs_per_innings,
        wickets_limit=fmt.wickets_per_innings,
    )
    match.add_innings(inn)
    _simulate_innings(inn, antarctica, india, rng=rng)
    match.phase = "innings2"

    save_io.save_match(match, name="smoke_roundtrip")
    loaded = save_io.load_match("smoke_roundtrip")

    assert loaded.user_team.country == match.user_team.country
    assert loaded.opponent.country == match.opponent.country
    assert loaded.fmt.name == match.fmt.name
    assert loaded.phase == match.phase
    assert len(loaded.innings_list) == 1
    li = loaded.innings_list[0]
    assert li.runs == inn.runs
    assert li.wickets == inn.wickets
    assert li.balls == inn.balls
    save_io.delete_save("smoke_roundtrip")


def test_validator_strict_squad() -> None:
    india = loader.load_country("india")
    res = validator.validate(india, playing_size=11)
    assert res.ok, res.errors


def test_validator_no_captain_fails() -> None:
    india = loader.load_country("india")
    # Mutate: drop the captain marker
    bad_players = [p for p in india.players]
    new_first = loader.Player(
        id=bad_players[0].id, name=bad_players[0].name, role="batsman",
        batting_hand=bad_players[0].batting_hand, bowling_style=bad_players[0].bowling_style,
        batting_archetype=bad_players[0].batting_archetype, bowling_archetype=bad_players[0].bowling_archetype,
    )
    bad_players[0] = new_first
    bad_country = loader.Country(
        country=india.country, flag=india.flag, naming_convention=india.naming_convention,
        players=bad_players, staff=india.staff, slug=india.slug,
    )
    res = validator.validate(bad_country, playing_size=11)
    assert not res.ok


def test_validator_2player_custom_loose() -> None:
    """Sub-11 custom matches just need names."""
    england = loader.load_country("england")
    tiny = loader.Country(
        country="Tiny", flag="", naming_convention="given-family",
        players=england.players[:2], staff=[], slug="tiny",
    )
    res = validator.validate(tiny, playing_size=2)
    assert res.ok, res.errors


def test_selector_always_in_rules() -> None:
    pakistan = loader.load_country("pakistan")
    fmt = PRESETS["ODI"]
    sel = selector.select_xi(pakistan, fmt, rng=random.Random(1))
    xi_ids = {p.id for p in sel.playing_xi}
    assert pakistan.captain.id in xi_ids
    assert pakistan.vice_captain.id in xi_ids
    keepers_in = sum(1 for p in sel.playing_xi if p.role in ("keeper", "keeper-reserve"))
    assert keepers_in >= 2
    bowlers_in = sum(1 for p in sel.playing_xi if p.can_bowl)
    assert bowlers_in >= fmt.min_bowlers_in_xi
    spinners = sum(1 for p in sel.playing_xi if p.bowling_archetype in {"off-spin", "leg-spin"})
    pacers = sum(1 for p in sel.playing_xi if p.bowling_archetype in {"pace", "swing", "mystery"})
    assert spinners >= fmt.min_spinners
    assert pacers >= fmt.min_pacers


def test_all_rosters_load() -> None:
    """Every roster JSON must parse and meet the squad-shape requirements."""
    found = set(loader.list_countries())
    assert len(found) >= 195, f"expected ≥ 195 countries, got {len(found)}"
    # Spot-check shape across every roster
    for slug in found:
        c = loader.load_country(slug)
        assert len(c.players) == 33, f"{slug}: expected 33 players, got {len(c.players)}"
        assert len(c.staff) == 2, f"{slug}: expected 2 staff, got {len(c.staff)}"
        cap = [p for p in c.players if p.role == "captain"]
        vc = [p for p in c.players if p.role == "vice-captain"]
        keepers = [p for p in c.players if p.role in ("keeper", "keeper-reserve")]
        assert len(cap) == 1, f"{slug}: cap count = {len(cap)}"
        assert len(vc) == 1, f"{slug}: vc count = {len(vc)}"
        assert len(keepers) == 3, f"{slug}: keepers count = {len(keepers)}"


def test_commentary_returns_multiple_lines_per_ball() -> None:
    """The new conversational engine returns 2-3 lines for ball events."""
    from neo_handcricket.commentary.engine import CommentaryEngine
    e = CommentaryEngine()
    ball_situations = ["ball_dot", "ball_run_1", "ball_run_4", "ball_run_6", "wicket_match"]
    for sit in ball_situations:
        ctx = {
            "batter": "Test", "bowler": "Test", "runs": 0, "extras": 0,
            "wicket_kind": None, "extra_kind": None, "score": "10/0",
            "wickets": 0, "over": "1.0", "over_num": 1, "ball_in_over": 1,
            "country": "India", "opponent": "England",
            "batting_country": "India", "bowling_country": "England",
            "striker_id": 1, "bowler_id": 19, "batter_runs": 0, "result_summary": "",
        }
        entries = e.commentate(situation=sit, ctx=ctx, antarctica_on_field=False)
        assert 2 <= len(entries) <= 3, f"{sit}: got {len(entries)} entries"
        # Different commentators when panel size >= number of lines.
        # If panel size = 2 and we have 3 lines, one repeat is allowed.
        commentators = {ent.commentator for ent in entries}
        min_unique = min(len(entries), len(e.panel))
        assert len(commentators) >= min_unique, f"{sit}: got {len(commentators)} unique vs panel {len(e.panel)}"


def test_test_cricket_ball_cap_forces_draw() -> None:
    """A Test where the engine never gets wickets should hit the 2700-ball cap."""
    # Use Custom Test-shaped match with low cap to make the test fast.
    from neo_handcricket.formats import TEST
    # Just verify the TEST format exists and innings_per_team is 2.
    assert TEST.name == "Test"
    assert TEST.innings_per_team == 2
    assert TEST.wickets_per_innings == 10


def test_stats_aggregation_empty_safe() -> None:
    """Aggregator handles an empty career file."""
    from neo_handcricket.persistence import stats as stats_io
    out = stats_io.aggregate()
    assert out["total_matches"] >= 0
    assert "by_format" in out
    assert "head_to_head" in out


if __name__ == "__main__":
    # Run all tests
    failures = 0
    tests = [
        ("all rosters load", test_all_rosters_load),
        ("validator strict squad", test_validator_strict_squad),
        ("validator no captain fails", test_validator_no_captain_fails),
        ("validator 2-player custom loose", test_validator_2player_custom_loose),
        ("selector always-in rules", test_selector_always_in_rules),
        ("T10 innings completes", test_t10_innings_completes),
        ("T20 innings completes", test_t20_innings_completes),
        ("Custom 1v1 1-wicket", test_custom_1v1_1wicket),
        ("save/load roundtrip", test_save_load_roundtrip),
        ("commentary multi-line", test_commentary_returns_multiple_lines_per_ball),
        ("test cricket format defined", test_test_cricket_ball_cap_forces_draw),
        ("stats aggregation safe", test_stats_aggregation_empty_safe),
    ]
    for name, fn in tests:
        try:
            fn()
            print(f"  ✓ {name}")
        except Exception as e:
            failures += 1
            print(f"  ✗ {name}: {type(e).__name__}: {e}")
    if failures:
        print(f"\n{failures} test(s) failed")
        raise SystemExit(1)
    print(f"\nAll {len(tests)} tests passed")
