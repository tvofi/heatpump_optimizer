import shutil, subprocess, sys, tempfile, pathlib
src = pathlib.Path("/tmp/claude-0/wt/tools/ci")
M = {
 "covered_deferral->False": ("        return (source_after(gate.get(\"started_at\") or \"\", others)\n                and any(", "        return False and (source_after(gate.get(\"started_at\") or \"\", others)\n                and any("),
 "drop source_after leg": ("        return (source_after(gate.get(\"started_at\") or \"\", others)\n                and any(", "        return (True\n                and any("),
 "drop covers leg": ("                and any(covers_newest(latest_gate(js), runs) for js in others.values()))", "                and True)"),
 "judged first-attempt read->False": ("        if r[\"run_attempt\"] < 2:\n            return False", "        if True:\n            return False"),
 "judged accepts any first attempt": ("return st == 200 and (latest_gate((body or {}).get(\"jobs\") or []) or {}).get(\"conclusion\") == \"success\"", "return st == 200"),
 "judged unreadable->True": ("return st == 200 and (latest_gate", "return st != 200 or (latest_gate"),
 "covered check before later": None,
}
for name, sub in M.items():
    if sub is None: continue
    d = pathlib.Path(tempfile.mkdtemp()); shutil.copytree(src, d/"ci")
    p = d/"ci"/"sweep.py"; t = p.read_text(); assert sub[0] in t, name
    p.write_text(t.replace(sub[0], sub[1], 1))
    r = subprocess.run([sys.executable, str(p), "--self-test"], capture_output=True, text=True)
    last = (r.stdout + r.stderr).strip().splitlines()[-1]
    print(f"RESULT mutant {name}: rc={r.returncode} {last}")
