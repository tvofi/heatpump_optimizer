"""Reviewer's probe: the merge-base writer (pinned by closures-autofix via base.sha) on the head's canonical table."""
import sys, json, io, contextlib, tempfile, shutil
from pathlib import Path
sys.path.insert(0, "tests"); import closure as new
sys.path.insert(0, "/Users/timmalmstrom/hpo-seats/review-2057/probe/old"); import closure_old as old
td = Path(tempfile.mkdtemp()); out = td / "closures.json"; shutil.copy("tests/closures.json", out)
tbl = json.loads(out.read_text()); s = "tests/layout.py"
files = tbl["closures"][s]; secs = tbl["recorded"][s]["seconds"]
rec = td / "rec"; rec.mkdir()
(rec / "layout.py.json").write_text(json.dumps({"script": s, "rc": 0, "seconds": secs * 5, "files": files}))
with contextlib.redirect_stdout(io.StringIO()):
    rc = old.merge(rec, out, partial=True)
text = out.read_text(); d = json.loads(text)
canon = json.dumps(d, indent=1, sort_keys=True) + "\n"
diff_lines = sum(1 for a, b in zip(text.splitlines(), canon.splitlines()) if a != b)
print(f"RESULT old_writer_rc={rc} layout_errors={new.layout_errors(d)} text_is_canonical={text == canon} lines_differing_from_canonical={diff_lines}")
print("RESULT recorded entry as written:", json.dumps(d['recorded'][s]), "inner key order", list(d['recorded'][s]))
