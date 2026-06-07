"""Optional local Textual TUI front-end (offline; no network).

Textual is an **optional** dependency (`pip install -e ".[tui]"`). This module is
safe to import without it — `is_available()` reports whether it can run, and
`run()` only imports Textual when actually launching, so the core CLI and the QA
gate never depend on it.
"""
from __future__ import annotations

from ..adapter import AdapterConfig, GameAdapter
from . import viewmodel


def is_available() -> bool:
    """True if Textual is installed and the TUI can run."""
    try:
        import textual  # noqa: F401
    except ImportError:
        return False
    return True


def run(config: AdapterConfig) -> None:
    """Launch the Textual TUI for one user-batting innings. Requires `[tui]`."""
    if not is_available():
        raise RuntimeError("Textual is not installed. Install with: pip install -e \".[tui]\"")

    from textual.app import App, ComposeResult
    from textual.widgets import Footer, Header, Input, Static

    adapter = GameAdapter(config)

    class HandCricketTUI(App):  # type: ignore[misc]
        TITLE = "neo-handcricket"
        BINDINGS = [("q", "quit", "Quit")]

        def compose(self) -> ComposeResult:
            yield Header()
            yield Static(id="board")
            yield Static(id="event")
            yield Input(placeholder="Pick 0–6", id="pick")
            yield Footer()

        def on_mount(self) -> None:
            self._refresh(None)

        def _refresh(self, events: list[tuple[str, str]] | None) -> None:
            state = adapter.state()
            self.query_one("#board", Static).update("\n".join(viewmodel.scoreboard_lines(state)))
            self.query_one("#event", Static).update(viewmodel.event_line(events or []))
            self.query_one("#pick", Input).placeholder = viewmodel.prompt_text(state)

        def on_input_submitted(self, message: Input.Submitted) -> None:
            raw = message.value.strip()
            message.input.value = ""
            if not raw.isdigit() or not (0 <= int(raw) <= 6) or adapter.is_complete:
                return
            res = adapter.submit_pick(int(raw))
            self._refresh(res["events"])

    HandCricketTUI().run()
