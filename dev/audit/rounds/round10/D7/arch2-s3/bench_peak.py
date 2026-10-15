"""Per-call CPU of the capacity term the solver evaluates, base tree against prototype trees.

Metric: thread CPU per call of ``tariff.peak_cost_batch`` (B=97 rows, the batched FD gradient's
shape) and ``tariff.peak_cost_smooth`` (one plan), n=96 and n=192 steps, 15- and 60-minute windows,
distinct days on, plateau and non-plateau plans; median of 9 interleaved blocks per tree, each tree in
its own child process. ratio = tree / base. Null arm: ``base_copy`` (a byte-identical copy of base).

Perturbation: --slow-arm NAME doubles that arm's work (each timed call runs twice); its ratio must
read ~2.

    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch2-s3/bench_peak.py --base DIR --arm NAME=DIR [...] [--slow-arm NAME]

Provisional (CPU timing): carries load1. Thread-pinned. Writes nothing.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import json  # noqa: E402
import statistics  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402

CHILD = r'''
import json, os, sys, time
import numpy as np
sys.path.insert(0, "custom_components")
from heatpump_optimizer import tariff as T
slow = os.environ.get("SLOW") == "1"
rng = np.random.default_rng(3)
out = {}
for n in (96, 192):
    for wm in (15, 60):
        for shape in ("plateau", "rough"):
            if shape == "plateau":
                plan = np.where(np.arange(n) % 24 < 8, 6.0, 1.0)
            else:
                plan = rng.uniform(0, 6, n)
            mat = plan + rng.normal(0, 0.01, (97, n))
            days = np.repeat(np.arange(n // 96 + 1), 96)[: T.metering_windows(np.zeros(n), wm, 0.25, 0).size]
            def batch():
                r = T.peak_cost_batch(mat, 1.5, 3.0, 20.0, wm, 0.25, 3, 0, window_days=days)
                if slow:
                    T.peak_cost_batch(mat, 1.5, 3.0, 20.0, wm, 0.25, 3, 0, window_days=days)
                return r
            def scalar():
                r = T.peak_cost_smooth(plan, 1.5, 3.0, 20.0, wm, 0.25, 3, 0, window_days=days)
                if slow:
                    T.peak_cost_smooth(plan, 1.5, 3.0, 20.0, wm, 0.25, 3, 0, window_days=days)
                return r
            for name, fn, reps in (("batch", batch, 30), ("scalar", scalar, 300)):
                fn()
                t = time.thread_time()
                for _ in range(reps):
                    fn()
                out[f"{name}/{n}/{wm}/{shape}"] = (time.thread_time() - t) / reps * 1e6
print("PEAKJSON" + json.dumps(out))
'''


def child(tree, slow):
    env = dict(os.environ)
    env["SLOW"] = "1" if slow else "0"
    r = subprocess.run([sys.executable, "-c", CHILD], cwd=tree, env=env, capture_output=True, text=True)
    line = next((ln for ln in r.stdout.splitlines() if ln.startswith("PEAKJSON")), None)
    if line is None:
        sys.exit(r.stderr[-2000:])
    return json.loads(line[8:])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--arm", action="append", default=[])
    ap.add_argument("--slow-arm")
    ap.add_argument("--blocks", type=int, default=9)
    a = ap.parse_args()
    arms = {"base": a.base, **{s.split("=", 1)[0]: s.split("=", 1)[1] for s in a.arm}}
    data = {k: [] for k in arms}
    for _ in range(a.blocks):
        for k, d in arms.items():
            data[k].append(child(d, k == a.slow_arm))
    keys = sorted(data["base"][0])
    for k in arms:
        if k == "base":
            continue
        ratios = {"batch": [], "scalar": []}
        for key in keys:
            b = statistics.median(r[key] for r in data["base"])
            v = statistics.median(r[key] for r in data[k])
            ratios[key.split("/")[0]].append(v / b)
        for kind, rs in ratios.items():
            print(f"RESULT {k}_{kind}_ratio_median={statistics.median(rs):.4f} ratio")
            print(f"RESULT {k}_{kind}_ratio_range={min(rs):.4f}..{max(rs):.4f} ratio")
    for key in keys:
        print(f"  base {key}: {statistics.median(r[key] for r in data['base']):.1f} us")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT thread_factor=1.0 (thread_time)")


if __name__ == "__main__":
    main()
