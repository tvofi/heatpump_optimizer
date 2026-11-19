#!/usr/bin/env python3
"""D9-s3 M2 / C1: does the stress gate's MEMORY channel see an injected 2x
retained-bytes regression, and where is it blind?

Metric (one line): per sweep scenario, whether `tests/stress.py`'s memory pass
FLAGS a retained ballast equal to the scenario's recorded traced peak (a 2x
traced regression) -- `detected` = the scenario is in the gate's own probe set
(`_memory_probe_labels`, exec'd from stress.py's source) AND the gate's own
thresholds (`traced_fail_threshold`, `rss_attrib_fail_threshold`) fire on the
injected probe reading. Count key: the reading the gate's own launcher
(`stress._run_memory_probe`) returns from the production solve with the
ballast retained inside `heatpump_optimizer.optimizer:HeatPumpOptimizer.optimize`.

Injection: a sitecustomize on the probe's PYTHONPATH wraps
`HeatPumpOptimizer.optimize` to allocate and RETAIN (module-level list on the
optimizer module) `HPO_D9S3_BALLAST_MB` MiB of touched numpy memory -- a leak
of exactly the recorded traced peak, i.e. 2x.

Perturbation: `--top-n 108` (the gate's STRESS_MEMORY_TOP_N, default 6) makes
the gate probe every scenario: RESULT detected_confined moves from the probe-set
size up to the scenario count. `--ballast-factor 0` is the null control (no
injection): RESULT detected_confined must read only the clean false positives.

Run (from the export root):
  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 \
    dev/audit/rounds/round11/D9/s3/mem_confined.py [--top-n N] [--jobs 2] \
    [--ballast-factor 1.0] [--only label,label]
Expected at 92d38ecb (default args): universe=54 scenarios, probed_by_gate=6,
  flagged_if_probed=54 (2x ballast), detected_confined=6 (=probed, exact),
  blind_confined=48 (exact); --ballast-factor 0 (null): detected_confined=0,
  flagged_if_probed=9 +/-3 (all unprobed: records the pass never re-reads,
  1.6-2.3x on this box's clean tree); --top-n 108: detected_confined=54.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: cloud box B3,
  Linux x86_64, Python 3.14, numpy 2.5 (bytes are final, RSS provisional).
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import ast  # noqa: E402
import json  # noqa: E402
import resource  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402
import time  # noqa: E402
from concurrent.futures import ThreadPoolExecutor  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--top-n", type=int, default=None,
                help="override STRESS_MEMORY_TOP_N for the gate's selection")
ap.add_argument("--jobs", type=int, default=2)
ap.add_argument("--ballast-factor", type=float, default=1.0,
                help="ballast = factor x recorded traced_peak_mb (1.0 = 2x)")
ap.add_argument("--only", default="")
args = ap.parse_args()

_argv = sys.argv
sys.argv = [_argv[0]]
sys.path.insert(0, "tests")
import stress  # noqa: E402

sys.argv = _argv

STRESS_SRC = "tests/stress.py"

SITE = '''
import os
_mb = float(os.environ.get("HPO_D9S3_BALLAST_MB", "0") or 0)
if _mb > 0:
    import numpy as _np
    from heatpump_optimizer import optimizer as _opt
    _orig = _opt.HeatPumpOptimizer.optimize
    _opt._D9S3_RETAINED = []
    def _leaky(self, *a, **k):
        _opt._D9S3_RETAINED.append(_np.ones(int(_mb * 1048576 / 8)))
        return _orig(self, *a, **k)
    _opt.HeatPumpOptimizer.optimize = _leaky
'''


def gate_probe_labels(budget_table: dict, top_n: int) -> list[str]:
    """Exec the gate's own `_memory_probe_labels` out of stress.py's source."""
    tree = ast.parse(open(STRESS_SRC).read())
    fn = next(n for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and n.name == "_memory_probe_labels")
    mod = ast.Module(body=[fn], type_ignores=[])
    g = {"MEMORY_TOP_N": top_n, "budget_table": budget_table}
    exec(compile(mod, STRESS_SRC, "exec"), g)
    return g["_memory_probe_labels"]()


def main() -> int:
    t0 = time.process_time()
    tt0 = time.thread_time()
    table = stress.load_budget_table()
    combos = {c["label"]: {k: v for k, v in c.items() if k != "label"}
              for c in stress.sweep_combinations()}
    top_n = args.top_n if args.top_n is not None else stress.MEMORY_TOP_N
    probed = [l for l in gate_probe_labels(table, top_n) if l in combos]
    labels = sorted(combos)
    if args.only:
        labels = [l for l in labels if l in args.only.split(",")]

    root = tempfile.mkdtemp(prefix="d9s3_mem_")
    with open(os.path.join(root, "sitecustomize.py"), "w") as fh:
        fh.write(SITE)
    base_env = stress._memory_probe_env()
    base_env["PYTHONPATH"] = root + os.pathsep + base_env["PYTHONPATH"]
    base_env.pop("HPO_D9S3_BALLAST_MB", None)
    baseline = float(stress._run_memory_probe(["--memory-baseline"], base_env)["rss_mb"])

    worker_cpu: list[float] = []

    def one(label):
        w0 = time.thread_time()
        try:
            return _one(label)
        finally:
            worker_cpu.append(time.thread_time() - w0)

    def _one(label):
        rec = table.get(label, {})
        ballast = args.ballast_factor * float(rec.get("traced_peak_mb", 0.0))
        env = dict(base_env)
        if ballast > 0:
            env["HPO_D9S3_BALLAST_MB"] = f"{ballast:.4f}"
        p = stress._run_memory_probe(
            ["--memory-probe", json.dumps(combos[label])], env)
        attrib = max(0.0, float(p["rss_mb"]) - baseline)
        rt, ra = float(rec.get("traced_peak_mb", 0)), float(rec.get("rss_attrib_mb", 0))
        flagged_traced = rt > 0 and float(p["traced_mb"]) > stress.traced_fail_threshold(rt)
        flagged_rss = ra > 0 and attrib > stress.rss_attrib_fail_threshold(ra)
        return label, {
            "ballast_mb": round(ballast, 3), "traced_mb": p["traced_mb"],
            "rec_traced_mb": rt, "traced_x": round(float(p["traced_mb"]) / rt, 3) if rt else None,
            "attrib_mb": round(attrib, 1), "rec_attrib_mb": ra,
            "flagged": bool(flagged_traced or flagged_rss),
            "flagged_traced": bool(flagged_traced), "flagged_rss": bool(flagged_rss),
            "probed_by_gate": label in probed,
        }

    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as ex:
        rows = dict(ex.map(one, labels))
    for label in labels:
        r = rows[label]
        print(f"ROW {label:<32} probed={int(r['probed_by_gate'])} "
              f"traced {r['traced_mb']:.2f}/{r['rec_traced_mb']:.2f} "
              f"(x{r['traced_x']}) attrib {r['attrib_mb']:.1f}/{r['rec_attrib_mb']:.1f} "
              f"flagged={int(r['flagged'])}")
    flagged = [l for l in labels if rows[l]["flagged"]]
    detected = [l for l in flagged if rows[l]["probed_by_gate"]]
    blind = [l for l in flagged if not rows[l]["probed_by_gate"]]
    print("PROBE_SET " + ",".join(probed))
    print("BLIND " + ",".join(blind))
    print(f"RESULT universe={len(labels)} scenarios")
    print(f"RESULT probed_by_gate={sum(rows[l]['probed_by_gate'] for l in labels)} scenarios")
    print(f"RESULT flagged_if_probed={len(flagged)} scenarios")
    print(f"RESULT detected_confined={len(detected)} scenarios")
    print(f"RESULT blind_confined={len(blind)} scenarios")
    print(f"RESULT baseline_rss={baseline:.1f} MiB provisional")
    xs = [rows[l]["traced_x"] for l in labels if rows[l]["traced_x"]]
    if xs:
        print(f"RESULT traced_x_min={min(xs):.3f} ratio")
        print(f"RESULT traced_x_max={max(xs):.3f} ratio")
    pc, tc = time.process_time() - t0, time.thread_time() - tt0
    # The worker threads are deliberate (they wait on probe subprocesses):
    # their CPU is subtracted and printed, per the harness contract.
    print(f"RESULT worker_thread_cpu={sum(worker_cpu):.3f} s")
    print(f"RESULT thread_factor={(pc - sum(worker_cpu)) / max(tc, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_CHILDREN).ru_majflt}")
    with open(os.path.join(root, "rows.json"), "w") as fh:
        json.dump(rows, fh, indent=1)
    print(f"ROWS_JSON {os.path.join(root, 'rows.json')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
