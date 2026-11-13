import subprocess, sys, pathlib, re
f = pathlib.Path("tools/audit/check_scopes.py"); src = f.read_text()
M = [
 ("M1 missing evaluation returns no gap", 'return gaps + [f"{path} is not in the tree: the start evaluation has not run"]', 'return gaps'),
 ("M2 missing previous record never tested", '    if prev not in tree:\n        gaps.append(', '    if False:\n        gaps.append('),
 ("M3 card decision never tested", 'if card.get("decision") not in DECISIONS:', 'if False:'),
 ("M4 accepted card merge never tested", 'elif card.get("decision") == "accepted" and not (card.get("merged") and merged(card["merged"])):', 'elif False:'),
 ("M5 evaluator==reviewer allowed", 'if not seat or not rev or seat == rev or "orchestrator" in (seat, rev):', 'if not seat or not rev or "orchestrator" in (seat, rev):'),
 ("M6 gaps do not reach exit code", '        ok = ok and not gaps\n', '        ok = ok\n'),
 ("R7 orchestrator allowed (reviewer's)", 'or seat == rev or "orchestrator" in (seat, rev):', 'or seat == rev:'),
 ("R8 evidence never tested (reviewer's)", 'elif not str(row.get("evidence", "")).strip():', 'elif False:'),
 ("R9 card reference never tested (reviewer's)", 'elif row["verdict"] != "keep" and row.get("card") not in cards:', 'elif False:'),
 ("R10 term rows never tested (reviewer's)", '            if not isinstance(row, dict):\n                gaps.append(f"{prev} has no term {t}")', '            if False:\n                gaps.append(f"{prev} has no term {t}")'),
 ("R11 round identity never tested (reviewer's)", 'if ev.get("round") != rnd or ev.get("reads") != prev:', 'if False:'),
 ("R12 verdict never tested (reviewer's)", 'if not isinstance(row, dict) or row.get("verdict") not in VERDICTS:', 'if not isinstance(row, dict):'),
 ("R13 enumerator never tested (reviewer's)", 'elif "value" in row and not str(row.get("enumerator", "")).strip():', 'elif False:'),
 ("R14 no_read reason never tested (reviewer's)", 'elif "value" not in row and not str(row.get("no_read", "")).strip():', 'elif False:'),
]
def run():
    r = subprocess.run([sys.executable, "-I", str(f), "--self-test", "--repo", "."], capture_output=True, text=True)
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr.strip().splitlines()[-1]
    false_arms = re.findall(r"'([^']+)': False", last)
    return r.returncode, false_arms, last[:160] if not false_arms else ""
print("BASE", run()[0])
for name, a, b in M:
    assert src.count(a) == 1, (name, src.count(a))
    f.write_text(src.replace(a, b))
    try: rc, arms, tail = run()
    finally: f.write_text(src)
    print(f"RESULT {name}: rc={rc} {'KILLED' if rc else 'SURVIVED'} arms={arms} {tail}")
print("BASE-AFTER", run()[0])
