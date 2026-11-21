#!/usr/bin/env python3
"""selftest_absorb.py -- the consumer of main's `selftest-closures` artifacts: one standing ref.

    python3 -I tools/audit/seat/selftest_absorb.py beat --repo-dir DIR [--repo OWNER/NAME]
        [--work DIR] [--max-runs N] [--run ID]... [--at SHA] [--push]
    python3 -I tools/audit/seat/selftest_absorb.py verify --repo-dir DIR --head SHA [--repo OWNER/NAME] [--work DIR]
    python3 tools/audit/seat/selftest_absorb.py --self-test

WHY (P-R11-SELFTEST-ABSORB; dev/audit/rca/R11-RCA-SELFTEST-TABLE-DRIFT.md
section 7). Main's push run measures every self-test step's reads and, where
tools/ci/selftest_closures.json misses one, computes the repaired table -- and
nothing committed it: each red became a hand hotfix measured at one sha and
outrun by the merges that added reads. This is the actor half, run by the
beatd row `selftest-absorb` (tools/audit/seat/beat_jobs.py).

ONE PASS:
  1. Reads main's newest ci.yml push runs (or the --run ids) and, per run, the
     drift step DRIFT of the JOB job: `red` when it concluded failure, `owed`
     when it concluded success with a `selftest-absorbed` artifact (the drift
     step's ABSORB OWED note, .github/workflows/governance.yml), `clean` when
     it succeeded without one; any other conclusion is no measurement.
  2. The newest measured run clean: `SELFTEST-ABSORB CLEAN`, rc 0, nothing written.
  3. Otherwise the `selftest-closures` artifact of every red or owed run back
     to the last clean one (at most --max-runs), absorbed by origin/main's TIP
     (or --at): a scratch clone under --work runs that commit's own
     `tools/ci/selftest_scope.py absorb --from A1 --from A2 ...`. At the tip,
     not at the runs' heads, so a merge since the runs is under the result and
     cannot outrun it.
  4. absorb added reads: `SELFTEST-ABSORB OWED <n> read(s), <m> step(s) ...`,
     rc 1. With --push the table is committed on the tip as the one standing
     ref STANDING, force-pushed by tools/pr/app_push.sh --branch-only
     (`pushed <sha>`), unless that ref already holds the same table on the
     same tip (`unchanged <sha>`); a refused push is `PUSH-REFUSED`.
  5. absorb added nothing: a refusal it reports remaining over the runs' own
     steps, or the newest run red at the tip itself (a refusal absorb cannot
     see: UNMEASURED, EXTRA, a wiring gap), is `SELFTEST-ABSORB RECORD-OWED`,
     rc 4, which only `selftest_scope.py record` repairs; else a repair merged
     since the runs: `SELFTEST-ABSORB CLEAN`, rc 0.
  rc 2: `SELFTEST-ABSORB UNREADABLE <why>` (gh, a run, an artifact, the clone
  or absorb).

A STOP ENDS THE TOOL IT RUNS (tools/audit/seat/pr_args.sh's pusher census,
`runner-py`). The pass runs app_push.sh, so a TERM or HUP unwinds like Ctrl-C
(`stop_on_signal`) and `sh` TERMs the running tool, whose own EXIT trap reaps
its tree, then waits for it; subprocess.run's own handler SIGKILLs, which runs
no trap, and an untrapped TERM orphans the push. The scratch clone carries
`maintenance.auto=false` (tests/throwaway_git.py's local layer), so no detached
repack outlives the pass in --work.

THE REVIEW of the standing pull request is mechanical
(dev/governance/roles/fix-review.md), and `verify` is it: the head changes
only the table; the commit message's `--at` is the head's parent; a pass
re-run there over the message's `--run` ids writes a table byte-identical to
the head's (`cmp`); and the parent's own `selftest_scope.py grows` finds no
read of the parent's table the head's drops. `SELFTEST-ABSORB VERIFIED`, rc 0;
else `SELFTEST-ABSORB VERIFY-REFUSED <why>`, rc 1; rc 2 unreadable.
"""
from __future__ import annotations

import json
import re
import shutil
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

JOB = "governance / instrument-self-tests"
DRIFT = "Refuse a self-test read set the committed table misses"
MEASURED, ABSORBED = "selftest-closures", "selftest-absorbed"
TABLE = "tools/ci/selftest_closures.json"
STANDING = "handoff/selftest-absorb"
SCOPE = "tools/ci/selftest_scope.py"
ADDED = re.compile(r"^selftest_scope absorb: (\d+) read\(s\) added to (\d+) step\(s\)$", re.M)
REMAIN = re.compile(r"^selftest_scope absorb: (\d+) refusal\(s\) remain over the sources' own steps$", re.M)
RUNS = "actions/workflows/ci.yml/runs?branch=main&event=push&status=completed&per_page=30"


class Unreadable(Exception):
    pass


TOOL_STOP_SECONDS = 10  # app_push.sh's reap grants its tree 2 s (pr_args.sh's PR_REAP_TENTHS)


def stop_on_signal() -> None:
    """TERM and HUP raise SystemExit(128 + signal), so a stop unwinds through `sh`."""
    def unwind(signum, _frame):
        raise SystemExit(128 + signum)
    for sig in (signal.SIGTERM, signal.SIGHUP):
        signal.signal(sig, unwind)


def sh(argv: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    try:
        p = subprocess.Popen(argv, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except OSError as e:
        return 127, "", f"{e.__class__.__name__}: {e}"
    try:
        out, err = p.communicate(timeout=900)
    except BaseException as e:  # a stop (stop_on_signal) or the timeout: TERM the tool, never orphan it
        p.terminate()
        try:
            p.wait(TOOL_STOP_SECONDS)
        except subprocess.TimeoutExpired:
            p.kill()
            p.wait()
        if isinstance(e, subprocess.TimeoutExpired):
            return 127, "", f"{e.__class__.__name__}: {e}"
        raise
    return p.returncode, out, err


def last(err: str) -> str:
    return (err.strip().splitlines() or [""])[-1][:200]


class Pass:
    """One beat's inputs; `run` is the edge the self-test replaces."""

    def __init__(self, repo: str, repo_dir: Path, work: Path, run=sh):
        self.repo, self.repo_dir, self.work, self.run = repo, repo_dir, work, run

    def gh(self, path: str) -> dict:
        rc, out, err = self.run(["gh", "api", f"repos/{self.repo}/{path}"])
        try:
            if rc == 0:
                return json.loads(out)
        except ValueError:
            pass
        raise Unreadable(f"gh api {path.split('?')[0]} rc={rc}: {last(err)}")

    def git(self, *args: str, cwd: Path | None = None) -> tuple[int, str, str]:
        return self.run(["git", *args], cwd)


def state(p: Pass, run_id: str) -> str | None:
    """`red`, `owed`, `clean`, or None when the run's drift step measured nothing."""
    jobs = p.gh(f"actions/runs/{run_id}/jobs?per_page=100&filter=latest")
    if jobs.get("total_count", 0) > len(jobs.get("jobs", [])):
        raise Unreadable(f"run {run_id} has more jobs than one page")
    step = next((s for j in jobs.get("jobs", []) if j.get("name") == JOB
                 for s in j.get("steps", []) if s.get("name") == DRIFT), {})
    if step.get("conclusion") == "failure":
        return "red"
    if step.get("conclusion") != "success":
        return None
    return "owed" if p.gh(f"actions/runs/{run_id}/artifacts?name={ABSORBED}").get("total_count", 0) else "clean"


def window(p: Pass, runs: list[tuple[str, str]], max_runs: int):
    """(the newest measured run as (id, sha, state) or None, the red or owed runs back to the last clean one)."""
    newest, take = None, []
    for rid, sha in runs:
        st = state(p, rid)
        if st is None:
            continue
        newest = newest or (rid, sha, st)
        if st == "clean" or len(take) >= max_runs:
            break
        take.append((rid, sha, st))
    return newest, take


def absorb(p: Pass, take: list, tip: str) -> tuple[int, int, int | None, Path, Path]:
    """Each run's artifact absorbed by the tip's own selftest_scope.py: (reads, steps, remaining, table, clone)."""
    if p.work.exists():
        shutil.rmtree(p.work)
    arts = []
    for rid, _, _ in take:
        d = p.work / "art" / str(rid)
        p.run(["gh", "run", "download", str(rid), "-R", p.repo, "-n", MEASURED, "-D", str(d)])
        if (d / "selftest_closures.json").is_file():
            arts.append(d / "selftest_closures.json")
    if not arts:
        raise Unreadable(f"no {MEASURED} artifact in run(s) {','.join(str(r) for r, _, _ in take)}")
    clone = p.work / "clone"
    out = p.work / "selftest_closures.json"
    for argv, cwd in ((["clone", "-c", "maintenance.auto=false", "-c", "gc.auto=0", "-q", "--shared", "--no-checkout", str(p.repo_dir), str(clone)], None),
                      (["checkout", "-q", "--detach", tip], clone)):
        rc, _, err = p.git(*argv, cwd=cwd)
        if rc != 0:
            raise Unreadable(f"git {argv[0]} rc={rc}: {last(err)}")
    argv = [sys.executable, "-I", SCOPE, "absorb", *[x for a in arts for x in ("--from", str(a))], "--out", str(out)]
    rc, text, err = p.run(argv, clone)
    added, remain = ADDED.search(text), REMAIN.search(text)
    if rc != 0 or not added:
        raise Unreadable(f"absorb at {tip[:12]} rc={rc}: {last(err) or last(text)}")
    return int(added[1]), int(added[2]), (int(remain[1]) if remain else None), out, clone


def push(p: Pass, clone: Path, tip: str, table: Path, ids: str, n: int, m: int) -> str:
    """The table committed on the tip as STANDING, force-pushed through app_push.sh; one result word and sha."""
    rc, url, err = p.git("-C", str(p.repo_dir), "remote", "get-url", "origin")
    if rc != 0 or p.git("-C", str(clone), "remote", "set-url", "origin", url.strip())[0] != 0:
        return f"PUSH-REFUSED origin url rc={rc}: {last(err)}"
    rc, have, err = p.git("-C", str(clone), "ls-remote", "origin", f"refs/heads/{STANDING}")
    if rc != 0:
        return f"PUSH-REFUSED ls-remote rc={rc}: {last(err)}"
    old = have.split()[0] if have.strip() else ""
    if old and p.git("-C", str(clone), "fetch", "-q", "origin", f"refs/heads/{STANDING}")[0] == 0:
        parent = p.git("-C", str(clone), "rev-parse", f"{old}^")[1].strip()
        blob = p.git("-C", str(clone), "rev-parse", f"{old}:{TABLE}")[1].strip()
        if parent == tip and blob and blob == p.git("-C", str(clone), "hash-object", str(table))[1].strip():
            return f"unchanged {old[:12]}"
    (clone / TABLE).parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(table, clone / TABLE)
    msg = (f"selftest-absorb: main's measured self-test reads at {tip[:12]}\n\n"
           f"{n} read(s) added to {m} step(s), absorbed from run(s) {ids} by the tip's own selftest_scope.py.\n"
           "Regenerate (fix-review.md, the standing absorb pull request): python3 -I "
           f"tools/audit/seat/selftest_absorb.py beat --repo-dir . --at {tip} "
           + " ".join(f"--run {r}" for r in ids.split(",")) + "\n")
    for argv in (["checkout", "-q", "-B", STANDING, tip], ["add", TABLE], ["commit", "-q", "-m", msg]):
        rc, _, err = p.git("-C", str(clone), *argv)
        if rc != 0:
            return f"PUSH-REFUSED git {argv[0]} rc={rc}: {last(err)}"
    rc, _, err = p.run(["bash", str(clone / "tools/pr/app_push.sh"), "--branch-only", p.repo, str(clone), STANDING], clone)
    if rc != 0:
        return f"PUSH-REFUSED app_push rc={rc}: {last(err)}"
    return f"pushed {p.git('-C', str(clone), 'rev-parse', 'HEAD')[1].strip()[:12]}"


def beat(p: Pass, runs_given: list[str], max_runs: int, at: str | None, do_push: bool) -> tuple[int, list[str]]:
    try:
        if runs_given:
            runs = [(r, "") for r in runs_given]
        else:
            runs = [(str(r["id"]), r["head_sha"]) for r in p.gh(RUNS).get("workflow_runs", [])]
        newest, take = window(p, runs, max_runs)
        if newest is None:
            raise Unreadable(f"no measured drift step in {len(runs)} run(s)")
        if newest[2] == "clean":
            at_sha = f" at {newest[1][:12]}" if newest[1] else ""
            return 0, [f"SELFTEST-ABSORB CLEAN{at_sha} (run {newest[0]}): nothing to absorb"]
        rc, _, err = p.git("-C", str(p.repo_dir), "fetch", "-q", "origin", "main")
        tip = at or p.git("-C", str(p.repo_dir), "rev-parse", "origin/main")[1].strip()
        if (rc != 0 and not at) or not re.fullmatch(r"[0-9a-f]{40}", tip):
            raise Unreadable(f"origin/main rc={rc}: {last(err)}")
        n, m, remain, table, clone = absorb(p, take, tip)
    except Unreadable as e:
        return 2, [f"SELFTEST-ABSORB UNREADABLE {e}"]
    ids = ",".join(str(r) for r, _, _ in take)
    if n:
        lines = [f"SELFTEST-ABSORB OWED {n} read(s), {m} step(s) at {tip[:12]} from run(s) {ids}; table {table}"]
        if do_push:
            lines.append(f"SELFTEST-ABSORB {push(p, clone, tip, table, ids, n, m)} {STANDING}")
        return 1, lines
    if remain is None:
        return 2, [f"SELFTEST-ABSORB UNREADABLE absorb at {tip[:12]} printed no remain line"]
    if remain or (newest[2] == "red" and newest[1] == tip):
        return 4, [f"SELFTEST-ABSORB RECORD-OWED drift red in run(s) {ids} and absorb at {tip[:12]} adds no read "
                   f"({remain} refusal(s) remain): re-record with python3 tools/ci/selftest_scope.py record --step ID (Linux)"]
    return 0, [f"SELFTEST-ABSORB CLEAN at {tip[:12]}: its table holds every read run(s) {ids} measured "
               "(a repair merged since)"]


def verify(p: Pass, head: str) -> tuple[int, list[str]]:
    """The standing pull request's mechanical review at `head`: regeneration and growth."""
    git = lambda *a: p.git("-C", str(p.repo_dir), *a)  # noqa: E731
    rc, parent, err = git("rev-parse", f"{head}^")
    rc2, paths, _ = git("diff", "--name-only", f"{head}^", head)
    rc3, msg, _ = git("log", "-1", "--format=%B", head)
    rc4, want, _ = git("show", f"{head}:{TABLE}")
    if rc or rc2 or rc3 or rc4:
        return 2, [f"SELFTEST-ABSORB UNREADABLE {head[:12]}: rc={rc}/{rc2}/{rc3}/{rc4}: {last(err)}"]
    parent, runs = parent.strip(), re.findall(r"--run (\d+)", msg)
    at = re.search(r"--at ([0-9a-f]{40})", msg)
    if paths.split() != [TABLE]:
        return 1, [f"SELFTEST-ABSORB VERIFY-REFUSED {head[:12]} changes {paths.split()}, not {TABLE} alone"]
    if not at or at[1] != parent or not runs:
        return 1, [f"SELFTEST-ABSORB VERIFY-REFUSED {head[:12]}'s message names no --at equal to its parent "
                   f"{parent[:12]} and --run ids"]
    rc, lines = beat(p, runs, len(runs), parent, False)
    if rc != 1:
        return 1, [f"SELFTEST-ABSORB VERIFY-REFUSED regeneration at {parent[:12]} absorbs nothing: {lines[0]}"]
    table, clone = p.work / "selftest_closures.json", p.work / "clone"
    if table.read_text() != want:
        return 1, [f"SELFTEST-ABSORB VERIFY-REFUSED the head's table differs from the regeneration at {parent[:12]} "
                   f"over run(s) {','.join(runs)} (cmp {table})"]
    rc, out, err = p.run([sys.executable, "-I", SCOPE, "grows", "--old", TABLE, "--new", str(table)], clone)
    if rc != 0:
        return 1, [f"SELFTEST-ABSORB VERIFY-REFUSED the head's table drops reads of its parent's: "
                   f"{last(out) or last(err)}"]
    return 0, [f"SELFTEST-ABSORB VERIFIED {head[:12]}: regenerated byte-identical at {parent[:12]} over run(s) "
               f"{','.join(runs)}, and it drops no read of its parent's table"]


def main(argv: list[str]) -> int:
    if argv[:1] == ["--self-test"]:
        return self_test()
    if argv[:1] not in (["beat"], ["verify"]):
        print(__doc__.split("\n\n")[0], file=sys.stderr)
        return 2
    opt = {"--repo": "tvofi/heatpump_optimizer", "--repo-dir": None, "--work": None, "--max-runs": "12", "--at": None,
           "--head": None}
    runs, i, args = [], 0, argv[1:]
    while i < len(args):
        if args[i] == "--push":
            opt["--push"] = "1"
            i += 1
        elif args[i] == "--run" and i + 1 < len(args):
            runs.append(args[i + 1])
            i += 2
        elif args[i] in opt and i + 1 < len(args):
            opt[args[i]] = args[i + 1]
            i += 2
        else:
            print(f"selftest_absorb: unknown argument {args[i]}", file=sys.stderr)
            return 2
    if not opt["--repo-dir"]:
        print("selftest_absorb: --repo-dir is required", file=sys.stderr)
        return 2
    stop_on_signal()
    repo_dir = Path(opt["--repo-dir"]).resolve()
    work = Path(opt["--work"] or repo_dir.parent / "selftest-absorb-work").resolve()
    if argv[0] == "verify":
        if not opt["--head"]:
            print("selftest_absorb: verify needs --head", file=sys.stderr)
            return 2
        rc, lines = verify(Pass(opt["--repo"], repo_dir, work), opt["--head"])
        print("\n".join(lines))
        return rc
    rc, lines = beat(Pass(opt["--repo"], repo_dir, work), runs, int(opt["--max-runs"]), opt["--at"],
                     opt.get("--push") == "1")
    print("\n".join(lines))
    return rc


# ---------------------------------------------------------------- self-test

#: The RCA's runs (P-R11-SELFTEST-ABSORB): the defect, run 44922703115 at
#: a8efe1d1c2 (7 refusals, 738 reads, absorbed equal to hotfix 25238b470a);
#: the fixed tree, the same run at 25238b470a (0 added); the null control,
#: green run 44379511133 at 107988b792.
DEFECT, GREEN = ("44922703115", "a8efe1d1c2" + "a" * 30), ("44379511133", "107988b792" + "b" * 30)
FIXED, NEWER = "25238b470a" + "c" * 30, "d" * 40


class Fake:
    """A gh/git/absorb world: runs {id: (drift conclusion, absorbed artifact?)}; records every argv."""

    def __init__(self, runs, order, added=(738, 7), remain=0, remote="", push_rc=0, tip=NEWER, gh_rc=0,
                 paths=TABLE + "\n", msg="", head_table='{"steps": {"x": {}}}', grows_rc=0):
        self.runs, self.order, self.added, self.remain = runs, order, added, remain
        self.remote, self.push_rc, self.tip, self.gh_rc, self.calls = remote, push_rc, tip, gh_rc, []
        self.paths, self.msg, self.head_table, self.grows_rc = paths, msg, head_table, grows_rc

    def __call__(self, argv, cwd=None):
        self.calls.append(list(argv))
        a = " ".join(argv)
        if argv[:2] == ["gh", "api"]:
            if self.gh_rc:
                return self.gh_rc, "", "HTTP 502"
            if "/workflows/ci.yml/runs" in a:
                return 0, json.dumps({"workflow_runs": [{"id": int(r), "head_sha": s} for r, s in self.order]}), ""
            rid = argv[2].split("/runs/")[1].split("/")[0]
            concl, absorbed = self.runs[rid]
            if "/jobs" in a:
                steps = [{"name": "Refuse a self-testing seat instrument that no step runs", "conclusion": "failure"},
                         {"name": DRIFT, "conclusion": concl}]
                return 0, json.dumps({"total_count": 2, "jobs": [{"name": "governance / gate", "steps": []},
                                                                  {"name": JOB, "steps": steps}]}), ""
            return 0, json.dumps({"total_count": int(absorbed)}), ""
        if argv[:3] == ["gh", "run", "download"]:
            d = Path(argv[argv.index("-D") + 1])
            d.mkdir(parents=True, exist_ok=True)
            (d / "selftest_closures.json").write_text('{"steps": {}}')
            return 0, "", ""
        if len(argv) > 3 and argv[3] == "absorb":
            n, m = self.added
            if n:
                Path(argv[argv.index("--out") + 1]).write_text('{"steps": {"x": {}}}')
            text = (f"selftest_scope absorb: {n} read(s) added to {m} step(s)\n"
                    + ("" if self.remain is None else
                       f"selftest_scope absorb: {self.remain} refusal(s) remain over the sources' own steps\n"))
            return 0, text, ""
        if len(argv) > 3 and argv[3] == "grows":
            return self.grows_rc, f"selftest_scope grows: {self.grows_rc} read(s) of the old table the new one drops\n", ""
        if argv[0] == "git":
            if "--name-only" in argv:
                return 0, self.paths, ""
            if "log" in argv:
                return 0, self.msg, ""
            if "show" in argv:
                return 0, self.head_table, ""
            if "rev-parse" in argv and "origin/main" in argv:
                return 0, self.tip + "\n", ""
            if "ls-remote" in argv:
                return 0, self.remote, ""
            if "rev-parse" in argv and argv[-1].endswith("^"):
                return 0, self.tip + "\n", ""
            if "rev-parse" in argv and argv[-1].endswith(TABLE):
                return 0, "blob1\n", ""
            if "hash-object" in argv:
                return 0, "blob1\n", ""
            if "rev-parse" in argv:
                return 0, "e" * 40 + "\n", ""
            if "get-url" in argv:
                return 0, "https://github.com/o/r.git\n", ""
            return 0, "", ""
        if argv[0] == "bash" and argv[1].endswith("app_push.sh"):
            return self.push_rc, "", "app_push: refused\n" if self.push_rc else ""
        return 0, "", ""

    def ran(self, word: str) -> int:
        return sum(word in " ".join(c) for c in self.calls)


def cases(mod) -> dict[str, bool]:
    res = {}
    tmp = Path(tempfile.mkdtemp())

    def go(f, runs=(), max_runs=12, at=None, push=False):
        return mod.beat(mod.Pass("o/r", tmp / "repo", tmp / "work", f), list(runs), max_runs, at, push)

    defect = {DEFECT[0]: ("failure", False), GREEN[0]: ("success", False)}
    f = Fake(defect, [DEFECT, GREEN], tip=DEFECT[1])
    rc, out = go(f)
    absorb_argv = next((c for c in f.calls if len(c) > 3 and c[3] == "absorb"), [])
    res["defect (run 44922703115 at a8efe1d1c2): OWED 738 read(s), 7 step(s), rc 1, from that run alone"] = (
        rc == 1 and out[0].startswith(f"SELFTEST-ABSORB OWED 738 read(s), 7 step(s) at {DEFECT[1][:12]} from run(s) "
                                      f"{DEFECT[0]};") and len(out) == 1
        and f.ran(f"download {DEFECT[0]}") == 1 and f.ran(f"download {GREEN[0]}") == 0
        and absorb_argv.count("--from") == 1 and absorb_argv[2] == SCOPE)
    f = Fake(defect, [DEFECT, GREEN], tip=NEWER)
    go(f)
    res["the runs are absorbed by origin/main's tip, never the runs' head"] = (
        ["checkout", "-q", "--detach", NEWER] in [c[1:] for c in f.calls if c[0] == "git"]
        and not any(DEFECT[1] in " ".join(c) for c in f.calls if c[0] == "git"))
    f = Fake(defect, [DEFECT, GREEN], added=(0, 0), tip=FIXED)
    rc, out = go(f)
    res["fixed (the same run at 25238b470a): absorb adds nothing, a repair merged since: CLEAN, rc 0, no push"] = (
        rc == 0 and out[0].startswith(f"SELFTEST-ABSORB CLEAN at {FIXED[:12]}") and f.ran("app_push.sh") == 0)
    f = Fake({GREEN[0]: ("success", False), DEFECT[0]: ("failure", False)}, [GREEN, DEFECT])
    rc, out = go(f, push=True)
    res["null (green run 44379511133): CLEAN, rc 0; no download, clone, absorb or push"] = (
        rc == 0 and out == [f"SELFTEST-ABSORB CLEAN at {GREEN[1][:12]} (run {GREEN[0]}): nothing to absorb"]
        and f.ran("download") + f.ran(" clone ") + f.ran(" absorb ") + f.ran("app_push") == 0)
    f = Fake({GREEN[0]: ("success", True), DEFECT[0]: ("success", False)}, [GREEN, DEFECT])
    rc, out = go(f)
    res["a green drift step with a selftest-absorbed artifact (rung 1's ABSORB OWED note) is owed, not clean"] = (
        rc == 1 and f.ran(f"download {GREEN[0]}") == 1 and f.ran(f"download {DEFECT[0]}") == 0)
    order = [("1", "1" * 40), ("2", "2" * 40), ("3", "3" * 40), ("4", "4" * 40), ("5", "5" * 40)]
    f = Fake({"1": ("failure", False), "2": ("cancelled", False), "3": ("success", True), "4": ("success", False),
              "5": ("failure", False)}, order)
    rc, out = go(f)
    res["the window: every red or owed run back to the last clean one; a cancelled run is no measurement"] = (
        rc == 1 and [c[3] for c in f.calls if c[:3] == ["gh", "run", "download"]] == ["1", "3"]
        and f.ran("runs/5/") == 0)
    f = Fake({"1": ("failure", False), "2": ("failure", False), "3": ("failure", False)}, order[:3])
    go(f, max_runs=2)
    res["the window stops at --max-runs"] = [c[3] for c in f.calls if c[:3] == ["gh", "run", "download"]] == ["1", "2"]
    f = Fake(defect, [DEFECT, GREEN], added=(0, 0), remain=3)
    rc, out = go(f)
    res["absorb adds nothing and refusals remain: RECORD-OWED, rc 4"] = (
        rc == 4 and out[0].startswith("SELFTEST-ABSORB RECORD-OWED ") and "(3 refusal(s) remain)" in out[0])
    f = Fake(defect, [DEFECT, GREEN], added=(0, 0), remain=0, tip=DEFECT[1])
    rc, out = go(f)
    res["absorb adds nothing at the red run's own head (UNMEASURED, EXTRA, a gap): RECORD-OWED, rc 4"] = (
        rc == 4 and "(0 refusal(s) remain)" in out[0])
    f = Fake(defect, [DEFECT, GREEN], added=(0, 0), remain=None, tip=FIXED)
    rc, out = go(f)
    res["an absorb that prints no remain line (a tip before it) is UNREADABLE, never clean"] = (
        rc == 2 and "printed no remain line" in out[0])
    f = Fake(defect, [DEFECT, GREEN], gh_rc=1)
    rc, out = go(f)
    res["an unreadable API is UNREADABLE, rc 2"] = rc == 2 and out[0].startswith("SELFTEST-ABSORB UNREADABLE gh api ")
    f = Fake(defect, [DEFECT, GREEN])
    orig = f.__call__

    def nodl(argv, cwd=None):
        return (1, "", "no artifact") if argv[:3] == ["gh", "run", "download"] else orig(argv, cwd)
    rc, out = go(nodl)
    res["a red run with no artifact is UNREADABLE, and nothing is absorbed"] = (
        rc == 2 and f"no {MEASURED} artifact in run(s) {DEFECT[0]}" in out[0] and f.ran(" absorb ") == 0)
    f = Fake(defect, [DEFECT, GREEN])
    rc, out = go(f, runs=[DEFECT[0]], at=FIXED)
    res["--run and --at: those runs, that commit; main's run list is not read"] = (
        rc == 1 and f.ran("ci.yml/runs") == 0 and ["checkout", "-q", "--detach", FIXED] in [c[1:] for c in f.calls])
    f = Fake(defect, [DEFECT, GREEN], remote="")
    rc, out = go(f, push=True)
    ap = next((c for c in f.calls if c[0] == "bash"), [])
    commit = next((c for c in f.calls if "commit" in c), [])
    res["--push: committed on the tip and force-pushed as the standing ref through app_push.sh --branch-only"] = (
        rc == 1 and out[1] == f"SELFTEST-ABSORB pushed {'e' * 12} {STANDING}"
        and ap[1:] == [str(tmp / "work" / "clone" / "tools/pr/app_push.sh"), "--branch-only", "o/r",
                       str(tmp / "work" / "clone"), STANDING]
        and ["checkout", "-q", "-B", STANDING, NEWER] in [c[3:] for c in f.calls if c[0] == "git"]
        and f"--at {NEWER} --run {DEFECT[0]}" in commit[-1])
    f = Fake(defect, [DEFECT, GREEN], remote=f"{'f' * 40}\trefs/heads/{STANDING}\n")
    rc, out = go(f, push=True)
    res["--push: a standing ref holding this table on this tip is unchanged, and nothing is pushed"] = (
        rc == 1 and out[1] == f"SELFTEST-ABSORB unchanged {'f' * 12} {STANDING}" and f.ran("app_push") == 0)
    f = Fake(defect, [DEFECT, GREEN], remote=f"{'f' * 40}\trefs/heads/{STANDING}\n", tip=FIXED)
    orig2 = f.__call__

    def moved(argv, cwd=None):
        if argv[0] == "git" and "rev-parse" in argv and argv[-1].endswith("^"):
            return 0, NEWER + "\n", ""
        return orig2(argv, cwd)
    rc, out = go(moved, push=True)
    res["--push: a standing ref on an older tip is re-cut and pushed (null control of the one above)"] = (
        rc == 1 and out[1].startswith("SELFTEST-ABSORB pushed ") and f.ran("app_push") == 1)
    f = Fake(defect, [DEFECT, GREEN], push_rc=1)
    rc, out = go(f, push=True)
    res["--push: a refused push is PUSH-REFUSED with its reason, still rc 1"] = (
        rc == 1 and out[1] == f"SELFTEST-ABSORB PUSH-REFUSED app_push rc=1: app_push: refused {STANDING}")
    # verify: the standing pull request's mechanical review (fix-review.md)
    head = "9" * 40
    msg = f"selftest-absorb: x\n\nRegenerate: python3 -I tools/audit/seat/selftest_absorb.py beat --repo-dir . --at {NEWER} --run {DEFECT[0]}\n"

    def ver(**kw):
        f = Fake(defect, [DEFECT, GREEN], **{"msg": msg, **kw})
        return (*mod.verify(mod.Pass("o/r", tmp / "repo", tmp / "work", f), head), f)
    rc, out, f = ver()
    grows = next((c for c in f.calls if len(c) > 3 and c[3] == "grows"), [])
    res["verify: the head regenerated byte-identical at its parent over its runs, dropping nothing: VERIFIED, rc 0"] = (
        rc == 0 and out[0].startswith(f"SELFTEST-ABSORB VERIFIED {head[:12]}: regenerated byte-identical at {NEWER[:12]} "
                                      f"over run(s) {DEFECT[0]}")
        and ["checkout", "-q", "--detach", NEWER] in [c[1:] for c in f.calls] and f.ran("ci.yml/runs") == 0
        and grows[4:] == ["--old", TABLE, "--new", str(tmp / "work" / "selftest_closures.json")])
    rc, out, _ = ver(head_table='{"steps": {"x": {}, "y": {}}}')
    res["verify: a head table that differs from the regeneration is refused"] = (
        rc == 1 and "differs from the regeneration" in out[0])
    rc, out, _ = ver(paths=f"{TABLE}\ntools/x.py\n")
    res["verify: a head that changes any other path is refused"] = rc == 1 and "not tools/ci/selftest_closures.json alone" in out[0]
    rc, out, _ = ver(msg=msg.replace(NEWER, FIXED))
    res["verify: a message whose --at is not the head's parent is refused"] = rc == 1 and "names no --at equal" in out[0]
    rc, out, _ = ver(grows_rc=1)
    res["verify: a head table that drops a read of its parent's is refused"] = rc == 1 and "drops reads" in out[0]
    # The literals this file reads, pinned where they are written.
    root = Path(__file__).resolve().parents[3]
    scope, wf = (root / SCOPE).read_text(), (root / ".github/workflows/governance.yml").read_text()
    res["the absorb summary and remain lines this file parses are the ones selftest_scope.py prints"] = (
        '"selftest_scope absorb: {len(added)} read(s) added to "' in scope.replace("f\"", "\"")
        and "refusal(s) remain over the sources' own steps" in scope and ADDED.pattern.endswith("step\\(s\\)$")
        and 'if argv[:1] == ["grows"] and "--old" in argv and "--new" in argv:' in scope)
    res["the drift step's name, the job and both artifact names are governance.yml's"] = (
        f"- name: {DRIFT}\n        id: drift\n" in wf and f"name: {MEASURED}\n" in wf and f"name: {ABSORBED}\n" in wf
        and f"\n  {JOB.split(' / ')[1]}:\n" in wf)
    res["app_push.sh force-pushes the standing ref this file names"] = (
        f"STANDING_ABSORB={STANDING}\n" in (root / "tools/pr/app_push.sh").read_text())
    shutil.rmtree(tmp, ignore_errors=True)
    return res


#: (old, new, the case that must fail). Each old string appears once in this file above the self-test.
MUTANTS = {
    "failure_not_red": ('    if step.get("conclusion") == "failure":\n        return "red"',
                        '    if step.get("conclusion") == "failurex":\n        return "red"',
                        "defect (run 44922703115 at a8efe1d1c2): OWED 738 read(s), 7 step(s), rc 1, from that run alone"),
    "absorbed_ignored": ('return "owed" if p.gh(', 'return "clean" if p.gh(',
                         "a green drift step with a selftest-absorbed artifact (rung 1's ABSORB OWED note) is owed, not clean"),
    "window_past_clean": ('        if st == "clean" or len(take) >= max_runs:', '        if len(take) >= max_runs:',
                          "the window: every red or owed run back to the last clean one; a cancelled run is no measurement"),
    "window_uncapped": ('        if st == "clean" or len(take) >= max_runs:', '        if st == "clean":',
                        "the window stops at --max-runs"),
    "absorb_at_run_head": ('(["checkout", "-q", "--detach", tip], clone)', '(["checkout", "-q", "--detach", take[0][1] or tip], clone)',
                           "the runs are absorbed by origin/main's tip, never the runs' head"),
    "remain_ignored": ("    if remain or (newest[2]", "    if (newest[2]", "absorb adds nothing and refusals remain: RECORD-OWED, rc 4"),
    "red_at_tip_ignored": ('    if remain or (newest[2] == "red" and newest[1] == tip):', '    if remain:',
                           "absorb adds nothing at the red run's own head (UNMEASURED, EXTRA, a gap): RECORD-OWED, rc 4"),
    "no_remain_is_clean": ("    if remain is None:\n        return 2", "    if False:\n        return 2",
                           "an absorb that prints no remain line (a tip before it) is UNREADABLE, never clean"),
    "unchanged_any_tip": ("        if parent == tip and blob", "        if blob",
                          "--push: a standing ref on an older tip is re-cut and pushed (null control of the one above)"),
    "unchanged_never": ("        if parent == tip and blob and", "        if False and",
                        "--push: a standing ref holding this table on this tip is unchanged, and nothing is pushed"),
    "push_refusal_silent": ('        return f"PUSH-REFUSED app_push rc={rc}: {last(err)}"', '        pass',
                            "--push: a refused push is PUSH-REFUSED with its reason, still rc 1"),
    "verify_no_cmp": ("    if table.read_text() != want:", "    if False:",
                      "verify: a head table that differs from the regeneration is refused"),
    "verify_any_paths": ("    if paths.split() != [TABLE]:", "    if False:", "verify: a head that changes any other path is refused"),
    "verify_any_at": ("    if not at or at[1] != parent or not runs:", "    if not runs:",
                      "verify: a message whose --at is not the head's parent is refused"),
    "verify_no_grows": ('    rc, out, err = p.run([sys.executable, "-I", SCOPE, "grows"', '    rc, out, err = 0, "", ""; (lambda *a: 0)([sys.executable, "-I", SCOPE, "grows"',
                        "verify: a head table that drops a read of its parent's is refused"),
    "clean_absorbs": ('    if newest[2] == "clean":\n', '    if newest[2] == "never":\n',
                      "null (green run 44379511133): CLEAN, rc 0; no download, clone, absorb or push"),
}


def stop_survivor(src: str, install: bool) -> bool | None:
    """Drive `src`'s `sh` over a tool that records its pid and sleeps, TERM the
    driver once the tool runs, and say whether the tool outlived it (None: the
    driver never started the tool). `install` calls stop_on_signal first, as
    `main` does; without it a TERM ends the driver at the default action."""
    import os
    import time
    d = Path(tempfile.mkdtemp())
    (d / "absorb_stop.py").write_text(src)
    pidf = d / "tool.pid"
    drv = ("import sys; sys.path.insert(0, sys.argv[1]); import absorb_stop as m; "
           + ("m.stop_on_signal(); " if install else "")
           + "m.sh(['bash', '-c', 'echo $$ > ' + sys.argv[2] + '; exec sleep 30'])")
    p = subprocess.Popen([sys.executable, "-I", "-c", drv, str(d), str(pidf)])
    pid = None
    try:
        for _ in range(100):
            if pidf.is_file() and pidf.read_text().strip():
                pid = int(pidf.read_text())
                break
            time.sleep(0.05)
        if pid is None:
            return None
        p.terminate()
        p.wait(TOOL_STOP_SECONDS + 5)
        time.sleep(0.2)
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        os.kill(pid, signal.SIGKILL)
        return True
    finally:
        if p.poll() is None:
            p.kill()
        shutil.rmtree(d, ignore_errors=True)


#: (old, new) narrowing `sh`'s reap to the timeout: a stop must then leave the tool running.
STOP_MUTANT = ("    except BaseException as e:  # a stop", "    except subprocess.TimeoutExpired as e:  # a stop")


def self_test() -> int:
    import importlib.util
    path = Path(__file__).resolve()
    src = path.read_text()
    body = src[:src.index("# ---------------------------------------------------------------- self-test")]

    def load(text: str, name: str):
        d = Path(tempfile.mkdtemp())
        (d / f"{name}.py").write_text(text)
        spec = importlib.util.spec_from_file_location(name, d / f"{name}.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        shutil.rmtree(d, ignore_errors=True)
        return mod
    res = cases(sys.modules[__name__])
    failed = 0
    for name, ok in res.items():
        print(f"  {'ok  ' if ok else 'FAIL'} {name}")
        failed += not ok
    total = len(res)
    for i, (mname, (old, new, case)) in enumerate(MUTANTS.items()):
        total += 1
        if body.count(old) != 1 or case not in res:
            print(f"  FAIL mutant {mname}: its site appears {body.count(old)} times, or its case is unnamed")
            failed += 1
            continue
        try:
            killed = cases(load(src.replace(old, new, 1), f"selftest_absorb_m{i}")).get(case) is False
        except Exception as e:  # a crash is no kill
            print(f"    mutant {mname} crashed: {e.__class__.__name__}: {e}")
            killed = False
        print(f"  {'ok  ' if killed else 'FAIL'} mutant {mname} killed by: {case}")
        failed += not killed
    stops = {"a TERM to the pass TERMs the tool `sh` runs, and none of it survives": stop_survivor(src, True) is False,
             "  null control: without stop_on_signal the TERM ends the pass and its tool survives":
                 stop_survivor(src, False) is True,
             "  mutant stop_orphans_tool (sh reaps on the timeout only): the stopped pass leaves its tool running":
                 body.count(STOP_MUTANT[0]) == 1 and stop_survivor(src.replace(*STOP_MUTANT, 1), True) is True}
    for name, ok in stops.items():
        print(f"  {'ok  ' if ok else 'FAIL'} {name}")
        failed += not ok
    total += len(stops)
    print(f"selftest_absorb self-test: {total} checks, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
