import subprocess, sys, pathlib
root = pathlib.Path(sys.argv[1])
FL = "tools/audit/fold_ledger.py"; RS = "tools/audit/seat/review_strength.py"
M = [
 (FL, "x is not None and t is not None and x > t)", "x is not None and t is not None and x >= t)"),
 (FL, '_git(root, "log", "--follow", "--diff-filter=A"', '_git(root, "log", "--diff-filter=A"'),
 (FL, '"--is-shallow-repository").strip() == "true"', '"--is-shallow-repository").strip() == "never"'),
 (FL, 'cited + [("rules", r) for r in e.get("rules", [])]', 'cited'),
 (FL, "dates[json.loads(lit)] = int(stamp)", "dates.setdefault(json.loads(lit), int(stamp))"),
 (FL, "(int(adds[-2]), adds[-1])", "(int(adds[0]), adds[1])"),
 (FL, "undated = sum(1 for _, x in rows if x is None or t is None)", "undated = sum(1 for _, x in rows if x is None)"),
 (FL, '"--first-parent", "--diff-merges=first-parent", ', ''),
 (FL, 'print(f"{head} no-class")\n            continue', 'pass'),
 (FL, 'if line.startswith("+") and not line.startswith("+++")', 'if line.startswith("+")'),
 (RS, "if len(keys) != len(set(keys)) or set(keys) != set(taught):", "if set(keys) != set(taught):"),
 (RS, "if len(keys) != len(set(keys)) or set(keys) != set(taught):", "if len(keys) != len(set(keys)):"),
 (RS, 'else clause if text and re.search(rf"^{m[2]}\\. ", text, re.M) else', 'else clause if text else'),
 (RS, 'return (clause_of or {}).get(v["cls"], f"(untaught) {v[\'cls\']}")', 'return v["cls"]'),
 (RS, 'pairs = PAIR_RE.findall(re.sub(r"//[^\\n]*", "", m[1]))', 'pairs = PAIR_RE.findall(m[1])'),
 (RS, 'return "(merge)" if v["kind"] == "merge" else "(no class)"', 'return "(no class)"'),
 (RS, "return {k: clause or None for k, clause in pairs}", "return {k: clause for k, clause in pairs}"),
]
for i, (f, a, b) in enumerate(M):
    p = root / f; src = p.read_text()
    n = src.count(a)
    if n != 1:
        print(f"M{i} {f} SKIP occurrences={n}: {a[:60]}"); continue
    p.write_text(src.replace(a, b))
    try:
        r = subprocess.run([sys.executable, "-I", f, "--self-test"], cwd=root, capture_output=True, text=True, timeout=600)
        out = r.stdout + r.stderr
        fails = [l for l in out.splitlines() if "FAIL" in l]
        print(f"M{i} {f} rc={r.returncode} fails={len(fails)} {'KILLED' if r.returncode or fails else 'SURVIVED'} :: {a[:70]!r} -> {b[:50]!r}")
        if fails: print("    first:", fails[0][:200])
    finally:
        p.write_text(src)
