"""Conversational commentary engine.

Each ball produces a 2–3 line conversation across different commentators in
the active panel. Per-match, a panel of 2-3 commentators is randomly chosen
and stays for the whole match. Within each ball:

  Turn 1 (opener)   — the most extrovert commentator gives the immediate reaction
  Turn 2 (analysis) — a different commentator gives the technical/contextual line
  Turn 3 (quip)     — optionally, the funniest commentator throws in a quip

Antarctica trigger: when Antarctica is on the field, more lines come from the
`antarctica_special` pool, and `tag:hilarious` / `tag:theatrical` traits are
preferred for line picking.

Match log is updated with every line + structured event. Callbacks (~10% chance
on opener turn) reach back into the log to reference earlier moments.
"""
from __future__ import annotations

import random
from typing import Any

from .commentators import COMMENTATORS, Commentator
from .lines import LINES
from .log import CommentaryEntry, MatchLog


class CommentaryEngine:
    def __init__(self, *, rng: random.Random | None = None) -> None:
        self.rng = rng or random.Random()
        self.log = MatchLog()
        self._used_lines: set[str] = set()  # raw templates already used this match (variety)
        # The active panel of commentators for this match.
        # Number of commentators is randomized in [2, 3].
        self.panel: list[Commentator] = self._make_panel()

    # --- panel selection ---

    def _make_panel(self) -> list[Commentator]:
        panel_size = self.rng.randint(2, 3)
        # Pick distinct commentators, prefer different countries + at least one from each gender if size>=2
        pool = list(COMMENTATORS)
        self.rng.shuffle(pool)
        chosen: list[Commentator] = []
        seen_countries: set[str] = set()
        for c in pool:
            if c.country in seen_countries and len(chosen) < panel_size:
                continue
            chosen.append(c)
            seen_countries.add(c.country)
            if len(chosen) >= panel_size:
                break
        # If diversity-filtering left us short (it shouldn't), top up
        while len(chosen) < panel_size:
            for c in pool:
                if c not in chosen:
                    chosen.append(c)
                    break
        # Try to ensure mix of genders for size 2+
        if panel_size >= 2 and len({c.gender for c in chosen}) == 1:
            # swap one for an opposite-gender commentator
            target_gender = "F" if chosen[0].gender == "M" else "M"
            for c in pool:
                if c.gender == target_gender and c.country not in {x.country for x in chosen[:-1]}:
                    chosen[-1] = c
                    break
        return chosen[:panel_size]

    # --- commentator-selection helpers ---

    def _pick_for_turn(self, turn: str, used: list[Commentator], antarctica_mode: bool) -> Commentator:
        """Pick the most appropriate panelist for this turn, preferring not-yet-used."""
        eligible = [c for c in self.panel if c not in used] or list(self.panel)
        # Score each by trait match for the turn
        scored = []
        for c in eligible:
            score = 0
            traits = set(c.traits)
            if turn == "opener":
                if "extrovert" in traits:
                    score += 2
                if "theatrical" in traits:
                    score += 1
            elif turn == "analysis":
                if "technical" in traits:
                    score += 2
                if "serious" in traits:
                    score += 1
                if "traditional" in traits:
                    score += 1
            elif turn == "quip":
                if "hilarious" in traits:
                    score += 3
                if "dry" in traits:
                    score += 1
            if antarctica_mode and "hilarious" in traits:
                score += 2
            scored.append((score, self.rng.random(), c))
        scored.sort(key=lambda x: (-x[0], x[1]))
        return scored[0][2]

    # --- line selection ---

    def _matching_lines(self, situation: str, turn: str, traits: tuple[str, ...]) -> list[dict]:
        sit = LINES.get(situation, {})
        if not isinstance(sit, dict):
            return []
        candidates = sit.get(turn, []) or []
        if not candidates:
            return []
        scored = []
        for line in candidates:
            tags = set(line.get("tags", []))
            overlap = len(tags & set(traits))
            scored.append((overlap, self.rng.random(), line))
        scored.sort(key=lambda x: (-x[0], x[1]))
        cutoff = max(1, len(scored) // 2)
        return [line for _, _, line in scored[:cutoff]]

    def _format(self, template: str, ctx: dict[str, Any]) -> str:
        try:
            return template.format(**ctx)
        except (KeyError, IndexError):
            return template

    # --- public ---

    def commentate(
        self,
        *,
        situation: str,
        ctx: dict[str, Any],
        antarctica_on_field: bool = False,
    ) -> list[CommentaryEntry]:
        """Return a list of 2-3 commentary entries forming a conversation about this ball.

        For non-ball events (over_start, milestone_*, innings_end, match_end), returns
        a single entry (those are accent moments, not full conversations).
        """
        # Determine if this is a "full ball" event (gets multi-line conversation)
        ball_situations = {
            "ball_dot", "ball_run_1", "ball_run_2", "ball_run_3", "ball_run_4",
            "ball_run_5", "ball_run_6", "wicket_match", "wicket_bowled",
            "wicket_lbw", "wicket_caught", "wide", "no_ball", "dead_ball", "byes", "leg_byes",
        }
        is_ball = situation in ball_situations
        entries: list[CommentaryEntry] = []

        # Decide turn count: 2-3 for ball events, 1 for accent events
        if is_ball:
            turn_count = self.rng.randint(2, 3)
        else:
            turn_count = 1
        all_turns = ["opener", "analysis", "quip"]
        turns = all_turns[:turn_count]

        # Antarctica injection: ~25% chance to lead with an antarctica_special line for ball events
        antarctica_inject_first = (
            antarctica_on_field and is_ball and self.rng.random() < 0.25
        )

        used_commentators: list[Commentator] = []

        for i, turn in enumerate(turns):
            # Choose source situation for THIS turn
            if i == 0 and antarctica_inject_first:
                source_situation = "antarctica_special"
            else:
                source_situation = situation

            comm = self._pick_for_turn(turn, used_commentators, antarctica_on_field)
            used_commentators.append(comm)

            candidates = self._matching_lines(source_situation, turn, comm.traits)
            if not candidates:
                # Fall back to base situation, then any non-empty pool
                if source_situation != situation:
                    candidates = self._matching_lines(situation, turn, comm.traits)
                if not candidates and turn != "opener":
                    # No analysis/quip lines defined? skip turn
                    continue
                if not candidates:
                    candidates = [{"text": "...", "tags": []}]

            # Prefer a template not yet used this match (variety / no repeats).
            fresh = [c for c in candidates if c["text"] not in self._used_lines]
            line = self.rng.choice(fresh or candidates)
            self._used_lines.add(line["text"])
            text = self._format(line["text"], ctx)

            # Callback injection on analysis turn (~12% chance, requires history)
            if (
                turn == "analysis"
                and source_situation == situation
                and len(self.log.entries) > 6
                and self.rng.random() < 0.12
                and "striker_id" in ctx
            ):
                cb = self._build_callback(ctx, comm.traits)
                if cb:
                    text = f"{text} {cb}"

            entry = CommentaryEntry(
                over=ctx.get("over_num", 0),
                ball_in_over=ctx.get("ball_in_over", 0),
                situation=situation,
                line=text,
                commentator=comm.name,
                meta={
                    k: v for k, v in ctx.items()
                    if k in ("striker_id", "bowler_id", "runs", "wicket_kind", "extra_kind")
                },
            )
            self.log.append(entry)
            entries.append(entry)

        return entries

    def _build_callback(self, ctx: dict[str, Any], traits: tuple[str, ...]) -> str | None:
        striker_id = ctx.get("striker_id")
        if striker_id is None:
            return None
        prev = self.log.find_for_batter(striker_id)
        if prev is None:
            return None
        cb_pool = LINES.get("callback", {})
        all_cb = (cb_pool.get("analysis") or []) + (cb_pool.get("quip") or [])
        if not all_cb:
            return None
        # Filter by trait overlap
        scored = []
        for line in all_cb:
            tags = set(line.get("tags", []))
            score = len(tags & set(traits))
            scored.append((score, self.rng.random(), line))
        scored.sort(key=lambda x: (-x[0], x[1]))
        line = scored[0][2]
        prev_event_short = {
            "ball_run_4": "that boundary",
            "ball_run_6": "the big six",
            "ball_dot": "that watchful block",
        }.get(prev.situation, "that moment")
        return self._format(line["text"], {
            "prev_over": prev.over,
            "prev_batter": ctx.get("batter", "him"),
            "prev_event_short": prev_event_short,
        })

    @property
    def panel_summary(self) -> str:
        return ", ".join(f"{c.name} ({c.country})" for c in self.panel)
