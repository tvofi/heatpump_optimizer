"""Reviewer's own null sweep (local-reviewer-s10, #2910), run at the PR head tree.

Every tracked .py carrying --self-test that self_test_hosts gives at least one host is
treated as changed; the arm records it and grades it as each host's record. A healthy
tree (main + this PR, green on closures) must predict nothing. Prints RESULT lines.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

root = Path(sys.argv[1]).resolve()
sys.path[:0] = [str(root / "tools" / "pr"), str(root / "tests")]
import ci_predict as c  # noqa: E402
import closure  # noqa: E402

data = json.loads((root / "tests" / "closures.json").read_text())
closures, inert = data.get("closures", {}), data.get("inert_reads", {})
files = subprocess.run(["git", "ls-files", "*.py"], cwd=root, capture_output=True, text=True).stdout.split()
st = [f for f in files if "--self-test" in (root / f).read_text(errors="replace")]
hosted = {f: c.self_test_hosts(root, f, closures, inert) for f in st}
hosted = {f: h for f, h in hosted.items() if h}
print(f"RESULT self-testing={len(st)} hosted-files={len(hosted)} pairs={sum(map(len, hosted.values()))}")
for f, h in sorted(hosted.items()):
    print(f"PAIR {f} -> {', '.join(h)}")
tot = 0
for f in sorted(hosted):
    notes = []
    t = time.time()
    preds = c.self_test_reads(root, {f}, closures, inert, closure, notes=notes)
    dt = time.time() - t
    tot += len(preds)
    print(f"RESULT file={f} preds={len(preds)} notes={len(notes)} secs={dt:.1f}")
    for p in preds:
        print("  PRED", p[1])
    for n in notes:
        print("  NOTE", n)
print(f"RESULT total-preds={tot}")
