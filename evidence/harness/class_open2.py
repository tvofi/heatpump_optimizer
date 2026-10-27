#!/usr/bin/env python3
"""Reviewer-built: the second site of the same predicate, plus the cheapest
discriminator (rev-parse vs cat-file) measured on the same fixture."""
import json, subprocess, sys, tempfile
from pathlib import Path
WT = Path("/private/tmp/rev-2883-r2/wt")
sys.path.insert(0, str(WT/"tools"/"audit")); sys.path.insert(0, str(WT/"tools"/"audit"/"seat")); sys.path.insert(0, str(WT/"tests"))
import merge_throughput as mt, roster_lib
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
    ros=json.dumps({"groups":[{"group":"R1-A","lane":"IN","size":"M","resume":{"stage":"fixing"}}]})
    crit=json.dumps({"at":"2026-10-01T00:00:00Z","critical":["R1-A"]})
    r0=mk("",{ROSTER:ros,CRIT:crit},"root","2026-10-01T00:00:00Z"); g("update-ref","refs/remotes/origin/roster",r0)
    # delete the CRITICAL blob's loose object only; roster blob stays readable
    cb=g("rev-parse",f"{r0}:{CRIT}"); (R/".git"/"objects"/cb[:2]/cb[2:]).unlink()
    print("RESULT crit_cat_file_e_rc =", subprocess.run(["git","-C",d,"cat-file","-e",f"{r0}:{CRIT}"],capture_output=True,text=True,env=env).returncode)
    print("RESULT crit_rev_parse_rc =", subprocess.run(["git","-C",d,"rev-parse","--verify","--quiet",f"{r0}:{CRIT}"],capture_output=True,text=True,env=env).returncode)
    print("RESULT absent_path_rev_parse_rc =", subprocess.run(["git","-C",d,"rev-parse","--verify","--quiet",f"{r0}:no/such/path"],capture_output=True,text=True,env=env).returncode)
    grp, why = roster_lib.critical_path_read(str(R), "refs/remotes/origin/roster")
    print("RESULT critical_path_read_on_unreadable_blob =", (grp, why))
    roster=json.loads(ros)
    wip=mt.flow_wip(roster, grp); print("RESULT wip_lanes =", wip)
    print("RESULT is_silent_empty_measurement =", grp==set() and why=="")
