import os, re, shutil, subprocess, sys
S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEAD = os.path.join(S, "head"); BASE = os.path.join(S, "base")
PY = os.path.join(S, "venv/bin/python")
src = open(os.path.join(HEAD, "tests/features.py")).read().splitlines(keepends=True)
start = next(i for i, l in enumerate(src) if l.startswith("# --- R9 N-future-instant"))
end = next(i for i, l in enumerate(src) if l.startswith("# --- R9 N-plausibility (#1659)"))
hdr = next(i for i, l in enumerate(src) if l.startswith('R.section("Input staleness'))
tail = ["\nsys.exit(R.close(\"FEATURE CHECKS\"))\n"]
mini = "".join(src[:hdr] + src[start:end]) + "".join(tail)
open(os.path.join(S, "mut/tail.txt"), "w").write("".join(tail))
CC = "custom_components/heatpump_optimizer/"
MUTANTS = {
 "control": [],
 "M1 store report dropped": [(CC+"coordinator.py", '"last_tick" in self._energy_store.bounded', "False")],
 "M2 ahead ignored": [(CC+"coordinator.py", "if ahead or gap_minutes < 0.0:", "if gap_minutes < 0.0:")],
 "M3 raw arm dropped": [(CC+"coordinator.py", "if ahead or gap_minutes < 0.0:", "if ahead:")],
 "M4 hits.append -> pass": [(CC+"store.py", 'hits.append("/".join(map(str, path)))', "pass")],
 "M5 bounded never assigned": [(CC+"store.py", "self.bounded = hits\n", "pass\n")],
 "M6 bound off (identity)": [(CC+"store.py", "data = _bound_instants(data, bound, where, self._naive_zone, hits)", "pass")],
 "M7 tz coercion dropped": [(CC+"coordinator.py", "        last = last.replace(tzinfo=now.tzinfo)\n    gap_minutes = _utc_age_seconds(now, last) / 60.0\n    if ahead", "        pass\n    gap_minutes = _utc_age_seconds(now, last) / 60.0\n    if ahead")],
 "M8 path key wrong (child index)": [(CC+"store.py", "path + (k,)", "path")],
}
which = sys.argv[1:] or list(MUTANTS)
for name in which:
    if name == "base":
        tree = BASE
        muts = []
    else:
        tree = HEAD; muts = MUTANTS[name]
    work = os.path.join(S, "mut/tree"); shutil.rmtree(work, ignore_errors=True)
    shutil.copytree(os.path.join(tree, "custom_components"), os.path.join(work, "custom_components"))
    shutil.copytree(os.path.join(tree, "tests"), os.path.join(work, "tests"))
    for path, old, new in muts:
        p = os.path.join(work, path); t = open(p).read()
        assert t.count(old) == 1, (name, old, t.count(old))
        open(p, "w").write(t.replace(old, new))
    open(os.path.join(work, "tests/_fi_mini.py"), "w").write(mini)
    env = dict(os.environ, PYTHONPATH="tests/hastub", OPENBLAS_CORETYPE="Haswell")
    r = subprocess.run([PY, "tests/_fi_mini.py"], cwd=work, env=env, capture_output=True, text=True)
    out = r.stdout + r.stderr
    lines = [l for l in out.splitlines() if re.match(r"\s*(ok|FAIL|fail)\b", l) or "Traceback" in l or "Error" in l]
    print(f"RESULT {name}: rc={r.returncode}")
    for l in lines: print("   ", l[:230])
