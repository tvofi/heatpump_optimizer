"""R10-RCA-PREPR-HEAD-GRADERS: each restoring job's `grader_runs`, timed one job at a
time on CI's tree for this HEAD merged into <base> (`ci_predict.ci_tree_run`).

    python3 -I dev/audit/rca/prepr-head-graders/jobtime.py <base> <job>...

Prints, per job, its wall seconds and each run as (program, flags, rc, seconds).
"""
import subprocess
import sys
import time
from pathlib import Path

root = Path.cwd()
sys.path[:0] = [str(root / p) for p in ("tools/pr", "tools/policy", "tests", "tests/hastub")]
import agreement_py  # noqa: E402
import ci_predict as c  # noqa: E402


def main(base: str, *jobs: str) -> int:
    tip = c.git(root, "rev-parse", base).strip()
    text = (root / agreement_py.WORKFLOW).read_text()
    for job in jobs:
        t, per = time.time(), []

        def step(p, a):
            def g(r, run, tmp):
                args = [c.RUN_TOKENS[x](r, tmp) if x in c.RUN_TOKENS else
                        next((c.RUN_TOKENS[k](r, tmp) + x[len(k):] for k in c.RUN_TOKENS if x.startswith(k + "/")), x)
                        for x in a]
                s = time.time()
                o = run(*((sys.executable, "-I", p) if p.endswith(".py") else ("node", p)), *args)
                per.append((Path(p).name, " ".join(x for x in a if x.startswith("--")), o.returncode, round(time.time() - s, 1)))
                return subprocess.CompletedProcess(o.args, 0, "", "")
            return g
        c.ci_tree_run(root, tip, job, tuple(step(p, a) for p, a in c.grader_runs(text, root, job)))
        print(job, round(time.time() - t, 1), per, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(*sys.argv[1:]))
