import subprocess, sys, pathlib
F = pathlib.Path(sys.argv[1]) / "tools/audit/seat/loop_ledger.py"
orig = F.read_text()
M = [
 ("edge return deleted", '        if op is EDGE:\n            return UNREAD, "main red at the first main run read, no green main run read before it"\n', ""),
 ("EDGE falsy", 'EDGE = {"id": None}', 'EDGE = {}'),
 ("status all in_progress", '("completed" if j.get("conclusion") else "in_progress", j.get("conclusion"))', '("in_progress", j.get("conclusion"))'),
 ("event != pull_request", 'if r.get("event") == "push" else None', 'if r.get("event") != "pull_request" else None'),
 ("headline product counts machinery", 'sum(a == _gate().RED for a, _ in pairs)', 'sum(b == _gate().RED for _, b in pairs)'),
 ("headline product != GREEN", 'sum(a == _gate().RED for a, _ in pairs)', 'sum(a != _gate().GREEN for a, _ in pairs)'),
 ("headline machinery != GREEN", 'sum(b == _gate().RED for _, b in pairs)', 'sum(b != _gate().GREEN for _, b in pairs)'),
 ("unread count over rows", 'on {len(reds) - len(pairs)}', 'on {len(rows) - len(pairs)}'),
 ("row pair swapped", '"product {}, machinery {}".format(*x["status"])', '"product {1}, machinery {0}".format(*x["status"])'),
 ("status class pr", '}, "push") if r.get', '}, "pr") if r.get'),
 ("status over all jobs", 'for j in at}, "push")', 'for j in docs[r["id"]]["jobs"]}, "push")'),
 ("edge on head rows only", '        if op is EDGE:\n', '        if op is EDGE and not _on_main(r):\n'),
]
cmd = ["python3", "-I", "tools/audit/seat/loop_ledger.py", "--self-test", "--no-mutants"]
for name, a, b in M:
    n = orig.count(a)
    if n != 1:
        print(f"SKIP {name}: matches {n}"); continue
    F.write_text(orig.replace(a, b))
    try:
        p = subprocess.run(cmd, cwd=F.parents[3], capture_output=True, text=True, timeout=300)
        out = p.stdout + p.stderr
        fails = [l for l in out.splitlines() if l.startswith("FAIL")]
        tail = out.strip().splitlines()[-1] if out.strip() else ""
        print(("KILLED" if (p.returncode or fails) else "SURVIVED"), name, "|", tail, "|", fails[:2])
    finally:
        F.write_text(orig)
