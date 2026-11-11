import subprocess, sys, pathlib
S="tools/plan/size_durations.py"; R="tools/plan/replan.py"
M = [
 ("rest-short", S, "if len(pulls) < 100:", "if not pulls:"),
 ("rest-since", S, 'if p["created_at"] < since:', 'if p["created_at"] <= since:'),
 ("rest-merged", S, 'if p.get("merged_at"):', 'if True:'),
 ("rest-first", S, 'first = ((commits or [{}])[0]', 'first = ((commits or [{}])[-1]'),
 ("read-replay", S, "return json.loads(Path(cache).read_text(encoding=\"utf-8\")), True", "return json.loads(Path(cache).read_text(encoding=\"utf-8\")), False"),
 ("note-run", S, 'out["sizes_provenance"] += input_note(via, since, len(prs), replayed)', 'pass'),
 ("run-via", S, "prs, replayed = read_prs(READS, via,", "prs, replayed = read_prs(READS, \"graphql\","),
 ("replan-via", R, "size_durations.DEFAULT_PERCENTILE, args.sizes_via)", "size_durations.DEFAULT_PERCENTILE)"),
 ("replan-cap", R, "unset = (\"live_remaining_fraction\",)", "unset = ()"),
]
for name, f, old, new in M:
    p = pathlib.Path(f); src = p.read_text()
    n = src.count(old)
    if n != 1: print(f"RESULT mutant={name} NOT-APPLIED count={n}"); continue
    p.write_text(src.replace(old, new))
    try:
        cp = subprocess.run([sys.executable, f, "--self-test"], capture_output=True, text=True, timeout=400)
        out = cp.stdout + cp.stderr
        fails=[l for l in out.splitlines() if "FAIL" in l]
        print(f"RESULT mutant={name} rc={cp.returncode} fails={len(fails)} {'KILLED' if cp.returncode else 'SURVIVED'}", fails[:2])
    finally:
        p.write_text(src)
