"""Unit tests for accessibility helpers (M010)."""
from __future__ import annotations

from neo_handcricket import a11y, config


def test_color_disabled_by_no_color(monkeypatch) -> None:
    monkeypatch.setenv("NO_COLOR", "1")
    assert a11y.color_enabled() is False
    monkeypatch.setenv("NO_COLOR", "")   # presence (even empty) disables
    assert a11y.color_enabled() is False


def test_color_enabled_by_default(monkeypatch) -> None:
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.delenv("NHC_A11Y", raising=False)
    monkeypatch.setattr(config, "A11Y_MODE", False)
    assert a11y.color_enabled() is True


def test_a11y_mode_disables_colour_and_animation(monkeypatch) -> None:
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setenv("NHC_A11Y", "1")
    assert a11y.a11y_enabled() is True
    assert a11y.color_enabled() is False
    assert a11y.animations_enabled() is False


def test_a11y_via_config_flag(monkeypatch) -> None:
    monkeypatch.delenv("NHC_A11Y", raising=False)
    monkeypatch.setattr(config, "A11Y_MODE", True)
    assert a11y.a11y_enabled() is True
    monkeypatch.setattr(config, "A11Y_MODE", False)
    monkeypatch.delenv("NHC_A11Y", raising=False)
    assert a11y.a11y_enabled() is False


def test_env_off_values_are_off(monkeypatch) -> None:
    for val in ("0", "false", "no", "off", ""):
        monkeypatch.setenv("NHC_A11Y", val)
        assert a11y.a11y_enabled() is False


def test_timer_seconds_and_untimed(monkeypatch) -> None:
    monkeypatch.delenv("NHC_UNTIMED", raising=False)
    monkeypatch.setattr(config, "TIMER_UNTIMED", False)
    assert a11y.timer_seconds() == float(config.TIMER_SECONDS)
    monkeypatch.setattr(config, "TIMER_UNTIMED", True)
    assert a11y.timer_seconds() is None
    monkeypatch.setattr(config, "TIMER_UNTIMED", False)
    monkeypatch.setenv("NHC_UNTIMED", "1")
    assert a11y.timer_seconds() is None


def test_signal_every_state_has_glyph_and_word() -> None:
    # Colour-never-alone: each signalling state carries a non-empty glyph AND label.
    for state, (glyph, label) in a11y.SIGNALS.items():
        assert glyph.strip(), state
        assert label.strip(), state
    # Required signalling states are all present.
    for required in ("wicket", "boundary4", "boundary6", "win", "loss", "draw", "timer_warn", "milestone"):
        assert required in a11y.SIGNALS


def test_signal_lookup_fallback() -> None:
    glyph, label = a11y.signal("unknown_state")
    assert glyph and label == "unknown_state"
