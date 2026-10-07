"""Reviewer r9c-rev-2018's replay (own harness, not the RCA seat's e2e.py).
Before: artifact as CI wrote it. After: stress.py.json rc forced to 0 -- what the
countermeasure would yield ONLY IF every stress FAIL line is a timing_check verdict;
that precondition is checked against the head's timing_check call sites, read from source."""
import ast, json, shutil, subprocess, sys, tempfile
from pathlib import Path
head_src = Path(sys.argv[1]).read_text()
names = []
for n in ast.walk(ast.parse(head_src)):
    if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "timing_check" and n.args \
       and isinstance(n.args[0], ast.Constant) and n.args[0].value != "probe":
        names.append(n.args[0].value)
print(f"RESULT timing_check sites at head: {len(names)}")
sys.path.insert(0, "tests"); import closure
for art in map(Path, sys.argv[2:]):
    fails = [l[7:] for l in (art / "stress.py.out").read_text().splitlines() if l.startswith("  FAIL ")]
    other = [f for f in fails if not any(f.startswith(t) for t in names)]
    for arm in ("before", "after"):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td) / "rec"; shutil.copytree(art, d)
            if arm == "after":
                assert not other, other
                r = json.loads((d / "stress.py.json").read_text()); r["rc"] = 0
                (d / "stress.py.json").write_text(json.dumps(r))
            st = closure.apply_under_scoped_recordings(d, partial=False)
            dc = subprocess.run(["git", "diff", "-U0", "tests/closures.json"], capture_output=True, text=True).stdout
            qw = any("quiet_windows.py" in l and l.startswith("+") for l in dc.splitlines())
            subprocess.run(["git", "checkout", "-q", "tests/closures.json"])
            print(f"RESULT run={art.name} arm={arm} fails={len(fails)} non_timing={len(other)} status={st} adds_quiet_windows={qw}")
