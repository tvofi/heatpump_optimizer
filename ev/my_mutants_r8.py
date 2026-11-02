"""Reviewer-built FAST-tier mutants (round 8), reusing the in-tree harness's fast() and apply()."""
import shutil, sys, tempfile
from pathlib import Path
sys.path.insert(0, "dev/audit/harnesses")
import r10_replay_real_day_mutants as h
E = h.EXPORT
MY = '        print(f"reading the recorder: {MYSQL_LABEL}", file=sys.stderr)\n'
SQ = '        label = SQLITE_URL_LABEL\n        print(f"reading the recorder: {SQLITE_URL_LABEL}", file=sys.stderr)\n'
DB = '        print(f"reading the recorder: SQLite database {db}", file=sys.stderr)\n'
DF = '    else:\n        print(f"reading the recorder: {SQLITE_URL_LABEL}", file=sys.stderr)\n'
ONLY = sys.argv[1:]
M = [
 ("mysql: url by f-string", MY, '        print(f"reading the recorder: {MYSQL_LABEL} {url}", file=sys.stderr)\n'),
 ("mysql: url by %-format", MY, '        print("reading the recorder: %s %s" % (MYSQL_LABEL, url), file=sys.stderr)\n'),
 ("mysql: url by str.format", MY, '        print("reading the recorder: {} {}".format(MYSQL_LABEL, url), file=sys.stderr)\n'),
 ("mysql: url by concatenation", MY, '        print("reading the recorder: " + MYSQL_LABEL + " " + url, file=sys.stderr)\n'),
 ("mysql: url as second print arg", MY, '        print(f"reading the recorder: {MYSQL_LABEL}", url, file=sys.stderr)\n'),
 ("mysql: password only", MY, '        print(f"reading the recorder: {MYSQL_LABEL} {urlsplit(url).password}", file=sys.stderr)\n'),
 ("mysql: line constant again", MY, '        print("reading the recorder", file=sys.stderr)\n'),
 ("mysql: line deleted", MY, ''),
 ("sqlite url: url by f-string", SQ, '        label = SQLITE_URL_LABEL\n        print(f"reading the recorder: {SQLITE_URL_LABEL} {url}", file=sys.stderr)\n'),
 ("sqlite url: db path by concat", SQ, '        label = SQLITE_URL_LABEL\n        print("reading the recorder: " + SQLITE_URL_LABEL + " " + str(db), file=sys.stderr)\n'),
 ("sqlite url: line constant again", SQ, '        label = SQLITE_URL_LABEL\n        print("reading the recorder", file=sys.stderr)\n'),
 ("sqlite url: line deleted", SQ, '        label = SQLITE_URL_LABEL\n'),
 ("--db: line constant again", DB, '        print("reading the recorder", file=sys.stderr)\n'),
 ("--db: kind dropped", DB, '        print(f"reading the recorder: {db}", file=sys.stderr)\n'),
 ("default: line constant again", DF, '    else:\n        print("reading the recorder", file=sys.stderr)\n'),
 ("default: line deleted", DF, '    else:\n        pass\n'),
 ("default: says MySQL", DF, '    else:\n        print(f"reading the recorder: {MYSQL_LABEL}", file=sys.stderr)\n'),
 ("rec.label restored at build_export", '    rec = open_recorder(config_dir, db, db_url)\n', '    rec = open_recorder(config_dir, db, db_url)\n    print(f"reading the recorder {rec.label}", file=sys.stderr)\n'),
 ("AWAY_COVERED misspelt (r4 f2)", None, None),
 ("unsupported-scheme echoes url (r4 f3)", '            raise SystemExit("the recorder URL is neither SQLite nor "', '            raise SystemExit(f"the recorder {url} is neither SQLite nor "'),
]
with tempfile.TemporaryDirectory() as tmp:
    tree = Path(tmp)
    for n in h.COPIED:
        shutil.copytree(h.ROOT / n, tree / n, ignore=shutil.ignore_patterns("__pycache__"))
    print("NULL red", h.fast(tree))
    for name, old, new in M:
        if ONLY and not any(o in name for o in ONLY): continue
        rel = E
        if old is None:
            rel, old, new = h.LANE, 'AWAY_COVERED = frozenset({"owner-2026-10-30-away.json"})', 'AWAY_COVERED = frozenset({"owner-2026-10-30-awy.json"})'
        orig = h.apply(tree, rel, old, new)
        try:
            red = h.fast(tree)
        finally:
            (tree / rel).write_text(orig)
        print(("KILLED" if red else "SURVIVED"), name, red)
