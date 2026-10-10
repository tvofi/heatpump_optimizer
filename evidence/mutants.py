import subprocess, sys, re
from pathlib import Path
WT = Path("/Users/timmalmstrom/hpo-seats/r9rev-2111/wt")
F = WT/"tools/audit/seat/record_row.py"
ORIG = F.read_text()

MUTS = {
 "M0 null control (unmutated)": [],
 "M1 plan_merges back to has_row alone (THE DEFECT)": [
   ('        if has_row(n, root) and (str(m.get("state") or "") == "open"\n'
    '                                 or row_matches_merge(n, merge_sha, root)):\n',
    '        if has_row(n, root):\n')],
 "M2 state==open clause dropped (control A perturbation)": [
   ('        if has_row(n, root) and (str(m.get("state") or "") == "open"\n'
    '                                 or row_matches_merge(n, merge_sha, root)):\n',
    '        if has_row(n, root) and row_matches_merge(n, merge_sha, root):\n')],
 "M3 _rewrite_granted -> return False (skip, never rewrite)": [
   ('    now = recorded_row_status(number, root)\n    want = line_status(line)\n',
    '    return False\n    now = recorded_row_status(number, root)\n    want = line_status(line)\n')],
 "M4 grant now/want boundary dropped": [
   ('    return (now is not None and want is not None and want[0] == "merged"\n'
    '            and now != want)',
    '    return (want is not None and want[0] == "merged" and now != want)')],
 "M4a grant direction dropped (want[0]==merged gone)": [
   ('return (now is not None and want is not None and want[0] == "merged"\n'
    '            and now != want)',
    'return (now is not None and want is not None and now != want)')],
 "M5 row_matches_merge ignores the sha": [
   ('    return status == "merged" and merge_sha.startswith(sha)',
    '    return status == "merged"')],
 "M6 one-line grant boundary dropped": [
   ('    if len(lines) != 1 or not rowed_line(number, lines[0]):',
    '    if not rowed_line(number, lines[0]):')],
 "M7 status regex loosened (facts inside the bold)": [
   (r'r"(?:,.*)?$")',
    r'r"(?:.*)?$")')],
 "M8 anchor key back to the entry number": [
   ('        number = int(m.group(1))',
    '        number = int(r.get("number") or 0)')],
 "M9 has_row dropped from the guard (control B perturbation)": [
   ('        if has_row(n, root) and (str(m.get("state") or "") == "open"',
    '        if (str(m.get("state") or "") == "open"')],
}

def run():
    p = subprocess.run([sys.executable,"-I",str(F),"--self-test"],
                       capture_output=True,text=True,cwd=str(WT))
    out = p.stdout + p.stderr
    fails = re.findall(r"^\s*(?:!!\s*)?FAIL[:\s]+(.*)$", out, re.M)
    m = re.search(r"(\d+)\s+self-test check\(s\) failed", out)
    n = int(m.group(1)) if m else 0
    return p.returncode, n, fails, out.strip().splitlines()[-1] if out.strip() else ""

rc0,n0,_,last = run()
print(f"BASELINE(unmutated) rc={rc0} failed={n0} :: {last}")
for name, subs in MUTS.items():
    F.write_text(ORIG)
    ok = True
    for old,new in subs:
        if old not in F.read_text():
            print(f"!! ANCHOR-MISS {name}: {old[:60]!r}"); ok=False; break
        F.write_text(F.read_text().replace(old,new,1))
    if not ok: continue
    rc,n,fails,last = run()
    print(f"{name:58} rc={rc} failed={n}")
    for f in fails[:12]: print("        FAIL:", f[:110])
F.write_text(ORIG)
rc,n,_,last = run()
print(f"RESTORED rc={rc} failed={n} :: {last}")
