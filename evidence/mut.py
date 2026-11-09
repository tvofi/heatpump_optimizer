import subprocess, sys, pathlib
ROOT = pathlib.Path(sys.argv[1])
M = [
 ("closed-drops-refused-deferred","tools/audit/seat/roster_lib.py",'CLOSED_STAGES = FINISHED_STAGES + ("refused", "deferred")','CLOSED_STAGES = FINISHED_STAGES',["tools/audit/seat/roster_lib.py"]),
 ("closeout_exempt-open","tools/audit/seat/roster_lib.py","G, open_ = groups_of(roster), set(unfinished_groups(roster))","G, open_ = groups_of(roster), set(open_groups(roster))",["tools/audit/seat/roster_lib.py","tools/audit/seat/closeout.py"]),
 ("roster_blockers-open","tools/audit/seat/closeout.py","roster_lib.unfinished_groups(roster)","roster_lib.open_groups(roster)",["tools/audit/seat/closeout.py"]),
 ("unfinished-reads-closed","tools/audit/seat/roster_lib.py",'if (g.get("resume") or {}).get("stage") not in FINISHED_STAGES}','if (g.get("resume") or {}).get("stage") not in CLOSED_STAGES}',["tools/audit/seat/roster_lib.py","tools/audit/seat/closeout.py"]),
 ("releasing-plus-deferred","tools/audit/seat/roster_lib.py","RELEASING_STAGES = FINISHED_STAGES + RULED_STAGES",'RELEASING_STAGES = FINISHED_STAGES + RULED_STAGES + ("deferred",)',["tools/audit/seat/roster_lib.py"]),
 ("gates-always-true","tools/audit/seat/roster_lib.py",'return (group.get("resume") or {}).get("stage") not in RELEASING_STAGES','return (group.get("resume") or {}).get("stage") not in FINISHED_STAGES',["tools/audit/seat/roster_lib.py","tools/audit/seat/handover_prompt.py","tools/plan/replan.py"]),
 ("held-not-transitive","tools/audit/seat/roster_lib.py","elif a in held and gates(G[a]):","elif False:",["tools/audit/seat/roster_lib.py"]),
 ("held-ignores-gates","tools/audit/seat/roster_lib.py","elif a in held and gates(G[a]):","elif a in held:",["tools/audit/seat/roster_lib.py","tools/plan/replan.py"]),
 ("depth-is_open","tools/audit/seat/roster_lib.py","oa = [a for a in g.get(\"after\") or [] if gates(G[a])]","oa = [a for a in g.get(\"after\") or [] if is_open(G[a])]",["tools/audit/seat/roster_lib.py"]),
 ("critpath-all","tools/audit/seat/roster_lib.py",'deps = [a for a in G[n].get("after") or [] if a in G and gates(G[a])]','deps = [a for a in G[n].get("after") or [] if a in G]',["tools/audit/seat/roster_lib.py"]),
 ("ready_next-revert","tools/audit/seat/handover_prompt.py",'if not any(roster_lib.gates(G[a]) for a in gr.get("after") or [] if a in G))','if all(a not in open_ for a in gr.get("after") or []))',["tools/audit/seat/handover_prompt.py"]),
 ("resume_doc-ready-revert","tools/audit/seat/resume_doc.py","if not any(roster_lib.gates(G[a]) for a in deps if a in G):","if all(a not in open_ for a in deps):",["tools/audit/seat/resume_doc.py"]),
 ("tick-skip-deferred","tools/audit/seat/orchestrator_tick.py","if gid not in open_g and stage not in DEFERRED_STAGES:","if gid not in open_g:",["tools/audit/seat/orchestrator_tick.py"]),
 ("tick-blockers-open","tools/audit/seat/orchestrator_tick.py","blockers = [a for a in (g.get(\"after\") or []) if a in groups and rl.gates(groups[a])]","blockers = [a for a in (g.get(\"after\") or []) if a in open_g]",["tools/audit/seat/orchestrator_tick.py"]),
 ("plan_page-blk-done","tools/audit/seat/plan_page.py",'if a in G and roster_lib.gates(G[a])]','if a in G and a not in done]',["tools/audit/seat/plan_page.py"]),
 ("replan-depgraph","tools/plan/replan.py","if a in open_ and roster_lib.gates(G[a]):","if a in open_:",["tools/plan/replan.py"]),
 ("replan-held-empty","tools/plan/replan.py","held = roster_lib.held_behind_deferred(G)","held = {}",["tools/plan/replan.py"]),
 ("replan-open-minus-held","tools/plan/replan.py","open_ = open_ - set(held)","open_ = open_",["tools/plan/replan.py"]),
 ("replan-stem-prefix","tools/plan/replan.py",'g == p or g.startswith(p + "-") for p in INSTRUMENT_NAME_STEMS','g.startswith(p) for p in INSTRUMENT_NAME_STEMS',["tools/plan/replan.py"]),
 ("replan-check-flag","tools/plan/replan.py",'if g.get("coordinator") and not g.get("exempt_coordinator")]','if g.get("coordinator")]',["tools/plan/replan.py"]),
 ("replan-cap-exempt-off","tools/plan/replan.py","n = pick(sorted(x for x in ready if x in crit), t, cap_exempt=True)","n = pick(sorted(x for x in ready if x in crit), t, cap_exempt=False)",["tools/plan/replan.py"]),
]
only = sys.argv[2:]
for name, f, old, new, tests in M:
    if only and name not in only: continue
    p = ROOT / f; src = p.read_text()
    if src.count(old) != 1:
        print(f"RESULT mutant {name}: NOT-APPLIED count={src.count(old)}"); continue
    p.write_text(src.replace(old, new))
    try:
        reds = []
        for t in tests:
            r = subprocess.run([sys.executable, "-I", t, "--self-test"], cwd=ROOT, capture_output=True, text=True, timeout=600)
            tail = (r.stdout + r.stderr).strip().splitlines()[-1:] or [""]
            if r.returncode != 0: reds.append(f"{t} rc={r.returncode} [{tail[0][:120]}]")
        print(f"RESULT mutant {name}: " + ("KILLED by " + "; ".join(reds) if reds else "SURVIVED " + ",".join(tests)), flush=True)
    finally:
        p.write_text(src)
