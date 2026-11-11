"""D7 round 8, seat s2 -- spot-mutation table for this year's train (method step 5).

Metric: per train item, whether ONE spot mutation of its owning production
symbol is killed by the test scripts that name that symbol, under the
suite's own kill rule (``tests/mutation_table.py:run_script``: exit status
changes, or the last ``N of M ... FAILED`` count rises above the unmutated
copy's). Output: one RESULT per mutant, killed=1 / survived=0, plus
survivors_total.

Each mutant is applied to a private copy of the tree under $TMPDIR (never the
tree itself); the SAME copy, unmutated, is the baseline/null control each
driver is compared against (the no-.git export fails some entities.py
checks for the environment; the comparison is against that, not against 0).

Command (from the tree root):
  PYTHONPATH=tests/hastub TMPDIR=<private> python3 tools/audit/round8/D7/s2_spot.py [--only M1,M4] [--jobs 2]
Expected at the baseline: see REPORT-s2.md's table (exact per mutant).
Perturbation: --null runs every mutant with its replacement text equal to
  the original (an identity mutation); every row must read survived=0 kills,
  i.e. killed=0 -- the kill column must fall to zero.
Baseline: cdf82daabcfe3777d98b31489f36df5555ec9d82. Machine: 4-vCPU cloud Linux
  container (audit-r8), python 3.11.15; verdicts are counts, not timing.
Root rule: ROOT = the working directory.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import concurrent.futures as cf
import shutil
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(".").resolve()
sys.path.insert(0, str(ROOT / "tests"))
from mutation_table import run_script  # noqa: E402  (the suite's kill rule)

P = "custom_components/heatpump_optimizer/"

# (id, train item, owning file, old text (unique), new text, drivers = the
#  test scripts that name the mutated symbol, excluding stress.py which
#  needs the gate lock and times the box)
MUTANTS = [
    ("M1", "batched gradient + bounds gate", P + "optimizer.py",
     "def _bounds_supported_by_batch(bounds: list[tuple[float, float]]) -> bool:\n",
     "def _bounds_supported_by_batch(bounds: list[tuple[float, float]]) -> bool:\n    return False\n",
     ["tests/optimality.py", "tests/features.py"]),
    ("M2", "weekly windows", P + "dhw_schedule.py",
     "            for d in days:\n                weekly[d].extend(wins)\n",
     "            for d in range(7):\n                weekly[d].extend(wins)\n",
     ["tests/entities.py", "tests/features.py"]),
    ("M3", "wood and coil variants (dhw coil drawing)", P + "topology.py",
     "        if dhw_coil:\n",
     "        if False:\n",
     ["tests/features.py"]),
    ("M4", "DHW confidence band", P + "coordinator.py",
     "        n = len(dhw_temp)\n        if not self._dhw_accuracy.has_lead_history():\n",
     "        n = len(dhw_temp)\n        if True:\n",
     ["tests/plan_view.py"]),
    ("M5", "re-anchor law", P + "coordinator.py",
     "    def _reanchor_house_heat_loss_scale(self, anchor: float | None) -> bool:\n",
     "    def _reanchor_house_heat_loss_scale(self, anchor: float | None) -> bool:\n        return False\n",
     ["tests/features.py"]),
    ("M6", "Tuya prefill table", P + "device_prefill.py",
     '    ("sensor", "T4"): (CONF_OUTDOOR_TEMP_ENTITY, 1.0),\n',
     "",
     ["tests/config_flow_steps.py", "tests/features.py"]),
    ("M7", "wood furnace variant", P + "wood_fuel.py",
     "def wood_furnace_on(",
     "def _d7s2_orig_wood_furnace_on(",
     ["tests/features.py"]),
]


def copy_tree(dest: Path) -> None:
    shutil.copytree(ROOT, dest, symlinks=True, ignore=shutil.ignore_patterns(
        "__pycache__", "round8"))


BASE: dict = {}


def baseline(drivers: set[str], timeout: int, jobs: int) -> None:
    """The unmutated copy's verdict per driver -- the null control."""
    tmp = Path(tempfile.mkdtemp(prefix="d7s2_base_", dir=os.environ.get("TMPDIR")))
    try:
        tree = tmp / "tree"
        copy_tree(tree)
        env = {"HPO_PLANDATA": str(tmp / "plandata"), "TMPDIR": str(tmp)}
        with cf.ThreadPoolExecutor(jobs) as ex:
            for d, r in zip(sorted(drivers), ex.map(
                    lambda d: run_script(d, tree, timeout, extra_env=env), sorted(drivers))):
                BASE[d] = r
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def run_mutant(m, null: bool, timeout: int) -> dict:
    mid, item, rel, old, new, drivers = m
    tmp = Path(tempfile.mkdtemp(prefix=f"d7s2_{mid}_", dir=os.environ.get("TMPDIR")))
    out = {"id": mid, "item": item, "file": rel, "drivers": {}}
    try:
        tree = tmp / "tree"
        copy_tree(tree)
        target = tree / rel
        src = target.read_text()
        assert src.count(old) == 1, f"{mid}: old text occurs {src.count(old)}x"
        env = {"HPO_PLANDATA": str(tmp / "plandata"), "TMPDIR": str(tmp)}
        base = BASE
        repl = new
        if mid.startswith("M7") and not null:
            # a deleted function body: keep the name, answer "never on"
            repl = ("def wood_furnace_on(*_a, **_k):\n    return False\n\n\n"
                    "def _d7s2_orig_wood_furnace_on(")
        target.write_text(src.replace(old, old if null else repl))
        killed = False
        for d in drivers:
            r = run_script(d, tree, timeout, extra_env=env)
            b = base[d]
            k = (r.rc != b.rc) or (r.failed > b.failed)
            killed = killed or k
            out["drivers"][d] = {"base_rc": b.rc, "base_failed": b.failed,
                                 "rc": r.rc, "failed": r.failed, "killed": k,
                                 "seconds": round(r.seconds, 1)}
        out["killed"] = killed
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--timeout", type=int, default=3000)
    ap.add_argument("--null", action="store_true")
    ap.add_argument("--closure", action="store_true",
                    help="drive each selected mutant with EVERY .py script whose recorded closure"
                         " (tests/closures.json) reaches its file, less the named-driver set,"
                         " env_drift.py (needs git) and stress.py (needs the lock)")
    args = ap.parse_args()
    t0p, t0t = time.process_time(), time.thread_time()
    sel = [m for m in MUTANTS if not args.only or m[0] in args.only.split(",")]
    if args.closure:
        import json
        clos = json.loads((ROOT / "tests" / "closures.json").read_text())["closures"]
        sel = [(mid + "c", item, rel, old, new, sorted(
                    k for k, v in clos.items() if rel in v and k.endswith(".py")
                    and k not in drivers and k not in ("tests/env_drift.py", "tests/stress.py")))
               for mid, item, rel, old, new, drivers in sel]
    baseline({d for m in sel for d in m[5]}, args.timeout, args.jobs)
    for d, b in sorted(BASE.items()):
        print(f"  baseline {d}: rc={b.rc} failed={b.failed} ({b.seconds:.0f}s, provisional)")
    with cf.ThreadPoolExecutor(args.jobs) as ex:
        results = list(ex.map(lambda m: run_mutant(m, args.null, args.timeout), sel))
    for r in results:
        for d, v in r["drivers"].items():
            print(f"  {r['id']} {d}: base rc={v['base_rc']} failed={v['base_failed']}"
                  f" -> mutant rc={v['rc']} failed={v['failed']} killed={v['killed']}")
        print(f"RESULT killed[{r['id']} {r['item']}]={int(r['killed'])} count")
    print(f"RESULT survivors_total={sum(not r['killed'] for r in results)} count")
    print(f"RESULT mutants_total={len(results)} count")
    pc, tc = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}  (drivers run as subprocesses; counts only)")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
