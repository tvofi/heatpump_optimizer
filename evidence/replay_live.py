"""Reviewer's own harness (not the fixer's): replay Train.main_green(--overlap)
and classify() on a LIVE check-runs snapshot taken while contexts were in flight,
no rewriting. argv: merge_train.py snapshot.json required.json"""
import importlib.util, json, sys, tempfile
from pathlib import Path
path, snap, reqf = sys.argv[1:4]
spec = importlib.util.spec_from_file_location("mt", path); mt = importlib.util.module_from_spec(spec); spec.loader.exec_module(mt)
runs = json.load(open(snap))["check_runs"]
req = sorted(set(json.load(open(reqf))) - set(mt.PR_ONLY))
body = "\n".join(json.dumps(c) for c in runs)
lines = []
with tempfile.TemporaryDirectory() as d:
    mt.Train("tvofi/heatpump_optimizer", Path(d), None, "", (), 1, run=lambda a, cwd=None, stdin=None: (0, body),
             sleep=lambda s: None, log=lines.append, overlap=True, base="batch/replay").main_green(
        "a"*40, req, "after #N's unproved merge: revert it first")
for l in lines: print("RESULT log:", l)
if not lines: print("RESULT log: (none)")
if hasattr(mt, "classify"):
    print("RESULT classify(main req):", mt.classify(mt.latest_runs(runs), req))
    print("RESULT classify(pr req):", mt.classify(mt.latest_runs(runs), sorted(json.load(open(reqf)))))
