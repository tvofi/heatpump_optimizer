import sys
sys.path.insert(0, "tests")
import comment_ratchet as c
orig = {k: getattr(c, k) for k in ("_split_trailing", "_is_heading", "_is_code", "_is_break", "_is_rule", "paragraphs")}
muts = {
  "split_trailing identity": ("_split_trailing", lambda path, src, line, kind, body: [body]),
  "is_heading False": ("_is_heading", lambda t: False),
  "is_code False": ("_is_code", lambda kind, line: False),
  "is_break blank-only": ("_is_break", lambda s: not s.strip()),
  "is_rule False": ("_is_rule", lambda t: False),
}
surv = 0
for name, (attr, fn) in muts.items():
    setattr(c, attr, fn)
    lines = []
    try:
        rc = c.self_test(lines.append)
    except Exception as e:
        rc, lines = 2, [f"CRASH {e!r}"]
    setattr(c, attr, orig[attr])
    fails = [l for l in lines if l.startswith(("FAIL ", "CRASH"))]
    killed = rc != 0
    surv += not killed
    print(("KILLED  " if killed else "SURVIVED"), name, "|", "; ".join(f for f in fails if "self-test" not in f)[:300])
print(f"RESULT reviewer_mutants={len(muts)} survived={surv}")
