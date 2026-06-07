"""Validate user-supplied rosters (in-game wizard output)."""
from __future__ import annotations

from dataclasses import dataclass

from .loader import Country


@dataclass
class ValidationResult:
    ok: bool
    errors: list[str]


def validate(country: Country, *, playing_size: int) -> ValidationResult:
    """Permissive validation (Q10b-ii):
       - Always need at least playing_size named players.
       - When squad >= 11: require captain + vice-captain + >= 3 keepers.
       - For sub-11 custom matches: just need names.
    """
    errors: list[str] = []
    n = len(country.players)
    if n < playing_size:
        errors.append(f"Need at least {playing_size} players (got {n}).")

    if n >= 11:
        captains = [p for p in country.players if p.role == "captain"]
        vcs = [p for p in country.players if p.role == "vice-captain"]
        keepers = [p for p in country.players if p.role in ("keeper", "keeper-reserve")]
        if len(captains) != 1:
            errors.append(f"Need exactly 1 captain (got {len(captains)}).")
        if len(vcs) != 1:
            errors.append(f"Need exactly 1 vice-captain (got {len(vcs)}).")
        if len(keepers) < 3:
            errors.append(f"Need at least 3 keepers (got {len(keepers)}).")

    return ValidationResult(ok=not errors, errors=errors)
