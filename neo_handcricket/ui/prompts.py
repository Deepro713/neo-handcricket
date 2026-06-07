"""Pre-match prompts and menus."""
from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ..formats import PRESETS, Format
from ..formats import custom as custom_fmt
from ..rosters import loader
from .input import read_key, read_line


def main_menu(console: Console) -> str:
    """Return one of: 'new', 'daily', 'load', 'stats', 'career', 'tutorial', 'quit'."""
    console.clear()
    console.print(Panel(
        Text("neo-handcricket\n  hand cricket — but make it a real fixture", style="bold cyan", justify="left"),
        border_style="cyan",
    ))
    options = [
        ("n", "New match"),
        ("d", "Daily challenge"),
        ("l", "Load a save"),
        ("s", "Career stats"),
        ("c", "Campaign & progression"),
        ("h", "How to play (tutorial)"),
        ("q", "Quit"),
    ]
    for k, label in options:
        console.print(f"  [bold yellow]{k}[/bold yellow]  {label}")
    console.print()
    while True:
        ch = read_key().lower()
        if ch in ("n", "d", "l", "s", "c", "h", "q"):
            return {"n": "new", "d": "daily", "l": "load", "s": "stats",
                    "c": "career", "h": "tutorial", "q": "quit"}[ch]


def select_country(console: Console, *, prompt: str, exclude: str | None = None) -> str:
    """Type-to-search country selection. Returns slug."""
    countries = loader.list_countries()
    if exclude:
        countries = [c for c in countries if c != exclude]
    while True:
        console.print(Panel(Text(prompt, style="bold"), border_style="green"))
        console.print("  Type to search, or paste a number from the list. Empty input = list all.\n")
        # Show top-10 alphabetical preview
        preview = countries[:14]
        for i, slug in enumerate(preview, 1):
            try:
                c = loader.load_country(slug)
                console.print(f"   {i:2}. {c.flag} {c.country}")
            except Exception:
                console.print(f"   {i:2}. {slug}")
        if len(countries) > 14:
            console.print(f"   ... and {len(countries) - 14} more")
        console.print()
        query = read_line("  > ").strip().lower()
        if not query:
            # Show all
            console.print()
            for i, slug in enumerate(countries, 1):
                try:
                    c = loader.load_country(slug)
                    console.print(f"   {i:2}. {c.flag} {c.country}")
                except Exception:
                    console.print(f"   {i:2}. {slug}")
            console.print()
            continue
        # Number?
        if query.isdigit():
            idx = int(query) - 1
            if 0 <= idx < len(countries):
                return countries[idx]
        # Substring match
        matches = [s for s in countries if query in s.lower() or query in loader.load_country(s).country.lower()]
        if not matches:
            console.print("[yellow]  no match — try again[/yellow]")
            continue
        if len(matches) == 1:
            slug = matches[0]
            c = loader.load_country(slug)
            console.print(f"  ✓ Selected: {c.flag} {c.country}\n")
            return slug
        console.print("  Multiple matches:")
        for i, slug in enumerate(matches, 1):
            c = loader.load_country(slug)
            console.print(f"   {i}. {c.flag} {c.country}")
        sel = read_line("  pick number > ").strip()
        if sel.isdigit() and 1 <= int(sel) <= len(matches):
            slug = matches[int(sel) - 1]
            c = loader.load_country(slug)
            console.print(f"  ✓ Selected: {c.flag} {c.country}\n")
            return slug


def select_format(console: Console) -> Format:
    console.print(Panel(Text("Choose match format", style="bold"), border_style="green"))
    table = Table.grid(padding=(0, 2))
    table.add_column(style="bold yellow")
    table.add_column()
    table.add_column(style="dim")
    table.add_row("1", "T10",   "10 ov · 10 wkts · 1 innings/team")
    table.add_row("2", "T20",   "20 ov · 10 wkts · 1 innings/team")
    table.add_row("3", "ODI",   "50 ov · 10 wkts · 1 innings/team")
    table.add_row("4", "Test",  "5 days · 90 ov/day cap · 4 innings · 10 wkts (v1: scaffolded)")
    table.add_row("5", "Custom","you pick everything")
    console.print(table)
    while True:
        ch = read_key()
        if ch == "1":
            return PRESETS["T10"]
        if ch == "2":
            return PRESETS["T20"]
        if ch == "3":
            return PRESETS["ODI"]
        if ch == "4":
            return PRESETS["Test"]
        if ch == "5":
            return custom_mode_wizard(console)


def custom_mode_wizard(console: Console) -> Format:
    """Innings → overs → wickets per Q8b-ii."""
    console.print(Panel(Text("Custom mode — answer 3 questions", style="bold"), border_style="green"))
    while True:
        s = read_line("  Innings per team (1 or 2): ").strip() or "1"
        if s.isdigit() and int(s) in (1, 2):
            innings = int(s)
            break
    while True:
        s = read_line("  Overs per innings (number, or '-' for no over cap): ").strip() or "20"
        if s == "-":
            overs = None
            break
        if s.isdigit() and int(s) > 0:
            overs = int(s)
            break
    while True:
        s = read_line("  Wickets per innings (>=1): ").strip() or "10"
        if s.isdigit() and int(s) >= 1:
            wickets = int(s)
            break
    while True:
        s = read_line("  Players per side (default 11; can be smaller for casual games): ").strip() or "11"
        if s.isdigit() and int(s) >= 1:
            playing = int(s)
            break
    return custom_fmt(overs=overs, wickets=wickets, innings_per_team=innings, playing_size=playing)


def select_timer(console: Console) -> bool:
    """Ask whether to play untimed (accessibility). Returns True for untimed."""
    console.print(Panel(Text("Per-ball timer", style="bold"), border_style="green"))
    console.print("  [yellow]t[/yellow]  Timed (3s per ball — the classic feel)")
    console.print("  [yellow]u[/yellow]  Untimed (take your time — no timeout)")
    while True:
        ch = read_key().lower()
        if ch in ("t", "u"):
            return ch == "u"


def select_difficulty(console: Console) -> str:
    console.print(Panel(Text("Choose difficulty", style="bold"), border_style="green"))
    console.print("  [yellow]e[/yellow]  Easy   — base profiles, plays its archetype (won't read you)")
    console.print("  [yellow]m[/yellow]  Medium — reads your patterns lightly, stays unpredictable")
    console.print("  [yellow]h[/yellow]  Hard   — reads frequency, WSLS & sequences; exploits more")
    console.print("  [yellow]l[/yellow]  Legend — full opponent model, exploits hard (punishes patterns)")
    while True:
        ch = read_key().lower()
        if ch in ("e", "m", "h", "l"):
            return {"e": "easy", "m": "medium", "h": "hard", "l": "legend"}[ch]


def choose_bat_or_bowl(console: Console) -> str:
    console.print("  Bat or bowl?  [yellow]b[/yellow]at  /  [yellow]B[/yellow]owl   ", end="")
    while True:
        ch = read_key().lower()
        if ch == "b":
            console.print("[bold]Bat[/bold]")
            return "bat"
        if ch == "B" or ch == "o":
            console.print("[bold]Bowl[/bold]")
            return "bowl"
        # Both lowercase 'b' for bat, lowercase 'o' for bowl (compromise)
        if ch == "b":
            return "bat"


def confirm_continue(console: Console, prompt: str = "Press any key to continue...") -> None:
    console.print(Text("  " + prompt, style="dim italic"))
    read_key()


def pause_menu(console: Console) -> str:
    """Return one of: 'resume', 'save', 'quit'."""
    console.print(Panel(Text("Pause menu", style="bold"), border_style="yellow"))
    console.print("  [yellow]r[/yellow]  Resume")
    console.print("  [yellow]s[/yellow]  Save and continue")
    console.print("  [yellow]Q[/yellow]  Quit (auto-saves first)")
    while True:
        ch = read_key().lower()
        if ch == "r":
            return "resume"
        if ch == "s":
            return "save"
        if ch == "q":
            return "quit"
