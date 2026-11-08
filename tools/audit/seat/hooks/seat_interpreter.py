#!/usr/bin/env python3
"""SessionStart hook: say when the seat interpreter is not the one seat_venv.sh builds.

    python3 -I tools/audit/seat/hooks/seat_interpreter.py [--state DIR]

WHY. A temp cleanup once deleted the seat venv and every seat ran the system
python3 without anyone noticing (2026-10-03, seat_venv.sh). This hook runs
`seat_venv.sh --check` -- the recipe's own report of what the venv must hold --
and prints one `SEAT-INTERPRETER` line, with the rebuild command, when it
refuses. Silent when it passes. INERT unless $HPO_STATE_DIR/orch-checkout
exists, as liveness.py is, so it binds only a seat host.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

SEAT = Path(__file__).resolve().parents[1]


def report(state: Path) -> list[str]:
    if not (state / "orch-checkout").is_file():
        return []
    r = subprocess.run(["bash", str(SEAT / "seat_venv.sh"), "--check"],
                       capture_output=True, text=True, env=dict(os.environ, HPO_STATE_DIR=str(state)))
    if r.returncode == 0:
        return []
    why = (r.stderr or r.stdout).strip().splitlines()[-1:] or ["no output"]
    return [f"SEAT-INTERPRETER refused: {why[0][:160]}; rebuild with tools/audit/seat/seat_venv.sh"]


def main(argv: list[str]) -> int:
    state = os.environ.get("HPO_STATE_DIR", "")
    if argv[:1] == ["--state"] and len(argv) > 1:
        state = argv[1]
    if state:
        for ln in report(Path(state)):
            print(ln)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
