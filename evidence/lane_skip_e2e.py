"""Reviewer-built: does self_test_reads reach entities.py as lane_skip.py's host, end to end?"""
import sys, json, importlib.util
from pathlib import Path
root = Path(sys.argv[1]); spec = importlib.util.spec_from_file_location("cp", root / "tools/pr/ci_predict.py")
cp = importlib.util.module_from_spec(spec); sys.modules["cp"] = cp; spec.loader.exec_module(cp)
cl = json.loads((root / "tests/closures.json").read_text())
f = "tests/lane_skip.py"
print("RESULT hosts", cp.self_test_hosts(root, f, cl["closures"]))
print("RESULT has --self-test text:", "--self-test" in (root / f).read_text())
calls = []
def rec(r, ff, out): calls.append(ff); return "stub: not recorded"
notes = []
try:
    got = cp.self_test_reads(root, {f}, cl["closures"], cl.get("inert_reads", {}), None, record=rec, notes=notes)
except Exception as e:
    got = f"raised {type(e).__name__}: {e}"
print("RESULT self_test_reads reached the recorder for:", calls, "preds:", got, "notes:", notes)
