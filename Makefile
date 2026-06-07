.PHONY: gate lint type test playtest run dev sync
dev:      ; python -m pip install -q -e ".[dev]"
lint:     ; ruff check .
type:     ; mypy neo_handcricket
test:     ; pytest
playtest: ; python -m tools.playtest
gate: lint type test playtest    ## the full QA gate — must pass before every ship
run:      ; neo-handcricket
sync:     ; python scripts/sync.py push
