"""Run the RCA prototype's production-call capture against a tree root."""
import json, os, subprocess, sys
sys.path.insert(0, "/Users/timmalmstrom/r9-f2-solver/rca-stress")
import stress as rca  # module-level only; __main__-guarded

root, out, labels = sys.argv[1], sys.argv[2], sys.argv[3]
env = dict(os.environ)
env["PYTHONPATH"] = os.path.join(root, "tests", "hastub")
p = subprocess.run(
    [sys.executable, "-c", rca.CALLS_PROBE_DRIVER, root, out, labels],
    capture_output=True, text=True, env=env,
)
sys.stderr.write(p.stderr[-2000:])
sys.exit(p.returncode)
