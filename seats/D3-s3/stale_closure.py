#!/usr/bin/env python3
"""D3.M5: committed closure entries a fresh recording of the same tree does
not touch, kept by the never-shrink rule, and the scoped-gate runs they force.

Metric (one line): for each named gate script S, KEPT(S) = the files of the
seat's cells that tests/closures.json lists for S, that a fresh
`tests/closure.py record S` on this very tree does not record, and that
tests/closure.py:merge (`--partial`, the `--single` path) nevertheless keeps
in S's entry after folding that fresh record in -- via
closure._keep_committed_files ("Never shrink a committed closure -- except
past a file that is gone"). Count key: the entry merge() writes for S, read
back from the merged table -- never the committed list alone.
Each kept file F makes closure.select([F]) run S, which (fresh record)
neither imports nor opens F: forced seconds = recorded.seconds of S.

Hooks: tests/closure.py:merge, tests/closure.py:_keep_committed_files,
tests/closure.py:select (all driven in-process on a private copy of
closures.json; recordings by the production recorder `closure.py record`).
Command:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 \
          dev/audit/rounds/round11/D3/s3/stale_closure.py \
          [--rec-dir DIR] [--perturb-shrink] tests/optimality.py tests/edge.py ...
  (--rec-dir reuses recordings already taken there; omitted: a private
  temp dir under $TMPDIR, each script recorded once.)
Perturbation: --perturb-shrink patches closure._keep_committed_files to
return the fresh set (phantom handling unchanged): kept_pairs must fall to
0 and the forced seconds with it (direction: down). Null control: a script
whose fresh record equals its committed entry contributes 0 either way.
Expected: exact counts for this tree (a recording reads what the run
opened; deterministic suite); seconds are committed recorded values.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box B3, 4 vCPU
(strace present, the Linux recorder path).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import contextlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path.cwd()
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(HERE))
import closure  # noqa: E402
import enumerate as en  # noqa: E402


def main() -> int:
    argv = sys.argv[1:]
    perturb = "--perturb-shrink" in argv
    rec_dir = None
    if "--rec-dir" in argv:
        i = argv.index("--rec-dir")
        rec_dir = Path(argv[i + 1])
        del argv[i:i + 2]
    scripts = [a for a in argv if not a.startswith("--")]
    t_cpu0, t_thr0 = time.process_time(), time.thread_time()
    tmp = Path(tempfile.mkdtemp(prefix="d3s3-stale-"))
    rec_dir = rec_dir or (tmp / "rec")
    rec_dir.mkdir(parents=True, exist_ok=True)
    for s in scripts:
        if (rec_dir / (Path(s).name + ".json")).exists():
            continue
        p = subprocess.run([sys.executable, "tests/closure.py", "record", s,
                            "--out-dir", str(rec_dir)], cwd=ROOT,
                           capture_output=True, text=True,
                           env={**os.environ, "PYTHONPATH": "tests/hastub"})
        print(f"  recorded {s}: rc={p.returncode}")
    cells = en.cells()
    committed = json.loads(closure.CLOSURES.read_text())
    out = tmp / "closures.json"
    shutil.copy(closure.CLOSURES, out)
    in_dir = tmp / "in"
    in_dir.mkdir()
    fresh = {}
    for s in scripts:
        src = rec_dir / (Path(s).name + ".json")
        r = json.loads(src.read_text())
        if r["rc"] != 0:
            print(f"  {s}: recording rc={r['rc']}; left out")
            continue
        fresh[s] = set(r["files"])
        shutil.copy(src, in_dir / src.name)
    orig = closure._keep_committed_files
    if perturb:
        def shrink(name, old, new):
            orig(name, {f for f in old if not closure._is_real_file(f)}, new)
            return sorted(new)
        closure._keep_committed_files = shrink
    try:
        with contextlib.redirect_stderr(io.StringIO()) as err:
            rc = closure.merge(in_dir, out, allow_failures=False, partial=True)
    finally:
        closure._keep_committed_files = orig
    print(f"  merge rc={rc}")
    merged = json.loads(out.read_text())
    rec = committed["recorded"]
    pairs, secs = 0, 0.0
    per = []
    for s in sorted(fresh):
        cm = set(committed["closures"].get(s, ()))
        mg = set(merged["closures"].get(s, ()))
        kept = sorted(f for f in (mg - fresh[s]) if f in cells
                      and f.startswith("custom_components/"))
        stale_all = sorted(f for f in (cm - fresh[s])
                           if f.startswith("custom_components/"))
        # does select() actually run s on a change to each kept file?
        forced = []
        saved = closure.CLOSURES
        closure.CLOSURES = out
        try:
            for f in kept:
                if s in closure.select([f])["run"]:
                    forced.append(f)
        finally:
            closure.CLOSURES = saved
        sec = float(rec.get(s, {}).get("seconds", 0.0))
        pairs += len(forced)
        secs += sec * len(forced)
        per.append((s, len(forced), sec, forced, stale_all))
        print(f"RESULT kept[{s}]={len(forced)} files (cells; select runs it: "
              f"{len(forced)}; recorded {sec} s each) "
              f"{[f.rsplit('/', 1)[-1] for f in forced]}; "
              f"all-package stale: {[f.rsplit('/', 1)[-1] for f in stale_all]}")
    print(f"RESULT scripts_recorded={len(fresh)} count")
    print(f"RESULT kept_pairs={pairs} count")
    print(f"RESULT forced_seconds={secs:.0f} s (sum over kept pairs of the "
          f"script's recorded seconds: one body edit to each kept file)")
    print(f"RESULT perturbed={perturb}")
    pc, tc = time.process_time() - t_cpu0, time.thread_time() - t_thr0
    print(f"RESULT thread_factor={pc / tc if tc else 0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = sum(int(ln.split()[1]) for ln in open("/proc/vmstat")
                 if ln.startswith("pswpin"))
    except OSError:
        sw = -1
    print(f"RESULT swapins={sw}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
