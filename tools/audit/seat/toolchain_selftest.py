#!/usr/bin/env python3
"""toolchain.py's cases, run by that file's own self-test flag.

Real git throughout: a bare origin whose main is six commits (c0..c5; c1, c3
and c5 touch a seat path), a side commit off main, and one clone as the tools
checkout. Only GitHub is a fake: a run listing and one job listing per run.
Each refusal has its null control beside it, the case where the same call
moves the ref. dev/audit/harnesses/r11_toolchain_mutants.py drops each rule
in turn against this file.
"""
from __future__ import annotations

import contextlib
import io
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "tests"))
from throwaway_git import throwaway_git_clone, throwaway_git_init  # noqa: E402
import toolchain as tc  # noqa: E402

REPO = "o/r"
T0 = 1794700800.0  # 2026-11-15T00:00:00Z
LINE = re.compile(r"PROMOTE 2026-11-15T00:00:00Z (absent|[0-9a-f]{12}) -> [0-9a-f]{12} run=\d+")


class World:
    """One origin, one checkout, and GitHub's answers about main's push runs."""

    def __init__(self, tmp: str):
        self.origin, self.work, src = f"{tmp}/origin.git", f"{tmp}/work", f"{tmp}/src"
        self.env = throwaway_git_init(src, "-q", "-b", "main")
        self.c = []
        for i in range(6):
            path = Path(src, "tools/audit/seat/x.sh" if i % 2 else "docs/x.md")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"{i}\n")
            self.sh(src, "add", "-A")
            self.sh(src, "commit", "-q", "-m", f"c{i}")
            self.c.append(self.sh(src, "rev-parse", "HEAD"))
        self.sh(src, "checkout", "-q", "-b", "side", self.c[2])
        Path(src, "side.txt").write_text("s\n")
        self.sh(src, "add", "-A")
        self.sh(src, "commit", "-q", "-m", "side")
        self.side = self.sh(src, "rev-parse", "HEAD")
        throwaway_git_clone(src, self.origin, "-q", "--bare")
        throwaway_git_clone(self.origin, self.work, "-q")
        self.sh(self.work, "checkout", "-q", "--detach", self.c[0])
        self.runs: list[dict] = []
        self.jobs: dict[int, list | None] = {}
        self.calls: list[str] = []
        self.lax = False  # a listing that ignores head_sha, so the caller's own filter is what holds
        self.git = tc.git_in(self.work)

    def sh(self, d: str, *args: str) -> str:
        p = subprocess.run(["git", "-C", d, *args], capture_output=True, text=True, env=self.env)
        assert p.returncode == 0, (args, p.stderr)
        return p.stdout.strip()

    def ref(self) -> str:
        return self.sh(self.origin, "for-each-ref", "--format=%(objectname)", f"refs/heads/{tc.REF}")

    def set_ref(self, sha: str) -> None:
        if sha:
            self.sh(self.origin, "update-ref", f"refs/heads/{tc.REF}", sha)
            self.sh(self.work, "fetch", "-q", "origin", f"+refs/heads/{tc.REF}:{tc.TRACKING}")
        elif self.ref():
            self.sh(self.origin, "update-ref", "-d", f"refs/heads/{tc.REF}")
            self.sh(self.work, "update-ref", "-d", tc.TRACKING)

    def run(self, sha: str, machinery: str = "success", product: str = "success", status: str = "completed", **over):
        """A main push run at <sha>; `machinery` and `product` conclude every job of that kind."""
        rid = 100 + len(self.runs)
        g = tc.gate_py()
        jobs = [{"name": n, "status": "completed", "conclusion": machinery if n in g.MACHINERY_JOBS else product}
                for n in (*g.REQUIRED["push"], "governance / instrument-self-tests")]
        for j in jobs:
            if j["name"] in over:
                j["status"], j["conclusion"] = over[j["name"]]
        self.runs.append({"id": rid, "head_sha": sha, "status": status})
        self.jobs[rid] = jobs
        return rid

    def api(self, argv: list[str]) -> tuple[int, str]:
        path = argv[2]
        self.calls.append(path)
        if "/jobs" in path:
            jobs = self.jobs.get(int(path.split("/runs/")[1].split("/")[0]))
            if jobs is None:
                return 1, "gh: HTTP 502"
            return 0, "".join(json.dumps(j) + "\n" for j in jobs) if "page=1" in path else ""
        if self.runs is None:
            return 1, "gh: HTTP 502"
        sha = re.search(r"head_sha=([0-9a-f]+)", path)
        return 0, json.dumps([r for r in self.runs if not sha or self.lax or r["head_sha"] == sha[1]])

    def promote(self, sha: str = "", create: bool = False, git=None) -> tuple:
        """(exit code or the exception class's name, what it printed, the ref afterwards)."""
        lines: list[str] = []
        self.calls.clear()
        try:
            rc = tc.promote(git or self.git, self.api, REPO, sha, create, now=lambda: T0, out=lines.append)
        except (tc.Refused, tc.Unreadable) as e:
            rc, lines = type(e).__name__, [str(e)]
        return rc, lines, self.ref()

    def jobs_read(self) -> int:
        return sum("/jobs" in c for c in self.calls)


def run() -> int:
    n = fails = 0

    def check(name: str, got, want=True) -> None:
        nonlocal n, fails
        n += 1
        if got != want:
            fails += 1
            print(f"FAIL {name}: got {got!r}, want {want!r}")

    def refused(fn, needle: str, exc=tc.Refused) -> bool:
        try:
            fn()
        except (tc.Refused, tc.Unreadable) as e:
            return type(e) is exc and needle in str(e)
        return False

    with tempfile.TemporaryDirectory() as tmp:
        w = World(tmp)
        c = w.c

        # ---- behind
        check("behind: an absent ref refuses with the init command, never a count against main",
              refused(lambda: tc.behind(w.git), tc.INIT))
        check("behind --fetch: a ref absent on origin refuses the same way",
              refused(lambda: tc.behind(w.git, fetch=True), tc.INIT))
        w.set_ref(c[4])
        check("behind counts the ref's commits touching the seat paths (c1, c3 of c1..c4)", tc.behind(w.git), 2)
        check("behind --all counts every commit of c1..c4", tc.behind(w.git, every=True), 4)
        check("behind --from counts from that commit, not HEAD", tc.behind(w.git, frm=c[3]), 0)
        check("null: --from a commit behind a seat-path change counts it", tc.behind(w.git, frm=c[2]), 1)
        w.sh(w.work, "checkout", "-q", "--detach", c[5])
        check("a checkout ahead of the ref is 0 behind: no caller is told to move backwards",
              (tc.behind(w.git), tc.behind(w.git, every=True)), (0, 0))
        w.sh(w.work, "checkout", "-q", "--detach", c[4])
        check("a checkout level with the ref is 0 behind", tc.behind(w.git), 0)
        w.sh(w.work, "checkout", "-q", "--detach", c[0])
        w.sh(w.origin, "update-ref", f"refs/heads/{tc.REF}", c[5])
        check("null: without --fetch a ref moved on origin is not seen", tc.behind(w.git), 2)
        check("behind --fetch reads the ref from origin first", tc.behind(w.git, fetch=True), 3)
        check("behind: a commit git cannot resolve is unreadable, never 0",
              refused(lambda: tc.behind(w.git, frm="0" * 40), "could not count", tc.Unreadable))
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            rcs = (tc.main(["behind", w.work]), tc.main(["behind", w.work, "--all", "--from", c[4]]))
            w.set_ref("")
            rcs += (tc.main(["behind", w.work]),)
        check("the verb prints the count and exits 0; an absent ref exits 1 and prints no count",
              (rcs, out.getvalue().split()), ((0, 0, 1), ["3", "1"]))

        # ---- promote: the absent ref and --init
        w.run(c[1])
        check("promote: an absent ref refuses with the init command and pushes nothing",
              (lambda r: (r[0], tc.INIT in r[1][0], r[2]))(w.promote()), ("Refused", True, ""))
        rc, lines, ref = w.promote(create=True)
        check("promote --init creates the ref at the newest machinery-green main commit and reads it back",
              (rc, ref, bool(LINE.fullmatch(lines[0])), lines[0].split()[2:]), (0, c[1], True, ["absent", "->", c[1][:12], "run=100"]))
        check("promote --init while the ref exists refuses and leaves it",
              (lambda r: (r[0], "only while" in r[1][0], r[2]))(w.promote(create=True)), ("Refused", True, c[1]))

        # ---- promote: the default walk
        rc, lines, ref = w.promote()
        check("promote with nothing newer prints PROMOTE-CURRENT, exits 0 and reads no job listing",
              (rc, lines, ref, w.jobs_read()), (0, [f"PROMOTE-CURRENT 2026-11-15T00:00:00Z {c[1][:12]}"], c[1], 0))
        w.run(c[2])
        rc, lines, ref = w.promote()
        check("null: a machinery-green main commit past the ref is a fast-forward and promotes",
              (rc, ref, lines[0].split()[2:]), (0, c[2], [c[1][:12], "->", c[2][:12], "run=101"]))
        w.run(c[3], machinery="failure")
        check("a main commit whose run reads MACHINERY red does not promote; one red is not held",
              w.promote(), (0, [f"PROMOTE-CURRENT 2026-11-15T00:00:00Z {c[2][:12]}"], c[2]))
        w.runs[-1]["head_sha"], red3 = c[2], w.runs[-1]
        w.run(c[3], product="failure")
        check("PRODUCT red with MACHINERY green promotes: the tools ref reads machinery alone",
              w.promote()[::2], (0, c[3]))
        red3["head_sha"] = c[3]
        w.set_ref(c[2])
        w.runs[-1]["status"] = "in_progress"
        check("null: the same run still in progress is not concluded and promotes nothing",
              w.promote()[::2], (0, c[2]))
        w.runs.pop()
        w.run(c[4], **{"tests / briefs": ("completed", "cancelled")})
        w.run(c[5], **{"governance / env-matrix": ("in_progress", None)})
        rc, lines, ref = w.promote()
        check("the newest three concluded runs past the ref red or unread: PROMOTE-HELD, exit 3, the ref unmoved",
              (rc, ref, lines), (3, c[2], [f"PROMOTE-HELD 2026-11-15T00:00:00Z {c[2][:12]}: the newest 3 concluded main runs "
                                           "past it read MACHINERY 104=unread, 103=unread, 102=red"]))
        w.jobs[104] = w.jobs[100]
        check("null: the same three with the newest green promote it and are not held", w.promote()[::2], (0, c[5]))
        w.set_ref(c[1])
        w.jobs[104] = w.jobs[102]
        w.runs.sort(key=lambda r: r["id"])
        rc, lines, ref = w.promote()
        check("a green run older than three bad ones still promotes, and the hold is still reported",
              (rc, ref, [ln.split()[0] for ln in lines], w.jobs_read()), (3, c[2], ["PROMOTE", "PROMOTE-HELD"], 4))
        rc, lines, ref = w.promote()
        check("the walk stops at the ref: three bad runs past it are held, the run at it is never read",
              (rc, ref, w.jobs_read()), (3, c[2], 3))
        w.runs[2:] = w.runs[2:3]
        check("null: one bad run past the ref is not three: PROMOTE-CURRENT, exit 0", w.promote()[0], 0)
        w.runs[2]["head_sha"], w.jobs[102] = w.side, w.jobs[100]
        check("a green run whose head descends from the ref and is not a commit of main refuses and leaves the ref",
              (lambda r: (r[0], "not a commit of origin/main" in r[1][0], r[2]))(w.promote()), ("Refused", True, c[2]))
        w.runs[2]["head_sha"] = c[3]
        w.run(c[4], machinery="failure")
        w.run(c[5], machinery="failure")
        check("null: two bad runs above a green third are not a hold: it promotes, exit 0", w.promote()[::2], (0, c[3]))

        # ---- promote <sha>
        w.runs.clear()
        w.set_ref(c[2])
        for i in (1, 3, 4):
            w.run(c[i], machinery="success" if i != 4 else "failure")
        w.run(w.side)
        for name, sha, needle in (("a commit not on main", w.side, "not a commit of origin/main"),
                                  ("a commit behind the ref (not a fast-forward)", c[1], "not a fast-forward"),
                                  ("a commit reading MACHINERY red", c[4], "MACHINERY red (run 102)"),
                                  ("a commit with no concluded push run (unread)", c[5], "MACHINERY unread (no concluded"),
                                  ("a word that is no sha", "main", "not a commit of origin/main")):
            check(f"promote <sha> refuses {name} and leaves the ref",
                  (lambda r: (r[0], needle in r[1][0], r[2]))(w.promote(sha)), ("Refused", True, c[2]))
        w.lax = True
        check("promote <sha> reads only a run at that commit, whatever the listing returns",
              (lambda r: (r[0], "MACHINERY unread (no concluded" in r[1][0], r[2]))(w.promote(c[5])), ("Refused", True, c[2]))
        w.lax = False
        check("promote <sha> at the ref's own commit prints PROMOTE-CURRENT",
              w.promote(c[2]), (0, [f"PROMOTE-CURRENT 2026-11-15T00:00:00Z {c[2][:12]}"], c[2]))
        rc, lines, ref = w.promote(c[3])
        check("null: promote <sha> of a green commit of main past the ref moves it",
              (rc, ref, lines[0].split()[2:]), (0, c[3], [c[2][:12], "->", c[3][:12], "run=101"]))
        w.sh(w.origin, "update-ref", f"refs/heads/{tc.REF}", w.side)
        w.run(c[5])
        check("a ref that left main is never moved: the walk's green commit is not a fast-forward of it",
              (lambda r: (r[0], "not a fast-forward" in r[1][0], r[2]))(w.promote()), ("Refused", True, w.side))

        # ---- the push's read-back, and the reads
        w.set_ref(c[3])

        def deaf(*args):                            # a push that reports success and moves nothing
            return (0, "") if args[0] == "push" else w.git(*args)
        check("a push that did not move the ref is refused by the read-back",
              (lambda r: (r[0], f"read back {c[3][:12]}" in r[1][0], r[2]))(w.promote(git=deaf)), ("Refused", True, c[3]))
        w.jobs[w.runs[-1]["id"]] = None
        check("a job listing that cannot be read is unreadable, never a verdict", w.promote()[::2], ("Unreadable", c[3]))
        w.runs = None
        check("a run listing that cannot be read is unreadable", w.promote()[::2], ("Unreadable", c[3]))
        w.runs = []
        check("null: an empty listing reads, and promotes nothing", w.promote()[::2], (0, c[3]))
        err = io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            tc.gh, real = (lambda argv: (1, "gh: HTTP 502")), tc.gh
            try:
                rc = tc.main(["promote", "--repo", REPO, "--dir", w.work])
            finally:
                tc.gh = real
        check("the verb exits 2 on a failed read and names it", (rc, err.getvalue().startswith("toolchain: UNREADABLE ")), (2, True))
        check("the ref's name sits under the family prune_refs.py keeps", tc.REF.startswith(tc.REF_PREFIX) and tc.REF != tc.REF_PREFIX)

    print(f"toolchain self-test: {n} checks, {fails} failed")
    return 1 if fails else 0
