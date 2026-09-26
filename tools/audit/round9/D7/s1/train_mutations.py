#!/usr/bin/env python3
"""D7-s1 / D7.M5: this year's train -- does deleting each addition fail a check?

Metric (one line): per train item, whether a one-site spot mutation that
deletes the addition is KILLED (a driver goes red naming more failing checks
than its unmutated baseline, tests/mutation_table.py:killed) by any driver in
the suite's recorded closure set that this box can run; count of survivors.

Count key: mutation_table.killed(script, run, baseline) on the real driver
run against a mutated copy of the tree -- the verdict the project's own
mutation instrument would give, never an exit status alone.

Drivers are tried cheapest first and the item stops at its first kill; a
survivor is driven through every runnable driver. Not driven, each for a
stated reason: env_drift.py / golden.py / stress.py / deployment_shape.py
need a git ref (the export has no .git) -- env_drift's behaviour comparison
is emulated for production survivors by --golden (two `env_drift.py
--capture <root> <out> --all` captures, baseline vs mutant, compared leaf by
leaf); structure.py and typing_ruler.py measure shape, not behaviour.

Null control: a comment-only line added to optimizer.py must survive every
driver (else the verdicts mean nothing).

Run (repository root):
    PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D7/s1/train_mutations.py [--only ID,...] [--golden] [--pin-leaf]

Finding D7-s1-02's arm:  --only null,drift,drift_leaf,drift_ctl,stress
  expected: survivors=3 (drift, drift_leaf, stress), drift_ctl killed, null survives.
Perturbation arm:        --only drift_leaf --pin-leaf   -> survivors=0 (drift_leaf killed by entities.py)
Expected at 1936d5ca (exact): see REPORT.md table; survivors named there.
Machine: cloud container (linux x86_64), baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1.
Writes only under tempfile.mkdtemp().
"""
from __future__ import annotations

import os

for _pin in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
             "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_pin, "1")

import argparse  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402
import shutil  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "tests"))
import mutation_table as mt  # noqa: E402

P = "custom_components/heatpump_optimizer/"
CARD = P + "www/heatpump-optimizer-card.js"

# id, train item, file, old (unique), new
MUTANTS = [
    ("null", "null control (comment only)", P + "optimizer.py",
     "def _bounds_supported_by_batch(bounds: list[tuple[float, float]]) -> bool:\n",
     "# d7s1 null control: a comment changes no behaviour\n"
     "def _bounds_supported_by_batch(bounds: list[tuple[float, float]]) -> bool:\n"),
    ("batch", "batched gradient", P + "optimizer.py",
     "            can_batch = _bounds_supported_by_batch(bounds)\n",
     "            can_batch = False\n"),
    ("bounds", "batched gradient's bounds gate", P + "optimizer.py",
     "        if lo > hi:\n            return False\n    return True\n",
     "        if False:\n            return False\n    return True\n"),
    ("drift", "drift gate (env_drift leaf comparison)", "tests/env_drift.py",
     "            _diff_leaves(baseline[name], branch[name], name, diffs)\n",
     "            pass  # d7s1: comparison deleted\n"),
    ("drift_leaf", "drift gate (the leaf comparator _diff_leaves)", "tests/env_drift.py",
     "    elif a != b:\n        out.append(f\"{path}: {a!r} vs {b!r}\")\n",
     "    elif False:\n        out.append(f\"{path}: {a!r} vs {b!r}\")\n"),
    ("drift_ctl", "positive control: a tested env_drift helper", "tests/env_drift.py",
     "    return len(parts) == 3 and all(p.isdigit() for p in parts)\n",
     "    return False\n"),
    ("scoped", "scoped gate (closure.select hit rule)", "tests/closure.py",
     "        hits = sorted({unit_of(f) for f in files} & set(closures[s]))\n"
     "        if hits:\n            run.append(s)\n            continue\n"
     "        if s == \"tests/env_drift.py\" and touched_integration:\n",
     "        hits = []\n"
     "        if hits:\n            run.append(s)\n            continue\n"
     "        if s == \"tests/env_drift.py\" and touched_integration:\n"),
    ("card", "card collaborators (HistorySource pan-back bound)", CARD,
     "    if (!this.api() || this.unavailable) return null;\n    return Date.now() - HISTORY_SPAN_MS;\n",
     "    return null;\n"),
    ("stress", "stress budgets (per-scenario comparison)", "tests/stress.py",
     "                if ratio > allowed:\n",
     "                if False:\n"),
    ("weekly", "weekly windows", P + "thermal_model.py",
     "            values[\"dhw_weekly_windows\"] = parse_weekly_windows(windows_spec)\n",
     "            values[\"dhw_weekly_windows\"] = None\n"),
    ("topology", "topology catalogue (unmodelled layout not selectable)", P + "topology.py",
     "            selectable=False,\n", ""),
    ("wood", "wood variant (wood-while-usable valve law)", P + "thermal_model.py",
     "    usable = min(1.0, max(0.0, (wood_temp - flow_set + margin) / m))\n",
     "    usable = 0.0\n"),
    ("coil", "coil variant (DHW refill through wood-tank coil)", P + "thermal_model.py",
     "            self.dhw_wood_coil_enabled\n            and self.dhw_enabled\n",
     "            False\n            and self.dhw_enabled\n"),
    ("dhwconf", "DHW confidence band", P + "coordinator.py",
     "        if not self._dhw_accuracy.has_lead_history():\n            return [None] * n, [None] * n\n",
     "        if True:\n            return [None] * n, [None] * n\n"),
    ("tuya", "Tuya prefill table", P + "device_prefill.py",
     "    \"tuya_heat_pump\": (_TUYA_HEAT_PUMP, _TUYA_HEAT_PUMP_SIGNATURE, \"_\"),\n", ""),
    ("reanchor", "re-anchor law", P + "coordinator.py",
     "        phi = house_loss_confidence(self._house_heat_loss_samples)\n",
     "        phi = 1.0\n"),
]

# Cheapest first (baseline seconds on this box in REPORT.md).
PY_DRIVERS = [
    "tests/guard_pins.py", "tests/doc_claims.py", "tests/finite_boundary.py",
    "tests/config_flow_steps.py", "tests/entities.py", "tests/features.py",
    "tests/plan_view.py", "tests/manual_plan.py", "tests/solar_alignment.py",
    "tests/wood_advisor.py", "tests/optimality.py", "tests/backtest.py",
    "tests/validate.py", "tests/edge.py",
]
NODE_DRIVERS = ["tests/card.mjs"]
TIMEOUT = 2400


def names(run: mt.ScriptRun) -> set[str]:
    """Failing check NAMES, detail stripped (a detail may carry run-random text)."""
    return {c.split("  [")[0].strip() for c in mt.failed_checks(run)}


PIN = False  # --pin-leaf: the perturbation arm (see main)
_PIN_TEXT = (
    "_d7s1_out = []\n"
    "_env_drift._diff_leaves({'a': 1}, {'a': 2}, 'x', _d7s1_out)\n"
    "R.check('d7s1 pin: the drift comparator reports a moved leaf', bool(_d7s1_out), repr(_d7s1_out))\n"
)


def copy_tree(dst: Path) -> None:
    def ignore(d: str, names: list[str]) -> set[str]:
        # Keep the earlier-round fixtures entities.py reads (round3..7-fix);
        # skip only this round's in-flight seat directories.
        skip = {n for n in names if n in ("__pycache__", ".git", "node_modules")}
        if Path(d).name == "round9":
            skip |= {n for n in names if n.startswith("D")}
        return skip
    shutil.copytree(ROOT, dst, ignore=ignore)
    if PIN:
        ent = dst / "tests/entities.py"
        tail = 'sys.exit(R.close("ENTITY CHECKS"))'
        src = ent.read_text()
        assert src.count(tail) == 1
        ent.write_text(src.replace(tail, _PIN_TEXT + tail))


def run_node(script: str, cwd: Path, env_extra: dict) -> mt.ScriptRun:
    started = time.monotonic()
    env = {**os.environ, "PYTHONPATH": "tests/hastub", **env_extra}
    pv = subprocess.run([sys.executable, "tests/plan_view.py"], cwd=cwd, env=env,
                        capture_output=True, text=True, timeout=TIMEOUT)
    proc = subprocess.run(["node", script], cwd=cwd, env=env, capture_output=True,
                          text=True, timeout=TIMEOUT)
    run = mt.ScriptRun(proc.returncode, 0, time.monotonic() - started,
                       pv.stdout[-2000:] + proc.stdout, proc.stderr)
    return run._replace(failed=mt.failing_count(run))


def drive(script: str, cwd: Path, env_extra: dict) -> mt.ScriptRun:
    if script.endswith(".mjs"):
        return run_node(script, cwd, env_extra)
    return mt.run_script(script, cwd, TIMEOUT, None, env_extra)


def drivers_for(target: str) -> list[str]:
    closures = json.loads((ROOT / "tests/closures.json").read_text())["closures"]
    unit = target
    out = [d for d in PY_DRIVERS + NODE_DRIVERS
           if d in closures and unit in closures[d]]
    if target.startswith("tests/"):
        # An instrument: closures.json does not list gate files (closure.py is
        # in none), so the drivers are the runnable scripts whose source
        # imports the module -- the only place its behaviour is exercised.
        mod = Path(target).stem
        out = [d for d in PY_DRIVERS
               if re.search(rf"^\s*(import {mod}\b|from {mod} import)|import_module\(.{mod}.\)"
                            rf"|_load\(.{mod}.|\"tests/{mod}.py\"",
                            (ROOT / d).read_text(), re.M)]
    return out


def golden_capture(root: Path, out: Path, env_extra: dict) -> dict:
    env = {**os.environ, "PYTHONPATH": "tests/hastub", **env_extra}
    subprocess.run([sys.executable, "tests/env_drift.py", "--capture", str(root),
                    str(out), "--all"], cwd=root, env=env, check=True,
                   capture_output=True, text=True, timeout=TIMEOUT)
    return json.loads(out.read_text())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--golden", action="store_true",
                    help="emulate env_drift --all for production survivors")
    ap.add_argument("--pin-leaf", action="store_true",
                    help="perturbation: add one entities.py check that drives "
                         "env_drift._diff_leaves on two differing payloads")
    args = ap.parse_args()
    global PIN
    PIN = args.pin_leaf
    only = set(filter(None, args.only.split(",")))
    c0, t0 = time.process_time(), time.thread_time()
    tmp = Path(tempfile.mkdtemp(prefix="d7s1_train_"))
    env_extra = {"HPO_PLANDATA": str(tmp / "plandata.json")}
    base = tmp / "base"
    copy_tree(base)
    baseline_runs: dict[str, mt.ScriptRun] = {}
    survivors = 0
    golden_base = None
    rows = []
    try:
        for mid, item, target, old, new in MUTANTS:
            if only and mid not in only:
                continue
            tree = tmp / f"m_{mid}"
            copy_tree(tree)
            path = tree / target
            src = path.read_text()
            assert src.count(old) == 1, f"{mid}: anchor not unique ({src.count(old)})"
            path.write_text(src.replace(old, new))
            verdict, killer, tried = "survived", "", []
            for d in drivers_for(target):
                if d not in baseline_runs:
                    baseline_runs[d] = drive(d, base, env_extra)
                    b = baseline_runs[d]
                    print(f"  baseline {d}: rc={b.rc} failed={b.failed} {b.seconds:.0f}s", flush=True)
                run = drive(d, tree, env_extra)
                k = mt.killed(d, run, baseline_runs[d])
                if k and baseline_runs[d].rc != 0:
                    # A driver red in this git-less export (entities.py: its
                    # git/HANDOVER checks) kills only with MORE failing checks
                    # AND a failing check name its baseline did not print.
                    fresh = names(run) - names(baseline_runs[d])
                    k = bool(fresh)
                tried.append(f"{d}:{'KILL' if k else 'live'}")
                print(f"  {mid} {d}: rc={run.rc} failed={run.failed} "
                      f"{'KILLED' if k else 'survived'} {run.seconds:.0f}s "
                      f"{sorted(names(run) - names(baseline_runs[d]))[:2] if k else ''}", flush=True)
                if k:
                    verdict, killer = "killed", d
                    break
            if (verdict == "survived" and args.golden and mid != "null"
                    and target.startswith(P) and not target.endswith(".js")):
                if golden_base is None:
                    golden_base = golden_capture(base, tmp / "gb.json", env_extra)
                gm = golden_capture(tree, tmp / f"g_{mid}.json", env_extra)
                moved = [n for n in sorted(set(golden_base) | set(gm))
                         if golden_base.get(n) != gm.get(n)]
                tried.append(f"env_drift-capture:{len(moved)} scenarios moved")
                if moved:
                    verdict, killer = "killed(golden drift)", "env_drift --capture"
                print(f"  {mid} golden: {len(moved)} scenarios moved {moved[:4]}", flush=True)
            if verdict == "survived" and mid != "null":
                survivors += 1
            rows.append((mid, item, target, verdict, killer, tried))
            print(f"RESULT {mid}_killed={0 if verdict == 'survived' else 1} count", flush=True)
            shutil.rmtree(tree, ignore_errors=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("\n| id | item | file | verdict | killer | drivers tried |")
    for r in rows:
        print(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {'; '.join(r[5])} |")
    print(f"RESULT survivors={survivors} count")
    c1, t1 = time.process_time(), time.thread_time()
    print(f"RESULT thread_factor={(c1-c0)/max(t1-t0,1e-9):.3f} ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [ln for ln in open("/proc/vmstat") if ln.startswith("pswpin")][0].split()[1]
    except OSError:
        sw = "n/a"
    print(f"RESULT swapins={sw}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
