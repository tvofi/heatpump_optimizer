#!/usr/bin/env python3
"""D3.M1 enumerator for seat D3-s3: every UNPINNED mutation-inventory site in
this seat's cells (tools/audit/check_scopes.py --seat D3-s3), one per line.

Metric: the universe of D3.M1/M2/M3/M4 -- unpinned sites tests/mutation_table.py
inventories (its seven RATCHETED operators, the same set `--list` prints),
restricted to the seat's production files. Key: the site's ledger anchor (mutation_table inventory `anchor`),
then FILE:LINE.
Command:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 \
          dev/audit/rounds/round11/D3/s3/enumerate.py [--weights]
Expected: 663 lines at baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (exact).
Machine:  box B3 (4 vCPU, linux). Source-only: no solve, no timing.
--weights appends the M1 consequence weight (see weight()).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "tests"))
import mutation_table as mt  # noqa: E402

BASELINE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
SEAT = "D3-s3"


def cells() -> set[str]:
    out = subprocess.run(
        [sys.executable, "tools/audit/check_scopes.py", "--repo", str(ROOT),
         "--ref", BASELINE, "--seat", SEAT],
        capture_output=True, text=True, check=True).stdout
    return {ln.split("\t")[2] for ln in out.splitlines() if ln.count("\t") >= 2}


# Consequence weight (D3.M1): guards, behaviour-gating constants, raise/return
# in validation, and anything naming a user-facing surface weigh more.
HOT = re.compile(r"(raise|vol\.|schema|errors\[|abort|_LOGGER\.(warning|error)|"
                 r"setpoint|min_temp|max_temp|legionella|disinfect|power|limit|"
                 r"comfort|floor|ceil|price|cost|stale|valid|reason|isfinite|nan|"
                 r"None\b)", re.I)
KIND_W = {"RAISE_DEL": 5, "GUARD_OFF": 3, "CMP_BOUND": 3, "CLAMP_DROP": 3,
          "CONST": 2, "BOOLOP": 2, "RETURN_DEL": 1}


def weight(s: dict) -> int:
    return KIND_W.get(s["kind"], 1) + (2 if HOT.search(s["old"]) else 0)


def universe() -> list[dict]:
    mine = cells()
    budgets = mt.load_budgets()
    sites = mt.inventory()
    return [s for s in sorted(mt.unpinned_sites(budgets, sites),
                              key=lambda m: (m["file"], m["line"], m["kind"]))
            if s["file"] in mine]


def main() -> int:
    show_w = "--weights" in sys.argv
    for s in universe():
        extra = f"\tw={weight(s)}" if show_w else ""
        print(f"{s['anchor']}\t{s['file']}:{s['line']}\t"
              f"{s['old'].strip()[:90]}{extra}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
