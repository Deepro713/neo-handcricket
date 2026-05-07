"""Bowler-archetype overlay shown at the start of each over."""
from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from ..rosters.loader import Player


def show_bowler_card(console: Console, bowler: Player, over_num: int, country_name: str) -> None:
    body = Text()
    body.append(bowler.name + "\n", style="bold")
    style_line = []
    if bowler.bowling_style:
        style_line.append(bowler.bowling_style)
    if bowler.batting_archetype:
        style_line.append(bowler.batting_archetype)
    if style_line:
        body.append(" · ".join(style_line), style="dim")
    title = Text(f"Over {over_num + 1} · {country_name} bowling", style="cyan bold")
    console.print(Panel(body, title=title, border_style="cyan", padding=(0, 2), expand=False))


def show_over_pause_hint(console: Console, message: str = "Press any key to continue") -> None:
    console.print(Text(f"  ⏸  {message}", style="dim italic"))
