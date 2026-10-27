#!/usr/bin/env python3
"""Reviewer-built class check: enumerate a source the board reads and make it
UNREADABLE in the way the fix's own docstring names ("git's own failure"), by
deleting the blob object while the commit and its tree stay intact. A source
that cannot be read must print UNAVAILABLE, never a zero."""
import json, subprocess, sys, tempfile, importlib.util
from dataclasses import replace
from datetime import timedelta
from pathlib import Path

WT = Path("/private/tmp/rev-2883-r2/wt")
sys.path.insert(0, str(WT / "tools" / "audit"))
sys.path.insert(0, str(WT / "tools" / "audit" / "seat"))
sys.path.insert(0, str(WT / "tests"))
import merge_throughput as mt, review_strength as rs, roster_lib
from throwaway_git import throwaway_git_env, throwaway_git_init

env = throwaway_git_env()
with tempfile.TemporaryDirectory() as d:
    R = Path(d); throwaway_git_init(R, "-q", "-b", "main")
    def g(*a, e=None):
        return subprocess.run(["git","-C",d,*a], capture_output=True, text=True,
                              check=True, env={**env, **(e or {})}).stdout.strip()
    ix = {"GIT_INDEX_FILE": str(R/".git"/"fixture-index")}
    def mk(parents, files, msg, t):
        g("read-tree", *([parents.split()[0]] if parents else ["--empty"]), e=ix)
        for path, text in files.items():
            (R/"blob").write_text(text)
            blob = g("hash-object","-w",str(R/"blob"), e=ix)
            g("update-index","--add","--cacheinfo",f"100644,{blob},{path}", e=ix)
        return g("commit-tree", g("write-tree", e=ix),
                 *[x for p in parents.split() for x in ("-p",p)],
                 "-m", msg, e={**ix,"GIT_COMMITTER_DATE":t,"GIT_AUTHOR_DATE":t})
    ROSTER = roster_lib.ROSTERS_DIR + "/wave-r1-groups.json"
    CRIT = roster_lib.CRITICAL_PATH_NAME
    def ros(a="fixing"):
        return json.dumps({"groups":[{"group":"R1-A","lane":"IN","size":"M",
                                      "resume":{"stage":a}}]})
    T = lambda h,m=0: f"2026-10-01T{h:02d}:{m:02d}:00Z"
    r0 = mk("", {ROSTER: ros(), CRIT: json.dumps({"at":T(0),"critical":["R1-A"]})}, "root", T(0))
    r1 = mk(r0, {ROSTER: ros("done")}, "roster: A done", T(1,30))
    g("update-ref","refs/remotes/origin/roster", r1)
    m0 = mk("", {"x":"0\n"}, "root main", T(0)); g("update-ref","refs/remotes/origin/main", m0)

    # Corrupt the BLOB at r1 only: delete its loose object. The commit and tree stay.
    blob = g("rev-parse", f"{r1}:{ROSTER}")
    obj = R/".git"/"objects"/blob[:2]/blob[2:]
    existed_loose = obj.exists()
    if existed_loose:
        obj.unlink()
    chk = subprocess.run(["git","-C",d,"cat-file","-e",f"{r1}:{ROSTER}"],
                         capture_output=True, text=True, env=env)
    show = subprocess.run(["git","-C",d,"show",f"{r1}:{ROSTER}"],
                          capture_output=True, text=True, env=env)
    print("RESULT corrupt_blob_was_loose =", existed_loose)
    print("RESULT cat_file_e_rc =", chk.returncode, "| show_rc =", show.returncode)

    roster = json.loads(ros("done"))
    ctx = mt.FlowCtx(repo=R, tree="refs/remotes/origin/main", remote="origin",
                     roster=roster, roster_unavailable="",
                     roster_ref="refs/remotes/origin/roster", roster_path=ROSTER,
                     prefix="", record_prefix="record/", critical=None)
    p = mt.period(ctx, rs.when(T(1)), rs.when(T(2)))
    print("RESULT closed_for_unreadable_object =", p["closed"])

    # control: the same window with the blob intact, via a fresh copy of the commit
    print("RESULT is_zero_without_reason =", p["closed"] == (0, ""))
