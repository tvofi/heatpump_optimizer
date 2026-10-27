#!/usr/bin/env python3
"""Reviewer-built null control for the unreadable-object finding: the same
fixture with the blob INTACT, so the number must not be UNAVAILABLE."""
import json, subprocess, sys, tempfile
from pathlib import Path
WT = Path("/private/tmp/rev-2883-r2/wt")
sys.path.insert(0, str(WT/"tools"/"audit")); sys.path.insert(0, str(WT/"tools"/"audit"/"seat")); sys.path.insert(0, str(WT/"tests"))
import merge_throughput as mt, review_strength as rs, roster_lib
from throwaway_git import throwaway_git_env, throwaway_git_init
env = throwaway_git_env()
with tempfile.TemporaryDirectory() as d:
    R=Path(d); throwaway_git_init(R,"-q","-b","main")
    def g(*a,e=None):
        return subprocess.run(["git","-C",d,*a],capture_output=True,text=True,check=True,env={**env,**(e or {})}).stdout.strip()
    ix={"GIT_INDEX_FILE":str(R/".git"/"fixture-index")}
    def mk(parents,files,msg,t):
        g("read-tree", *([parents.split()[0]] if parents else ["--empty"]), e=ix)
        for p,txt in files.items():
            (R/"blob").write_text(txt); b=g("hash-object","-w",str(R/"blob"),e=ix)
            g("update-index","--add","--cacheinfo",f"100644,{b},{p}",e=ix)
        return g("commit-tree",g("write-tree",e=ix),*[x for p in parents.split() for x in ("-p",p)],"-m",msg,e={**ix,"GIT_COMMITTER_DATE":t,"GIT_AUTHOR_DATE":t})
    ROSTER=roster_lib.ROSTERS_DIR+"/wave-r1-groups.json"; CRIT=roster_lib.CRITICAL_PATH_NAME
    ros=lambda a="fixing": json.dumps({"groups":[{"group":"R1-A","lane":"IN","size":"M","resume":{"stage":a}}]})
    r0=mk("",{ROSTER:ros(),CRIT:json.dumps({"at":"2026-10-01T00:00:00Z","critical":["R1-A"]})},"root","2026-10-01T00:00:00Z")
    r1=mk(r0,{ROSTER:ros("done")},"roster: A done","2026-10-01T01:30:00Z")
    g("update-ref","refs/remotes/origin/roster",r1); m0=mk("",{"x":"0\n"},"root","2026-10-01T00:00:00Z"); g("update-ref","refs/remotes/origin/main",m0)
    roster=json.loads(ros("done"))
    ctx=mt.FlowCtx(repo=R,tree="refs/remotes/origin/main",remote="origin",roster=roster,roster_unavailable="",
                   roster_ref="refs/remotes/origin/roster",roster_path=ROSTER,prefix="",record_prefix="record/",critical=None)
    print("RESULT control_closed_intact_blob =", mt.period(ctx, rs.when("2026-10-01T01:00:00Z"), rs.when("2026-10-01T02:00:00Z"))["closed"])
    print("RESULT control_critical_intact =", roster_lib.critical_path_read(str(R),"refs/remotes/origin/roster"))
