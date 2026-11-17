import subprocess, sys, pathlib
WT = pathlib.Path(sys.argv[1])
S = WT / "tools/audit/seat"
LL, RL, RM = S / "loop_ledger.py", S / "roster_lib.py", S / "round_metrics.py"
M = [
 # is_cause, the body's four
 ("is_cause: #n pattern dropped", RL, "(isinstance(cause, str) and bool(_PR.match(cause)))", "isinstance(cause, str)"),
 ("is_cause: CAUSES arm dropped", RL, "return cause in CAUSES or (isinstance", "return (isinstance"),
 ("is_cause: roster-group arm dropped", RL, " or (cause in names and cause != me)\n", "\n"),
 ("is_cause: own-group refusal dropped", RL, "(cause in names and cause != me)", "(cause in names)"),
 ("convergence_why: is_cause call dropped", RL, "if not is_cause(cause, names, me):", "if False:"),
 # producer
 ("fetch_runs: head_sha dropped", RM, '"head_sha": r.get("head_sha"),', '"head_sha": None,'),
 ("fetch_runs: event dropped", RM, '"event": r.get("event"),', '"event": None,'),
 ("fetch_runs: head_branch dropped", RM, '"head_branch": r.get("head_branch"),', '"head_branch": None,'),
 ("fetch_runs: pr always null", RM, 'next((q.get("number") for q in r.get("pull_requests") or []), None)', "None"),
 ("fetch_runs: ci_runs.json written narrow", RM, 'write(d / "ci_runs.json", json.dumps(ci))', 'write(d / "ci_runs.json", json.dumps(narrow))'),
 # reader, mine (not the table's)
 ("green: latest attempt -> first", LL, "last = g[max(g)] if g else None", "last = g[min(g)] if g else None"),
 ("green: non-failure latest reads red", LL, 'True if last == "success" else False if last == "failure" else None', 'True if last == "success" else False'),
 ("green: no-listing first-attempt success not green", LL, '            green[r["id"]] = True  # one attempt', '            pass  # one attempt'),
 ("mains: unread main runs kept out", LL, 'if _on_main(r) and green.get(r["id"]) is not None]', 'if _on_main(r) and green.get(r["id"]) is not False]'),
 ("cause: main spell step removed", LL, "        if op is not None:\n", "        if False:\n"),
 ("cause: subject unread -> uncleared", LL, 'UNREAD, f"main red since run {op[\'id\']}, whose subject names no pull request")', 'UNCLEARED, f"main red since run {op[\'id\']}, whose subject names no pull request")'),
 ("cause: head row uses own opener, not main's last", LL, 'op = opener.get(r["id"]) if _on_main(r) else opener[before[-1]["id"]] if before else None', 'op = opener.get(r["id"])'),
 ("cause: main row takes head-row path", LL, 'op = opener.get(r["id"]) if _on_main(r) else opener[before[-1]["id"]] if before else None', 'op = opener[before[-1]["id"]] if before else None'),
 ("cause: no-pr head reads uncleared", LL, 'return UNREAD, "no run at the head names a pull request"', 'return UNCLEARED, "no run at the head names a pull request"'),
 ("rows: blind run dropped", LL, '                rows.append({**base, "attempt": r["attempt"], "blind": True})', "                pass"),
 ("rows: gate job counted as failed job", LL, ' and j.get("name") != "gate"})', "})"),
 ("rows: failed = any conclusion", LL, '\n                             and j.get("conclusion") == "failure" and j.get("name")', '\n                             and j.get("name")'),
 ("owed: prelude and gate not owed", LL, 'owed = set(gate.gate_required()) | {"prelude", "gate"}', "owed = set(gate.gate_required())"),
 ("summary: main/heads counts swapped", LL, "f\"(main {sum(x['main'] for x in reds)}, heads {sum(not x['main'] for x in reds)}) \"", "f\"(main {sum(not x['main'] for x in reds)}, heads {sum(x['main'] for x in reds)}) \""),
 ("summary: unread causes counted as caused", LL, 'if x["cause"] not in (UNREAD, UNCLEARED))', 'if x["cause"] not in (UNCLEARED,))'),
 ("main(): --runs ignored", LL, "red_lines(Path(a.runs) if a.runs else None, git_subject(a.repo))", "red_lines(None, git_subject(a.repo))"),
 ("_when: order by id alone", LL, 'return (round_metrics.epoch(r["t"]), r["id"])', 'return (0, r["id"])'),
 ("gate job name", LL, 'for j in doc["jobs"] if j.get("name") == "gate"}', 'for j in doc["jobs"]}'),
]
CMDS = {LL: [["python3","-I",str(LL),"--self-test","--no-mutants"]],
        RM: [["python3","-I",str(RM),"--self-test","--no-mutants"],["python3","-I",str(LL),"--self-test","--no-mutants"]],
        RL: [["python3","-I",str(LL),"--self-test","--no-mutants"],["python3","-I",str(S/"roster_edit.py"),"--self-test"]]}
surv = 0
for name, f, old, new in M:
    src = f.read_text()
    if src.count(old) != 1:
        print(f"STALE   {name}: needle occurs {src.count(old)} time(s)"); continue
    f.write_text(src.replace(old, new))
    try:
        fails = []
        for c in CMDS[f]:
            try:
                p = subprocess.run(c, cwd=WT, capture_output=True, text=True, timeout=200)
                if p.returncode != 0:
                    ln = [l for l in (p.stdout + p.stderr).splitlines() if l.startswith("FAIL") or "Error" in l]
                    fails.append(f"{pathlib.Path(c[2]).name} rc={p.returncode}: {(ln or ['?'])[0][:150]}" + (f" (+{len(ln)-1} more)" if len(ln) > 1 else ""))
            except subprocess.TimeoutExpired:
                fails.append(f"{pathlib.Path(c[2]).name} timeout")
    finally:
        f.write_text(src)
    if fails: print(f"KILLED  {name} :: " + " | ".join(fails), flush=True)
    else: surv += 1; print(f"SURVIVED {name}", flush=True)
print(f"RESULT reviewer mutants: {len(M)} drawn, {surv} survived")
