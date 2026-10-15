"""Solve CPU and wall, prototype trees against a base tree and an identical copy of it (the null arm).

Metric: per scenario, median over reps of ``tests/stress.py:build_case``'s own ``solve_thread_ms``
(this thread's CPU inside ``optimizer.optimize``, thread-pinned BLAS) and of the solve's wall
(perf_counter around ``build_case``). Reported as ratio = median(tree) / median(base), and the same
ratio for ``base_copy`` -- a byte-identical copy of the base tree run as a separate arm, interleaved
in random order with the others. The copy's ratio is the null control: whatever spread it shows is
the noise floor a prototype's ratio has to clear. Each child also takes ``reference_solve()`` (the
stress ruler) so a load swing between children is visible.

Bit identity: each scenario's achieved objective (float.hex) and a sha1 of the planned schedules
must equal the base tree's in every rep (``plan_identical``) -- a CPU change that moves the plan is
not a refactor.

Perturbation: ``--slow-arm NAME`` wraps that arm's ``HeatPumpOptimizer.optimize`` in a 20 % CPU
spin (busy loop for 0.2 x the solve's own thread time, inside the timed section via the child's
monkeypatch); its ratio must read >= 1.15 while the null arm stays inside its band.

    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch2-s3/bench_solve.py \
        --base DIR --arm NAME=DIR [--arm NAME=DIR ...] [--reps 5] [--slow-arm NAME]

Each DIR holds ``custom_components/`` and ``tests/`` (a copy of the tree under test). Provisional:
wall and CPU are contention-sensitive; every RESULT carries load1 and thread_factor.
Writes nothing but stdout.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import json  # noqa: E402
import random  # noqa: E402
import statistics  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402

SPECS = [
    ("winter/1z/dhw", dict(season="winter")),
    ("winter/2z/dhw", dict(season="winter", two_zone=True, dhw=True)),
    ("winter/2z/dhw+tariff", dict(season="winter", two_zone=True, dhw=True, tariff=True)),
    ("shoulder/2z/tariff+pv+cycle", dict(season="shoulder", two_zone=True, dhw=True, tariff=True,
                                          pv=True, cycling=1.0)),
    ("winter/1z/space+tariff", dict(season="winter", dhw=False, tariff=True)),
    ("winter/heavy_old", dict(season="winter", building="heavy_old")),
    ("winter/2z/fusecap", dict(season="winter", two_zone=True, dhw=True, power_cap_kw=3.68)),
    ("flat/2z/dhw+tariff", dict(season="flat", two_zone=True, dhw=True, tariff=True)),
]

CHILD = r'''
import hashlib, json, os, sys, time
sys.argv = ["stress"]
import stress
import numpy as np
specs = json.loads(os.environ["BENCH_SPECS"])
slow = os.environ.get("BENCH_SLOW") == "1"
if slow:
    from heatpump_optimizer.optimizer import HeatPumpOptimizer
    _orig = HeatPumpOptimizer.optimize
    def _slowed(self, *a, **k):
        t0 = time.thread_time()
        r = _orig(self, *a, **k)
        spent = time.thread_time() - t0
        end = time.thread_time() + 0.2 * spent
        while time.thread_time() < end:
            pass
        return r
    HeatPumpOptimizer.optimize = _slowed
ref = sorted(stress.reference_solve()[2] for _ in range(3))[1]
out = {"ref_thread_ms": ref, "rows": {}}
for label, spec in specs:
    t0 = time.perf_counter()
    run = stress.build_case(**spec)
    wall = (time.perf_counter() - t0) * 1000.0
    res = run["result"]
    h = hashlib.sha1()
    for name in ("power_schedule", "dhw_power_schedule", "room_temp_trajectory", "predicted_cost"):
        v = getattr(res, name, None)
        if v is not None:
            h.update(np.asarray(v, dtype=float).tobytes())
    obj = getattr(res, "objective_value", None)
    out["rows"][label] = {"thread_ms": run["solve_thread_ms"], "cpu_ms": run["solve_cpu_ms"],
                          "evals": run.get("solver_evals"),
                          "wall_ms": wall, "plan": h.hexdigest(),
                          "objective": None if obj is None else float(obj).hex()}
print("BENCHJSON" + json.dumps(out))
'''


def child(tree: str, slow: bool) -> dict:
    env = dict(os.environ)
    env["PYTHONPATH"] = os.path.join(tree, "tests", "hastub") + os.pathsep + os.path.join(tree, "tests")
    env["BENCH_SPECS"] = json.dumps(SPECS)
    env["BENCH_SLOW"] = "1" if slow else "0"
    r = subprocess.run([sys.executable, "-c", CHILD], cwd=tree, env=env, capture_output=True, text=True)
    line = next((ln for ln in r.stdout.splitlines() if ln.startswith("BENCHJSON")), None)
    if line is None:
        sys.exit(f"child failed in {tree}:\n{r.stderr[-3000:]}")
    return json.loads(line[len("BENCHJSON"):])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--arm", action="append", default=[])
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--slow-arm", default=None)
    ap.add_argument("--seed", type=int, default=1015)
    a = ap.parse_args()
    arms = {"base": a.base}
    for spec in a.arm:
        name, _, path = spec.partition("=")
        arms[name] = path
    rnd = random.Random(a.seed)
    data = {n: [] for n in arms}
    loads = []
    for rep in range(a.reps):
        order = list(arms)
        rnd.shuffle(order)
        for name in order:
            loads.append(os.getloadavg()[0])
            data[name].append(child(arms[name], slow=(name == a.slow_arm)))
        print(f"rep {rep + 1}/{a.reps} done, order {order}", flush=True)
    base_rows = data["base"]
    print(f"{'scenario':30s} " + " ".join(f"{n:>22s}" for n in arms if n != "base"))
    ratios = {n: {"thread": [], "wall": []} for n in arms if n != "base"}
    identical = {n: True for n in arms}
    for label, _ in SPECS:
        bt = statistics.median(r["rows"][label]["thread_ms"] for r in base_rows)
        bw = statistics.median(r["rows"][label]["wall_ms"] for r in base_rows)
        ref_plan = base_rows[0]["rows"][label]["plan"]
        ref_obj = base_rows[0]["rows"][label]["objective"]
        cells = []
        for n in arms:
            if n == "base":
                continue
            rows = data[n]
            tt = statistics.median(r["rows"][label]["thread_ms"] for r in rows)
            ww = statistics.median(r["rows"][label]["wall_ms"] for r in rows)
            ratios[n]["thread"].append(tt / bt)
            ratios[n]["wall"].append(ww / bw)
            same = all(r["rows"][label]["plan"] == ref_plan and r["rows"][label]["objective"] == ref_obj
                       for r in rows)
            identical[n] &= same
            cells.append(f"cpu {tt / bt:5.3f} wall {ww / bw:5.3f}{'' if same else ' PLAN!'}")
        print(f"{label:30s} " + " ".join(f"{c:>22s}" for c in cells) + f"   base cpu {bt:7.1f} ms")
    for n, r in ratios.items():
        th = sorted(r["thread"])
        print(f"RESULT {n}_cpu_ratio_median={statistics.median(th):.4f} ratio")
        print(f"RESULT {n}_cpu_ratio_range={th[0]:.4f}..{th[-1]:.4f} ratio")
        loo = sorted(th)[:-1] if statistics.median(th) >= 1 else sorted(th)[1:]
        print(f"RESULT {n}_cpu_ratio_median_drop_most_favourable={statistics.median(loo):.4f} ratio")
        print(f"RESULT {n}_wall_ratio_median={statistics.median(r['wall']):.4f} ratio")
        print(f"RESULT {n}_plan_identical={int(identical[n])} bool")
    refs = {n: statistics.median(d["ref_thread_ms"] for d in data[n]) for n in arms}
    print("RESULT reference_solve_thread_ms=" + ",".join(f"{n}:{v:.1f}" for n, v in refs.items()))
    tf = statistics.median(r["rows"][lb]["cpu_ms"] / r["rows"][lb]["thread_ms"]
                           for d in data.values() for r in d for lb, _ in SPECS)
    print(f"RESULT load1={statistics.median(loads):.2f}")
    print(f"RESULT thread_factor={tf:.3f}")
    print(f"RESULT reps={a.reps} count")
    return 0


if __name__ == "__main__":
    sys.exit(main())
