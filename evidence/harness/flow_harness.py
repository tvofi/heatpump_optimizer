#!/usr/bin/env python3
"""Reviewer-built harness (mine, not the fixer's) over one throwaway repo.

Pins, with RESULT lines:
  * window boundaries: a merge exactly at the window start is counted, one
    exactly at the end is not; an empty period counts nothing;
  * a group closed once is counted once in a period (and a 1 h period after
    it does not re-count it);
  * first-pass yield: blocked-then-merge at the SAME head, and at a MOVED
    head -- how many judgements each contributes;
  * the unreadable-source-zero hunt: a roster ref whose critical-path.json
    cannot be read, and a roster commit whose JSON is malformed;
  * the finding's own perturbation + null control (the critical-path file).
"""
import json
import subprocess
import sys
import tempfile
from dataclasses import replace
from datetime import timedelta
from pathlib import Path

WT = Path("/private/tmp/rev-2883-r2/wt").expanduser()
sys.path.insert(0, str(WT / "tools" / "audit"))
sys.path.insert(0, str(WT / "tools" / "audit" / "seat"))
sys.path.insert(0, str(WT / "tests"))

import merge_throughput as mt          # noqa: E402
import review_strength as rs           # noqa: E402
import roster_lib                       # noqa: E402
from throwaway_git import throwaway_git_env, throwaway_git_init  # noqa: E402

fails = []


def check(name, got, want):
    ok = got == want
    if not ok:
        fails.append(name)
    print(f"RESULT {'ok  ' if ok else 'FAIL'} {name}: got={got!r} want={want!r}")


env = throwaway_git_env()
with tempfile.TemporaryDirectory() as d:
    R = Path(d)
    throwaway_git_init(R, "-q", "-b", "main")

    def g(*args, e=None):
        return subprocess.run(["git", "-C", d, *args], capture_output=True,
                              text=True, check=True,
                              env={**env, **(e or {})}).stdout.strip()

    ix = {"GIT_INDEX_FILE": str(R / ".git" / "fixture-index")}

    def mk(parents, files, msg, t):
        g("read-tree", *([parents.split()[0]] if parents else ["--empty"]), e=ix)
        for path, text in files.items():
            if text is None:            # deletion
                g("update-index", "--force-remove", path, e=ix)
                continue
            (R / "blob").write_text(text)
            blob = g("hash-object", "-w", str(R / "blob"), e=ix)
            g("update-index", "--add", "--cacheinfo", f"100644,{blob},{path}", e=ix)
        return g("commit-tree", g("write-tree", e=ix),
                 *[x for p in parents.split() for x in ("-p", p)],
                 "-m", msg, e={**ix, "GIT_COMMITTER_DATE": t,
                               "GIT_AUTHOR_DATE": t})

    ROSTER = roster_lib.ROSTERS_DIR + "/wave-r1-groups.json"
    CRIT = roster_lib.CRITICAL_PATH_NAME

    def ros(a="fixing", b="not-started", bad=False):
        if bad:
            return "{not json"
        return json.dumps({"groups": [
            {"group": "R1-A", "lane": "IN", "size": "M", "resume": {"stage": a}},
            {"group": "R1-B", "lane": "F", "size": "S", "resume": {"stage": b}},
            {"group": "R1-C", "lane": "tooling", "size": "L",
             "resume": {"stage": "fixing"}},
            {"group": "R1-D", "lane": "IN", "size": "M",
             "resume": {"stage": "fixing"}}]})

    T = lambda h, m=0: f"2026-10-01T{h:02d}:{m:02d}:00Z"
    crit = json.dumps({"at": T(0), "critical": ["R1-A"]})

    # roster history: root, A done at 01:30, B done at 02:30
    r0 = mk("", {ROSTER: ros(), CRIT: crit}, "root", T(0))
    r1 = mk(r0, {ROSTER: ros(a="done")}, "roster: A done", T(1, 30))
    r2 = mk(r1, {ROSTER: ros(a="done", b="done")}, "roster: B done", T(2, 30))
    # a ref whose tip carries the roster but NOT the critical-path file
    r2nc = mk(r1, {ROSTER: ros(a="done", b="done"), CRIT: None},
              "roster: B done, no critical file", T(2, 30))
    # a ref whose tip carries an INVALID critical-path.json (unreadable, not absent)
    r2bc = mk(r1, {ROSTER: ros(a="done", b="done"), CRIT: "{not json"}, 
              "roster: B done, broken critical file", T(2, 30))
    # a ref whose only in-window roster commit is malformed JSON
    rbad = mk(r0, {ROSTER: ros(bad=True)}, "roster: broken", T(1, 30))
    g("update-ref", "refs/remotes/origin/roster", r2)
    g("update-ref", "refs/remotes/origin/roster-nocrit", r2nc)
    g("update-ref", "refs/remotes/origin/roster-bad", rbad)
    g("update-ref", "refs/remotes/origin/roster-badcrit", r2bc)

    # main: group merge exactly at 01:00, fly-in exactly at 03:00,
    # record exactly at 04:00
    m0 = mk("", {"x": "0\n"}, "root main", T(0))
    b1 = mk(m0, {"f1": "1\n"}, "pr1 work", T(0, 30))
    m1 = mk(f"{m0} {b1}", {"f1": "1\n"}, "Merge pull request #1 from o/fix/r1-a", T(1, 0))
    fb = mk(m1, {"hot": "x\n"}, "flyin", T(2, 30))
    m2 = mk(f"{m1} {fb}", {"hot": "x\n"}, "Merge pull request #2 from o/hotfix/x", T(3, 0))
    rc = mk(m2, {"dev/programme/delivery/9.md": "row\n"}, "record", T(3, 30))
    m3 = mk(f"{m2} {rc}", {"dev/programme/delivery/9.md": "row\n"},
            "Merge pull request #3 from o/record/auto", T(4, 0))
    g("update-ref", "refs/remotes/origin/main", m3)

    roster = json.loads(ros(a="done", b="done"))
    crit_set = roster_lib.critical_path_groups(R, "refs/remotes/origin/roster")
    base = mt.FlowCtx(repo=R, tree="refs/remotes/origin/main", remote="origin",
                      roster=roster, roster_unavailable="",
                      roster_ref="refs/remotes/origin/roster",
                      roster_path=ROSTER, prefix="", record_prefix="record/",
                      critical=crit_set)

    empty = g("hash-object", "-t", "tree", "-w", "/dev/null")

    def verdict(pr, kind, head, t, cls=""):
        ref = f"refs/remotes/origin/review/{pr}"
        par = subprocess.run(["git", "-C", d, "rev-parse", "-q", "--verify", ref],
                             capture_output=True, text=True)
        subj = (f"verdict: #{pr} Fix review: {kind} {head}"
                + (f" {cls}:" if cls else ""))
        sha = g("commit-tree", empty,
                *(["-p", par.stdout.strip()] if par.returncode == 0 else []),
                "-m", subj, e={"GIT_COMMITTER_DATE": t, "GIT_AUTHOR_DATE": t})
        g("update-ref", ref, sha)

    # PR 1: blocked then merge at the SAME head (b1).
    verdict(1, "blocked", b1, T(1, 10), "harness")
    verdict(1, "merge", b1, T(1, 20))
    # PR 2: blocked at fb, merge at the MOVED head m2.
    verdict(2, "blocked", fb, T(2, 10), "regression")
    verdict(2, "merge", m2, T(2, 20))

    a0, a5 = rs.when(T(0)), rs.when(T(5))

    # ---- 1. classification / closures / lead ------------------------------
    p = mt.period(base, a0, a5)
    check("moves split group/record/roster/flyin",
          (p["moves"][0]["counts"]["group"], p["moves"][0]["counts"]["record"],
           p["moves"][0]["counts"]["roster"], p["moves"][0]["counts"]["flyin"]),
          (1, 1, 0, 1))
    check("groups closed once each (A and B)", p["closed"], (2, ""))
    check("fly-ins", p["flyins"], (1, ""))
    check("lead per size", p["lead"], (({"M": [0.5]}, 0), ""))

    # ---- 2. window boundaries ---------------------------------------------
    # group merge exactly at a=01:00 is IN; fly-in exactly at b=03:00 is OUT.
    p = mt.period(base, rs.when(T(1)), rs.when(T(3)))
    check("merge exactly at window start counted",
          p["moves"][0]["counts"]["group"], 1)
    check("merge exactly at window end excluded (fly-in)",
          p["moves"][0]["counts"]["flyin"], 0)
    # one second later it is in
    p = mt.period(base, rs.when(T(1)), rs.when(T(3)) + timedelta(seconds=1))
    check("the same fly-in counted one second past the end",
          p["moves"][0]["counts"]["flyin"], 1)
    # record merge exactly at a=04:00
    p = mt.period(base, rs.when(T(4)), rs.when(T(5)))
    check("record merge exactly at start counted", p["moves"][0]["counts"]["record"], 1)
    # an empty hour
    p = mt.period(base, rs.when(T(6)), rs.when(T(7)))
    check("empty hour: nothing counted, no UNAVAILABLE",
          (p["moves"][0]["counts"]["group"], p["closed"][0], p["yield"][0],
           p["yield"][1]), (0, 0, (0, 0), ""))

    # ---- 3. a closure is not re-counted in a later window -----------------
    p = mt.period(base, rs.when(T(2)), rs.when(T(5)))
    check("a later window does not re-count A (closed at 01:30)", p["closed"], (1, ""))
    p = mt.period(base, rs.when(T(2, 45)), rs.when(T(5)))
    check("a window after both closures counts 0 (not a re-count)", p["closed"], (0, ""))

    # ---- 4. first-pass yield, same head vs moved head ---------------------
    p = mt.period(base, a0, a5)
    check("same-head and moved-head PRs each contribute ONE judgement",
          p["yield"], ((0, 2), ""))
    # same-head PR alone: blocked then merge at b1
    p = mt.period(base, rs.when(T(1)), rs.when(T(1, 30)))
    check("same-head block then merge: first pass is the blocked one only",
          p["yield"], ((0, 1), ""))
    # moved-head PR alone: blocked at fb, merge at m2
    p = mt.period(base, rs.when(T(2)), rs.when(T(2, 30)))
    check("moved-head block then merge: the merge is not a second judgement",
          p["yield"], ((0, 1), ""))
    check("blocked-class mix over both", dict(p["classes"][0]), {"regression": 1})

    # ---- 5. THE ZERO HUNT: unreadable critical-path.json -----------------
    crit_ok = mt.critical_of(R, "refs/remotes/origin/roster", roster)
    crit_none = mt.critical_of(R, "refs/remotes/origin/roster-nocrit", roster)
    check("critical-path with the file present", crit_ok, {"r1-a"})
    check("critical-path with the file absent reads None (no failure signal)",
          crit_none, None)
    open_roster = json.loads(ros())   # A fixing, B not-started, C fixing, D fixing
    check("WIP lanes with the critical file present",
          mt.flow_wip(open_roster, crit_ok), {"A": 1, "B": 1, "C": 1, "F": 1})
    check("WIP lanes with the file UNREADABLE: A prints 0, not UNAVAILABLE",
          mt.flow_wip(open_roster, crit_none), {"A": 0, "B": 2, "C": 1, "F": 1})
    ctx_nc = replace(base, roster_ref="refs/remotes/origin/roster-nocrit",
                     critical=crit_none)
    text = mt.render_board(mt.board(ctx_nc, a5))
    check("the rendered board says nothing about the unreadable critical file",
          ("UNAVAILABLE" in text.split("### WIP")[1].split("## Rules")[0]
           if "### WIP" in text else None), False)

    crit_bad = mt.critical_of(R, "refs/remotes/origin/roster-badcrit", roster)
    check("critical-path INVALID JSON reads None, indistinguishable from absent",
          crit_bad, None)
    check("WIP lanes with INVALID critical JSON: A prints 0",
          mt.flow_wip(open_roster, crit_bad), {"A": 0, "B": 2, "C": 1, "F": 1})
    text = mt.render_board(mt.board(replace(base, roster_ref="refs/remotes/origin/roster-badcrit",
                                            critical=crit_bad), a5))
    wip = text.split("### WIP")[1].split("## Rules")[0]
    check("the board renders the invalid critical file as a numeric zero",
          ("UNAVAILABLE" in wip), False)

    # ---- 6. an unreadable roster at a commit is a silent zero ------------
    ctx_bad = replace(base, roster_ref="refs/remotes/origin/roster-bad",
                      roster_path=ROSTER)
    p = mt.period(ctx_bad, rs.when(T(1)), rs.when(T(2)))
    check("a malformed roster at the only in-window commit reads 0, not UNAVAILABLE",
          p["closed"], (0, ""))

    # ---- 6b. the default window ends exactly at the tree tip's own time --
    u = mt.flow_default_until(R, "refs/remotes/origin/main",
                              "refs/remotes/origin/roster")
    p = mt.period(base, u - timedelta(hours=24), u)
    check("default until is the tree tip time", u.isoformat(), rs.when(T(4)).isoformat())
    check("the tip merge at exactly until is EXCLUDED from the board", 
          p["moves"][0]["counts"]["record"], 0)
    p = mt.period(base, u - timedelta(hours=24), u + timedelta(seconds=1))
    check("the same tip merge is counted one second later",
          p["moves"][0]["counts"]["record"], 1)

    # ---- 7. the self-test's own UNAVAILABLE arms do move ----------------
    import merge_throughput as mt2
    src = (WT / "tools" / "audit" / "merge_throughput.py").read_text()
    print("RESULT self_test_reads_no_review_refs_arm=",
          "no review refs reads UNAVAILABLE" in src)

print("RESULT failures=", len(fails), fails)
sys.exit(1 if fails else 0)
