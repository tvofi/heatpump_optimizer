"""Reviewer's harness: the first post-merge push's grade under the tree's
PROBE_REFERENCE_S and under the fleet-implied one (22.23 for 3.14, 3.13 scaled
by the tree's own 3.13/3.14 ratio), the merge run being the newest real run
with every heavy job probed at P seconds. Equivalent probe under the tree's
constants: P * 17.50 / 22.23."""
exec(open("/root/h/sim.py").read().split("def g(w)")[0])
tree = dict(cr.PROBE_REFERENCE_S)
fleet = {"3.14": 22.23, "3.13": round(22.23 * tree["3.13"] / tree["3.14"], 2)}
for label, refs in (("tree", tree), ("fleet-implied", fleet)):
    cr.PROBE_REFERENCE_S.clear(); cr.PROBE_REFERENCE_S.update(refs)
    for p in (38, 40):
        print(f"{label} {refs}: first post-merge push, merge run probed {p} s on every heavy job: {cr.window_work_minutes([probed(runs[0], p, rid=1)] + runs[:15])}  (budget 21.983 + 1.3 = 23.283)")
cr.PROBE_REFERENCE_S.clear(); cr.PROBE_REFERENCE_S.update(tree)
