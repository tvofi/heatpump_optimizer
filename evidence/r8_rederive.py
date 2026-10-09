"""Round-8 reviewer's own re-derive of the mutation ratchet and the delta's
effect, at head d1538a73b (round 7's head b511f9dc5 plus one bot "ci: pin
killed mutants" commit).

Calls tests/mutation_table.py's own functions -- the lane's, not mine -- for
every number it prints. Writes nothing. This is my instrument, disclosed per
fix-review.md step 9, built because the bot push left no committed harness of
its own for the reviewer to re-run.

usage (from a checkout at the head):
    python3 -I r8_rederive.py
"""
import sys
sys.path.insert(0, "tests")
sys.path.insert(0, "tests/hastub")
import mutation_table as mt  # noqa: E402

BASE = "b2b6acd64cde652676a568e93c05f021571ebe5e"
HEAD = "d1538a73bbd89e806f01af6c01fc72090304e4f6"

budgets = mt.load_budgets()
sites = mt.inventory()
unp = mt.unpinned_sites(budgets, sites)
base_sites = mt.base_unpinned_sites(BASE, sites)
sides = mt.diff_sides(BASE)
added = mt.added_unpinned(unp, base_sites or [], sides)
pool = mt.new_unpinned(unp, base_sites or [])

print(f"head              {HEAD}")
print(f"ratchet base      {BASE}")
print(f"candidate sites   {len(sites)}")
print(f"unpinned here     {len(unp)}")
print(f"unpinned at base  {len(base_sites) if base_sites is not None else 'UNREADABLE'}")
print(f"added by this diff {len(added)}")
print(f"pass pool (new_unpinned) {len(pool)}")
print(f"ratchet_refusal   {mt.ratchet_refusal(len(base_sites) if base_sites is not None else None, unp)}")
print(f"pin_shard_count   {mt.pin_shard_count(f'... {len(added)} of them added by this diff')}")
print(f"keys added_keys   {len(mt.added_keys(added))}")

print("\n-- validators, all must be [] --")
print("triage_problems:", mt.triage_problems(budgets.get("survivor_triage", {})))
print("ledger_form_problems:", mt.ledger_form_problems(budgets))
print("layout_problems:", mt.layout_problems())
print("completeness_problems:", mt.completeness_problems(budgets, sites))

ak = {mt.triage_key(s) for s in added}
pk = {mt.triage_key(s) for s in pool}
print(f"\nin pool not charged ({len(pk - ak)}): {sorted(pk - ak)}")
print(f"charged not in pool ({len(ak - pk)}): {sorted(ak - pk)}")
