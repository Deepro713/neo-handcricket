"""Match commentary log — append every line + structured event for callbacks."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CommentaryEntry:
    over: int                # 0-indexed
    ball_in_over: int        # 1-6 (0 if pre/post-over flavor)
    situation: str
    line: str
    commentator: str
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class MatchLog:
    entries: list[CommentaryEntry] = field(default_factory=list)

    def append(self, entry: CommentaryEntry) -> None:
        self.entries.append(entry)

    def recent(self, n: int = 10) -> list[CommentaryEntry]:
        return self.entries[-n:]

    def find_for_batter(self, batter_id: int, exclude_situation: str | None = None) -> CommentaryEntry | None:
        for e in reversed(self.entries):
            if e.meta.get("striker_id") != batter_id:
                continue
            if exclude_situation and e.situation == exclude_situation:
                continue
            return e
        return None

    def boundary_count_for_batter(self, batter_id: int) -> int:
        return sum(
            1 for e in self.entries
            if e.meta.get("striker_id") == batter_id and e.situation in ("ball_run_4", "ball_run_6")
        )
