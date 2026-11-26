#!/usr/bin/env python3
"""Step 6d's predictor timed per arm over one fixed diff, at one tree (R10-RCA-OPEN-PREPR-SLOW, C4).

    python3 dev/audit/harnesses/prepr_6d_arms.py <commit> [<file> ...]

In a throwaway worktree of <commit>, commits one comment line appended to each
<file> (default `TOUCH`, the paths of slim-p2's diff at 6671786843 that a gate
cannot scope, code and prose, that still exist), then runs that tree's own
`tools/pr/ci_predict.py --base <commit> --record-self-tests`, prepr's 6d call,
with each arm, each restoring job of GRADER and each STEP REPLAY replay timed.
The diff is the same bytes at any <commit> where the files exist, so two
commits run on one host, seconds apart, compare the predictor and nothing else:
`<merge base>` is the before, `<fixed head>` the after. Prints one
`ARM <name> <s>` line per arm, `JOB` per restoring job, `REPLAY` per replay,
then `wall_s`, `predict_sha1` (a sha1 of the sorted PREDICT lines: the
before/after identity check `open_prepr_6d.sh` prints) and `predict_lines`,
`left_to_ci` (the steps the replay budget left to CI) and the predictor's
last line. Hours at a full diff on a 4-CPU container; run it in the background.
"""
from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

TOUCH = (".github/workflows/governance.yml", ".github/workflows/tests.yml", "tests/entities.py",
         "tools/pr/ci_predict.py", "tools/audit/seat/merge_train.py", "tools/audit/seat/body_push.sh",
         "tools/audit/seat/bus.sh", "tools/audit/seat/postmerge.py", "tools/pr/app_approve.sh",
         "dev/governance/roles/fixer.md", "CLAUDE.md")

# Runs inside the throwaway tree: wraps the module's own functions, changes none.
TIMER = r'''
import sys, time
sys.path.insert(0, "tools/pr")
import ci_predict as cp
def say(*a):
    print(*a, file=sys.stderr, flush=True)
def wrap(name, label):
    f = getattr(cp, name, None)
    if f is None:
        return
    def timed(*a, **k):
        t = time.monotonic(); r = f(*a, **k)
        say(label(a, r), f"{time.monotonic() - t:.1f}")
        return r
    setattr(cp, name, timed)
wrap("ci_tree_run", lambda a, r: f"JOB {a[2]}")
wrap("replay_step", lambda a, r: f"REPLAY rc={r}")
arms = cp.run_arms
def run_arms(arms_, only, record):
    out = []
    for name, arm in arms_:
        if cp.arm_runs(name, only, record):
            t = time.monotonic(); p = arm(); out += p
            say(f"ARM {name}", f"{time.monotonic() - t:.1f}")
    return out
cp.run_arms = run_arms
sys.exit(cp.main(sys.argv[1:]))
'''


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    commit, files = argv[0], tuple(argv[1:]) or TOUCH
    repo = Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip())
    with tempfile.TemporaryDirectory() as d:
        wt = Path(d) / "t"
        subprocess.run(["git", "-C", str(repo), "worktree", "add", "-q", "--detach", str(wt), commit], check=True)
        try:
            sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=wt, text=True).strip()
            held = [f for f in files if (wt / f).is_file()]
            for f in held:
                with open(wt / f, "a") as fh:
                    fh.write("\n<!-- prepr_6d_arms touch -->\n" if f.endswith(".md") else "\n# prepr_6d_arms touch\n")
            subprocess.run(["git", "-c", "user.name=h", "-c", "user.email=h@h", "commit", "-qam",
                            "prepr_6d_arms touch"], cwd=wt, check=True)
            (Path(d) / "timer.py").write_text(TIMER)
            env = dict(os.environ, PYTHONPATH="tests/hastub")
            t = time.monotonic()
            r = subprocess.run([sys.executable, str(Path(d) / "timer.py"), "--base", sha, "--record-self-tests"],
                               cwd=wt, env=env, capture_output=True, text=True)
            wall = time.monotonic() - t
        finally:
            subprocess.run(["git", "-C", str(repo), "worktree", "remove", "--force", str(wt)])
    timed = [l for l in r.stderr.splitlines() if l.startswith(("ARM ", "JOB ", "REPLAY "))]
    pred = sorted(l for l in r.stdout.splitlines() if l.startswith("PREDICT"))
    left = [l for l in r.stdout.splitlines() if l.startswith("NOTE    LEFT TO CI")]
    print(f"at={sha} touched={len(held)} rc={r.returncode}")
    print("\n".join(timed))
    print(f"wall_s={wall:.0f}")
    print(f"predict_sha1={hashlib.sha1(''.join(l + chr(10) for l in pred).encode()).hexdigest()} "
          f"predict_lines={len(pred)}")
    print(f"left_to_ci={left[0].split()[4] if left else 0}")
    print((r.stdout.strip().splitlines() or ["(no output)"])[-1])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
