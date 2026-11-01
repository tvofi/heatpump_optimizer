"""Reviewer's own mutants, round 4 (R10-REPLAY-REAL-DAY #3078), FAST tier:
controls() + sanitiser_checks(committed fixtures) + synthetic_reproduces() in a fresh
interpreter on a copied tree, one exact substitution each. Usage: python3 my_mutants.py <worktree>"""
import json, os, shutil, subprocess, sys, tempfile
from pathlib import Path
SRC = Path(sys.argv[1]).resolve()
DRV = ("import json,sys;sys.path.insert(0,'tests');import replay;"
       "r=replay.controls()+replay.sanitiser_checks(sorted(replay.FIXTURES.glob('*.json')))+[replay.synthetic_reproduces()];"
       "print('RED '+json.dumps([n for n,ok,_ in r if not ok]))")
L, E = "tests/replay.py", "tools/replay/export.py"
M = [
 ("null", None, None, None),
 ("AWAY_COVERED names no committed fixture (typo)", L, 'AWAY_COVERED = frozenset({"owner-2026-10-30-away.json"})', 'AWAY_COVERED = frozenset({"owner-2026-10-30-awy.json"})'),
 ("coverage requires any event, not an active one", L, "    return [] if any(e[1] for e in events or ()) else [", "    return [] if any(True for e in events or ()) else ["),
 ("expect_commanded inverted", L, "    if expect_commanded:\n", "    if not expect_commanded:\n"),
 ("sanitiser coverage line always green", L, "not away_coverage_offenders(path.name, events),", "True,"),
 ("sqlite url label falls back to path", E, "label or f\"SQLite {db}\", qmark=True)", "f\"SQLite {db}\", qmark=True)"),
 ("mysql non-sqlite refusal names the url", E, 'raise SystemExit("the recorder URL is neither SQLite nor "', 'raise SystemExit(f"the recorder {url} is neither SQLite nor "'),
]
for name, f, old, new in M:
    with tempfile.TemporaryDirectory() as td:
        for d in ("tests", "custom_components", "tools"):
            shutil.copytree(SRC / d, Path(td) / d, ignore=shutil.ignore_patterns("__pycache__"))
        if old:
            p = Path(td) / f; s = p.read_text(); assert s.count(old) == 1, (name, s.count(old)); p.write_text(s.replace(old, new))
        pr = subprocess.run([sys.executable, "-c", DRV], cwd=td, capture_output=True, text=True,
                            env={**os.environ, "PYTHONPATH": "tests/hastub", "OPENBLAS_NUM_THREADS": "1", "HASTUB_TZ": "Europe/Stockholm"})
        line = next((l for l in pr.stdout.splitlines() if l.startswith("RED ")), None)
        red = json.loads(line[4:]) if line else ["no result " + pr.stderr[-300:]]
        v = ("NULL-GREEN" if not red else "NULL-RED") if old is None else ("KILLED" if red else "SURVIVED")
        print(f"{v:10} {name}: red {red}", flush=True)
