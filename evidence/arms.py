import sys, importlib.util, pathlib, subprocess
wt = pathlib.Path(sys.argv[1]); f = wt/"tools/audit/check_scopes.py"; src = f.read_text()
M = {"base": None,
 "D2": ('missing = [c for c in classes if c not in', 'missing = [] and [c for c in classes if c not in'),
 "D3": ('unkeyed = sum(r.get("seat_class") != "orchestrator" and', 'unkeyed = 0 and sum(r.get("seat_class") != "orchestrator" and'),
 "D5": ('win = [r for r in rows if r.get("t") and a <= at(r["t"]) < b]', 'win = [r for r in rows if r.get("t")]')}
for k, m in M.items():
    f.write_text(src if m is None else src.replace(*m))
    try:
        code = "import sys,os;sys.path[:0]=['tools/audit','tests'];os.chdir('.');import check_scopes as c;a=c.ledger_round_self_test();print([n for n,v in a.items() if not v] or 'all held', len(a))"
        r = subprocess.run(["python3","-c",code], cwd=wt, capture_output=True, text=True)
        print(k, (r.stdout.strip() or r.stderr.strip()[-300:]))
    finally:
        f.write_text(src)
