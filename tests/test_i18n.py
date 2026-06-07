"""Unit tests for the localization scaffold (M013)."""
from __future__ import annotations

from neo_handcricket import i18n


def test_default_locale_lookup() -> None:
    assert i18n.t("menu.new") == "New match"
    assert i18n.t("common.bye") == "bye"


def test_unknown_key_returns_key() -> None:
    assert i18n.t("does.not.exist") == "does.not.exist"


def test_unknown_locale_falls_back_to_en() -> None:
    assert i18n.t("menu.quit", locale="xx") == i18n.t("menu.quit", locale="en")


def test_stub_locale_overrides_then_falls_back() -> None:
    i18n.add_locale("zz", {"menu.quit": "Leave"})
    try:
        assert i18n.t("menu.quit", locale="zz") == "Leave"      # overridden
        assert i18n.t("menu.new", locale="zz") == "New match"   # falls back to en
        assert "zz" in i18n.available_locales()
    finally:
        i18n.STRINGS.pop("zz", None)


def test_format_args() -> None:
    i18n.add_locale("fmt", {"greet": "Hi {name}"})
    try:
        assert i18n.t("greet", locale="fmt", name="Ari") == "Hi Ari"
        # Missing format arg degrades gracefully to the template.
        assert i18n.t("greet", locale="fmt") == "Hi {name}"
    finally:
        i18n.STRINGS.pop("fmt", None)


def test_en_is_default_and_available() -> None:
    assert i18n.DEFAULT_LOCALE == "en"
    assert "en" in i18n.available_locales()
