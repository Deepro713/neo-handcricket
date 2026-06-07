"""Thin renderer + driver for the onboarding tutorial (no game logic)."""
from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from ..onboarding import Tutorial
from .input import read_key


def render_step(console: Console, tut: Tutorial) -> None:
    step = tut.current
    body = Text()
    body.append(step.body + "\n\n", style="default")
    body.append(f"  step {min(tut.index + 1, tut.total)}/{tut.total}", style="dim")
    body.append("    [n]ext · [b]ack · [s]kip", style="dim")
    console.print(Panel(body, title=Text(f"📖  {step.title}", style="bold cyan"), border_style="cyan"))


def run_tutorial(console: Console) -> None:
    """Walk the tutorial. Thin: reads keys, advances the pure model, renders."""
    tut = Tutorial()
    while not tut.done:
        console.clear()
        render_step(console, tut)
        ch = read_key().lower()
        if ch == "b":
            tut.back()
        elif ch == "s":
            tut.skip()
        else:
            tut.advance()
