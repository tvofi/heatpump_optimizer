"""Fix reviewer's (round 4, #2873) mutants -- reviewer-built. Driver: tests/debug_collect.py and tests/features.py over a copy of the head tree."""
import os, shutil, subprocess, sys
HEAD = sys.argv[1]; OUT = sys.argv[2]; name = sys.argv[3]
DG = "custom_components/heatpump_optimizer/diagnostics.py"; IN = "custom_components/heatpump_optimizer/inputs.py"
M = {"NULL": [],
 "N1_over_age_exception_off": [(DG, '        problem.get("problem") not in OUTRANKS_STALE\n        and', '        True\n        and')],
 "N1b_outranks_empty": [(IN, 'OUTRANKS_STALE: frozenset[str] = frozenset({"implausible"})', 'OUTRANKS_STALE: frozenset[str] = frozenset()')],
 "N4_reader_precedence_off": [(IN, '    if reading.problem is None or problem in OUTRANKS_STALE:', '    if reading.problem is None:')],
 "N5_reader_always_overwrites": [(IN, '    if reading.problem is None or problem in OUTRANKS_STALE:', '    if True:')],
 "N2_stale_never_promoted": [(DG, '    return {**entry, "problem": "stale"} if _over_age(entry) else entry', '    return entry')],
 "N3_age_not_rebased": [(DG, '    entry = {**problem, "age_minutes": aged(problem.get("age_minutes"))}', '    entry = {**problem}')],
}
d = os.path.join(OUT, name); shutil.rmtree(d, ignore_errors=True)
shutil.copytree(HEAD, d, ignore=shutil.ignore_patterns(".git", "node_modules"))
for f, old, new in M[name]:
    p = os.path.join(d, f); s = open(p).read(); assert s.count(old) == 1, (name, s.count(old)); open(p, "w").write(s.replace(old, new))
tests = sys.argv[4:] or ["tests/debug_collect.py"]
for t in tests:
    r = subprocess.run([sys.executable, t], cwd=d, env=dict(os.environ, PYTHONPATH="tests/hastub"), capture_output=True, text=True)
    out = r.stdout + r.stderr; open(os.path.join(OUT, f"{name}.{os.path.basename(t)}.log"), "w").write(out)
    fails = [l.strip() for l in out.splitlines() if l.strip().startswith("FAIL") and "a16:" not in l]
    last = out.strip().splitlines()[-1][:140] if out.strip() else ""
    print(f"RESULT {name} {t}: rc={r.returncode} FAIL(non-a16)={len(fails)} | {last}")
    for l in fails[:4]: print("   ", l[:220])
shutil.rmtree(d)
