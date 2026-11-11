#!/usr/bin/env python3
"""R10-CI-LAYOUT P2b, unit U5b's null control: script_runs_per_push, unchanged.

    python3 dev/audit/harnesses/r10_ci_layout_u5/script_runs.py [--plant-drop-pair]

The every-script-measured-once count tests/ci_budgets.json records
script_runs_per_push at, from the two instruments' own enumerations, as
tests/entities.py's `_cir_once_count` takes it: the closures lane's full plan
(tests/closure.py test_scripts less SLOW_GATED) plus the coverage `fast`
stage's scripts (tools/coverage/coverage_tree.sh's DERIVED and `fast)` lines,
run by bash). Moving the architecture-score pair out of `fast` must leave it
at the budget: the pair's closures rows are still recorded, and the coverage
stage never ran it. --plant-drop-pair takes the pair out of the closures plan
(what a payment that stopped measuring it would do), which must read 2 lower.
Prints `script_runs_per_push=<n> budget=<b>`; exit 0 when the reading is
what the arm wants (the budget, or budget-2 under the plant).
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
sys.path.insert(0, str(ROOT / "tests"))
import closure  # noqa: E402

PAIR = {"tests/arch_score.py", "tests/arch_score_head.py"}


def count(drop_pair: bool) -> int:
    plan = [s for s in closure.test_scripts() if Path(s).name not in closure.SLOW_GATED]
    if drop_pair:
        plan = [s for s in plan if s not in PAIR]
    sh = (ROOT / "tools" / "coverage" / "coverage_tree.sh").read_text()
    derived = re.search(r"^DERIVED=\$\(.*?\)$", sh, re.M | re.S)
    fast = re.search(r"^\s*fast\)\s+(SCRIPTS=.*?) ;;$", sh, re.M)
    out = subprocess.run(["bash", "-c", f'{derived.group(0)}\n{fast.group(1)}\nprintf "%s\\n" "$SCRIPTS"'],
                         cwd=ROOT, capture_output=True, text=True, check=True, timeout=60)
    return len(plan) + len(out.stdout.split())


def main(argv: list[str]) -> int:
    plant = "--plant-drop-pair" in argv
    budget = json.loads((ROOT / "tests" / "ci_budgets.json").read_text())["script_runs_per_push"]
    n = count(plant)
    print(f"script_runs_per_push={n} budget={budget}{' (PLANT: the pair dropped from the closures plan)' if plant else ''}")
    return 0 if n == (budget - 2 if plant else budget) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
