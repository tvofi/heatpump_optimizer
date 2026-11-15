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
name; a fake tools/pr/app_mint.sh records which repository the token is minted
for, and a fake `curl` plays GitHub's update-branch on the origin. --mutant=<name>
deletes the line ending `# mut:<name>` (remergeforkarg, remergeforkback) and
expects the self-test to fail.
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
CURL = r"""#!/bin/bash
echo "$*" >> "$FAKE_LOG"
o=$FAKE_ORIGIN
case "$*" in
  *"-X PUT"*update-branch*)
    [ "$FAKE_MODE" = refused ] && { echo "curl: (22) The requested URL returned error: 422" >&2; exit 22; }
    [ "$FAKE_MODE" = still ] && exit 0
    old=$(git -C "$o" rev-parse refs/pull/1/head); m=$(git -C "$o" rev-parse main)
    t=$(git -C "$o" merge-tree --write-tree "$old" "$m")
    [ "$FAKE_MODE" = extra ] && t=$(git -C "$o" rev-parse "$old^{tree}")
    # side: the second parent is main's tree on a commit off main's first-parent line; notold: the first parent is not the old head
    [ "$FAKE_MODE" = side ] && m=$(git -C "$o" commit-tree "$m^{tree}" -p "$m" -m "beside main")
    if [ "$FAKE_MODE" = commit ]; then c=$(git -C "$o" commit-tree "$t" -p "$old" -m "not a merge")
    elif [ "$FAKE_MODE" = notold ]; then c=$(git -C "$o" commit-tree "$t" -p "$old^" -p "$m" -m merge)
    else c=$(git -C "$o" commit-tree "$t" -p "$old" -p "$m" -m merge); fi
    git -C "$o" update-ref refs/pull/1/head "$c" ;;
  *pulls/1) printf '{"head": {"sha": "%s"}}' "$(git -C "$o" rev-parse refs/pull/1/head)" ;;
  *) echo "fake curl: unexpected $*" >&2; exit 1 ;;
esac
"""
MINT = r"""mint_cleanup() { [ -z "${PRIV:-}" ] || rm -rf "$PRIV"; }
mint_identity() { :; }
mint_token() { echo "minted $1" >> "$FAKE_LOG"; PRIV=$(mktemp -d); echo "Authorization: Bearer t" > "$PRIV/token.h"; }
"""


def fork_case(root, script, mode, head_repo=FORK):
    """remerge_main.sh --head-repo on a head that is only refs/pull/1/head; <mode> is the fake
    GitHub's answer (ok, refused, still: accepted and nothing moved, extra: a tree that is not the merge, commit: a 1-parent head)
    or `conflict` (the fork head edits what main edited). Returns (run, facts)."""
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
    old = sh("git", "rev-parse", "refs/pull/1/head", cwd=o).stdout.strip()
    ours = sh("git", "rev-parse", "fix/x", cwd=o).stdout.strip()
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
    body = root / "body.md"
    body.write_text("Closes #1\n")
    run = sh("bash", "tools/audit/seat/remerge_main.sh", "1", str(w), "fix/x", str(body), "--head-repo", head_repo,
             cwd=r, env={"PATH": f"{bindir}:{os.environ['PATH']}", "FAKE_LOG": str(log), "FAKE_ORIGIN": str(o),
                         "FAKE_MODE": mode, "REMERGE_POLLS": "2"})
    return run, {"old": old, "new": sh("git", "rev-parse", "refs/pull/1/head", cwd=o).stdout.strip(),
                 "ours_kept": sh("git", "rev-parse", "fix/x", cwd=o).stdout.strip() == ours, "log": log.read_text()}


def fork_checks(root, script):
    ok, f = fork_case(root, script, "ok")
    put = "-X PUT" in f["log"] and f"repos/{OURS}/pulls/1/update-branch" in f["log"] \
        and '{"expected_head_sha":"%s"}' % f["old"] in f["log"]
    out = {
        "a fork head is merged by update-branch at the expected head and reads back PUSHED at the new head":
            ok.returncode == 0 and put and f["new"] != f["old"]
            and f"PUSHED {f['new']} to {FORK}:fix/x" in ok.stdout and "RECARRY: fork head" in ok.stdout,
        "... the token is minted for OUR repository, never the fork's, and app_push.sh is not run":
            f"minted {OURS}\n" in f["log"] and f"minted {FORK}" not in f["log"] and "app_push" not in f["log"],
        "... and our own branch of the fork's branch name is neither read as the start nor moved":
            f["ours_kept"] and ok.returncode == 0,
    }
    no, f = fork_case(root, script, "refused")
    out["a refused update-branch is REMERGE FAILED at push naming the fork, non-zero, never PUSHED"] = (
        no.returncode != 0 and f"REMERGE FAILED 1 at push (fork {FORK}:fix/x)" in no.stdout
        and "maintainer edits" in no.stdout and "PUSHED" not in no.stdout and f["new"] == f["old"])
    no, f = fork_case(root, script, "still")
    out["an update-branch GitHub accepted that moved nothing is REMERGE FAILED at push saying so, never PUSHED"] = (
        no.returncode != 0 and f"did not move off {f['old']}" in no.stdout and "PUSHED" not in no.stdout)
    for mode, what in (("extra", "a tree that is not git's automatic merge"), ("commit", "one parent"),
                       ("side", "a second parent that is no first-parent commit of main (its tree is main's)"),
                       ("notold", "a first parent that is not the old head (the tree is the automatic merge)")):
        no, f = fork_case(root, script, mode)
        out[f"a new head with {what} fails the read-back: not PUSHED, non-zero"] = (
            no.returncode != 0 and "is not the automatic 2-parent merge" in no.stdout and "PUSHED" not in no.stdout)
    no, f = fork_case(root, script, "conflict")
    out["a fork head main does not merge into is MERGE CONFLICT before any token or update-branch"] = (
        no.returncode != 0 and "MERGE CONFLICT 1" in no.stdout and f["log"] == "")
    no, f = fork_case(root, script, "ok", head_repo=OURS)
    out["--head-repo naming our own repository refuses at args, nothing fetched, minted or asked"] = (
        no.returncode != 0 and "REMERGE FAILED 1 at args" in no.stdout and f["log"] == "" and f["new"] == f["old"])
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
