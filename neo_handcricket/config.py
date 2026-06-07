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
INTER_BALL_GAP_SECONDS = 10.0        # minimum total seconds between balls (skippable)
COMMENTARY_LINE_GAP_SECONDS = 3.0    # pause between successive commentary lines (skippable)

# Test cricket
TEST_BALL_CAP = 2700                 # 5 days × 90 overs × 6 balls
TEST_FOLLOW_ON_THRESHOLD = 200       # lead at which follow-on can be enforced
TEST_BOT_DECLARE_LEAD = 280          # bot captain declares once lead crosses this
TEST_BOT_FOLLOW_ON_LEAD = 250        # bot captain enforces follow-on at this lead

# Difficulty → adaptation alpha
DIFFICULTY_ALPHA = {
    "easy": 0.0,
    "medium": 0.3,
    "hard": 0.6,
}

# Bowler fatigue (M005). A bowler's effectiveness decays with overs bowled and
# recovers with rest. Fatigue (0=fresh, 1=gassed) flattens the bowler's base
# distribution toward uniform (easier to score off) and lowers its effective α
# (worse at reading the batter). Pace-like bowlers tire faster than spinners.
FATIGUE_DECAY_PACE = 0.12         # stamina lost per over bowled (pace/swing/mystery)
FATIGUE_DECAY_SPIN = 0.07         # spinners tire slower
FATIGUE_RECOVERY_PER_OVER = 0.05  # stamina regained per over rested since last spell
