"""Unit tests for the onboarding tutorial model (M010)."""
from __future__ import annotations

from rich.console import Console

from neo_handcricket import onboarding
from neo_handcricket.ui import tutorial as ui_tutorial


def test_steps_complete_and_nonempty() -> None:
    assert len(onboarding.TUTORIAL_STEPS) >= 5
    for s in onboarding.TUTORIAL_STEPS:
        assert s.title.strip() and s.body.strip()
    titles = " ".join(s.title.lower() + " " + s.body.lower() for s in onboarding.TUTORIAL_STEPS)
    # Covers the essentials the tutorial must explain.
    for topic in ("number", "out", "bat", "bowl", "format", "control"):
        assert topic in titles


def test_advance_to_done() -> None:
    t = onboarding.Tutorial()
    assert not t.done and t.index == 0
    for _ in range(t.total):
        t.advance()
    assert t.done


def test_back_does_not_underflow() -> None:
    t = onboarding.Tutorial()
    t.back()
    assert t.index == 0
    t.advance()
    t.advance()
    t.back()
    assert t.index == 1


def test_skip_ends_immediately() -> None:
    t = onboarding.Tutorial()
    t.skip()
    assert t.done and t.skipped


def test_replay_resets() -> None:
    t = onboarding.Tutorial()
    for _ in range(t.total):
        t.advance()
    assert t.done
    t.replay()
    assert not t.done and t.index == 0 and not t.skipped


def test_current_is_stable_at_end() -> None:
    t = onboarding.Tutorial()
    for _ in range(t.total + 3):
        t.advance()
    assert t.current == onboarding.TUTORIAL_STEPS[-1]


def test_render_step_smoke() -> None:
    console = Console(file=open("/dev/null", "w"), force_terminal=False)
    ui_tutorial.render_step(console, onboarding.Tutorial())
