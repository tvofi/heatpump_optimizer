"""Reviewer's own harness (review-2061): replay added_unpinned old (merge base
4647321d) vs new (head cf84e0a4) over real merges on main, using each merge's
own inventory and base sites. Prints RESULT lines. Run from a checkout at C."""
import ast, os, sys, time
sys.path[:0] = ["tests", "tests/hastub"]
import mutation_table as m
def fn_src(path, name):
    src = open(path).read()
    for n in ast.parse(src).body:
        if isinstance(n, ast.FunctionDef) and n.name == name:
            return ast.get_source_segment(src, n)
OLD, NEW = sys.argv[1], sys.argv[2]
base = sys.argv[3]
ns_old, ns_new = dict(vars(m)), dict(vars(m))
exec(fn_src(OLD, "added_unpinned"), ns_old)
exec(fn_src(NEW, "added_unpinned"), ns_new)
t = time.time()
budgets = m.load_budgets(); sites = m.inventory()
unp = m.unpinned_sites(budgets, sites)
bs = m.base_unpinned_sites(base, sites)
if bs is None:
    print("RESULT base-unreadable"); sys.exit(0)
sides = m.diff_sides(base)
key = lambda s: (s["file"], s["line"], s["kind"])
o = sorted(map(key, ns_old["added_unpinned"](unp, bs, sides)))
n = sorted(map(key, ns_new["added_unpinned"](unp, bs, sides)))
print(f"RESULT unpinned={len(unp)} base={len(bs)} old_added={len(o)} new_added={len(n)} same={o==n} t={time.time()-t:.1f}s")
if o != n:
    print("  old-only", sorted(set(o)-set(n))); print("  new-only", sorted(set(n)-set(o)))
