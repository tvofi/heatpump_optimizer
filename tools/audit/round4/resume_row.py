#!/usr/bin/env python3
"""Rewrite one dimension's row in RESUME.md, and copy that finder's evidence in.

    python3 tools/audit/round4/resume_row.py D7 landed "3 findings: ..."

Exists so updating the resume state costs one command rather than an edit a
tiring session skips. Run from the branch checkout's root.
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

TREES = {"D0": "audit-r4-D0", "D3": "audit-r4-D3", "D9": "audit-r4-D9", "D11": "audit-r4-D11"}
SUBJECT = {
    "D0": "price optimality", "D1": "robustness and stability",
    "D2": "mathematical and physical sanity", "D3": "test-suite gaps", "D4": "UI/UX",
    "D5": "docs structure, flow, comments", "D6": "documentation claim verification",
    "D7": "architecture and maintainability", "D8": "sensor verification and ordering",
    "D9": "CPU and memory efficiency", "D10": "HA quality scale",
    "D11": "governance and policy", "D12": "generalization",
}

dim, status, note = sys.argv[1], sys.argv[2], sys.argv[3]
root = Path(__file__).resolve().parents[3]
worktrees = root.parent

src = worktrees / TREES.get(dim, "audit-r4-baseline") / "tools" / "audit" / "round4" / dim
dst = root / "tools" / "audit" / "round4" / dim
if src.is_dir():
    shutil.rmtree(dst, ignore_errors=True)
    shutil.copytree(src, dst)
    # REPORT.md is the basename COMMON.md prescribes, so a TRACKED one is a file
    # a policy document names with no cap, and policy_lint's `named-docs` refuses
    # it. #859 hit this with JUDGE.md and renamed rather than excluded, because a
    # basename collision a reader must resolve is a defect and not a note. The
    # landed archive therefore takes round 3's own layout, D<k>/reports/FINDER.md;
    # the finder's working tree keeps writing REPORT.md, which is untracked.
    report = dst / "REPORT.md"
    if report.exists():
        (dst / "reports").mkdir(exist_ok=True)
        report.rename(dst / "reports" / "FINDER.md")
        print(f"renamed REPORT.md -> {dim}/reports/FINDER.md (policy_lint named-docs)")
    n = sum(1 for _ in dst.rglob("*") if _.is_file())
    print(f"copied {n} file(s) from {src}")
else:
    print(f"no evidence tree at {src} -- row updated only")

resume = root / "tools" / "audit" / "round4" / "RESUME.md"
text = resume.read_text()
row = f"| {dim} | {SUBJECT[dim]} | {status} | {note} |"
new, count = re.subn(rf"^\| {dim} \|.*$", row.replace("\\", "\\\\"), text, count=1, flags=re.M)
if count != 1:
    sys.exit(f"refusing: matched {count} rows for {dim}, expected exactly 1")
resume.write_text(new)
print(f"RESULT resume_row_updated={dim} status={status}")
subprocess.run(["git", "add", "-A", "tools/audit/round4"], cwd=root, check=True)
