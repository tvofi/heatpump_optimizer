"""Reviewer's probe (#2057): does closure.check() refuse every text write_closures would not write?"""
import sys, json, io, contextlib, tempfile, subprocess
from pathlib import Path
sys.path.insert(0, "tests"); import closure
script = "tests/layout.py"
canon_tbl = {"_comment": closure.CLOSURES_COMMENT, "recorded": {script: {"rc": 0, "seconds": 1.0}},
             "closures": {script: [script]}, "inert_reads": {script: ["LICENSE", "VERSION"]}}
def run_check(text):
    with tempfile.TemporaryDirectory() as td:
        td = Path(td); fake = td / "c.json"; fake.write_text(text)
        rec = td / "rec"; rec.mkdir()
        (rec / "layout.py.json").write_text(json.dumps({"script": script, "rc": 0, "seconds": 1.0, "files": [script]}))
        orig = closure.CLOSURES; closure.CLOSURES = fake; buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                rc = closure.check(rec, partial=True)
        finally:
            closure.CLOSURES = orig
        return rc, buf.getvalue().strip().splitlines()[-1][:90]
canon_text = json.dumps(canon_tbl, indent=1, sort_keys=True) + "\n"
variants = {
  "canonical (null control)": canon_text,
  "inert list unsorted (the PR's own case)": json.dumps({**canon_tbl, "inert_reads": {script: ["VERSION", "LICENSE"]}}, indent=1, sort_keys=True) + "\n",
  "recorded entry keys seconds-before-rc (pre-PR writer's order)": json.dumps({"_comment": canon_tbl["_comment"], "closures": canon_tbl["closures"], "inert_reads": canon_tbl["inert_reads"], "recorded": {script: {"seconds": 1.0, "rc": 0}}}, indent=1) + "\n",
  "top-level keys unsorted": json.dumps({"recorded": canon_tbl["recorded"], "_comment": canon_tbl["_comment"], "closures": canon_tbl["closures"], "inert_reads": canon_tbl["inert_reads"]}, indent=1) + "\n",
  "indent=2": json.dumps(canon_tbl, indent=2, sort_keys=True) + "\n",
}
for name, text in variants.items():
    rc, last = run_check(text)
    print(f"RESULT variant={name!r} canonical_text={text == canon_text} layout_errors={closure.layout_errors(json.loads(text))} check_rc={rc} last={last!r}")
