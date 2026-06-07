"""Thin campaign / progression UI — renders career state, owns no logic."""
from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ..career import achievements as ach
from ..career import progression as prog


def render_dashboard(console: Console, state: dict[str, Any], earned: set[str]) -> None:
    """Show currency, owned/available unlocks and achievements. ``state`` is a
    progression dict; ``earned`` is the set of achievement ids unlocked so far."""
    currency = int(state.get("currency", 0))
    owned = list(state.get("unlocks", []))

    console.print(Panel(
        Text(f"💰 Reputation: {currency}", style="bold yellow"),
        title=Text("Campaign & Progression", style="bold cyan"),
        border_style="cyan",
    ))

    unlock_t = Table(title="Unlocks", show_lines=False)
    unlock_t.add_column("Item")
    unlock_t.add_column("Cost", justify="right")
    unlock_t.add_column("Status")
    for uid, spec in prog.UNLOCKS.items():
        if uid in owned:
            status = Text("✓ owned", style="green")
        elif currency >= int(spec["cost"]):
            status = Text("can unlock", style="bold yellow")
        else:
            status = Text("locked", style="dim")
        unlock_t.add_row(str(spec["label"]), str(spec["cost"]), status)
    console.print(unlock_t)

    ach_t = Table(title="Achievements", show_lines=False)
    ach_t.add_column("")
    ach_t.add_column("Achievement")
    for aid, spec in ach.ACHIEVEMENTS.items():
        mark = Text("🏆", style="bold yellow") if aid in earned else Text("·", style="dim")
        style = "white" if aid in earned else "dim"
        ach_t.add_row(mark, Text(str(spec["label"]), style=style))
    console.print(ach_t)

    done = len(earned & set(ach.ACHIEVEMENTS))
    console.print(Text(f"  {done}/{len(ach.ACHIEVEMENTS)} achievements earned", style="dim"))


def unlock_toast(console: Console, label: str) -> None:
    console.print(Panel(Text(f"🔓 Unlocked: {label}", style="bold green"), border_style="green"))
