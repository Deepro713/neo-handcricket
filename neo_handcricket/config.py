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
SAVE_SCHEMA_VERSION = 2              # v2 (M008): forward-compatible; v1 saves auto-migrate on load
INTER_BALL_GAP_SECONDS = 10.0        # minimum total seconds between balls (skippable)
COMMENTARY_LINE_GAP_SECONDS = 3.0    # pause between successive commentary lines (skippable)

# Test cricket
TEST_BALL_CAP = 2700                 # 5 days × 90 overs × 6 balls
TEST_FOLLOW_ON_THRESHOLD = 200       # lead at which follow-on can be enforced
TEST_BOT_DECLARE_LEAD = 280          # bot captain declares once lead crosses this
TEST_BOT_FOLLOW_ON_LEAD = 250        # bot captain enforces follow-on at this lead

# Difficulty → adaptation alpha (legacy frequency mixing strength)
DIFFICULTY_ALPHA = {
    "easy": 0.0,
    "medium": 0.3,
    "hard": 0.6,
    "legend": 0.8,
}

# Bowler fatigue (M005). A bowler's effectiveness decays with overs bowled and
# recovers with rest. Fatigue (0=fresh, 1=gassed) flattens the bowler's base
# distribution toward uniform (easier to score off) and lowers its effective α
# (worse at reading the batter). Pace-like bowlers tire faster than spinners.
FATIGUE_DECAY_PACE = 0.12         # stamina lost per over bowled (pace/swing/mystery)
FATIGUE_DECAY_SPIN = 0.07         # spinners tire slower
FATIGUE_RECOVERY_PER_OVER = 0.05  # stamina regained per over rested since last spell

# Batsman match-state / momentum (M005). A new batter is tentative and accelerates
# as they settle (balls faced); a chase raises intent as the required rate climbs.
# Both feed a single "aggression" scalar (0=blocking, 0.5=neutral, 1=all-out) that
# reshapes the batsman base distribution toward boundaries (or away, when tentative).
SETTLE_BALLS_K = 8               # balls faced at which settledness reaches 0.5
AGGRO_BASE = 0.35               # aggression of a fresh batter not under chase pressure
AGGRO_SETTLE_WEIGHT = 0.30      # how much being settled adds to aggression
AGGRO_INTENT_WEIGHT = 0.35      # how much chase pressure adds to aggression
AGGRO_TILT = 0.8                # strength of the boundary tilt at full aggression swing

# Match-up-aware bowling rotation (M005). The captain blends the existing
# phase/rotation preference with an archetype match-up advantage vs the current
# batter and bowler freshness (1 - fatigue) when choosing the next bowler.
ROTATION_MATCHUP_WEIGHT = 2.0    # weight on bowler-vs-batter archetype advantage
ROTATION_FRESHNESS_WEIGHT = 1.5  # weight on bowler freshness (1 - fatigue)

# Strategic AI / opponent modelling (M006). The bot predicts the human's next
# pick by blending three models — recent frequency, Win-Stay-Lose-Shift, and a
# bigram (sequence) predictor — then balances exploitation against the
# matching-pennies mixed-strategy equilibrium via an epsilon (0 = exploit hard,
# 1 = uniform / unexploitable). Higher difficulty exploits more (lower epsilon).
OPP_WINDOW = 20                  # picks of history fed to the opponent model
OPP_WEIGHT_FREQ = 1.0            # weight on the frequency model
OPP_WEIGHT_WSLS = 1.2            # weight on the Win-Stay-Lose-Shift model
OPP_WEIGHT_NGRAM = 1.0           # weight on the bigram (sequence) model
DIFFICULTY_EPSILON = {           # exploit-vs-mix epsilon per difficulty
    "easy": 0.85,
    "medium": 0.5,
    "hard": 0.25,
    "legend": 0.08,
}

# Player-facing "tells" (M006). OFF by default. When enabled, before the user bats
# the bot bowler drops a coarse, sometimes-bluffing hint about its likely *zone*
# (low/middle/high — never an exact number). Truthful only TELLS_TRUTHFUL_PROB of
# the time, so it adds mind-games without breaking the hidden-pick core.
TELLS_ENABLED = False
TELLS_TRUTHFUL_PROB = 0.6

# Big-moment event detection (M007). Thresholds for the pure event detector that
# turns ball/innings state into typed commentary events.
MILESTONE_RUNS = (50, 100)       # individual batting milestones
PARTNERSHIP_MILESTONE = 50       # partnership milestone
COLLAPSE_WINDOW = 12             # legal balls over which a collapse is measured
COLLAPSE_WICKETS = 3             # wickets within the window that count as a collapse
LAST_BALL_FINISH_BALLS = 1       # balls remaining at/under which a winning hit is a "last-ball" finish

# Context-aware commentary (M007). Occasional flavour lines that reference live
# fatigue / settledness / AI-read state. Gated on thresholds + a low emit chance.
CONTEXT_LINE_PROB = 0.25         # chance to emit a context line when a condition holds
CONTEXT_FATIGUE_THRESHOLD = 0.6  # bowler fatigue at/above which "tired" lines unlock
CONTEXT_SETTLED_THRESHOLD = 0.6  # batter settledness at/above which "set" lines unlock
