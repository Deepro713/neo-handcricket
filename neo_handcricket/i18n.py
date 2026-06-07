"""Localization scaffold (pure logic).

A locale-keyed string table with English (``en``) as the default and fallback. The
structure lets the (currently English-only) user-facing strings be translated later
without code changes — add a locale mapping and the same keys resolve. No real
translations are shipped yet; this is the scaffold + a couple of wired strings as a
proof. All strings are original.
"""
from __future__ import annotations

DEFAULT_LOCALE = "en"

STRINGS: dict[str, dict[str, str]] = {
    "en": {
        "app.tagline": "hand cricket — but make it a real fixture",
        "menu.new": "New match",
        "menu.daily": "Daily challenge",
        "menu.load": "Load a save",
        "menu.stats": "Career stats",
        "menu.career": "Campaign & progression",
        "menu.tutorial": "How to play (tutorial)",
        "menu.quit": "Quit",
        "common.bye": "bye",
        "toss.call": "Call it: heads / tails",
        "result.you_won": "You won!",
        "result.you_lost": "You lost.",
        "result.draw": "Match drawn.",
        "pick.bat": "BAT — pick 0–6",
        "pick.bowl": "BOWL — pick 0–6",
    },
}


def available_locales() -> list[str]:
    return sorted(STRINGS)


def add_locale(locale: str, mapping: dict[str, str]) -> None:
    """Register/extend a locale's strings (for translations / tests)."""
    STRINGS.setdefault(locale, {}).update(mapping)


def t(key: str, locale: str = DEFAULT_LOCALE, **fmt: object) -> str:
    """Look up ``key`` in ``locale``, falling back to the default locale, then to the
    key itself. Optional ``**fmt`` are applied with ``str.format``."""
    val = STRINGS.get(locale, {}).get(key)
    if val is None:
        val = STRINGS[DEFAULT_LOCALE].get(key, key)
    if fmt:
        try:
            return val.format(**fmt)
        except (KeyError, IndexError):
            return val
    return val
