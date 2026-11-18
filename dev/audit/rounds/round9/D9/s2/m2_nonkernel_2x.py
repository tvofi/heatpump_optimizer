#!/usr/bin/env python3
"""D9-s2 (round 9, D9.M2) -- can the shipped stress gate see a 2x regression of
the solver's NON-KERNEL work (everything optimize() does outside the three
metered simulate seams)?

METRIC: number of tests/stress.py rules tripped when every sweep scenario's
non-kernel solve CPU is doubled, the rules being the gate's own, evaluated with
the gate's own functions over its own sweep:
  * cpu_ceiling        solve_cpu > live_solve_budget_ratio() * unit
  * cpu_per_scenario   ratio > scenario_budget(label, table)   (x3.0 of record)
  * sweep              sum(cpu)/sum(ref) > SWEEP_BUDGET_RATIO
  * work evals / simulate / kernel-cost   work_drift_compare(injected, plain)
    (the PLAIN arm of this same process is the baseline, as stress.py's
    capture_baseline_work supplies one from the merge base).
INJECTION (in memory, never on disk): HeatPumpOptimizer.optimize is wrapped;
after the real solve it spins process CPU for exactly (solve CPU - kernel CPU
metered by the live stress.SolverWork instance during that solve), i.e. an
exact 2x of the solve's non-kernel work. Counts, plan and kernel per-call cost
are untouched by construction -- this is the shape of a regression in the
objective assembly, the DHW planning loops' own Python, candidate scoring or
result building. Count key: rules tripped by the gate's own verdict functions.
Also printed: the sweep's non-kernel share of solve CPU (sum over scenarios),
and the per-scenario range of that share.
ARMS: plain (baseline), nonkernel2x (the injection), plain2 (null control:
a second clean sweep judged exactly like the injection), twice (positive
control: optimize() run twice, the h7/h8 injection -- must trip work rules).
COMMAND (from the export root; takes the gate lease like stress.py):
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tests/gate_lock.py \
      auto-lease --label d9s2-m2 -- /home/claude/venv314/bin/python \
      tools/audit/round9/D9/s2/m2_nonkernel_2x.py
  (--arms plain,nonkernel2x to skip the controls; --arms plain,nonkernel2x_one
   --victim LABEL confines the injection to ONE scenario, #346's shape)
PERTURBATION: --scale 4 on the confined arm (spin 4x the victim's non-kernel
  CPU, a 5x of that part) -> nonkernel2x_one.tripped_total UP 0 -> 1 (the
  per-scenario CPU rule, x3.0 of record, fires only past ~x3 of the solve).
EXPECTED (baseline 1936d5ca, this box): nonkernel2x.tripped_total=1 (the
  sweep rule alone: x1.61 of the sweep ratio; every per-scenario rule and all
  three count/kernel channels 0); nonkernel2x_one.tripped_total=0 for
  --victim winter/2z/dhw (the default two-zone DHW solve), twice_one >= 1
  (positive control), plain2.tripped_total=0 (null control).
  Counts exact; ratios provisional (+-10 %).
  Measured runs: --arms plain,nonkernel2x,plain2,twice (uniform) and
  --arms plain,nonkernel2x_one,twice_one --victim winter/2z/dhw (confined);
  perturbation --arms plain,nonkernel2x_one@2.19,nonkernel2x_one@4 --victim
  winter/2z/dhw (@2.19 = the victim's whole solve CPU x2.0, all of it
  non-kernel; @4 = x2.8, past the x3.0-of-record budget).
MACHINE: round-9 box B5 (Linux container, Intel Xeon @ 2.80GHz, 4 vCPU, 16 GB, numpy 2.4.6/scipy 1.17.1,
  Python 3.14.0rc2). Root rule: os.getcwd() (run from the tree under test).
"""
from __future__ import annotations

import os

for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")

import argparse
import statistics
import sys
import time

ROOT = os.getcwd()
for _p in ("tests", os.path.join("tests", "hastub"), "custom_components"):
    sys.path.insert(0, os.path.join(ROOT, _p))

import stress  # noqa: E402
from heatpump_optimizer import optimizer as opt_mod  # noqa: E402

TABLE = stress.load_budget_table()
_ORIG = opt_mod.HeatPumpOptimizer.optimize
_ORIG_ENTER = stress.SolverWork.__enter__
LIVE = {"work": None, "scale": 1.0, "victim": "shoulder/cycle", "victims": set()}


def _enter(self):
    LIVE["work"] = self
    return _ORIG_ENTER(self)


stress.SolverWork.__enter__ = _enter


def _nonkernel2x(self, *a, **k):
    work = LIVE["work"]
    k0 = work.kernel_ms if work is not None else 0.0
    c0 = time.process_time()
    res = _ORIG(self, *a, **k)
    cpu_ms = (time.process_time() - c0) * 1000.0
    kern = (work.kernel_ms - k0) if work is not None else 0.0
    until = time.process_time() + LIVE["scale"] * max(0.0, cpu_ms - kern) / 1000.0
    while time.process_time() < until:
        pass
    return res


def _solvecpu2x(self, *a, **k):
    """An extra solve's worth of CPU, all of it outside the kernel seams."""
    c0 = time.process_time()
    res = _ORIG(self, *a, **k)
    until = time.process_time() + (time.process_time() - c0)
    while time.process_time() < until:
        pass
    return res


def _twice(self, *a, **k):
    _ORIG(self, *a, **k)
    return _ORIG(self, *a, **k)


def concurrent() -> int:
    return len(os.popen(
        "ps ax -o args= | grep -E '[s]tress\\.py|[t]ests/run\\.sh|[m]2_nonkernel'"
    ).read().splitlines())


def R(name, value, unit):
    text = f"{value:.6g}" if isinstance(value, float) else str(value)
    print(f"RESULT {name}={text} {unit}", flush=True)


def sweep(mode: str) -> tuple[dict, float, float, float]:
    cal = stress.Calibration(stress.CALIBRATION_WINDOW)
    cal.warm_up()
    rows, sref, scpu = {}, 0.0, 0.0
    p0, t0 = time.process_time(), time.thread_time()
    for combo in [dict(c) for c in stress.sweep_combinations()]:
        name = combo.pop("label")
        sample = cal.sample()
        unit = max(cal.unit_ms, 1e-6)
        if mode == "nonkernel2x" or (mode == "nonkernel2x_one" and name == LIVE["victim"]):
            opt_mod.HeatPumpOptimizer.optimize = _nonkernel2x
        elif mode == "solvecpu2x_set" and name in LIVE["victims"]:
            opt_mod.HeatPumpOptimizer.optimize = _solvecpu2x
        elif mode == "twice" or (mode == "twice_one" and name == LIVE["victim"]):
            opt_mod.HeatPumpOptimizer.optimize = _twice
        try:
            run = stress.build_case(**combo)
        finally:
            opt_mod.HeatPumpOptimizer.optimize = _ORIG
        cpu = float(run["solve_cpu_ms"])
        rows[name] = {"ratio": cpu / unit, "cpu": cpu, "unit": unit,
                      "evals": int(run["solver_evals"]),
                      "sim": int(run["solver_simulate_steps"]),
                      "kernel": float(run["solver_kernel_ms"]),
                      "obj": float(run["result"].objective_value)}
        sref += sample
        scpu += cpu
    pc, tc = time.process_time() - p0, time.thread_time() - t0
    return rows, scpu / max(sref, 1e-9), pc, tc


def judge(tag: str, rows: dict, sweep_ratio: float, base: dict | None) -> int:
    ceiling = [n for n, r in rows.items()
               if r["cpu"] > stress.live_solve_budget_ratio() * r["unit"]]
    per = [n for n, r in rows.items()
           if (b := stress.scenario_budget(n, TABLE)) is not None and r["ratio"] > b]
    sweep_trip = int(sweep_ratio > stress.SWEEP_BUDGET_RATIO)
    over = sim_over = cost_over = covered = doubt = 0
    if base is not None:
        v = stress.work_drift_compare(
            {n: r["evals"] for n, r in rows.items()},
            {n: r["sim"] for n, r in rows.items()},
            {n: r["obj"] for n, r in rows.items()},
            {n: r["kernel"] for n, r in rows.items()},
            {n: {"evals": r["evals"], "simulate": r["sim"], "objective": r["obj"],
                 "kernel_ms": r["kernel"]} for n, r in base.items()})
        over, sim_over, cost_over = len(v.over), len(v.sim_over), len(v.cost_over)
        covered, doubt = len(v.covered), len(v.cost_doubt)
    total = len(ceiling) + len(per) + sweep_trip + over + sim_over + cost_over
    R(f"{tag}.sweep_ratio", sweep_ratio, "ratio")
    R(f"{tag}.sweep_budget", stress.SWEEP_BUDGET_RATIO, "ratio")
    R(f"{tag}.tripped_cpu_ceiling", len(ceiling), "count")
    R(f"{tag}.tripped_cpu_per_scenario", len(per), "count")
    R(f"{tag}.tripped_sweep", sweep_trip, "count")
    R(f"{tag}.tripped_work_evals", over, "count")
    R(f"{tag}.tripped_work_simulate", sim_over, "count")
    R(f"{tag}.tripped_kernel_cost", cost_over, "count")
    R(f"{tag}.kernel_cost_doubt", doubt, "count")
    R(f"{tag}.work_covered", covered, "count")
    R(f"{tag}.tripped_total", total, "count")
    return total


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="plain,nonkernel2x,plain2,twice")
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--victim", default="shoulder/cycle")
    ap.add_argument("--victims", default="winter/2z/dhw,winter/1z/dhw,shoulder/1z/space,"
                    "heavy_old/winter,summer/2z/dhw,typical_slab/winter")
    args = ap.parse_args()
    LIVE["victims"] = set(args.victims.split(","))
    LIVE["scale"] = args.scale
    LIVE["victim"] = args.victim
    arms = args.arms.split(",")
    R("scenarios", len(stress.sweep_combinations()), "count")
    R("scale", args.scale, "x_nonkernel_spun")
    base, tfs = None, []
    for arm in arms:
        # "ARM@S" runs ARM with --scale S for that arm only (tag keeps the @S).
        name_only, _, sc = arm.partition("@")
        LIVE["scale"] = float(sc) if sc else args.scale
        mode = "plain" if name_only.startswith("plain") else name_only
        started = time.perf_counter()
        rows, sr, pc, tc = sweep(mode)
        tfs.append(pc / tc if tc else float("nan"))
        R(f"{arm}.wall_s", time.perf_counter() - started, "s")
        R(f"{arm}.concurrent_processes", concurrent(), "count")
        if arm == "plain":
            base = rows
            shares = [(r["cpu"] - r["kernel"]) / r["cpu"] for r in rows.values() if r["cpu"] > 0]
            R("plain.nonkernel_share_of_sweep_cpu",
              sum(r["cpu"] - r["kernel"] for r in rows.values())
              / sum(r["cpu"] for r in rows.values()), "ratio")
            R("plain.nonkernel_share_min", min(shares), "ratio")
            R("plain.nonkernel_share_median", statistics.median(shares), "ratio")
            R("plain.nonkernel_share_max", max(shares), "ratio")
            judge("plain", rows, sr, None)
            plain_sr = sr
            continue
        judge(arm, rows, sr, base)
        R(f"{arm}.sweep_ratio_over_plain", sr / plain_sr, "ratio")
        if name_only in ("nonkernel2x_one", "twice_one"):
            v = args.victim
            R(f"{arm}.victim_cpu_x", rows[v]["ratio"] / base[v]["ratio"], "ratio")
            R(f"{arm}.victim_nonkernel_share",
              (base[v]["cpu"] - base[v]["kernel"]) / base[v]["cpu"], "ratio")
            R(f"{arm}.victim_evals_x", rows[v]["evals"] / base[v]["evals"], "ratio")
            R(f"{arm}.victim_sim_x", rows[v]["sim"] / base[v]["sim"], "ratio")
            R(f"{arm}.victim_kernel_x", rows[v]["kernel"] / base[v]["kernel"], "ratio")
            R(f"{arm}.victim_budget_x",
              stress.scenario_budget(v, TABLE) / base[v]["ratio"], "ratio")
        if name_only == "solvecpu2x_set":
            xs = []
            for v in sorted(LIVE["victims"]):
                x = rows[v]["ratio"] / base[v]["ratio"]
                xs.append(x)
                b = stress.scenario_budget(v, TABLE)
                R(f"{arm}.victim[{v}].cpu_x", x, "ratio")
                R(f"{arm}.victim[{v}].evals_x", rows[v]["evals"] / base[v]["evals"], "ratio")
                R(f"{arm}.victim[{v}].sim_x", rows[v]["sim"] / base[v]["sim"], "ratio")
                R(f"{arm}.victim[{v}].kernel_x", rows[v]["kernel"] / base[v]["kernel"], "ratio")
                R(f"{arm}.victim[{v}].over_per_scenario_budget", int(rows[v]["ratio"] > b), "bool")
            R(f"{arm}.victims", len(xs), "count")
            R(f"{arm}.victim_cpu_x_min", min(xs), "ratio")
            R(f"{arm}.victim_cpu_x_max", max(xs), "ratio")
            R(f"{arm}.victim_cpu_x_drop_lowest_min", sorted(xs)[1], "ratio")
        if name_only == "nonkernel2x":
            per = sorted(rows[n]["ratio"] / base[n]["ratio"] for n in rows)
            R("nonkernel2x.scenario_cpu_x_min", per[0], "ratio")
            R("nonkernel2x.scenario_cpu_x_median", statistics.median(per), "ratio")
            R("nonkernel2x.scenario_cpu_x_max", per[-1], "ratio")
    print(f"RESULT thread_factor={max(tfs):.4f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        with open("/proc/vmstat") as fh:
            print(f"RESULT swapins={next(int(l.split()[1]) for l in fh if l.startswith('pswpin'))}")
    except Exception:  # noqa: BLE001
        print("RESULT swapins=-1")
    return 0


if __name__ == "__main__":
    sys.exit(main())
