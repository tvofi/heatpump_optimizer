#!/usr/bin/env python3
"""D9-s2 (round 9, D9.M2) -- what the budgeted gates cannot see: a 2x of the
coordinator's LOOP-THREAD work (everything a cycle does on the event loop,
outside the executor job that carries the solve).

METRIC: offenders returned by tests/replay.py:cost_offenders (the only budget
that runs the real coordinator cycle: nightly, COST_BUDGETS
["synthetic-dhw-only.json"]) for four arms, each replayed in its own
interpreter through tests/replay.py:run_fixture:
  none    -- no injection (null control: must be 0)
  cpu     -- replay's OWN perturbation, the whole cycle doubled at
             _async_update_data (positive control: must be >= 1)
  loop2x  -- the loop-thread work doubled exactly: after each real
             HeatPumpOptimizerCoordinator._async_update_data the cycle spins
             for (its thread CPU - the CPU of its executor jobs), and after
             each entity read (replay.sweep) for that read's own CPU
  loopNx  -- the same with --scale N (perturbation)
plus, per PR: how many functions of coordinator.py / sensor.py /
topology.py run when tests/stress.py solves a sweep scenario (build_case),
traced with sys.setprofile -- the per-PR stress gate's reach into the cycle.
Count key: the offender list the gate's own function returns.
COMMAND (from the export root):
    PYTHONPATH=tests/hastub /home/claude/venv314/bin/python \
        tools/audit/round9/D9/s2/m2_loop_blind.py
PERTURBATION: --scale 4 (loop work x5) -> loop.offenders UP (0 -> 1).
EXPECTED (baseline 1936d5ca): none.offenders=0, cpu.offenders=1,
  loop2x.offenders=0 exact; stress_cycle_functions=0 exact; ratios
  provisional (+-10 %).
MACHINE: round-9 box B5 (Linux container, Intel Xeon @ 2.80GHz, 4 vCPU, 16 GB, numpy 2.4.6/scipy 1.17.1,
  Python 3.14.0rc2). Root rule: os.getcwd().
"""
from __future__ import annotations

import os

for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path.cwd() / "tools" / "audit" / "round9" / "D9" / "s2"
sys.path.insert(0, str(HERE))
MARK = "<<<m2-loop>>>"


def spin(seconds: float) -> None:
    until = time.thread_time() + seconds
    while time.thread_time() < until:
        pass


def one_arm(arm: str, scale: float) -> dict:
    import _rig
    import replay

    extra = None
    if arm == "loop":
        def extra(real):
            async def upd(self):
                p = _rig.PROBE
                t0 = time.thread_time()
                e0 = p.cur["exec_cpu"] if p.cur else 0.0
                out = await real(self)
                loop = (time.thread_time() - t0) - ((p.cur["exec_cpu"] if p.cur else 0.0) - e0)
                spin(scale * max(0.0, loop))
                return out
            return upd

        real_sweep = replay.sweep

        def sweep(*a, **k):
            t0 = time.thread_time()
            out = real_sweep(*a, **k)
            spin(scale * (time.thread_time() - t0))
            return out

        replay.sweep = sweep
    _rig.install(extra_update_wrap=extra)
    out = _rig.run(1, inject="cpu" if arm == "cpu" else None)
    fig = {k: out["cost"][k] for k in ("cpu_ratio", "peak_kib")}
    budget = replay.COST_BUDGETS.get("synthetic-dhw-only.json")
    offenders = replay.cost_offenders(fig, budget)
    cyc = [c for i, c in enumerate(_rig.PROBE.cycles) if i >= 2 and i % 2 == 0]
    loop = sum(c["thread_cpu"] - c["exec_cpu"] + c.get("sweep_cpu", 0.0) for c in cyc)
    tot = sum(c["thread_cpu"] + c.get("sweep_cpu", 0.0) for c in cyc)
    return {"arm": arm, "cpu_ratio": fig["cpu_ratio"], "budget": budget["cpu_ratio"],
            "offenders": [o for o in offenders if o.startswith("cpu_ratio")],
            "loop_share": loop / tot if tot else float("nan"),
            "counts": out["counts"]}


def stress_reach() -> dict:
    import _rig  # noqa: F401  (puts tests/ and the hastub on sys.path)
    import stress
    names: set[tuple[str, str]] = set()

    def prof(frame, event, arg):
        if event == "call":
            f = frame.f_code.co_filename
            if "heatpump_optimizer" in f:
                names.add((Path(f).name, frame.f_code.co_name))

    combo = dict(stress.sweep_combinations()[0])
    label = combo.pop("label")
    sys.setprofile(prof)
    try:
        stress.build_case(**combo)
    finally:
        sys.setprofile(None)
    cyc = {n for n in names if n[0] in ("coordinator.py", "sensor.py", "topology.py",
                                        "entity.py", "narrative.py", "price_model.py")}
    return {"label": label, "functions": len(names), "cycle_functions": len(cyc),
            "files": sorted({n[0] for n in names})}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--one", default=None)
    args = ap.parse_args()
    if args.one:
        p0, t0 = time.process_time(), time.thread_time()
        res = stress_reach() if args.one == "stress" else one_arm(args.one, args.scale)
        res["tf"] = (time.process_time() - p0) / max(time.thread_time() - t0, 1e-9)
        print(MARK + json.dumps(res))
        return 0
    p0 = time.process_time()
    c0 = os.times()
    results = {}
    arms = [("none", 1.0), ("cpu", 1.0), ("loop", args.scale), ("stress", 1.0)]
    for arm, scale in arms:
        proc = subprocess.run([sys.executable, __file__, "--one", arm, "--scale", str(scale)],
                              capture_output=True, text=True, env=os.environ.copy())
        line = next((l for l in proc.stdout.splitlines() if l.startswith(MARK)), None)
        if line is None:
            print(proc.stdout[-2000:], proc.stderr[-3000:])
            return 1
        results[arm] = json.loads(line[len(MARK):])
    c1 = os.times()
    child_cpu = (c1.children_user + c1.children_system) - (c0.children_user + c0.children_system)
    tag = {"none": "none", "cpu": "cpu", "loop": f"loop{args.scale + 1:g}x"}
    for arm in ("none", "cpu", "loop"):
        r = results[arm]
        print(f"# {arm}: {r['offenders']} counts={r['counts']}")
        print(f"RESULT {tag[arm]}.cycle_cpu_ratio={r['cpu_ratio']:.4f} ref_solves")
        print(f"RESULT {tag[arm]}.offenders={len(r['offenders'])} count")
    print(f"RESULT cpu_ratio_budget={results['none']['budget']:.4f} ref_solves")
    print(f"RESULT none.loop_share_of_budgeted_cycle={results['none']['loop_share']:.4f} ratio")
    print(f"RESULT loop_over_none={results['loop']['cpu_ratio'] / results['none']['cpu_ratio']:.4f} ratio")
    print(f"RESULT cpu_over_none={results['cpu']['cpu_ratio'] / results['none']['cpu_ratio']:.4f} ratio")
    s = results["stress"]
    print(f"# stress.build_case({s['label']}) ran files {s['files']}")
    print(f"RESULT stress_solve_functions={s['functions']} count")
    print(f"RESULT stress_cycle_functions={s['cycle_functions']} count")
    # Every arm is a child interpreter doing the work on its main thread.
    print(f"RESULT child_cpu_s={child_cpu:.2f} s_cpu")
    print(f"RESULT thread_factor={max(r['tf'] for r in results.values()):.4f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        with open("/proc/vmstat") as fh:
            print(f"RESULT swapins={next(int(l.split()[1]) for l in fh if l.startswith('pswpin'))}")
    except Exception:  # noqa: BLE001
        print("RESULT swapins=-1")
    return 0


if __name__ == "__main__":
    sys.exit(main())
