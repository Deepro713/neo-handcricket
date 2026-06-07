"""Thin daily-challenge UI — renders the challenge + your best, owns no logic."""
from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from ..daily import modifiers as mods
from ..daily.seed import DailyChallenge


def render_daily(console: Console, challenge: DailyChallenge, best: dict[str, Any] | None) -> None:
    body = Text()
    body.append(f"{challenge.date_iso}\n", style="bold")
    body.append(f"{challenge.fmt}  ", style="bold cyan")
    body.append(f"{challenge.team_a} vs {challenge.team_b}", style="bold")
    body.append(f"   ({challenge.difficulty})\n\n", style="dim")
    body.append("Modifiers:\n", style="bold")
    if challenge.modifiers:
        for mid in challenge.modifiers:
            body.append(f"  • {mods.label(mid)}\n")
    else:
        body.append("  • (none today)\n", style="dim")
    if best:
        body.append(f"\nYour best: {best.get('score', 0)}", style="bold yellow")
        if best.get("summary"):
            body.append(f"  ({best['summary']})", style="dim")
    else:
        body.append("\nNo attempt yet today — set the pace!", style="dim italic")
    console.print(Panel(body, title=Text("🗓️  Daily Challenge", style="bold cyan"), border_style="cyan"))


def render_result(console: Console, score: int, share_code: str) -> None:
    console.print(Panel(
        Text(f"Daily score: {score}\n\nShare code (offline):\n{share_code}", style="bold"),
        title=Text("Daily result", style="bold green"), border_style="green",
    ))
