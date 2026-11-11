#!/usr/bin/env python3
"""remerge_main.sh exits non-zero when the App push refuses (carry 15).

Run: python3 -I tools/audit/seat/remerge_main_selftest.py

Copies remerge_main.sh, pr_args.sh and gh_read.py into a throwaway repo beside a
bare origin, with a fake `gh` and a fake tools/pr/app_push.sh that prints PUSHED
only when the worktree is attached to the branch (as the real one refuses a
detached HEAD). The detached case must end non-zero with `REMERGE FAILED ... at
push`; the attached case must end 0 (null control). --mutant plants the old
tail (RESULT with no exit) and expects the detached case to be seen passing,
i.e. the self-test to fail.
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tests"))
from throwaway_git import throwaway_git_clone, throwaway_git_env, throwaway_git_init  # noqa: E402

SEAT = Path(__file__).resolve().parent


def sh(*a, cwd=None, env=None):
    return subprocess.run(a, cwd=cwd, capture_output=True, text=True, env={**throwaway_git_env(), **(env or {})})


def case(root, script, detached):
    o, r, w = root / "o", root / "r", root / "w"
    for d in (o, r, w):
        shutil.rmtree(d, ignore_errors=True)
    throwaway_git_init(o, "-q", "-b", "main")
    for name, branch in (("a", None), ("b", "fix/x"), ("c", "main")):
        if branch and branch != "main":
            sh("git", "checkout", "-q", "-b", branch, cwd=o)
        elif branch == "main":
            sh("git", "checkout", "-q", "main", cwd=o)
        (o / name).write_text(name)
        sh("git", "add", name, cwd=o)
        sh("git", "commit", "-qm", name, cwd=o)
    throwaway_git_clone(o, r, "-q")
    for f in ("pr_args.sh", "gh_read.py"):
        (r / "tools/audit/seat").mkdir(parents=True, exist_ok=True)
        shutil.copy(SEAT / f, r / "tools/audit/seat" / f)
    (r / "tools/audit/seat/remerge_main.sh").write_text(script)
    (r / "tools/pr").mkdir(parents=True, exist_ok=True)
    (r / "tools/pr/app_push.sh").write_text(
        '#!/bin/bash\nW=$3\nif git -C "$W" symbolic-ref -q HEAD >/dev/null; then echo PUSHED; '
        'else echo "REFUSE: worktree HEAD is not the committed tip"; fi\n')
    (r / "tests").mkdir(exist_ok=True)
    (r / "tests/env_drift.py").write_text("")
    bindir = root / "bin"
    bindir.mkdir(exist_ok=True)
    (bindir / "gh").write_text("#!/bin/bash\necho " + "e" * 40 + "\n")
    (bindir / "gh").chmod(0o755)
    sh("git", "fetch", "-q", "origin", cwd=r)
    if detached:
        sh("git", "worktree", "add", "-q", "--detach", str(w), "origin/fix/x", cwd=r)
    else:
        sh("git", "worktree", "add", "-q", "-B", "fix/x", str(w), "origin/fix/x", cwd=r)
    body = root / "body.md"
    body.write_text("Closes #1\n")
    # the script's sleep 5 is the real one; shorten it in the copy
    (r / "tools/audit/seat/remerge_main.sh").write_text(
        (r / "tools/audit/seat/remerge_main.sh").read_text().replace("sleep 5;", ""))
    return sh("bash", "tools/audit/seat/remerge_main.sh", "1", str(w), "fix/x", str(body), cwd=r,
              env={"PATH": f"{bindir}:{os.environ['PATH']}"})


def main():
    mutant = "--mutant" in sys.argv
    script = (SEAT / "remerge_main.sh").read_text()
    if mutant:
        script = script.replace('exit 1; fi  # mut:remergepush', 'true; fi  # mut:remergepush')
        assert script != (SEAT / "remerge_main.sh").read_text()
    fails = 0
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        det = case(root, script, True)
        att = case(root, script, False)
    checks = {
        "a refused push (detached worktree) exits non-zero and says REMERGE FAILED at push":
            det.returncode != 0 and "REMERGE FAILED 1 at push" in det.stdout,
        "null control: the attached worktree pushes and exits 0": att.returncode == 0 and "PUSHED" in att.stdout,
    }
    for k, v in checks.items():
        print(("  ok   " if v else "  FAIL ") + k)
        fails += not v
    print(f"remerge_main self-test: {len(checks)} checks, {fails} failed")
    return 1 if fails else 0


sys.exit(main())
