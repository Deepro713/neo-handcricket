"""Paths and global constants."""
from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PACKAGE_ROOT = Path(__file__).resolve().parent

ROSTERS_DIR = PACKAGE_ROOT / "rosters" / "data"
SAVES_DIR = PROJECT_ROOT / "saves"
STATS_DIR = PROJECT_ROOT / "stats"

# Game tunables
TIMER_SECONDS = 3.0
RETOSS_CAP = 3                       # consecutive 0s before fair-flip fallback
EXTRAS_BASE_PCT = 0.05               # 5% base chance per ball for wide/no-ball
ADAPTIVE_WINDOW = 5                  # last N user picks tracked for adaptation
NUMBER_RANGE = range(0, 7)           # 0-6 inclusive
SAVE_SCHEMA_VERSION = 1

# Difficulty → adaptation alpha
DIFFICULTY_ALPHA = {
    "easy": 0.0,
    "medium": 0.3,
    "hard": 0.6,
}
