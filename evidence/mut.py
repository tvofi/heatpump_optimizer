import subprocess, sys, pathlib
W = pathlib.Path.home()/"wt3633"
M = [
 ("R1-finder_gate-any","tools/audit/seat/roster_lib.py","return v if isinstance(v, bool) else None","return v","rl"),
 ("R2-unmarked-read-gating","tools/audit/seat/roster_lib.py","if finder_gate(g) is not True]","if finder_gate(g) is False]","rl"),
 ("R3-unmarked-never-flagged","tools/audit/seat/roster_lib.py","if finder_gate(groups_of(roster)[k]) is None]","if False]","rl"),
 ("R4-closed-listed","tools/audit/seat/roster_lib.py","for k, g in open_groups(roster).items() if finder_gate","for k, g in groups_of(roster).items() if finder_gate","rl"),
 ("C1-nongating-unmerged-is-gap","tools/audit/check_scopes.py","elif not gating and not (c and merged(c)):","elif False:","cs"),
 ("C2-no-bool-not-refused","tools/audit/check_scopes.py","            gaps.append(f\"{path} card {cid} is accepted and carries no boolean gates_finders","            0 and gaps.append(f\"{path} card {cid} is accepted and carries no boolean gates_finders","cs"),
 ("C3-group-rc-0","tools/audit/check_scopes.py","return {\"open_groups\": groups, \"unmarked_groups\": unmarked}, 1 if unmarked else 0, lines","return {\"open_groups\": groups, \"unmarked_groups\": unmarked}, 0, lines","cs"),
 ("C4-card-rc-0","tools/audit/check_scopes.py","\"unmarked_cards\": unmarked}, 1 if unmarked else 0, lines","\"unmarked_cards\": unmarked}, 0, lines","cs"),
 ("C5-joined-rc-cards-only","tools/audit/check_scopes.py","max(crc, grc)","crc","cs"),
 ("C6-joined-drops-group-lines","tools/audit/check_scopes.py","clines + glines","clines","cs"),
 ("C7-null-reviewer-accepted","tools/audit/check_scopes.py","norm(ev[k]) if full(ev.get(k)) else \"\"","norm(str(ev.get(k) or \"\"))","cs"),
 ("C8-parallel-not-appended","tools/audit/check_scopes.py","                parallel.append(cid)","                pass","cs"),
 ("C7b-base-line-restored","tools/audit/check_scopes.py","norm(ev[k]) if full(ev.get(k)) else \"\"","norm(ev.get(k, \"\"))","cs"),
 ("E1-set-field-gates-not-bool","tools/audit/seat/roster_edit.py","elif field in (\"hotfix\", \"gates_finders\"):","elif field == \"hotfix\":","re"),
 ("B1-brief_lint-rule-off","tools/policy/brief_lint.mjs","if (g.gates_finders !== undefined && typeof g.gates_finders !== 'boolean') {","if (false) {","bl"),
]
CMD = {"rl":["python3","tools/audit/seat/roster_lib.py","--self-test"],
       "cs":["python3","tools/audit/check_scopes.py","--repo",".","--self-test"],
       "re":["python3","tools/audit/seat/roster_edit.py","--self-test"],
       "bl":["node","tools/policy/brief_lint.mjs"]}
sel = sys.argv[1:]
for name,f,old,new,t in M:
    if sel and name not in sel: continue
    p = W/f; src = p.read_text()
    if src.count(old)!=1: print(f"RESULT {name} NOT-APPLIED count={src.count(old)}", flush=True); continue
    p.write_text(src.replace(old,new))
    try:
        r = subprocess.run(CMD[t], cwd=W, capture_output=True, text=True, timeout=600)
        tail = [l[:160] for l in (r.stdout+r.stderr).strip().splitlines()[-1:]]
        fails=[l[:200] for l in (r.stdout+r.stderr).splitlines() if l.startswith("FAIL ") or "VACUOUS" in l][:2]
        print(f"RESULT {name} {'KILLED' if r.returncode else 'SURVIVED'} rc={r.returncode} {tail} {fails}", flush=True)
    finally:
        p.write_text(src)
subprocess.run(["git","-C",str(W),"status","--short"])
