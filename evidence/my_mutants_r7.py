"""Reviewer's own FAST-tier mutants for PR #3078 round 7 (reviewer-built; reuses the in-tree harness's fast()/apply())."""
import shutil, sys, tempfile
from pathlib import Path
sys.path.insert(0, "dev/audit/harnesses")
import r10_replay_real_day_mutants as h
E, L = "tools/replay/export.py", "tests/replay.py"
OPEN = '    print("reading the recorder", file=sys.stderr)\n'
M = [
 ("fixer's mutant: rec.label restored (f-string)", E, OPEN, '    print(f"reading the recorder {rec.label}", file=sys.stderr)\n'),
 ("rec.label by %-format", E, OPEN, '    print("reading the recorder %s" % rec.label, file=sys.stderr)\n'),
 ("rec.label as a second print argument", E, OPEN, '    print("reading the recorder", rec.label, file=sys.stderr)\n'),
 ("db interpolated by str.format", E, OPEN, '    print("reading the recorder {}".format(db), file=sys.stderr)\n'),
 ("db_url by concatenation", E, OPEN, '    print("reading the recorder " + str(db_url), file=sys.stderr)\n'),
 ("open line deleted", E, OPEN, '    pass\n'),
 ("AWAY_COVERED typo (round-4 finding 2)", L, 'AWAY_COVERED = frozenset({"owner-2026-10-30-away.json"})', 'AWAY_COVERED = frozenset({"owner-2026-10-30-awy.json"})'),
 ("non-sqlite refusal names the url (round-4 finding 3)", E, '            raise SystemExit("the recorder URL is neither SQLite nor "', '            raise SystemExit(f"the recorder {url} is neither SQLite nor "'),
]
with tempfile.TemporaryDirectory() as t:
    tree = Path(t)
    for n in h.COPIED:
        shutil.copytree(h.ROOT / n, tree / n, ignore=shutil.ignore_patterns("__pycache__"))
    print("NULL red", h.fast(tree))
    for name, rel, old, new in M:
        orig = h.apply(tree, rel, old, new)
        try:
            red = h.fast(tree)
        finally:
            (tree / rel).write_text(orig)
        print(("KILLED  " if red else "SURVIVED"), name, "red", red[:4])
