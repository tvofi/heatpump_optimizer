"""Reviewer harness (NOT the fixer's): plant a +1 on every count the arm reads
and on each of the six unprotected instances, and report whether the arm flags it.
Run: PYTHONPATH=<head>/tests python3 plant.py <head-root>
"""
import sys, pathlib
HEAD = pathlib.Path(sys.argv[1]).resolve()
sys.path.insert(0, str(HEAD / "tests"))
sys.path.insert(0, str(HEAD / "custom_components" / ".."))
import doc_claims as dc

def rows_of(corpus, facts):
    r, _ = dc.prose_count_census(corpus, facts)
    return r  # (doc, line, quantity, stated, measured)

def flagged(corpus, facts):
    """Set of (doc, quantity) the arm reports FALSE."""
    return {(d, q) for (d, _l, q, s, m) in rows_of(corpus, facts) if m is not None and s != m}

def plant_by_span(corpus, doc, line, span_start, span_end, stated):
    """Replace the digits at [span_start,span_end) on `line` of `doc` with stated+1."""
    lines = corpus[doc].splitlines(keepends=True)
    ln = lines[line-1]
    lines[line-1] = ln[:span_start] + str(stated+1) + ln[span_end:]
    out = dict(corpus)
    out[doc] = "".join(lines)
    return out

def plant_text(corpus, doc, old, new, count=1):
    out = dict(corpus)
    assert old in out[doc], f"{old!r} not in {doc}"
    out[doc] = out[doc].replace(old, new, count)
    return out

facts = dc.tree_count_facts()
rows, unread = dc.prose_count_scan(dc.CORPUS, facts)

print("=== A. plant +1 at every count the arm already reads (shape coverage) ===")
covered_shapes = {}
for (doc, line, start, end, qty, stated, measured) in rows:
    if measured is None:
        continue
    pert = plant_by_span(dc.CORPUS, doc, line, start, end, stated)
    flg = flagged(pert, facts)
    ok = (doc, qty) in flg
    covered_shapes.setdefault(qty, []).append(ok)
    print(f"  {'FIRE' if ok else 'MISS'}  {doc}:{line} {qty} {stated}->{stated+1}")
print("  shapes with >=1 FIRE:", sorted({k for k,v in covered_shapes.items() if any(v)}))

print("\n=== B. the six unprotected instances from the LANE's own RCA (plant +1) ===")
CASES = [
    ("README.md", "all 31 fields", "all 32 fields", "fields_of_set_thermal_parameters"),
    ("configuration.md", "the 23 options pages", "the 24 options pages", "options_pages"),
    ("setup.md", "the 23 options pages", "the 24 options pages", "options_pages"),
    ("README.md", "22 you can edit", "23 you can edit", "editable_options_pages"),
    ("dashboard-card.md", "its five pages", "its six pages", "five_pages(WORD)"),
    ("ecl110.md", "All eight settings", "All nine settings", "eight_settings(WORD)"),
]
for doc, old, new, qty in CASES:
    pert = plant_text(dc.CORPUS, doc, old, new)
    flg = flagged(pert, facts)
    hit = [q for (d,q) in flg if d == doc] or ([q for (d,q) in flg])
    print(f"  {'READ ' if flg else 'BLIND'}  {doc}: {old!r} -> {new!r}  ({qty})  flagged={sorted(set(hit))}")
