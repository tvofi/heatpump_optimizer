#!/usr/bin/env python3
"""R10-FLY-CI-RATCHET-WINDOW: the ci-ratchet window step's two pins, each against a mutant.

    python3 dev/audit/harnesses/r10_ci_ratchet_window_mutants.py            # all
    python3 dev/audit/harnesses/r10_ci_ratchet_window_mutants.py M0 M1      # named

The runner is r10_ci_layout_p0_mutants.py's, unchanged: per mutant a detached
worktree of HEAD (the branch's own tree is never edited), one substitution
that must apply exactly once, a full `tests/entities.py` run, KILLED only when
entities exits non-zero AND an aimed check is among the FAIL lines.

  M1  `|| true` back on the per-lane listing      -> the failed-listing pin
  M2  the unfiltered listing restored             -> the by-name pin
  M3  a lane dropped from LANES                   -> the by-name pin
  M4  the 15-run cap per lane deleted             -> the by-name pin
  M5  this run no longer excluded                 -> the by-name pin
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "p0", Path(__file__).with_name("r10_ci_layout_p0_mutants.py"))
p0 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(p0)

YML = ".github/workflows/tests.yml"
BY_NAME = "the ci-ratchet window lists each upload lane by name"
FAILED = "a failed artifacts listing stops the gather step"
p0.MUTANTS = {
    "M0": ([], []),
    "M1": ([(YML, '>> "$RUNNER_TEMP/lanes.json"\n',
             '>> "$RUNNER_TEMP/lanes.json" || true\n')], [FAILED]),
    "M2": ([(YML, "artifacts?name=ci-metrics-$lane&per_page=100",
             "artifacts?per_page=100")], [BY_NAME]),
    "M3": ([(YML, 'LANES="fast coverage closures"', 'LANES="fast coverage"')],
           [BY_NAME]),
    "M4": ([(YML, "| reverse | .[:15]'", "| reverse'")], [BY_NAME]),
    "M5": ([(YML, "!= ($ENV.GITHUB_RUN_ID | tonumber))\n                     | {id",
             "!= -1)\n                     | {id")], [BY_NAME]),
}

if __name__ == "__main__":
    raise SystemExit(p0.main(sys.argv[1:]))
