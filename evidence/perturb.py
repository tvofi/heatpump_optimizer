"""Reviewer perturbation harness: does the arm's comparison actually carry each shape?
Run: PYTHONPATH=<head>/tests python3 perturb.py <head-root>
"""
import sys, pathlib, io, contextlib
HEAD = pathlib.Path(sys.argv[1]).resolve()
sys.path.insert(0, str(HEAD / "tests"))
import doc_claims as dc
from harness import Results

def run_check(corpus=None):
    dc.R = Results("probe")
    saved = dc.CORPUS
    if corpus is not None:
        dc.CORPUS = corpus
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            dc.check_prose_tree_counts()
    finally:
        dc.CORPUS = saved
    out = buf.getvalue()
    fails = [l for l in out.splitlines() if l.strip().startswith("FAIL")]
    return fails, out

def plant(doc, old, new):
    c = dict(dc.CORPUS); c[doc] = c[doc].replace(old, new, 1); return c

print("=== baseline (unmodified head corpus) ===")
f, o = run_check()
print("  FAILs:", f or "none")

print("=== plant stale options_pages in two docs ===")
c = plant("configuration.md", "the 23 options pages", "the 26 options pages")
c = plant2 = {**c, "setup.md": c["setup.md"].replace("the 23 options pages", "the 26 options pages", 1)}
f, o = run_check(plant2)
print("  FAILs:", f or "none")
for l in o.splitlines():
    if "documented=" in l: print("   ", l.strip())

print("=== M1: comparison neutralized (measured := stated) + same plant ===")
orig_census = dc.prose_count_census
def neutral(corpus, facts=None):
    rows, unread = orig_census(corpus, facts)
    return [r if r[4] == r[3] else (r[0], r[1], r[2], r[3], r[3]) for r in rows], unread
dc.prose_count_census = neutral
f, o = run_check(plant2)
print("  FAILs:", f or "none")

print("=== per-quantity neutralization: plant quantity X, keep X unfalsifiable ===")
QTYS = ["modules", "modules_importing_homeassistant", "modules_free_of_homeassistant",
        "services", "options_pages", "editable_options_pages", "fields_of_set_thermal_parameters"]
PLANTS = {
 "modules": ("architecture.md", "75 modules, of which", "99 modules, of which"),
 "modules_importing_homeassistant": ("architecture.md", "27 of the 75 modules", "28 of the 75 modules"),
 "modules_free_of_homeassistant": ("architecture.md", "The other 47 modules", "The other 48 modules"),
 "services": ("configuration.md", "13 services", "14 services"),
 "options_pages": ("configuration.md", "the 23 options pages", "the 26 options pages"),
 "editable_options_pages": ("README.md", "22 you can edit", "23 you can edit"),
 "fields_of_set_thermal_parameters": ("README.md", "all 31 fields", "all 32 fields"),
}
def neutral_for(target):
    def n(corpus, facts=None):
        rows, unread = orig_census(corpus, facts)
        return [r if r[2] != target else (r[0], r[1], r[2], r[3], r[3]) for r in rows], unread
    return n
for q in QTYS:
    doc, old, new = PLANTS[q]
    cp = plant(doc, old, new)
    # all comparisons live:
    dc.prose_count_census = orig_census
    f_live, _ = run_check(cp)
    live = bool([l for l in f_live if "tree-measurable set the reader corpus states" in l])
    # this shape's comparison disabled:
    dc.prose_count_census = neutral_for(q)
    f_off, _ = run_check(cp)
    off = bool([l for l in f_off if "tree-measurable set the reader corpus states" in l])
    print(f"  {q:34s} plant_live={'RED' if live else 'green'}  plant_shape_neutralized={'RED' if off else 'green'}")
dc.prose_count_census = orig_census
