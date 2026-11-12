"""Reviewer's driver: _gate_reader_barrier_self_test alone, at the tree in argv[1]. Prints N checks, F failed."""
import sys
sys.path.insert(0, sys.argv[1] + "/tools/audit/seat")
import merge_train as m
res = []
m._gate_reader_barrier_self_test(lambda name, ok: res.append((name, bool(ok))))
bad = [n for n, ok in res if not ok]
print(f"barrier self-test: {len(res)} checks, {len(bad)} failed" + "".join("\n  FAIL " + n[:150] for n in bad))
