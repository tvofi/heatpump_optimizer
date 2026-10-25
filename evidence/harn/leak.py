"""Reviewer's instrument: does a restored CONST mutant leak into the next run
on the same worker tree? Sequence exactly as null_drive.py's work_on: write the
mutant, run block_duty, write the original back, then run boost_drift_replay."""
import sys, time, os
from pathlib import Path
sys.path.insert(0, sys.argv[1] + "/tests")
import mutation_table as mt
rel = "custom_components/heatpump_optimizer/boost.py"
w = mt.clone_tree(Path(sys.argv[2]))
try:
    for drv in ("tests/boost_drift_replay.py",):
        a, e = mt.drive_spec(drv, "HEAD^1"); r = mt.run_script(drv, w, 3600, a, e)
        print("pre  unmutated", drv, r.rc, r.failed, flush=True)
    p = w / rel; orig = p.read_text()
    p.write_text(orig.replace("BLOCK_HOURS = 2\n", "BLOCK_HOURS = 4\n", 1))
    a, e = mt.drive_spec("tests/block_duty.py", "HEAD^1"); r = mt.run_script("tests/block_duty.py", w, 3600, a, e)
    print("mutant block_duty", r.rc, r.failed, f"{r.seconds:.1f}s", flush=True)
    p.write_text(orig)
    print("restored; source mtime_ns", p.stat().st_mtime_ns, "size", p.stat().st_size)
    pyc = list((p.parent / "__pycache__").glob("boost.*.pyc"))
    print("pyc", [(x.name, x.stat().st_mtime_ns) for x in pyc])
    import importlib.util, struct
    for x in pyc:
        b = x.read_bytes()[:16]; print("pyc header flags/mtime/size", struct.unpack("<4xIII", b))
    a, e = mt.drive_spec("tests/boost_drift_replay.py", "HEAD^1"); r = mt.run_script("tests/boost_drift_replay.py", w, 3600, a, e)
    print("post unmutated boost_drift_replay", r.rc, r.failed, [l.strip()[:100] for l in r.stdout.splitlines() if l.strip().startswith("FAIL")], flush=True)
finally:
    mt.drop_tree(w)
