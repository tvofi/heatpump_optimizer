#!/usr/bin/env python3
"""D3.M2 reach of the differential gate, seat D3-s3: the production lines the
branch-side capture of `tests/env_drift.py --all` executes.

Why: env_drift.py's own run rebuilds its capture child's PYTHONPATH, so
tests/mutation_table.py's reach tracer never records that child
(reach_problems: "no traced run" / unrecorded child) and env_drift keeps
every pair. That is safe for the lane but leaves the census (reach_census.py)
unable to say which unpinned site the golden differential can see. This
harness runs the very child env_drift.py runs -- `env_drift.py --capture
<root> <out> --all`, the branch side of the comparison -- under the lane's
own tracer (mutation_table.hook_env / traced_pythonpath / collect) and
writes its reach where reach_census.py reads it, as driver
`tests/env_drift.py[capture]`.

Metric (one line): the set of (file, line) pairs in the seat's production
cells the capture child fires a LINE event on. Count key: production code
objects' LINE events, never a script attribute.
Hooks: tests/env_drift.py:capture_tree (driven), the golden capture it calls
(tests/golden.py:capture / capture_coordinator) and every production symbol
those execute; tracer = tests/mutation_table.py:REACH_HOOK.
Command:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 \
          dev/audit/rounds/round11/D3/s3/drift_reach.py
Perturbation: --scenarios N truncates nothing in production; instead
--drop-file FILE removes one file's hits from the written row (a census
re-run then moves every site only the capture executed in FILE to
REACH-DEAD -- direction up). Null control: --drop-file of a cell file the
capture never executes leaves the census unchanged.
Expected: exact line sets (deterministic capture); wall provisional.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box B3, 4 vCPU.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path.cwd()
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tests"))
import mutation_table as mt  # noqa: E402


def main() -> int:
    drop = None
    if "--drop-file" in sys.argv:
        drop = sys.argv[sys.argv.index("--drop-file") + 1]
    t_cpu0, t_thr0 = time.process_time(), time.thread_time()
    with tempfile.TemporaryDirectory(prefix="d3s3-drift-reach-") as d:
        out = Path(d)
        env = mt.hook_env(out / "trace")
        cap = out / "branch.json"
        full_env = {**os.environ, **env,
                    "PYTHONPATH": mt.traced_pythonpath(env, str(ROOT / "tests" / "hastub"))}
        t = time.monotonic()
        p = subprocess.run([sys.executable, str(ROOT / "tests/env_drift.py"),
                            "--capture", str(ROOT), str(cap), "--all"],
                           cwd=ROOT, env=full_env, capture_output=True, text=True)
        wall = time.monotonic() - t
        reach = mt.collect(out / "trace")
        reach["rc"] = p.returncode
        n_scen = len(json.loads(cap.read_text())) if cap.exists() else 0
    if p.returncode != 0:
        print(p.stdout[-2000:], p.stderr[-2000:])
    hits = {k: v for k, v in reach["hits"].items() if k.startswith(mt.PKG)}
    if drop:
        hits.pop(drop, None)
    rec = {"script": "tests/env_drift.py[capture]", "rc": p.returncode,
           "failed": 0 if p.returncode == 0 else 1, "seconds": round(wall, 1),
           "reach": {"hits": hits,
                     "reads": [r for r in reach["reads"] if r.startswith(mt.PKG)],
                     "problems": mt.reach_problems(reach),
                     "processes": reach["processes"]}}
    (HERE / "reach").mkdir(exist_ok=True)
    (HERE / "reach" / "tests_env_drift.py_capture.json").write_text(
        json.dumps(rec, indent=0))
    print(f"RESULT scenarios_captured={n_scen} count")
    print(f"RESULT files_hit={len(hits)} count")
    print(f"RESULT lines_hit={sum(len(v) for v in hits.values())} count")
    print(f"RESULT problems={len(rec['reach']['problems'])} count "
          f"{rec['reach']['problems']}")
    print(f"RESULT wall={wall:.0f} s (provisional)")
    pc, tc = time.process_time() - t_cpu0, time.thread_time() - t_thr0
    print(f"RESULT thread_factor={pc / tc if tc else 0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = sum(int(ln.split()[1]) for ln in open("/proc/vmstat")
                 if ln.startswith("pswpin"))
    except OSError:
        sw = -1
    print(f"RESULT swapins={sw}")
    return 0 if p.returncode == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
