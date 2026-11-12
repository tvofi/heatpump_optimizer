"""Reviewer plants: append a reader to review_packet.py, run the barrier block alone, restore."""
import sys, types
from pathlib import Path
seat = Path("tools/audit/seat"); sys.path.insert(0, str(seat))
import merge_train as m
rp = seat / "review_packet.py"; orig = rp.read_text()
def block():
    failed = []
    m._gate_reader_barrier_self_test(lambda name, ok: None if ok else failed.append(name[:110]))
    return failed
print("NO PLANT failed =", block())
try:
    for sp in ("None, **kw", "(), **opts", "busy=None, **kw", "*rest, busy=None", "[x for x in r if 0]", "(not 1) and r",
               "r if f'' else ()", "frozenset()", "frozenset(r)"):
        rp.write_text(orig + f"\n\ndef _planted_reader(l, r, *rest, **kw):\n    opts = kw\n    return classify(l, r, {sp})\n" if "*rest" not in sp
                      else orig + f"\n\ndef _planted_reader(l, r, *rest, **kw):\n    return classify(l, {sp})\n")
        f = block()
        print(f"PLANT {sp!r:40} failed={len(f)} {f[:1]}")
finally:
    rp.write_text(orig)
