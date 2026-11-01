"""R10-RCA-PREPR-HEAD-GRADERS: each mutant of the graders arm's predicates, run against
graders_self_test from a copy of tools/pr/; prints each mutant's failing checks.

    python3 -I dev/audit/rca/prepr-head-graders/mutants.py .
"""
import subprocess, sys, tempfile, shutil
from pathlib import Path
root = Path(sys.argv[1]).resolve(); src = (root / "tools/pr/ci_predict.py").read_text()
M = {
 "M1 restored_hit keys nothing": ("return sorted(p for p in names if p in at_tip and any(covers(s, p) for s in specs))", "return []"),
 "M2 restored_hit ignores the base tip": ("p in at_tip and any(covers(s, p)", "any(covers(s, p)"),
 "M3 grader_runs drops no exemption": ("not in GRADER_EXEMPT.keys() | AGREEMENT_RUNS]", "not in AGREEMENT_RUNS]"),
 "M4 predict's graders entry removed": ('        ("graders", lambda: grader_preds(root, base_ref)),\n', ""),
 "M5 ci_tree_run restores nothing": ('        run("git", "checkout", tip, f"--pathspec-from-file={tmp / \'pinned.list\'}", "--pathspec-file-nul")\n', ""),
}
for name, (a, b) in M.items():
    assert src.count(a) == 1, name
    d = Path(tempfile.mkdtemp()); shutil.copytree(root / "tools/pr", d / "pr")
    (d / "pr/ci_predict.py").write_text(src.replace(a, b))
    out = subprocess.run([sys.executable, "-I", "-c", f"import sys; sys.path.insert(0, {str(d/'pr')!r}); from pathlib import Path; import ci_predict as c; print('bad', c.graders_self_test(Path({str(root)!r})))"],
                         capture_output=True, text=True, cwd=root).stdout
    fails = [l.strip()[:110] for l in out.splitlines() if "FAIL" in l]
    print(f"{name}: {out.strip().splitlines()[-1] if out.strip() else 'no output'}; {len(fails)} FAIL")
    for f in fails: print("   ", f)
    shutil.rmtree(d)
