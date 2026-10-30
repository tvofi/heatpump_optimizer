import subprocess, sys
from pathlib import Path
wt = Path(sys.argv[1]); src = wt / "tools/audit/seat/merge_train.py"
MUT = [
    ("R1 merged/ran falls through to admit",
     '    return "merged by this train" if state == "merged" else "run by this train"\n',
     '    return None\n'),
    ("R2 BRANCH_POLICY_SAID never matches",
     're.compile(r"base branch policy prohibits the merge", re.I)',
     're.compile(r"NEVER-MATCHES-XYZ", re.I)'),
    ("R3 cure any skipped entry with a record, not only merged",
     '.get("state") == "merged"})', '.get("state") is not None})'),
    ("R4 ran is admitted, merged held",
     '"merged by this train" if state == "merged" else "run by this train"',
     '("merged by this train" if state == "merged" else None)'),
]
text = src.read_text()
for i, (name, old, new) in enumerate(MUT):
    n = text.count(old)
    if n != 1:
        print(name, "STALE", n); continue
    dst = src.parent / f"_rmut_{i}.py"
    dst.write_text(text.replace(old, new))
    try:
        r = subprocess.run([sys.executable, str(dst), "--self-test"], cwd=wt, capture_output=True, text=True, timeout=600)
    finally:
        dst.unlink()
    fails = [l for l in r.stdout.splitlines() if l.lstrip().startswith("FAIL")]
    print(name, "KILLED" if (fails or r.returncode) else "SURVIVED", f"rc={r.returncode}")
    for l in fails[:3]:
        print("   ", l[:200])
