import subprocess, sys, pathlib
root = pathlib.Path(sys.argv[1]); F = root / "tools/audit/seat/loop_ledger.py"
orig = F.read_text()
M = [
 ("NULL control (no change)", None, None),
 ("event != pull_request", 'if r.get("event") == "push" else None', 'if r.get("event") != "pull_request" else None'),
 ("summary product counts machinery", 'sum(a == _gate().RED for a, _ in pairs)', 'sum(b == _gate().RED for _, b in pairs)'),
 ("summary product != GREEN", 'sum(a == _gate().RED for a, _ in pairs)', 'sum(a != _gate().GREEN for a, _ in pairs)'),
 ("summary machinery != GREEN", 'sum(b == _gate().RED for _, b in pairs)', 'sum(b != _gate().GREEN for _, b in pairs)'),
 ("unread count over rows", 'on {len(reds) - len(pairs)}', 'on {len(rows) - len(pairs)}'),
 # reviewer extras on the same lines
 ("event not in (pull_request, merge_group)", 'if r.get("event") == "push" else None', 'if r.get("event") not in ("pull_request", "merge_group") else None'),
 ("event not in (pull_request, workflow_dispatch)", 'if r.get("event") == "push" else None', 'if r.get("event") not in ("pull_request", "workflow_dispatch") else None'),
 ("unread count over reds alone", 'on {len(reds) - len(pairs)}', 'on {len(reds)}'),
 ("summary machinery counts product", 'sum(b == _gate().RED for _, b in pairs)', 'sum(a == _gate().RED for a, _ in pairs)'),
]
cmd = ["python3", "-I", "tools/audit/seat/loop_ledger.py", "--self-test", "--no-mutants"]
for name, a, b in M:
    if a is not None:
        head, tail = orig.split("\nMUTANTS = {", 1)  # mutate production code above the table only
        n = head.count(a)
        if n != 1: print(f"SKIP {name}: matches {n}"); continue
        F.write_text(head.replace(a, b) + "\nMUTANTS = {" + tail)
    try:
        p = subprocess.run(cmd, cwd=root, capture_output=True, text=True, timeout=300)
        out = p.stdout + p.stderr
        fails = [l for l in out.splitlines() if l.startswith("FAIL")]
        tail = out.strip().splitlines()[-1] if out.strip() else ""
        print(("KILLED" if (p.returncode or fails) else "SURVIVED"), name, "|", tail, "|", fails[:2], flush=True)
    finally:
        F.write_text(orig)
