#!/usr/bin/env python3
"""D3-s2 round 9, step D3.M5: what the closure drivers of the eight solver-side modules cost and buy.

Metric (per driver, unmutated baseline tree): wall s and child CPU s (os.wait4 rusage), checks
  asserted (ok + FAIL lines, or ALL N PASSED), HeatPumpOptimizer.optimize calls (solves, counted
  by prescreen.py's sitecustomize hook), checks per solve, CPU / recorded seconds
  (tests/closures.json); and, from results.jsonl, kills per driver over the pool (sole kills =
  mutants no other driver that ran on them killed).
Command:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D3/s2/resources.py [--skip-run]
Expected: counts exact (checks, solves, kills); wall/CPU PROVISIONAL (shared 4-CPU box; the
  judge's quiet window re-takes them) -- quote load1 and thread_factor beside them.
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: box B2 (4-CPU Linux container).
Instrumented symbol: heatpump_optimizer.optimizer:HeatPumpOptimizer.optimize (solve counter).
Perturbation: D3S2_DRIVERS=<one script> restricts the run; a driver's solve count moves with the
  number of scenarios it drives (e.g. golden.py --only <one> -> 1 solve).
Writes: resources.json beside this file; worker tree under a mkdtemp root.
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prescreen as ps  # noqa: E402

HERE = Path(__file__).resolve().parent
DRIVERS = [d for d in os.environ.get("D3S2_DRIVERS", "").split(",") if d] or [
    "tests/typing_ruler.py", "tests/solar_alignment.py", "tests/wood_advisor.py",
    "tests/guard_pins.py", "tests/plan_view.py", "tests/deployment_shape.py",
    "tests/structure.py", "tests/doc_claims.py", "tests/manual_plan.py",
    "tests/config_flow_steps.py", "tests/validate.py", "tests/finite_boundary.py",
    "tests/entities.py", "tests/features.py", "tests/optimality.py"]


def main() -> int:
    import subprocess
    _cl, rec = ps.closures()
    out = {}
    path = HERE / "resources.json"
    if "--skip-run" in sys.argv and path.exists():
        out = json.loads(path.read_text())["drivers"]
    else:
        root = Path(tempfile.mkdtemp(prefix="d3s2res-"))
        tree = ps.make_tree(root, "w")
        wk = root / "work"
        (wk / "site").mkdir(parents=True)
        (wk / "site" / "sitecustomize.py").write_text(ps.SITECUSTOMIZE)
        try:
            for d in DRIVERS:
                r = ps.run_driver(d, tree, wk, "HEAD^1")
                r.pop("_run")
                r["recorded_seconds"] = rec.get(d, {}).get("seconds")
                out[d] = r
                print(f"  {d}: rc={r['rc']} wall={r['wall']}s cpu={r['cpu']}s checks={r['checks']} "
                      f"solves={r['solves']}", flush=True)
        finally:
            subprocess.run(["git", "worktree", "remove", "--force", str(tree)], capture_output=True)
    # kills per driver from the pre-screen
    rows = [json.loads(l) for p in sorted(HERE.glob("results*.jsonl"))
            for l in p.read_text().splitlines() if l.strip()]
    rows = [r for r in rows if r["id"] != "NULL"]
    kills, sole, ran = {}, {}, {}
    for r in rows:
        for run in r["runs"]:
            if "skipped" in run:
                continue
            ran[run["script"]] = ran.get(run["script"], 0) + 1
            if run.get("killed"):
                kills[run["script"]] = kills.get(run["script"], 0) + 1
        if len(r["killers"]) == 1:
            sole[r["killers"][0]] = sole.get(r["killers"][0], 0) + 1
    base = json.loads((HERE / "baseline.json").read_text())
    for d in sorted(set(out) | set(ran)):
        o = out.get(d, {})
        cps = (o["checks"] / o["solves"]) if o.get("solves") else None
        print(f"RESULT {d.split('/')[-1]}_checks={o.get('checks')} checks")
        print(f"RESULT {d.split('/')[-1]}_solves={o.get('solves')} solves")
        if cps is not None:
            print(f"RESULT {d.split('/')[-1]}_checks_per_solve={cps:.3f} ratio")
        if o:
            print(f"RESULT {d.split('/')[-1]}_cpu={o['cpu']} s provisional")
            print(f"RESULT {d.split('/')[-1]}_wall={o['wall']} s provisional (recorded {o['recorded_seconds']})")
        print(f"RESULT {d.split('/')[-1]}_kills={kills.get(d, 0)}/{ran.get(d, 0)} mutants (sole {sole.get(d, 0)})")
    if "tests/env_drift.py" in base:
        print(f"RESULT env_drift.py_wall_baseline={base['tests/env_drift.py']['wall']} s provisional "
              f"(recorded {base['tests/env_drift.py'].get('recorded_seconds')})")
    (HERE / "resources.json").write_text(json.dumps(
        {"drivers": out, "kills": kills, "sole_kills": sole, "ran": ran}, indent=1, sort_keys=True) + "\n")
    pt, tt = time.process_time(), time.thread_time()
    print(f"RESULT thread_factor={pt / tt if tt else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = 0
    for line in Path("/proc/vmstat").read_text().splitlines():
        if line.startswith("pswpin "):
            sw = int(line.split()[1])
    print(f"RESULT swapins={sw}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
