"""20 commentator personalities — 5 cricket nations × 2M + 2F."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Commentator:
    name: str
    country: str
    gender: str           # "M" | "F"
    traits: tuple[str, ...]


# Trait vocabulary:
#   serious / hilarious
#   technical / casual
#   theatrical / dry
#   extrovert / introvert
#   traditional / modern

COMMENTATORS: list[Commentator] = [
    # --- India ---
    Commentator("Rajat Thapliyal",      "India",        "M", ("hilarious", "extrovert", "theatrical", "modern")),
    Commentator("Vikram Iyer",          "India",        "M", ("serious",   "technical", "dry",        "traditional")),
    Commentator("Anjali Mukherjee",     "India",        "F", ("hilarious", "extrovert", "casual",     "modern")),
    Commentator("Nandita Krishnamurthy","India",        "F", ("serious",   "technical", "traditional")),

    # --- England ---
    Commentator("Geoffrey Pemberton",   "England",      "M", ("serious",   "technical", "dry",        "traditional")),
    Commentator("Marcus Whitfield",     "England",      "M", ("hilarious", "extrovert", "theatrical")),
    Commentator("Eleanor Hartwell",     "England",      "F", ("serious",   "modern",    "casual")),
    Commentator("Helena Crowhurst",     "England",      "F", ("hilarious", "dry",       "introvert")),

    # --- Australia ---
    Commentator("Mick Carraway",        "Australia",    "M", ("hilarious", "extrovert", "casual")),
    Commentator("Reg Prentice",         "Australia",    "M", ("serious",   "dry",       "technical")),
    Commentator("Charlene Dell",        "Australia",    "F", ("theatrical","extrovert", "casual")),
    Commentator("Sandra Whitford",      "Australia",    "F", ("serious",   "technical", "traditional")),

    # --- Pakistan ---
    Commentator("Imran Sajjad",         "Pakistan",     "M", ("serious",   "theatrical","traditional")),
    Commentator("Zaheer Kamali",        "Pakistan",     "M", ("hilarious", "extrovert", "casual")),
    Commentator("Sana Aziz",            "Pakistan",     "F", ("serious",   "modern",    "technical")),
    Commentator("Faryal Tariq",         "Pakistan",     "F", ("hilarious", "dry",       "introvert")),

    # --- West Indies ---
    Commentator("Vivian Hartwell",      "West Indies",  "M", ("hilarious", "theatrical","extrovert")),
    Commentator("Calypso Brathwaite",   "West Indies",  "M", ("serious",   "dry",       "technical")),
    Commentator("Marlene Daniels",      "West Indies",  "F", ("theatrical","extrovert", "casual")),
    Commentator("Cherise Springer",     "West Indies",  "F", ("serious",   "modern",    "traditional")),
]


def by_name(name: str) -> Commentator:
    for c in COMMENTATORS:
        if c.name == name:
            return c
    raise KeyError(name)
