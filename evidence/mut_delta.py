import subprocess, sys, pathlib
root = pathlib.Path(sys.argv[1]); F = root / "tools/audit/seat/loop_ledger.py"
orig = F.read_text(); cut = orig.index("def _self_test_reds")
M = [
 ("control (unmutated)", None, None),
 ("event != pull_request", 'if r.get("event") == "push" else None', 'if r.get("event") != "pull_request" else None'),
 ("headline product counts machinery", 'sum(a == _gate().RED for a, _ in pairs)', 'sum(b == _gate().RED for _, b in pairs)'),
 ("headline product != GREEN", 'sum(a == _gate().RED for a, _ in pairs)', 'sum(a != _gate().GREEN for a, _ in pairs)'),
 ("headline machinery != GREEN", 'sum(b == _gate().RED for _, b in pairs)', 'sum(b != _gate().GREEN for _, b in pairs)'),
 ("unread count over rows", 'on {len(reds) - len(pairs)}', 'on {len(rows) - len(pairs)}'),
]
cmd = ["python3", "-I", "tools/audit/seat/loop_ledger.py", "--self-test", "--no-mutants"]
for name, a, b in M:
    if a is not None:
        head = orig[:cut]
        n = head.count(a)
        if n != 1: print(f"SKIP {name}: production matches {n}"); continue
        F.write_text(head.replace(a, b) + orig[cut:])
    try:
        p = subprocess.run(cmd, cwd=root, capture_output=True, text=True, timeout=300)
        out = p.stdout + p.stderr
        fails = [l for l in out.splitlines() if l.startswith("FAIL")]
        tail = out.strip().splitlines()[-1] if out.strip() else ""
        print(("KILLED" if (p.returncode or fails) else "SURVIVED"), name, "|", tail, "|", fails[:3], flush=True)
    finally:
        F.write_text(orig)
