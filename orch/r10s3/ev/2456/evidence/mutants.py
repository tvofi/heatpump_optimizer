"""Reviewer's targeted mutants of tools/release/stamp.py at 8f3e72f4: each is applied to a
copy in place, then --self-test and the new entities block are run; the file is restored."""
import subprocess, sys, shutil
from pathlib import Path
P = Path("tools/release/stamp.py"); orig = P.read_text()
M = {
 "M1 no restore call": ("    text, _, _ = restore_suspended(text)\n", "    pass\n"),
 "M2 stale restored too (no live check)": ("        if name in live:\n            stale.append(name)\n            continue\n", ""),
 "M3 missing tail tolerated": ("        if not tail or tail.group(\"name\") != name:\n            raise ValueError(", "        if False:\n            raise ValueError("),
 "M4 two notes tolerated": ("        if name in restored or name in stale:\n            raise ValueError", "        if False:\n            raise ValueError"),
 "M5 tail name mismatch tolerated": ("if not tail or tail.group(\"name\") != name:", "if not tail:"),
 "M6 entry not verbatim (strip)": ("out.append(f\"# may-drift: {tail.group('entry')}\")", "out.append(f\"# may-drift: {tail.group('entry').split(' -- ')[0]} -- restored\")"),
 "M7 continuation dropped": ("        i += 2\n", "        i += 3\n"),
}
for k,(a,b) in M.items():
    assert orig.count(a)==1, k
    P.write_text(orig.replace(a,b))
    try:
        st = subprocess.run([sys.executable, str(P), "--self-test"], capture_output=True, text=True)
        fails = [l.strip() for l in st.stdout.splitlines() if l.strip().startswith("FAIL")]
        res = [l for l in st.stdout.splitlines() if l.startswith("RESULT")]
        cv = subprocess.run([sys.executable, "/tmp/seat/rev2456/ev/stcov_block.py", str(P)], capture_output=True, text=True, env={"PYTHONPATH":"tests/hastub","PATH":"/usr/bin:/bin"})
        print(f"== {k}\n  selftest: {res} rc={st.returncode}\n  fails: {fails}\n  stcov: {cv.stdout.strip()[:160]} {cv.stderr.strip()[-200:]}")
    finally:
        P.write_text(orig)
print("restored:", P.read_text()==orig)
