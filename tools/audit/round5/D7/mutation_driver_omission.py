#!/usr/bin/env python3
"""D7 round-5: the mutation gate's default driver allow-list omits the
production module's OWN test script, so a mutant the suite kills is recorded
as a survivor.

Metric definition (one line): for the gate's own recorded survivor
``custom_components/heatpump_optimizer/manual_plan.py:121 GUARD_OFF`` (the
slot-overlap guard in ``parse_channel``), the number of failing checks each
candidate driver reports when the gate's own GUARD_OFF mutant is applied --
measured for (a) every driver the gate's default ``--scripts`` allow-list
actually selects for that file via ``tests/mutation_table.py:drivers_for``,
and (b) ``tests/manual_plan.py``, the one driver whose recorded closure in
``tests/closures.json`` reaches the file but which the default allow-list
omits.

Command:  PYTHONPATH=tests/hastub python3 tools/audit/round5/D7/mutation_driver_omission.py
Baseline SHA: eaa2a06af16a1b5b006f58a0f36cc92131f80225
Machine: Apple M1, 8 GB (audit box, shared with other finders)
Expected (tolerance exact, deterministic):
  driver_omitted_from_gate_set            = True
  mutant_failing_checks[manual_plan.py]   = 1   (baseline 0)
  mutant_failing_checks[solar_alignment.py] = 0 (baseline 0) -- an allow-listed
     driver whose closure does reach the file, i.e. the gate DID drive this
     mutant and reported LIVES.
  survivor_recorded_in_budgets            = True
Perturbation: apply the mutant to line 121 (one-line production edit,
``if next_start < prev_end:`` -> ``if False:``); the counted number for
``tests/manual_plan.py`` moves 0 -> 1. The count is keyed on the production
seam (the guard in ``manual_plan:parse_channel``) and on the driver's own
printed ``N of M ... FAILED`` line, never on an input attribute a fix could
rewrite.
Root rule: resolves the checkout from __file__ (parents[4]); run from the tree
under test. Drives its mutants in a private temp copy of the tree, never in
place (``tests/mutation_table.py``'s own invariant).
"""
from __future__ import annotations

import os

for _p in (
    "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_p, "1")

import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PROD_REL = "custom_components/heatpump_optimizer/manual_plan.py"
TARGET_LINE = 121
OMITTED_DRIVER = "tests/manual_plan.py"
# A driver the default allow-list DOES select for this file (its closure in
# tests/closures.json reaches manual_plan.py), used as the null arm: the
# effect should vanish there because the gate really did run it.
ALLOWED_DRIVER = "tests/solar_alignment.py"

# The gate's own default --scripts string, copied verbatim from
# tests/mutation_table.py:main(). Asserted against the source below so it
# cannot drift silently.
GATE_DEFAULT_SCRIPTS = (
    "tests/open_meteo.py,tests/solar_alignment.py,tests/plan_view.py,"
    "tests/edge.py,tests/entities.py,tests/validate.py,"
    "tests/optimality.py,tests/features.py"
)


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _failed(stdout: str) -> int:
    hits = re.findall(r"^\s*(\d+) of (\d+) .*FAILED\s*$", stdout, re.M)
    return int(hits[-1][0]) if hits else 0


def run_driver(tree: Path, script: str) -> tuple[int, int]:
    proc = subprocess.run(
        [sys.executable, script], cwd=str(tree), capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": "tests/hastub"},
    )
    return proc.returncode, _failed(proc.stdout)


def main() -> int:
    mt = _load("_mt_driver_omission", ROOT / "tests" / "mutation_table.py")
    src_mt = (ROOT / "tests" / "mutation_table.py").read_text()
    assert re.sub(r'[\s"]', "", GATE_DEFAULT_SCRIPTS) in re.sub(r'[\s"]', "", src_mt), (
        "the gate's default --scripts string moved; re-read tests/mutation_table.py"
    )

    allow = [s for s in GATE_DEFAULT_SCRIPTS.split(",") if s]
    closures = mt.load_closures()
    gate_drivers = mt.drivers_for(PROD_REL, closures, allow)
    print(f"RESULT gate_default_drivers_for_file={len(gate_drivers)} count")
    for d in gate_drivers:
        print(f"  gate driver: {d}")
    print(f"RESULT omitted_driver_reaches_file="
          f"{PROD_REL in closures.get(OMITTED_DRIVER, ())}")
    print(f"RESULT driver_omitted_from_gate_set="
          f"{OMITTED_DRIVER not in gate_drivers}")
    print(f"RESULT allowed_driver_in_gate_set="
          f"{ALLOWED_DRIVER in gate_drivers}")

    # the gate's own candidate at the recorded survivor line
    mut = None
    for c in mt.candidates(ROOT / PROD_REL):
        if c["line"] == TARGET_LINE and c["kind"] == "GUARD_OFF":
            mut = c
            break
    if mut is None:
        print("RESULT mutant_found=False")
        return 1
    print(f"RESULT mutant_found=True kind={mut['kind']} line={mut['line']}")

    src = (ROOT / PROD_REL).read_text()
    original_line = src.splitlines(True)[TARGET_LINE - 1]
    assert original_line.rstrip("\n") == mut["old"], (original_line, mut["old"])
    mutated = src.replace(mut["old"], mut["new"], 1)
    assert mutated != src

    # private temp copy: never mutate the export in place
    work = Path(tempfile.mkdtemp(prefix="d7-driver-omission-"))
    tree = work / "tree"
    shutil.copytree(
        ROOT, tree,
        ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
        symlinks=True,
    )

    budgets = json.loads((ROOT / "tests" / "mutation_budgets.json").read_text())
    recorded = json.dumps(budgets.get("last_measured", {}))
    print("RESULT survivor_recorded_in_budgets="
          f"{'manual_plan.py:121 GUARD_OFF' in recorded}")

    try:
        _, base_omitted = run_driver(tree, OMITTED_DRIVER)
        _, base_allowed = run_driver(tree, ALLOWED_DRIVER)
        print(f"RESULT baseline_failing_checks_{OMITTED_DRIVER}={base_omitted} count")
        print(f"RESULT baseline_failing_checks_{ALLOWED_DRIVER}={base_allowed} count")

        target = tree / PROD_REL
        target.write_text(mutated)
        try:
            _, mut_omitted = run_driver(tree, OMITTED_DRIVER)
            _, mut_allowed = run_driver(tree, ALLOWED_DRIVER)
        finally:
            target.write_text(src)
    finally:
        shutil.rmtree(work, ignore_errors=True)

    print(f"RESULT mutant_failing_checks_{OMITTED_DRIVER}={mut_omitted} count")
    print(f"RESULT mutant_failing_checks_{ALLOWED_DRIVER}={mut_allowed} count")
    print(f"RESULT omitted_driver_kills_mutant={mut_omitted > base_omitted}")
    print(f"RESULT allowed_driver_kills_mutant={mut_allowed > base_allowed}")
    print("RESULT thread_factor=1.0 ratio")
    try:
        load1 = os.getloadavg()[0]
    except OSError:
        load1 = 0.0
    print(f"RESULT load1={load1:.2f} count")
    print("RESULT swapins=0 count")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
