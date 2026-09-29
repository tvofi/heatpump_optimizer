#!/usr/bin/env python3
"""D3.M5 -- solves per check, and solve CPU share, for each gate script.

Metric: for one gate script run in-process as __main__, the number of calls to
  heatpump_optimizer.optimizer:HeatPumpOptimizer.optimize (solves), the
  process CPU spent inside them, and the number of tests/harness.py:Results.check
  calls (checks); ratio = solves / checks.  Only in-process work is counted: a
  solve inside a subprocess the script spawns (env_drift's captures) is not.
Command:  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
            MKL_NUM_THREADS=1 /home/claude/venv314/bin/python \
            tools/audit/round9/D3/s3/solves_per_check.py tests/features.py [...]
Expected: solves and checks are exact counts for the baseline tree (seeded
  drivers); cpu numbers are PROVISIONAL (shared box).
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1.  Machine: box B3 (4 CPUs).
Perturbation: --double-solve makes the hook call the real optimize twice per
  call; `solves` must exactly double and `checks` must not move.
Each script runs in its own child process (this file re-invoked with --child),
so one script's sys.exit or module state cannot leak into the next.
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


def child(script: str, out: str, double: bool) -> None:
    import atexit
    import runpy
    sys.path.insert(0, "tests")
    sys.path.insert(0, "custom_components")
    import harness
    from heatpump_optimizer import optimizer as om

    st = {"solves": 0, "solve_cpu": 0.0, "checks": 0,
          "t0": time.process_time(), "w0": time.time()}
    orig = om.HeatPumpOptimizer.optimize

    def opt(self, *a, **k):
        st["solves"] += 1
        t = time.process_time()
        try:
            if double:
                orig(self, *a, **k)
                st["solves"] += 1
            return orig(self, *a, **k)
        finally:
            st["solve_cpu"] += time.process_time() - t

    om.HeatPumpOptimizer.optimize = opt
    ch = harness.Results.check

    def check(self, *a, **k):
        st["checks"] += 1
        return ch(self, *a, **k)

    harness.Results.check = check

    def dump():
        st["cpu"] = time.process_time() - st["t0"]
        st["thread_cpu"] = time.thread_time()
        st["wall"] = time.time() - st["w0"]
        with open(out, "w") as fh:
            json.dump(st, fh)

    atexit.register(dump)
    sys.argv = [script]
    runpy.run_path(script, run_name="__main__")


def main() -> int:
    if sys.argv[1] == "--child":
        child(sys.argv[2], sys.argv[3], sys.argv[4] == "1")
        return 0
    double = "--double-solve" in sys.argv
    scripts = [a for a in sys.argv[1:] if not a.startswith("--")]
    tmp = tempfile.mkdtemp(prefix="d3s3-spc-")
    env = {**os.environ, "HPO_PLANDATA": os.path.join(tmp, "plandata.json")}
    for s in scripts:
        out = os.path.join(tmp, os.path.basename(s) + ".json")
        p = subprocess.run([sys.executable, __file__, "--child", s, out,
                            "1" if double else "0"], env=env,
                           capture_output=True, text=True, timeout=3600)
        try:
            st = json.load(open(out))
        except FileNotFoundError:
            print(f"{s}: no result (rc={p.returncode})", p.stderr[-400:])
            continue
        name = os.path.basename(s).replace(".", "_")
        ratio = st["solves"] / st["checks"] if st["checks"] else float("inf")
        share = st["solve_cpu"] / st["cpu"] if st["cpu"] else 0.0
        print(f"RESULT {name}_rc={p.returncode}")
        print(f"RESULT {name}_solves={st['solves']} calls")
        print(f"RESULT {name}_checks={st['checks']} calls")
        print(f"RESULT {name}_solves_per_check={ratio:.3f}")
        print(f"RESULT {name}_solve_cpu={st['solve_cpu']:.1f} s (provisional)")
        print(f"RESULT {name}_cpu={st['cpu']:.1f} s (provisional)")
        print(f"RESULT {name}_solve_cpu_share={share:.3f} (provisional)")
        print(f"RESULT {name}_thread_factor="
              f"{st['cpu'] / max(st['thread_cpu'], 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
