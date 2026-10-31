"""EG-B5 (#1743): the mutation ledger against the inventory and both ratchets, without driving a mutant.
    PYTHONPATH=tests/hastub python3 tools/audit/round9/EG-B5/ledger_check.py BASE
The last line before the refusal is the null control: the per-site match without #1748's move pairing.
"""
import sys
sys.path.insert(0, "tests")
import mutation_table as mt
base = sys.argv[1]
b = mt.load_budgets()
print("form/layout:", mt.ledger_form_problems(b) + mt.layout_problems())
sites = mt.inventory()
print("sites:", len(sites))
print("completeness:", mt.completeness_problems(b, sites))
unp = mt.unpinned_sites(b, sites)
rbase = mt.ratchet_base("changed", base)
bs = mt.base_unpinned_sites(rbase, sites)
print("unpinned here:", len(unp), "at base", rbase, ":", None if bs is None else len(bs))
sides = mt.diff_sides(rbase)
print("diff sides removed:", sorted(sides[0]), "added:", sorted(sides[1]))
added = mt.added_unpinned(unp, bs or [], sides)
print("added unpinned:", len(added))
for s in added: print("   ", mt.triage_key(s), s["old"].strip()[:70])
noside = mt.added_unpinned(unp, bs or [], (set(), set()))
print("null control -- same match without the #1748 move pairing:", len(noside))
print("ratchet_refusal:", mt.ratchet_refusal(None if bs is None else len(bs), unp))
