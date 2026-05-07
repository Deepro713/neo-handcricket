"""Generate commentary lines from match state.

Active commentator rotates: switches every over (alternating gendered pairs from
different countries to keep it lively). Lines are picked by tag overlap with the
commentator's traits, with weighted randomness.

When Antarctica is on the field, we boost `tag:hilarious` and occasionally
inject lines from `antarctica_special`.
"""
from __future__ import annotations

import random
from typing import Any

from .commentators import COMMENTATORS, Commentator
from .lines import LINES, situation_for_ball
from .log import CommentaryEntry, MatchLog


class CommentaryEngine:
    def __init__(self, *, rng: random.Random | None = None) -> None:
        self.rng = rng or random
        self.log = MatchLog()
        # Active commentator pair indexes; we rotate per over.
        self._active_pair: tuple[Commentator, Commentator] = self._pick_pair()
        self._last_pair_over: int = -1

    # --- commentator selection ---

    def _pick_pair(self) -> tuple[Commentator, Commentator]:
        # Pick one M and one F from different countries
        males = [c for c in COMMENTATORS if c.gender == "M"]
        females = [c for c in COMMENTATORS if c.gender == "F"]
        m = self.rng.choice(males)
        f_pool = [c for c in females if c.country != m.country] or females
        f = self.rng.choice(f_pool)
        return (m, f)

    def maybe_rotate_pair(self, over_idx: int) -> None:
        if over_idx != self._last_pair_over and over_idx % 3 == 0:
            self._active_pair = self._pick_pair()
        self._last_pair_over = over_idx

    def pick_active_commentator(self) -> Commentator:
        return self.rng.choice(self._active_pair)

    # --- line selection ---

    def _matching_lines(self, situation: str, traits: tuple[str, ...]) -> list[dict]:
        candidates = LINES.get(situation, [])
        if not candidates:
            return []
        # Score each line by how many of its tags overlap with the commentator's traits
        scored = []
        for line in candidates:
            tags = set(line.get("tags", []))
            overlap = len(tags & set(traits))
            scored.append((overlap, line))
        # Prefer high-overlap, but allow low-overlap occasionally
        scored.sort(key=lambda x: (-x[0], self.rng.random()))
        # Take top half
        cutoff = max(1, len(scored) // 2)
        return [line for _, line in scored[:cutoff]]

    def _format_line(self, template: str, ctx: dict[str, Any]) -> str:
        try:
            return template.format(**ctx)
        except (KeyError, IndexError):
            # Missing placeholder — fall back to template as-is
            return template

    # --- public ---

    def commentate(
        self,
        *,
        situation: str,
        ctx: dict[str, Any],
        antarctica_on_field: bool = False,
    ) -> CommentaryEntry:
        comm = self.pick_active_commentator()

        # Antarctica special injection: ~30% chance to swap in an antarctica_special line
        if antarctica_on_field and situation.startswith("ball_") and self.rng.random() < 0.30:
            situation_to_use = "antarctica_special"
        else:
            situation_to_use = situation

        # When Antarctica is in play, prefer the hilarious slot of the pair
        traits = comm.traits
        if antarctica_on_field:
            funny = [c for c in self._active_pair if "hilarious" in c.traits]
            if funny:
                comm = self.rng.choice(funny)
                traits = comm.traits

        candidates = self._matching_lines(situation_to_use, traits)
        if not candidates:
            candidates = LINES.get(situation_to_use) or LINES.get(situation) or [{"text": "...", "tags": []}]

        line = self.rng.choice(candidates)
        text = self._format_line(line["text"], ctx)

        # Callback injection (~12% chance for non-special situations, when log has history)
        if (
            situation_to_use != "antarctica_special"
            and len(self.log.entries) > 6
            and self.rng.random() < 0.12
            and "striker_id" in ctx
        ):
            cb = self._build_callback(ctx)
            if cb:
                text = f"{text} {cb}"

        entry = CommentaryEntry(
            over=ctx.get("over_num", 0),
            ball_in_over=ctx.get("ball_in_over", 0),
            situation=situation,
            line=text,
            commentator=comm.name,
            meta={k: v for k, v in ctx.items() if k in ("striker_id", "bowler_id", "runs", "wicket_kind", "extra_kind")},
        )
        self.log.append(entry)
        return entry

    def _build_callback(self, ctx: dict[str, Any]) -> str | None:
        striker_id = ctx.get("striker_id")
        if striker_id is None:
            return None
        prev = self.log.find_for_batter(striker_id)
        if prev is None:
            return None
        templates = LINES.get("callback", [])
        if not templates:
            return None
        tmpl = self.rng.choice(templates)
        prev_event_short = {
            "ball_run_4": "that boundary",
            "ball_run_6": "the big six",
            "ball_dot": "that watchful block",
        }.get(prev.situation, "that moment")
        return self._format_line(tmpl["text"], {
            "prev_over": prev.over,
            "prev_batter": ctx.get("batter", "him"),
            "prev_event_short": prev_event_short,
        })
