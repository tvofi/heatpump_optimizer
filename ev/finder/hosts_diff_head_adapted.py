"""Reviewer harness: hosts self_test_hosts returns with the old vs new regex, over every tracked file at the head."""
import sys, json, re, subprocess, importlib.util
from pathlib import Path
WT = Path(sys.argv[1])
spec = importlib.util.spec_from_file_location("cp", WT / "tools/pr/ci_predict.py"); cp = importlib.util.module_from_spec(spec); spec.loader.exec_module(cp)
closures = json.loads((WT / "tests/closures.json").read_text())["closures"]
files = subprocess.run(["git", "ls-files", "tools", "tests", "dev/audit"], cwd=WT, capture_output=True, text=True).stdout.split()
files = [f for f in files if f.endswith((".py", ".sh", ".mjs"))]
new = {f: cp.self_test_hosts(WT, f, closures) for f in files}
orig = cp.re.search
def old(p, s, *a, **k):
    return orig(r"self[-_]test", s, *a, **k) if p == r"--self[-_]test" else orig(p, s, *a, **k)
cp.re.search = old; _keep = cp._RUNS_SELF_TEST; cp._RUNS_SELF_TEST = re.compile(r"self[-_]test")
oldh = {f: cp.self_test_hosts(WT, f, closures) for f in files}
cp.re.search = orig; cp._RUNS_SELF_TEST = _keep
lost = {f: sorted(set(oldh[f]) - set(new[f])) for f in files if set(oldh[f]) - set(new[f])}
gained = {f: sorted(set(new[f]) - set(oldh[f])) for f in files if set(new[f]) - set(oldh[f])}
print(f"RESULT files {len(files)} old-pairs {sum(map(len, oldh.values()))} new-pairs {sum(map(len, new.values()))}")
for f, hs in sorted(lost.items()): print(f"LOST {f} <- {hs}")
for f, hs in sorted(gained.items()): print(f"GAINED {f} <- {hs}")
