"""Reviewer's replay of the 15 committed killed_by pins: apply each mutant inside
its named function, run tests/debug_collect.py, restore. Plus a null (comment) control."""
import json, re, subprocess, sys, os
from pathlib import Path
wt = Path(sys.argv[1]); src = wt / "custom_components/heatpump_optimizer/debugger.py"
orig = src.read_text()
env = {**os.environ, "PYTHONPATH": "tests/hastub"}
def run():
    p = subprocess.run([sys.executable, "tests/debug_collect.py"], cwd=wt, env=env,
                       capture_output=True, text=True, timeout=300)
    fails = [l for l in p.stdout.splitlines() if l.strip().startswith("FAIL") and "a16:" not in l]
    return p.returncode, fails, (p.stdout + p.stderr).strip().splitlines()[-1:]
def func_span(lines, name):
    parts = name.split(".")
    i = 0; indent = -1
    for part in parts:
        pat = re.compile(rf"^(\s*)(async\s+)?(def|class)\s+{re.escape(part)}\b")
        for j in range(i, len(lines)):
            m = pat.match(lines[j])
            if m and len(m.group(1)) > indent:
                i, indent = j, len(m.group(1)); break
        else: raise SystemExit(f"no {part}")
    end = len(lines)
    for j in range(i + 1, len(lines)):
        s = lines[j]
        if s.strip() and (len(s) - len(s.lstrip())) <= indent and not s.lstrip().startswith(("#", ")", "]")):
            end = j; break
    return i, end
results = []
PINS = set(Path(x).name for x in sys.argv[2:])
try:
    rc, fails, tail = run(); print(f"RESULT null_unmutated rc={rc} fails={len(fails)}")
    lines = orig.splitlines(keepends=True)
    i, e = func_span(lines, "capped")
    lines.insert(i + 1, "    # reviewer null control\n"); src.write_text("".join(lines))
    rc, fails, tail = run(); print(f"RESULT null_comment rc={rc} fails={len(fails)}")
    src.write_text(orig)
    for f in sorted((wt / "tests/mutation_ledger/killed_by/debugger.py").glob("*.json")):
        d = json.loads(f.read_text())
        if f.name not in PINS: continue
        loc, kind, _h = d["anchor"].split(" ")
        func = loc.split(":", 1)[1]
        new = re.search(r"\(`(.*?)`\)", d["reason"]).group(1)
        lines = orig.splitlines(keepends=True); i, e = func_span(lines, func)
        hits = [k for k in range(i, e) if lines[k].rstrip("\n") == d["old"]]
        if len(hits) != 1:
            print(f"RESULT {f.name} UNLOCATED hits={len(hits)}"); continue
        k = hits[0]; ind = d["old"][: len(d["old"]) - len(d["old"].lstrip())]
        lines[k] = ind + new.strip() + "\n"; src.write_text("".join(lines))
        rc, fails, tail = run(); src.write_text(orig)
        print(f"RESULT {func} {kind} rc={rc} fails={len(fails)} killed={rc != 0} first={(fails or tail)[:1]}")
finally:
    src.write_text(orig)
