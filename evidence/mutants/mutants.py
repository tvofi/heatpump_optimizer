"""Reviewer's mutants for #2873, driver tests/debug_collect.py over a copy of the head tree."""
import os, shutil, subprocess, sys
HEAD = os.path.expanduser("~/hpo-seats/r10s6/rev-prod-s8/2873"); OUT = sys.argv[1]; name = sys.argv[2]
DG = "custom_components/heatpump_optimizer/diagnostics.py"
M = {"NULL": (DG, None, None),
 "N1_implausible_relabelled": (DG, '        problem.get("problem") != "implausible"\n        and', '        True\n        and'),
 "N2_stale_never_promoted": (DG, '    return {**entry, "problem": "stale"} if _over_age(entry) else entry', '    return entry'),
 "N3_age_not_rebased": (DG, '    entry = {**problem, "age_minutes": aged(problem.get("age_minutes"))}', '    entry = {**problem}'),
}
f, old, new = M[name]
d = os.path.join(OUT, name); shutil.rmtree(d, ignore_errors=True)
shutil.copytree(HEAD, d, ignore=shutil.ignore_patterns(".git", "mutation_ledger", "node_modules"))
if old is not None:
    p = os.path.join(d, f); s = open(p).read(); assert s.count(old) == 1, (name, s.count(old)); open(p, "w").write(s.replace(old, new))
r = subprocess.run([sys.executable, "tests/debug_collect.py"], cwd=d, env=dict(os.environ, PYTHONPATH="tests/hastub"), capture_output=True, text=True)
out = r.stdout + r.stderr; open(os.path.join(OUT, name + ".log"), "w").write(out)
fails = [l.strip() for l in out.splitlines() if l.strip().startswith("FAIL")]
print(f"RESULT {name}: rc={r.returncode} FAIL={len(fails)} | {out.strip().splitlines()[-1][:120] if out.strip() else ''}")
for l in fails[:4]: print("   ", l[:200])
shutil.rmtree(d)
