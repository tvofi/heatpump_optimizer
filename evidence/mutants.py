"""Reviewer's targeted mutants of population_axes at the head; each applied to a copy, self-test run, restored."""
import subprocess, sys, pathlib, re
wt = pathlib.Path(sys.argv[1]); f = wt / "tools/audit/enumerate.py"; src = f.read_text()
M = [
 ("declared branch off", 'if n == "NO-READ" and name in declared:', 'if False:'),
 ("PAIRS raise deleted", '    totals["PAIRS"] += totals["LEVELS"] * sum(added) + (sum(added) ** 2 - sum(n * n for n in added)) // 2\n', ''),
 ("cross-declared term deleted", ' + (sum(added) ** 2 - sum(n * n for n in added)) // 2', ''),
 ("LEVELS raise deleted", '    totals["LEVELS"] += sum(added)\n', ''),
 ("raises swapped", '    totals["PAIRS"] += totals["LEVELS"] * sum(added) + (sum(added) ** 2 - sum(n * n for n in added)) // 2\n    totals["LEVELS"] += sum(added)\n',
                    '    totals["LEVELS"] += sum(added)\n    totals["PAIRS"] += totals["LEVELS"] * sum(added) + (sum(added) ** 2 - sum(n * n for n in added)) // 2\n'),
 ("R: added.append deleted", '            added.append(len(declared[name]))\n', ''),
 ("R: name-in-declared guard dropped", 'if n == "NO-READ" and name in declared:', 'if n == "NO-READ":'),
 ("R: cells are values not names", '[str(k) for k in a["levels"]]', '[str(k) for k in a["levels"].values()]'),
 ("R: cross term not halved", '- sum(n * n for n in added)) // 2', '- sum(n * n for n in added))'),
 ("R: cross term keeps same-axis pairs", '(sum(added) ** 2 - sum(n * n for n in added)) // 2', '(sum(added) ** 2) // 2'),
 ("R: an empty levels row counts as declared", 'for a in spec if a.get("levels")}', 'for a in spec if "levels" in a}'),
 ("R: only the first level kept", 'axes[name] = declared[name]\n', 'axes[name] = declared[name][:1]\n'),
]
surv = 0
for name, old, new in M:
    assert src.count(old) == 1, (name, src.count(old))
    f.write_text(src.replace(old, new))
    try:
        r = subprocess.run([sys.executable, "-I", "tools/audit/enumerate.py", "--self-test"], cwd=wt, capture_output=True, text=True)
    finally:
        f.write_text(src)
    out = (r.stdout + r.stderr)
    fails = re.findall(r"^\s*FAIL[: ]+(.*)$", out, re.M)
    last = out.strip().splitlines()[-1][:200] if out.strip() else ""
    verdict = "KILLED" if r.returncode != 0 else "SURVIVED"; surv += r.returncode == 0
    print(f"MUTANT {name}: {verdict} rc={r.returncode} fails={[x[:90] for x in fails][:6]} last={last!r}")
r = subprocess.run([sys.executable, "-I", "tools/audit/enumerate.py", "--self-test"], cwd=wt, capture_output=True, text=True)
print("RESTORED:", r.stdout.strip().splitlines()[-1], "rc", r.returncode)
print(f"RESULT reviewer-mutants total={len(M)} survived={surv}")
