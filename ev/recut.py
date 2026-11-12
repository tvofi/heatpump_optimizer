"""Feasibility of the binding half of the re-cut: every candidate must be READS. In memory, nothing written."""
import sys, types
from pathlib import Path
seat = Path("tools/audit/seat"); sys.path.insert(0, str(seat))
p = seat / "merge_train.py"; src = p.read_text()
old = "return READS not in got or REFUSED in got"
assert src.count(old) == 1
mod = types.ModuleType("mt_recut"); mod.__file__ = str(p); sys.modules["mt_recut"] = mod
exec(compile(src.replace(old, "return got != {READS}"), str(p), "exec"), mod.__dict__)
failed = []
mod._gate_reader_barrier_self_test(lambda n, ok: None if ok else failed.append(n[:160]))
print("barrier block under `return got != {READS}`: failed =", len(failed)); [print("  ", f) for f in failed]
c = lambda s: mod.blind_classify_readers(f"def f():\n    return {s}\n").get("f", 0)
for s in ("classify(l, r, None, **kw)", "classify(l, r, (), **opts)", "classify(l, r, busy=(), **kw)", "classify(*a, busy=None)",
          "classify(l, *rest, busy=())", "classify(l, r, **{'busy': ()}, **kw)", "classify(l, r, **{'busy': (), k: b})",
          "classify(l, r, b, **kw)", "classify(l, r, busy=b, **kw)", "classify(*a)", "classify(l, r, **kw)", "classify(l, r, *rest, **kw)"):
    print(f"  counted={c(s)}  {s}")
