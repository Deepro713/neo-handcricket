"""Launcher for the optional Textual TUI: `python -m neo_handcricket.tui`."""
from __future__ import annotations

import argparse
import sys

from ..adapter import AdapterConfig
from . import app


def main() -> int:
    ap = argparse.ArgumentParser(description="neo-handcricket — optional Textual TUI (local, offline)")
    ap.add_argument("--batting", default="india")
    ap.add_argument("--bowling", default="australia")
    ap.add_argument("--format", dest="fmt", default="T20")
    ap.add_argument("--difficulty", default="medium")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    if not app.is_available():
        print("The TUI needs Textual. Install it with:  pip install -e \".[tui]\"", file=sys.stderr)
        return 1
    app.run(AdapterConfig(
        batting=args.batting, bowling=args.bowling, fmt=args.fmt,
        difficulty=args.difficulty, seed=args.seed,
    ))
    return 0


if __name__ == "__main__":
    sys.exit(main())
