"""Reviewer-built: host pairs under the base rule (self[-_]test word) vs the head rule, over tests/closures.json."""
import json, re, sys, importlib.util
from pathlib import Path
root = Path(sys.argv[1]); spec = importlib.util.spec_from_file_location("cph", sys.argv[2])
cp = importlib.util.module_from_spec(spec); sys.modules["cph"] = cp; spec.loader.exec_module(cp)
cl = json.loads((root / "tests/closures.json").read_text())["closures"]
files = sorted({f for v in cl.values() for f in v if f.endswith(".py") and (root / f).is_file()
                and (len(sys.argv) < 4 or "--self-test" in (root / f).read_text(errors="replace"))})
new = {(f, h) for f in files for h in cp.self_test_hosts(root, f, cl)}
cp._RUNS_SELF_TEST = re.compile(r"self[-_]test")
old = {(f, h) for f in files for h in cp.self_test_hosts(root, f, cl)}
print(f"RESULT candidates={len(files)} old_pairs={len(old)} new_pairs={len(new)} lost={len(old-new)} gained={len(new-old)}")
for f, h in sorted(old - new): print("LOST  ", f, "<-", h)
for f, h in sorted(new - old): print("GAINED", f, "<-", h)
for f, h in sorted(new): print("KEPT  ", f, "<-", h)
