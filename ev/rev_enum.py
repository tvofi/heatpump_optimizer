import sys, ast
sys.path.insert(0, "tools/audit/seat")
import merge_train as m
def cnt(src): return m.blind_classify_readers(f"def f():\n    return {src}\n").get("f", 0)
groups = {
 "BINDING: busy is definitely blind, another candidate reads (expect counted=1)": [
  "classify(l, r, None, **kw)", "classify(l, r, (), **opts)", "classify(l, r, **kw, busy=None)",
  "classify(l, r, busy=(), **kw)", "classify(*a, busy=None)", "classify(l, *rest, busy=())",
  "classify(l, r, **{'busy': ()}, **kw)", "classify(l, r, frozenset(), **{k: b})",
  "classify(l, r, None, *rest)", "classify(l, r, (), required=q, **kw)",
  "classify(l, r, **{'busy': (), 'x': b})", "classify(l, r, **{'busy': (), k: b})"],
 "STEER: truth fixed by syntax, not folded (expect counted=1)": [
  "classify(l, r, [x for x in runs if 0])", "classify(l, r, [x for x in runs if ()])",
  "classify(l, r, {x for x in runs if None})", "classify(l, r, {x: 0 for x in runs if False})",
  "classify(l, r, (not 1) and b)", "classify(l, r, (not ()) or b)", "classify(l, r, b if not 1 else ())",
  "classify(l, r, () if not () else b)", "classify(l, r, f'' and b)", "classify(l, r, b if f'' else ())",
  "classify(l, r, (0 or 0) and b)", "classify(l, r, (1 and 1) or b)", "classify(l, r, b if (0 or ()) else None)",
  "classify(l, r, (() if c else ()) and b)", "classify(l, r, b if (() if c else 0) else ())",
  "classify(l, r, [x for e in [] or () for x in runs])", "classify(l, r, [b for e in (() or ())])",
  "classify(l, r, [b for e in [*()]])", "classify(l, r, (*(),) and b)", "classify(l, r, [*[]] and b)", "classify(l, r, {**{}} and b)"],
 "CONTROL blind (expect 1)": ["classify(l, r)", "classify(l, r, ())", "classify(l, r, () and b)", "classify(l, r, b if 0 else ())"],
 "CONTROL reads (expect 0)": ["classify(l, r, b)", "classify(l, r, busy=b, **kw)", "classify(l, r, b, **kw)", "classify(l, r, [x for x in runs if c])", "classify(l, r, [x for x in runs if 1])"],
}
for g, rows in groups.items():
    print("##", g)
    for s in rows:
        print(f"  counted={cnt(s)}  {s}")
