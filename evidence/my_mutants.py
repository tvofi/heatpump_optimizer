"""Reviewer's own mutants (R10-REPLAY-REAL-DAY round 3) against tests/replay.py controls().
Usage: python3 my_mutants.py <worktree>. Each: copy tests/ + custom_components/ + tools/, one substitution, controls() in a fresh interpreter."""
import json, os, shutil, subprocess, sys, tempfile
from pathlib import Path
SRC = Path(sys.argv[1]).resolve()
DRV = "import json,sys;sys.path.insert(0,'tests');import replay;r=replay.controls();print('RED '+json.dumps([n for n,ok,_ in r if not ok]))"
M = [
 ("null", None, None),
 ("drop override arm", 'if not (o["active"] and o["override"] and floor_ok):', 'if not (o["active"] and floor_ok):'),
 ("drop floor arm", 'if not (o["active"] and o["override"] and floor_ok):', 'if not (o["active"] and o["override"]):'),
 ("recovering read as not recovering", 'floor_ok = o["recovery"] or (', 'floor_ok = False or ('),
 ("events arm off", 'for o in observations if events is not None else ():', 'for o in ():'),
 ("held ignores inactive", 'held = returns if active else None', 'held = returns'),
 ("setpoint exemption any config key", 'if any(config.get(k) is not None and _is(v, config[k]) for k in supplied):', 'if any(_is(v, x) for x in config.values() if isinstance(x, (int, float))):'),
 ("setpoint exemption drops value test", 'if any(config.get(k) is not None and _is(v, config[k]) for k in supplied):', 'if supplied:'),
]
for name, old, new in M:
    with tempfile.TemporaryDirectory() as td:
        for d in ("tests", "custom_components", "tools"):
            shutil.copytree(SRC / d, Path(td) / d, ignore=shutil.ignore_patterns("__pycache__"))
        f = Path(td) / "tests/replay.py"
        if old:
            s = f.read_text(); assert s.count(old) == 1, (name, s.count(old)); f.write_text(s.replace(old, new))
        p = subprocess.run([sys.executable, "-c", DRV], cwd=td, capture_output=True, text=True,
                           env={**os.environ, "PYTHONPATH": "tests/hastub", "OPENBLAS_NUM_THREADS": "1"})
        line = next((l for l in p.stdout.splitlines() if l.startswith("RED ")), None)
        red = json.loads(line[4:]) if line else ["no result " + p.stderr[-200:]]
        verdict = ("NULL-GREEN" if not red else "NULL-RED") if old is None else ("KILLED" if red else "SURVIVED")
        print(f"{verdict:10} {name}: red {red}")
