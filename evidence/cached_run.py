"""Reviewer's driver (mine, not the fixer's): run tests/arch_score.py (or a mutant copy) with
calibrate.collect either recorded to a pickle (record) or replayed from it (replay)."""
import pickle, runpy, sys
from pathlib import Path
script, mode, pk = sys.argv[1], sys.argv[2], sys.argv[3]
sys.argv = [script]
root = Path("/Users/timmalmstrom/hpo-seats/1851-review/wt")
sys.path.insert(0, str(root / "tools/audit")); sys.path.insert(0, str(root / "tests"))
from archscore import calibrate
real = calibrate.collect
def rec(*a, **k):
    out = real(*a, **k); pickle.dump(out, open(pk, "wb")); return out
def rep(*a, **k):
    out = pickle.load(open(pk, "rb"))
    if mode == "replay-relabel":  # M4: rt_04h treated as an ordinary GAME (KNOWN_OPEN entry dropped)
        for c in out:
            if c.get("id") == "rt_04h_dup_assert_uncharged":
                c["label"] = "GAME"
    return out
calibrate.collect = rec if mode == "record" else rep
runpy.run_path(script, run_name="__main__")
