"""Unit tests for relics registry + draft (M012)."""
from __future__ import annotations

from neo_handcricket.career import relics


def test_apply_empty_is_defaults() -> None:
    assert relics.apply_relics([]) == relics.EFFECTIVE_DEFAULTS


def test_effect_is_correct_and_bounded() -> None:
    eff = relics.apply_relics(["short_rope"])
    assert eff["boundary_value_bonus"] == 1.0
    assert relics.apply_relics(["marathoners"])["fatigue_mult"] == 0.5


def test_compose_order_independent() -> None:
    ids = ["short_rope", "marathoners", "merchant"]
    a = relics.apply_relics(ids)
    b = relics.apply_relics(list(reversed(ids)))
    assert a == b


def test_mult_relics_multiply() -> None:
    eff = relics.apply_relics(["marathoners", "fresh_attack"])  # 0.5 * 0.8
    assert abs(eff["fatigue_mult"] - 0.4) < 1e-9
    assert relics.apply_relics(["merchant"])["currency_mult"] == 1.5


def test_bonus_relics_add() -> None:
    eff = relics.apply_relics(["short_rope", "big_hitter"])  # +1 +2
    assert eff["boundary_value_bonus"] == 3.0


def test_unknown_relic_ignored() -> None:
    assert relics.apply_relics(["does_not_exist"]) == relics.EFFECTIVE_DEFAULTS


def test_draft_offer_deterministic_and_excludes_owned() -> None:
    o1 = relics.draft_offer(123, owned=[])
    o2 = relics.draft_offer(123, owned=[])
    assert o1 == o2 and len(o1) == 3
    owned = [o1[0]]
    nxt = relics.draft_offer(123, owned=owned)
    assert owned[0] not in nxt


def test_draft_offer_caps_at_pool_size() -> None:
    all_owned = list(relics.RELICS)[:-2]
    offer = relics.draft_offer(1, owned=all_owned, count=5)
    assert len(offer) == 2 and all(r not in all_owned for r in offer)


def test_choose_adds_and_respects_offer() -> None:
    offer = relics.draft_offer(7, owned=[])
    owned = relics.choose([], offer[0], offer=offer)
    assert owned == [offer[0]]
    # already owned → no-op
    assert relics.choose(owned, offer[0], offer=offer) == owned
    # not on offer → no-op
    not_offered = next(r for r in relics.RELICS if r not in offer)
    assert relics.choose(owned, not_offered, offer=offer) == owned
    # unknown → no-op
    assert relics.choose(owned, "nope") == owned


def test_labels_and_desc() -> None:
    assert relics.relic_label("short_rope") == "Short Rope"
    assert "boundaries" in relics.relic_desc("short_rope").lower()
    assert relics.relic_label("unknown") == "unknown"
