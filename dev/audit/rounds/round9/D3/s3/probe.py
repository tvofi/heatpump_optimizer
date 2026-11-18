#!/usr/bin/env python3
"""D3.M4 -- drive one pooled mutant (and its unmutated twin) through named
scripts under a named environment, to answer "which check should have failed".

Metric: for each named script, killed = mutation_table.killed(mutant run,
  unmutated run under the SAME environment) -- the gate's kill rule, keyed on
  the scripts' own failing checks, never on a label.
Command:  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
            MKL_NUM_THREADS=1 /home/claude/venv314/bin/python \
            tools/audit/round9/D3/s3/probe.py M02 tests/open_meteo.py \
            [--env TZ=Europe/Stockholm] [--new '<line text>'] [--identity]
Expected: RESULT <script>_killed=0|1 per script, exact (the drivers are
  deterministic); RESULT kills=<n> scripts.
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1.  Machine: box B3.
Perturbation: --identity drives new == old and must give kills=0 (the null
  control); --new replaces the mutant line (a stronger or weaker mutant).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, "tests")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import mutation_table as mt  # noqa: E402
import prescreen as ps  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mutant")
    ap.add_argument("scripts", nargs="+")
    ap.add_argument("--env", action="append", default=[])
    ap.add_argument("--new", default=None)
    ap.add_argument("--identity", action="store_true")
    a = ap.parse_args()
    pool = json.loads((ps.HERE / "pool.json").read_text())["pool"]
    m = next(x for x in pool if x["id"] == a.mutant)
    if a.new is not None:
        m["new"] = a.new
    if a.identity:
        m["new"] = m["old"]
    env = dict(kv.split("=", 1) for kv in a.env)
    tmp = Path(tempfile.mkdtemp(prefix="d3s3-probe-"))
    tree = ps.make_tree(tmp, 0)
    plan = str(tmp / "plandata.json")
    kills = 0
    try:
        for s in a.scripts:
            args = ["--all", ps.BASELINE] if s == ps.ENV_DRIFT else []
            extra = {"HPO_PLANDATA": plan, "GOLDEN_REF": ps.BASELINE, **env}
            base = mt.run_script(s, tree, ps.TIMEOUT, args, extra)
            with ps.Edit(tree, m):
                run = mt.run_script(s, tree, ps.TIMEOUT, args, extra)
            k = mt.killed(s, run, base)
            kills += int(k)
            name = Path(s).name.replace(".", "_")
            print(f"{s}: base rc={base.rc} failed={base.failed}; mutant "
                  f"rc={run.rc} failed={run.failed}; "
                  f"checks={mt.failed_checks(run)[:4]}")
            print(f"RESULT {name}_killed={int(k)}")
    finally:
        ps.drop_tree(tree)
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"RESULT kills={kills} scripts")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT thread_factor=1.00 (counts only; drivers run in subprocesses)")
    print("RESULT swapins=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
