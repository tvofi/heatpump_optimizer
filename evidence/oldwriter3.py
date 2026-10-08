"""Reviewer's probe, round 2: the pre-#2057 writer (closures-autofix pins base.sha) writes into this head's table;
does this head's check() refuse it, is the refusal an UNDER-SCOPED (which would re-trigger autofix), and does
`closure.py canonical` repair it with no entry changed?"""
import sys, json, io, contextlib, tempfile, shutil
from pathlib import Path
sys.path.insert(0, "tests"); import closure as new
import _rv2057_closure_old as old
td = Path(tempfile.mkdtemp()); out = td / "closures.json"; shutil.copy("tests/closures.json", out)
tbl = json.loads(out.read_text()); s = "tests/layout.py"; files = tbl["closures"][s]; secs = tbl["recorded"][s]["seconds"]
rec = td / "rec"; rec.mkdir()
(rec / "layout.py.json").write_text(json.dumps({"script": s, "rc": 0, "seconds": secs * 5, "files": files}))
with contextlib.redirect_stdout(io.StringIO()):
    rc_old = old.merge(rec, out, partial=True)
orig = new.CLOSURES; new.CLOSURES = out; buf = io.StringIO()
try:
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        rc = new.check(rec, partial=True)
finally:
    new.CLOSURES = orig
o = buf.getvalue()
before = json.loads(out.read_text())
with contextlib.redirect_stdout(io.StringIO()):
    new.canonical(out)
after_text = out.read_text()
print(f"RESULT old_writer_rc={rc_old} head_check_rc={rc} under_scoped_in_output={'UNDER-SCOPED' in o} names_remedy={'closure.py canonical' in o}")
print(f"RESULT canonical_repair: content_equal={json.loads(after_text)==before} layout_errors_after={new.layout_errors(json.loads(after_text), after_text)}")
print("RESULT check tail:", o.strip().splitlines()[-3:])
