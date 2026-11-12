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
 "M4 predict's graders entry removed": ('        ("graders", lambda: grader_preds(root, base_ref, body, notes)),\n', ""),
 "M6 ci_tree_run reads governance.yml for every job": ("(r / (workflow or agreement_py.WORKFLOW))", "(r / agreement_py.WORKFLOW)"),
 "M7 the enumeration reads governance.yml only": ('for wf in sorted((root / WORKFLOWS).glob("*.y*ml")):', 'for wf in [root / WORKFLOWS / "governance.yml"]:'),
 "M5 ci_tree_run restores nothing": ('        run("git", "checkout", tip, f"--pathspec-from-file={tmp / \'pinned.list\'}", "--pathspec-file-nul")\n', ""),
 "R1-I the run regex drops bash/.sh": ('(?:node|python3(?: -I)?|bash)\\s+([\\w./-]+\\.(?:mjs|py|sh))', '(?:node|python3(?: -I)?)\\s+([\\w./-]+\\.(?:mjs|py))'),
 "R1-K the no-body skip is off": ("if PR_BODY in argv and body is None:", "if False:"),
 "R1-L event tokens unsubstituted": ("a = ctx.get(a, a)", "a = a"),
 "R1-O $INTENDED stood in empty": ('args += sorted(set(re.findall(r"\\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\\s*:?\\s+#(\\d+)", body or "", re.I)))', "pass"),
 "R1-P stdin redirect dropped": ("stdin = (tmp / Path(a).name).read_text()", "stdin = None"),
 "R1-E partial missing-input swallow deleted": ('if "reviews could not be read" in out.stdout:', "if False:"),
 "R1-H stdout redirect kept as arguments": ('rest = rest.split(">")[0]', "pass"),
 "R1-F collision key is the bare job": ('{j if names.count(j) == 1 else f"{Path(w).stem}/{j}": (w, j, t) for w, j, t in found}', "{j: (w, j, t) for w, j, t in found}"),
 "R1-N codescan_wait exemption deleted": ('GRADER_EXEMPT[("pr-contract", "codescan_wait.py", "--pr", "--base")] = "it queries the code-scanning API and grades no file"', "pass"),
 "R1-S summary always owes a repair": ('tail = ("repair before the handoff; " if boot < reds else "") + who', 'tail = "repair before the handoff; " + who'),
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
