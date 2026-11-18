#!/usr/bin/env python3
"""D3.M2 reach rows for gate scripts the mutation lane does not drive in the
pre-screen (the brief skips edge.py and backtest.py there), so reach_census.py
can say whether ANY gate script but stress.py executes an unpinned site.

Metric (one line): the (file, line) pairs of production code each named
script's unmutated, green run fires LINE events on, via the lane's own
tracer. Count key: production code objects' LINE events.
Hooks: tests/mutation_table.py:traced_baseline (REACH_HOOK) around
mutation_table.run_script, the very path prescreen.py's baselines take.
Command:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 \
          dev/audit/rounds/round11/D3/s3/trace_extra.py tests/edge.py tests/backtest.py
--allow-red keeps the trace of a run red at this export's baseline (rc and
failing-check count recorded; reach_problems then names it as not green).
Perturbation: none of its own -- it writes reach rows; reach_census.py's
--drop DRIVER is the control on what a row contributes (drop it: every site
only it executed moves to REACH-DEAD).
Expected: exact line sets (deterministic suite). Wall provisional.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box B3, 4 vCPU.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json
import sys
import time
from pathlib import Path

ROOT = Path.cwd()
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tests"))
import mutation_table as mt  # noqa: E402


def main() -> int:
    t_cpu0, t_thr0 = time.process_time(), time.thread_time()
    (HERE / "reach").mkdir(exist_ok=True)
    allow_red = "--allow-red" in sys.argv
    for script in [a for a in sys.argv[1:] if not a.startswith("--")]:
        if allow_red:
            # mutation_table.traced_baseline re-runs a red traced run untraced
            # and keeps no reach. A script red at THIS export's baseline on
            # checks that read no production file (entities.py: two machinery
            # checks; doc_claims.py: the finder wall's absent backlog) still
            # runs every other check, so its trace is kept, marked rc!=0.
            import tempfile
            with tempfile.TemporaryDirectory(prefix="reach-") as d:
                out = Path(d)
                env = mt.hook_env(out)
                tenv = {**env, "PYTHONPATH": mt.traced_pythonpath(env, "tests/hastub")}
                got = mt.run_script(script, ROOT, 6000, None, tenv)
                reach = None if got.timed_out else mt.collect(out)
            if reach is not None:
                reach["rc"] = got.rc
                print(f"  {script}: traced run rc={got.rc} failed={got.failed}: "
                      + "; ".join(mt.failed_checks(got)[:0] or []) )
        else:
            got, reach = mt.traced_baseline(mt.run_script, script, ROOT, 6000,
                                            None, None)
        rec = {"script": script, "rc": got.rc, "failed": got.failed,
               "seconds": round(got.seconds, 1), "reach": None}
        if reach is not None:
            rec["reach"] = {
                "hits": {k: v for k, v in reach["hits"].items()
                         if k.startswith(mt.PKG)},
                "reads": [r for r in reach["reads"] if r.startswith(mt.PKG)],
                "problems": mt.reach_problems(reach),
                "processes": reach["processes"]}
        # an --allow-red row goes to reach_red/, where prescreen.py's own
        # baseline (which records a red driver as untraced) cannot clobber it
        outdir = HERE / ("reach_red" if allow_red else "reach")
        outdir.mkdir(exist_ok=True)
        (outdir / (script.replace("/", "_") + ".json")).write_text(
            json.dumps(rec, indent=0))
        n = sum(len(v) for v in (rec["reach"] or {}).get("hits", {}).values())
        print(f"RESULT {script}:rc={got.rc} count")
        print(f"RESULT {script}:lines_hit={n} count")
        print(f"RESULT {script}:problems="
              f"{(rec['reach'] or {}).get('problems', ['no trace'])}")
        print(f"RESULT {script}:wall={got.seconds:.0f} s (provisional)")
    pc, tc = time.process_time() - t_cpu0, time.thread_time() - t_thr0
    print(f"RESULT thread_factor={pc / tc if tc else 0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = sum(int(ln.split()[1]) for ln in open("/proc/vmstat")
                 if ln.startswith("pswpin"))
    except OSError:
        sw = -1
    print(f"RESULT swapins={sw}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
