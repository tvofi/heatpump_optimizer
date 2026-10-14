"""Reviewer's own runner: import the worktree's tests/replay.py and run tibber_price_checks."""
import sys, importlib.util
from pathlib import Path
wt = Path(sys.argv[1]).resolve()
sys.path[:0] = [str(wt / "tests"), str(wt / "tests" / "hastub")]
spec = importlib.util.spec_from_file_location("replay_t", wt / "tests" / "replay.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
bad = 0
for name, ok, detail in m.tibber_price_checks():
    bad += not ok
    print(f"RESULT {'ok  ' if ok else 'FAIL'} {name} :: {detail}")
print(f"RESULT failed={bad}")
sys.exit(1 if bad else 0)
