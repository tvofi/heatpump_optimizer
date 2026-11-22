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

The fork cases (decision 0017, --head-repo): the head lives only at
refs/pull/1/head of the origin, beside a branch of OURS with the fork's branch
name. remerge_main.sh must refuse before it fetches, mints a token, merges or
pushes, whatever the fork's state (a stale head, a head main conflicts with),
and a fake `curl` and fake tools/pr/app_mint.sh record any call. --mutant=<name>
deletes the line ending `# mut:<name>` (remergeforkrefuse) and expects the
self-test to fail.
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


FORK = "contributor/heatpump_optimizer"
OURS = "tvofi/heatpump_optimizer"
CURL = """#!/bin/bash
echo "curl $*" >> "$FAKE_LOG"
exit 1
"""
MINT = """mint_cleanup() { :; }
mint_identity() { echo "minted" >> "$FAKE_LOG"; }
mint_token() { echo "minted $1" >> "$FAKE_LOG"; }
"""


def fork_case(root, script, mode, head_repo=FORK):
    """remerge_main.sh --head-repo on a head that is only refs/pull/1/head, stale against main
    (mode `stale`) or in conflict with it (`conflict`). Returns (run, facts): the origin's refs
    before and after, and the log of every curl, mint and app_push the script made."""
    o, r, w = root / "o", root / "r", root / "w"
    for d in (o, r, w):
        shutil.rmtree(d, ignore_errors=True)
    throwaway_git_init(o, "-q", "-b", "main")

    def commit(name, text):
        (o / name).write_text(text)
        sh("git", "add", name, cwd=o)
        sh("git", "commit", "-qm", name, cwd=o)
    commit("a", "a")
    sh("git", "checkout", "-q", "-b", "fix/x", cwd=o)  # OUR branch of the fork's branch name
    commit("ours", "ours")
    sh("git", "checkout", "-q", "--detach", "main", cwd=o)
    commit("c" if mode == "conflict" else "b", "fork")  # the fork's head: a pull ref, no branch
    sh("git", "update-ref", "refs/pull/1/head", "HEAD", cwd=o)
    sh("git", "checkout", "-q", "main", cwd=o)
    commit("c", "main")
    refs = lambda: sh("git", "for-each-ref", "--format=%(refname) %(objectname)", cwd=o).stdout  # noqa: E731
    before = refs()
    throwaway_git_clone(o, r, "-q")
    for f in ("pr_args.sh", "gh_read.py"):
        (r / "tools/audit/seat").mkdir(parents=True, exist_ok=True)
        shutil.copy(SEAT / f, r / "tools/audit/seat" / f)
    (r / "tools/audit/seat/remerge_main.sh").write_text(script.replace("sleep 5;", ""))
    (r / "tools/pr").mkdir(parents=True, exist_ok=True)
    (r / "tools/pr/app_mint.sh").write_text(MINT)
    (r / "tools/pr/app_push.sh").write_text('#!/bin/bash\necho "app_push $*" >> "$FAKE_LOG"\necho PUSHED\n')
    (r / "tests").mkdir(exist_ok=True)
    (r / "tests/env_drift.py").write_text("")
    bindir = root / "forkbin"
    bindir.mkdir(exist_ok=True)
    (bindir / "curl").write_text(CURL)
    (bindir / "curl").chmod(0o755)
    log = root / "fork.log"
    log.write_text("")
    sh("git", "fetch", "-q", "origin", "+refs/pull/1/head:refs/remotes/pull/1/head", cwd=r)
    sh("git", "worktree", "add", "-q", "--detach", str(w), "refs/remotes/pull/1/head", cwd=r)
    head_before = sh("git", "rev-parse", "HEAD", cwd=w).stdout
    body = root / "body.md"
    body.write_text("Closes #1\n")
    # a `git` wrapper that records every fetch or push the script attempts
    (bindir / "git").write_text('#!/bin/bash\ncase "$*" in *" fetch "*|"fetch "*|*" push "*|"push "*|*" -C "*" fetch "*) echo "git $*" >> "$FAKE_LOG";; esac\nexec '
                                + shutil.which("git") + ' "$@"\n')
    (bindir / "git").chmod(0o755)
    run = sh("bash", "tools/audit/seat/remerge_main.sh", "1", str(w), "fix/x", str(body), "--head-repo", head_repo,
             cwd=r, env={"PATH": f"{bindir}:{os.environ['PATH']}", "FAKE_LOG": str(log), "FAKE_ORIGIN": str(o)})
    return run, {"refs_same": refs() == before, "log": log.read_text(),
                 "worktree_same": sh("git", "rev-parse", "HEAD", cwd=w).stdout == head_before}


def fork_checks(root, script):
    out = {}
    for mode, what in (("stale", "a stale fork head (main moved past it)"), ("conflict", "a fork head main conflicts with")):
        no, f = fork_case(root, script, mode)
        out[f"{what} is refused, naming the fork and saying the contributor brings the branch up to date with main"] = (
            no.returncode != 0 and f"REMERGE FAILED 1 at fork ({FORK}:fix/x)" in no.stdout
            and "the contributor brings the branch up to date with main" in no.stdout
            and "PUSHED" not in no.stdout and "MERGE CONFLICT" not in no.stdout)
        out[f"... for {what}: nothing is fetched, minted, curled, app_pushed or pushed, and no ref or worktree moved"] = (
            f["log"] == "" and f["refs_same"] and f["worktree_same"])
    return out


def main():
    mutant = "--mutant" in sys.argv
    script = (SEAT / "remerge_main.sh").read_text()
    for name in (a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--mutant=")):
        kept = [ln for ln in script.splitlines(keepends=True) if not ln.rstrip().endswith(f"# mut:{name}")]
        assert len(kept) < script.count("\n"), f"no line ends `# mut:{name}`"
        script = "".join(kept)
    if mutant:
        script = script.replace('exit 1; fi  # mut:remergepush', 'true; fi  # mut:remergepush')
        assert script != (SEAT / "remerge_main.sh").read_text()
    fails = 0
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        det = case(root, script, True)
        att = case(root, script, False)
        fork = fork_checks(root, script)
    checks = {
        "a refused push (detached worktree) exits non-zero and says REMERGE FAILED at push":
            det.returncode != 0 and "REMERGE FAILED 1 at push" in det.stdout,
        "null control: the attached worktree pushes and exits 0": att.returncode == 0 and "PUSHED" in att.stdout,
        **fork,
    }
    for k, v in checks.items():
        print(("  ok   " if v else "  FAIL ") + k)
        fails += not v
    print(f"remerge_main self-test: {len(checks)} checks, {fails} failed")
    return 1 if fails else 0


sys.exit(main())
