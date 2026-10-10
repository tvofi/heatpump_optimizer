import subprocess, sys, re
from pathlib import Path
WT = Path("/Users/timmalmstrom/hpo-seats/r9rev-2111/wt")
F = WT/"tools/audit/seat/record_row.py"
ORIG = F.read_text()
# correct loosening: allow extra content between the sha backtick and the closing **
M7_OLD = r'r"^- \[#\d+\]\([^()\s]*/pull/\d+\) — \*\*(open|merged `([0-9a-f]+)`)\*\*"'
M7_NEW = r'r"^- \[#\d+\]\([^()\s]*/pull/\d+\) — \*\*(open|merged `([0-9a-f]+)`[^*]*)\*\*"'
MUTS = {
 "M7 CORRECTED status regex loosened (facts inside the bold)": [(M7_OLD, M7_NEW)],
 "M4-B grant now/want boundary: want is not None dropped too": [
   ('    return (now is not None and want is not None and want[0] == "merged"\n'
    '            and now != want)',
    '    return (want[0] == "merged" and now != want)')],
}
def run():
    p = subprocess.run([sys.executable,"-I",str(F),"--self-test"],capture_output=True,text=True,cwd=str(WT))
    out=(p.stdout+p.stderr)
    m = re.search(r"(\d+) self-test check\(s\) failed:\s*(.*)", out)
    names = m.group(2) if m else ""
    return p.returncode,(int(m.group(1)) if m else 0),names
for name, subs in MUTS.items():
    F.write_text(ORIG); ok=True
    for old,new in subs:
        if old not in F.read_text(): print(f"!! ANCHOR-MISS {name}"); ok=False; break
        F.write_text(F.read_text().replace(old,new,1))
    if not ok: continue
    rc,n,names = run()
    print(f"{name}\n   rc={rc} failed={n}\n   arms: {names}")
F.write_text(ORIG)
print("RESTORED:", run())
