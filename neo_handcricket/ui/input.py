"""Single-keystroke input + 3-second timer with audible BEL.

Unix-only (macOS / Linux). Uses termios + tty + select.

Public API:
    read_key()                            — block until a key is pressed; return the char
    read_key_with_timer(secs, tick=None)  — read one key with timeout; tick callback fires periodically
    beep()                                — audible BEL
    is_tty()                              — True if stdin is a TTY (raw mode safe)
"""
from __future__ import annotations

import contextlib
import select
import sys
import termios
import time
import tty
from collections.abc import Callable


def is_tty() -> bool:
    return sys.stdin.isatty() and sys.stdout.isatty()


def beep() -> None:
    try:
        sys.stdout.write("\a")
        sys.stdout.flush()
    except Exception:
        pass


@contextlib.contextmanager
def _cbreak_mode():
    if not is_tty():
        yield
        return
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        yield
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def read_key() -> str:
    """Block until a key is pressed; return the single character (no echo)."""
    if not is_tty():
        line = sys.stdin.readline()
        return line[:1] if line else ""
    with _cbreak_mode():
        return sys.stdin.read(1)


def read_key_with_timer(
    timeout: float,
    *,
    tick: Callable[[float], None] | None = None,
    tick_interval: float = 0.1,
) -> str | None:
    """Read one key with timeout. Returns the char or None on timeout.

    `tick(remaining_seconds)` is called periodically so the UI can render a countdown.
    """
    if not is_tty():
        # Non-interactive fallback: just read or timeout via line buffer
        ready, _, _ = select.select([sys.stdin], [], [], timeout)
        if ready:
            line = sys.stdin.readline()
            return line[:1] if line else None
        return None

    with _cbreak_mode():
        deadline = time.monotonic() + timeout
        if tick:
            tick(timeout)
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                if tick:
                    tick(0.0)
                return None
            wait = min(tick_interval, remaining)
            ready, _, _ = select.select([sys.stdin], [], [], wait)
            if ready:
                return sys.stdin.read(1)
            if tick:
                tick(max(0.0, deadline - time.monotonic()))


def read_line(prompt: str = "") -> str:
    """Read a full line (Enter-terminated) from stdin."""
    try:
        return input(prompt)
    except EOFError:
        return ""
