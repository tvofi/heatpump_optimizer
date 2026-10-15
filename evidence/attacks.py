import json, os, subprocess, sys, tempfile, pathlib
W = pathlib.Path(sys.argv[1]); sys.path.insert(0, str(W/"tools/audit/seat")); sys.path.insert(0, str(W/"tests"))
import roster_lib as rl
from throwaway_git import throwaway_git_environ, throwaway_git_init, throwaway_git_clone
def g(*a, cwd=None): return subprocess.run(["git",*a], cwd=cwd, capture_output=True, text=True, check=True).stdout
def tool(t, *a, cwd): r=subprocess.run([sys.executable, str(W/"tools/audit/seat"/t), *a], cwd=cwd, capture_output=True, text=True); return r.returncode, (r.stdout+r.stderr)
R9=f"{rl.ROSTERS_DIR}/wave-r9-groups.json"; R10=f"{rl.ROSTERS_DIR}/wave-r10-groups.json"; R11=f"{rl.ROSTERS_DIR}/wave-r11-groups.json"
def roster(gid): return json.dumps({"repo":"x/y","session":"s","groups":[{"group":gid,"lane":"L1","issues":[],"fixes":[],"after":[],"brief":"b.","resume":{"stage":"not-started"}}]}, indent=2)+"\n"
with throwaway_git_environ(), tempfile.TemporaryDirectory() as td:
    td=pathlib.Path(td); seed=td/"seed"; (seed/rl.ROSTERS_DIR).mkdir(parents=True)
    throwaway_git_init(seed,"-q","-b","main")
    lint=seed/".claude/workflows/brief_lint.mjs"; lint.parent.mkdir(parents=True); lint.write_text("console.log('TOTAL: 0 error(s) across 1 file(s)');\n")
    (seed/R9).write_text(roster("R9-A")); g("add","-A",cwd=seed); g("commit","-q","-m","r9",cwd=seed)
    origin=td/"origin.git"; throwaway_git_clone(seed, origin, "-q","--bare")
    drv=td/"drv"; throwaway_git_clone(origin, drv, "-q")
    # A: text sort trap with r9, r10, r11 and a decoy
    print("RESULT A newest of r9,r10,r11,r1 =", rl.newest_roster(["wave-r9-groups.json","wave-r10-groups.json","wave-r11-groups.json","wave-r1-groups.json","wave-r100-groups.json.bak"]))
    # B: r10 present on the checkout (untracked), absent at the ref
    (drv/R10).write_text(roster("R10-A"))
    print("RESULT B at ref origin/main ->", rl.roster_path(str(drv),"origin/main"), "| on disk ->", rl.roster_path(str(drv)))
    rc,o=tool("plan_table.py","--roster-ref","origin/main",cwd=drv); print("RESULT B plan_table at origin/main rc",rc,"R10-A in out:", "R10-A" in o, "R9-A in out:", "R9-A" in o)
    rc,o=tool("state_docs.py","--checkout",str(drv),"--pr-state",os.devnull if False else str(td/"p.json"),cwd=drv) if (td/"p.json").write_text("[]") or True else None
    print("RESULT B state_docs default ->", [l for l in o.splitlines() if "round state" in l or "REFUSED" in l][:2])
    # D: roster_edit with no ref/branch args never pushes to main
    main_before=g("rev-parse","refs/heads/main",cwd=origin).strip()
    rc,o=tool("roster_edit.py","wire-issue","R9-A","4242","--checkout",str(drv),"--worktree",str(td/"wtD"),"--lint-cwd",str(seed),"--push",cwd=drv)
    heads=g("for-each-ref","--format=%(refname:short)","refs/heads",cwd=origin).split()
    print("RESULT D no-args rc",rc,"main moved:", g("rev-parse","refs/heads/main",cwd=origin).strip()!=main_before, "heads:",heads, "::", o.strip().splitlines()[0])
    # D2: an R10 group with no args while main carries only r9 -> refuses (not silent)
    rc,o=tool("roster_edit.py","wire-issue","R10-A","4243","--checkout",str(drv),"--worktree",str(td/"wtD2"),"--lint-cwd",str(seed),"--push",cwd=drv)
    print("RESULT D2 r10 group, main has r9 only: rc",rc,"::",o.strip().splitlines()[-1][:160])
    # D3: main carries r9+r10 -> default lands on handoff/audit-r10-roster
    s2=td/"seed"; (s2/R10).write_text(roster("R10-A")); g("add","-A",cwd=s2); g("commit","-q","-m","r10",cwd=s2); g("push","-q",str(origin),"main:refs/heads/main",cwd=s2)
    main_before=g("rev-parse","refs/heads/main",cwd=origin).strip()
    (drv/R10).unlink()
    rc,o=tool("roster_edit.py","wire-issue","R10-A","4244","--checkout",str(drv),"--worktree",str(td/"wtD3"),"--lint-cwd",str(seed),"--push",cwd=drv)
    print("RESULT D3 rc",rc,"main moved:", g("rev-parse","refs/heads/main",cwd=origin).strip()!=main_before, "heads:", g("for-each-ref","--format=%(refname:short)","refs/heads",cwd=origin).split(), "::", o.strip().splitlines()[0])
    # D4: explicit --roster-ref main without --branch (documented: branch = roster-ref)
    rc,o=tool("roster_edit.py","wire-issue","R10-A","4245","--checkout",str(drv),"--roster-ref","main","--worktree",str(td/"wtD4"),"--lint-cwd",str(seed),cwd=drv)
    print("RESULT D4 explicit --roster-ref main, no --push: rc",rc,"::",o.strip().splitlines()[0])
    # C: override naming a missing file, per tool
    for t,a in [("roster_edit.py",["wire-issue","R10-A","1","--checkout",str(drv),"--worktree",str(td/"wtC"),"--roster-path","nope.json","--branch","c"]),
                ("plan_table.py",["--roster-ref","origin/main","--roster-path","nope.json"]),
                ("resume_doc.py",["--roster-ref","origin/main","--roster-path","nope.json","--offline","--pr-state",str(td/"p.json")]),
                ("handover_prompt.py",["--roster-ref","origin/main","--roster-path","nope.json"]),
                ("state_docs.py",["--checkout",str(drv),"--roster-path","nope.json","--pr-state",str(td/"p.json")]),
                ("orchestrator_tick.py",["--checkout",str(drv),"--roster-ref","origin/main","--roster-path","nope.json","--only","PLAN"])]:
        rc,o=tool(t,*a,cwd=drv); last=[l for l in o.splitlines() if l.strip()][-1][:150]
        print(f"RESULT C {t} rc={rc} tb={'Traceback' in o} :: {last}")
