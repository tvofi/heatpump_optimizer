#!/usr/bin/env python3
"""R10-SAV-COMFORT (#2492): drive tests/mutation_table.py's OWN operator mutants for named sites.

`r10_sav_comfort_mutants.py` beside this file holds hand-written mutants of the fix's predicates.
This one holds none of its own. It takes `file:line KIND` keys, exactly as `tools/pr/ci_predict.py`
prints them under `ADDED UNPINNED` (a `*N` suffix is dropped: every mutant of that operator on the
line is driven). For each key it keeps the mutants `mutation_table.candidates()` generates there.
So the mutant driven is the one CI's `mutation` job drives, and not a paraphrase of it. Each mutant
is applied to its own copy of <copy>, a `git ls-files` copy of the head. A NULL (unmutated) copy runs
in the same pool. Stage `section` runs tests/features.py's "3L-G7" section alone, taking the
SECTION text from `r10_sav_comfort_mutants.py`. Stage `full` runs all of tests/features.py. Read
a mutant as killed by `mutation_table.killed()`'s rule: a red run naming more failing checks than
the NULL's. An uncaught exception counts as one (`failing_count`), so a crash prints its stderr.

    PYTHONPATH=tests/hastub:tests:custom_components JOBS=4 \\
      python3 dev/audit/harnesses/r10_sav_comfort_opmutants.py <copy> section|full <key> [<key> ...]
"""
import concurrent.futures as cf
import os
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(sys.argv[1]).resolve()
STAGE = sys.argv[2]
KEYS = sys.argv[3:]
assert STAGE in ("section", "full"), STAGE
sys.path.insert(0, str(ROOT / "tests"))
import mutation_table as mt  # noqa: E402  (the copy's own operators)

_src = (ROOT / "dev/audit/harnesses/r10_sav_comfort_mutants.py").read_text()
_s = _src.index('SECTION = """') + len('SECTION = """')
SECTION = _src[_s:_src.index('"""', _s)].replace("\\\\", "\\")

want = set()
for k in KEYS:
    loc, kind = k.split(" ")
    f, ln = loc.rsplit(":", 1)
    want.add((f, int(ln), kind.split("*")[0]))
muts = [dict(m, file=f) for (f, ln, kind) in sorted(want)
        for m in mt.candidates(ROOT / f) if m["line"] == ln and m["kind"] == kind]
print(f"{len(muts)} mutants for {len(want)} keys", flush=True)


def run(job):
    i, m = job
    d = pathlib.Path(f"{ROOT}-m{i}")
    if d.exists():
        shutil.rmtree(d)
    shutil.copytree(ROOT, d, symlinks=True)
    try:
        if m["old"] is not None:
            p = d / m["file"]
            lines = p.read_text().splitlines(keepends=True)
            assert lines[m["line"] - 1].rstrip("\n") == m["old"], m
            lines[m["line"] - 1] = m["new"] + "\n"
            p.write_text("".join(lines))
        cmd = ([sys.executable, "-c", SECTION] if STAGE == "section"
               else [sys.executable, "tests/features.py"])
        out = subprocess.run(cmd, cwd=d, capture_output=True, text=True,
                             env={**os.environ, "PYTHONPATH": "tests/hastub:tests:custom_components"})
    finally:
        shutil.rmtree(d)
    fails = [l.strip()[:140] for l in out.stdout.splitlines() if l.strip().startswith("FAIL")]
    return m, out.returncode, fails, out.stderr[-300:]


null = dict(file="NULL", line=0, kind="NULL", old=None, new=None)
with cf.ThreadPoolExecutor(int(os.environ.get("JOBS", "3"))) as ex:
    for m, rc, fails, err in ex.map(run, [(0, null)] + list(enumerate(muts, 1))):
        print(f"{m['file']}:{m['line']} {m['kind']} new={m['new']!r}: rc={rc} failing={len(fails)}", flush=True)
        for l in fails:
            print("    " + l, flush=True)
        if rc and not fails:
            print("    stderr: " + err.replace("\n", " | "), flush=True)
