import subprocess, sys, pathlib
wt = pathlib.Path(sys.argv[1])
M = [
 ("M4", "tools/audit/seat/token_ledger.py", 'if first and o.get("type") == "user":', 'if o.get("type") == "user":', "tools/audit/seat/token_ledger.py --self-test"),
 ("M5", "tools/audit/seat/token_ledger.py", 'd["t"] = max(d["t"], stamp)', 'd["t"] = stamp', "tools/audit/seat/token_ledger.py --self-test"),
 ("D1 stub-key guard restored", "tools/audit/seat/cloud_dispatch.py", '    try:\n        key = token_ledger.header(', '    if publish_ref: return {"job_config": {}} if False else None\n    try:\n        key = token_ledger.header(', None),
 ("D1b key only for whole prompt", "tools/audit/seat/cloud_dispatch.py", '    text = f"{first} {key}\\n{rest}"\n    payload', '    text = f"{first} {key}\\n{rest}" if not publish_ref else text\n    payload', "tools/audit/seat/cloud_dispatch.py --self-test"),
 ("D2 missing classes dropped", "tools/audit/check_scopes.py", 'missing = [c for c in classes if c not in', 'missing = [] and [c for c in classes if c not in', "tools/audit/check_scopes.py --repo . --self-test"),
 ("D3 unkeyed dropped", "tools/audit/check_scopes.py", 'unkeyed = sum(r.get("seat_class") != "orchestrator" and', 'unkeyed = 0 and sum(r.get("seat_class") != "orchestrator" and', "tools/audit/check_scopes.py --repo . --self-test"),
 ("D4 orchestrator exclusion dropped", "tools/audit/check_scopes.py", 'r.get("seat_class") != "orchestrator" and r.get("seat"', 'True and r.get("seat"', "tools/audit/check_scopes.py --repo . --self-test"),
 ("D5 window ignored for classes", "tools/audit/check_scopes.py", 'win = [r for r in rows if r.get("t") and a <= at(r["t"]) < b]', 'win = [r for r in rows if r.get("t")]', "tools/audit/check_scopes.py --repo . --self-test"),
 ("D6 unread print dropped", "tools/audit/check_scopes.py", '    if why:  # a seat found', '    if False and why:  # a seat found', "tools/audit/check_scopes.py --repo . --self-test"),
 ("D7 unread returns early (refusal lost)", "tools/audit/check_scopes.py", 'an evaluator or reviewer seat of the graded round is not checked whole")\n', 'an evaluator or reviewer seat of the graded round is not checked whole")\n        return []\n', "tools/audit/check_scopes.py --repo . --self-test"),
]
for name, f, old, new, cmd in M:
    if cmd is None: continue
    p = wt / f; src = p.read_text()
    n = src.count(old)
    if n != 1:
        print(f"{name}: SKIP target count {n}"); continue
    p.write_text(src.replace(old, new))
    try:
        r = subprocess.run(["python3", "-I", *cmd.split()], cwd=wt, capture_output=True, text=True, timeout=600)
        out = r.stdout + r.stderr
        fails = [l for l in out.splitlines() if "FAIL" in l or "not held" in l.lower() or "failed" in l.lower()][:4]
        verdict = "KILLED" if r.returncode != 0 else "SURVIVED"
        print(f"{name}: {verdict} rc={r.returncode}"); [print("   ", l[:200]) for l in fails]
    finally:
        p.write_text(src)
