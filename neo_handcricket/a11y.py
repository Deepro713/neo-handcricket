"""Accessibility helpers (mostly pure).

A single source of truth for the UI's accessibility decisions:
- **colour** is disabled when `NO_COLOR` is set (community standard) or in a11y mode;
- **a11y mode** (static, no-animation, screen-reader-friendlier) is on via the
  `NHC_A11Y` env var or `config.A11Y_MODE`;
- **animations** (the redraw timer bar) are off in a11y mode;
- the per-ball **timer** can be disabled (untimed) via `NHC_UNTIMED` / `config.TIMER_UNTIMED`.

It also provides a **colour-never-alone** signal map so meaning is always carried by a
glyph + word, not colour alone. Only the env reads touch the environment; the rest
is pure and takes explicit overrides for testing.
"""
from __future__ import annotations

import os

from . import config


def _env_set(name: str) -> bool:
    """True when an env var is present and not an explicit off value."""
    val = os.environ.get(name)
    if val is None:
        return False
    return val.strip().lower() not in ("", "0", "false", "no", "off")


def a11y_enabled(*, override: bool | None = None) -> bool:
    if override is not None:
        return override
    return _env_set("NHC_A11Y") or bool(config.A11Y_MODE)


def color_enabled(*, a11y: bool | None = None) -> bool:
    # NO_COLOR (community standard): present → disable colour, regardless of value.
    if os.environ.get("NO_COLOR") is not None:
        return False
    return not a11y_enabled(override=a11y)


def animations_enabled(*, a11y: bool | None = None) -> bool:
    return not a11y_enabled(override=a11y)


def timer_seconds(*, untimed: bool | None = None) -> float | None:
    """The per-ball timer length, or None when untimed (no timeout)."""
    is_untimed = untimed if untimed is not None else (_env_set("NHC_UNTIMED") or bool(config.TIMER_UNTIMED))
    return None if is_untimed else float(config.TIMER_SECONDS)


# --- Colour-never-alone signal map (glyph + word, never colour alone) ---
SIGNALS: dict[str, tuple[str, str]] = {
    "wicket":     ("✖", "OUT"),
    "boundary4":  ("→", "FOUR"),
    "boundary6":  ("⇒", "SIX"),
    "dot":        ("·", "dot"),
    "win":        ("✓", "WON"),
    "loss":       ("✗", "LOST"),
    "draw":       ("=", "DRAW"),
    "tie":        ("≈", "TIE"),
    "timer_ok":   ("●", "time"),
    "timer_warn": ("!", "hurry"),
    "milestone":  ("★", "milestone"),
}


def signal(state: str) -> tuple[str, str]:
    """Return ``(glyph, label)`` for a signalling state — both always non-empty so
    meaning never relies on colour alone."""
    return SIGNALS.get(state, ("•", state))
