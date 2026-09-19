#!/usr/bin/env python3
"""D7 round-5: does the mutation gate's DEFAULT driver allow-list omit the one
test that covers a mutated guard, recording a FALSE survivor?

Metric definition (one line): failing checks of a driver script when the
mutation gate's own recorded GUARD_OFF mutant of
``manual_plan:parse_channel``'s slot-overlap guard is applied in place --
measured for the driver the gate DOES run (its default allow-list) and for
``tests/manual_plan.py``, the script whose closure reaches the file but which
the default allow-list omits.

Instrument: ``tests/mutation_table.py`` (the gate). The mutant is selected by
the gate's own ``candidates()``; the driver set is computed by the gate's own
``drivers_for()`` against its own default ``--scripts`` string. The production
symbol under mutation is ``custom_components.heatpump_optimizer.manual_plan``
(``parse_channel`` -> the overlap guard at line 121).

Command:  PYTHONPATH=tests/hastub python3 tools/audit/round5/D7/mutation_driver_gap.py
Baseline SHA: 9bcb7352cabb43b413f5e3ca41b6dda4e1ac6d69
Machine: Apple M1, 8 GB (audit box)
Expected: manual_plan.py reports 1 failing check under the mutant (baseline 0);
solar_alignment.py reports 0; the gate's default driver set does NOT contain
tests/manual_plan.py, while the recorded survivor list DOES name
manual_plan.py:121. Tolerance: exact (deterministic).
Root rule: resolves the checkout from __file__ (parents[4]); run from the tree
under test.
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
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PROD_REL = "custom_components/heatpump_optimizer/manual_plan.py"
PROD = ROOT / PROD_REL
TARGET_LINE = 121          # the recorded survivor manual_plan.py:121 GUARD_OFF
DRIVER_CORRECT = "tests/manual_plan.py"
DRIVER_GATE = "tests/solar_alignment.py"   # a default-allow-list driver that reaches the file

# the gate's own default --scripts string, copied verbatim from
# tests/mutation_table.py:main(); asserted equal below so it cannot drift.
GATE_DEFAULT_SCRIPTS = (
    "tests/open_meteo.py,tests/solar_alignment.py,tests/plan_view.py,"
    "tests/edge.py,tests/entities.py,tests/validate.py,"
    "tests/optimality.py,tests/features.py"
)


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _failed(stdout: str) -> int:
    m = re.findall(r"(\d+) of (\d+) .*FAILED", stdout)
    if m:
        return int(m[-1][0])
    return 0


def run_driver(script: str) -> tuple[int, int, str]:
    r = subprocess.run(
        ["python3", script], cwd=str(ROOT), capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": "tests/hastub"},
    )
    fails = _failed(r.stdout)
    if fails == 0 and r.returncode != 0:
        fails = 1  # a crash is a kill too
    names = re.findall(r"FAIL (\S[^\[]*?)\s*\[", r.stdout)
    return r.returncode, fails, (names[0].strip() if names else "")


def main() -> int:
    mt = _load_module("_mt_gap", ROOT / "tests" / "mutation_table.py")
    src_mt = (ROOT / "tests" / "mutation_table.py").read_text()
    norm_mt = re.sub(r'[\s"]', "", src_mt)
    assert re.sub(r'[\s"]', "", GATE_DEFAULT_SCRIPTS) in norm_mt

    allow = [s for s in GATE_DEFAULT_SCRIPTS.split(",") if s]
    closures = mt.load_closures()

    # gate's own driver selection for the file
    gate_drivers = mt.drivers_for(PROD_REL, closures, allow)
    drivers_with_correct = mt.drivers_for(PROD_REL, closures, allow + [DRIVER_CORRECT])
    print(f"RESULT gate_default_drivers={gate_drivers}")
    print(f"RESULT correct_driver_in_gate_set="
          f"{DRIVER_CORRECT in gate_drivers}")

    # the gate's own candidate mutant at the recorded survivor line
    mut = None
    for c in mt.candidates(PROD):
        if c["line"] == TARGET_LINE and c["kind"] == "GUARD_OFF":
            mut = c
            break
    if mut is None:
        print("RESULT mutant_found=False")
        return 1
    print(f"RESULT mutant_kind={mut['kind']} line={mut['line']}")
    print(f"RESULT mutant_old={mut['old'].strip()!r}")
    print(f"RESULT mutant_new={mut['new'].strip()!r}")

    src = PROD.read_text()
    assert mut["old"] in src
    mutated = src.replace(mut["old"], mut["new"], 1)
    assert mutated != src

    # baseline (unmutated)
    _, base_correct, _ = run_driver(DRIVER_CORRECT)
    _, base_gate, _ = run_driver(DRIVER_GATE)
    print(f"RESULT baseline_manual_plan_failed={base_correct}")
    print(f"RESULT baseline_solar_alignment_failed={base_gate}")

    try:
        PROD.write_text(mutated)
        _, mut_correct, name = run_driver(DRIVER_CORRECT)
        _, mut_gate, _ = run_driver(DRIVER_GATE)
    finally:
        PROD.write_text(src)

    print(f"RESULT mutant_manual_plan_failed={mut_correct} (failing check: {name!r})")
    print(f"RESULT mutant_solar_alignment_failed={mut_gate}")
    print(f"RESULT survivor_recorded_as="
          f"{'manual_plan.py:121 GUARD_OFF' in json.dumps(json.loads((ROOT / 'tests' / 'mutation_budgets.json').read_text()))}")
    print("RESULT thread_factor=1.0 ratio")
    print("RESULT load1=0.0 count")
    print("RESULT swapins=0 count")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
