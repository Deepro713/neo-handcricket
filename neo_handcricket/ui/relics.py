"""Thin relic draft / owned-relics UI (no logic)."""
from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ..career import relics


def render_owned(console: Console, owned: list[str]) -> None:
    if not owned:
        console.print(Text("  No relics yet — win rounds to draft them.", style="dim"))
        return
    t = Table(title="Your relics", show_lines=False)
    t.add_column("Relic")
    t.add_column("Effect", style="dim")
    for rid in owned:
        t.add_row(relics.relic_label(rid), relics.relic_desc(rid))
    console.print(t)


def render_draft(console: Console, offer: list[str]) -> None:
    console.print(Panel(Text("Draft a relic", style="bold cyan"), border_style="cyan"))
    for i, rid in enumerate(offer, 1):
        console.print(f"  [yellow]{i}[/yellow]  [bold]{relics.relic_label(rid)}[/bold] — {relics.relic_desc(rid)}")
    console.print("  [yellow]0[/yellow]  Decline")
