"""Reviewer-owned driver (fix-review.md step 9: disclosed as mine, not the
finder's): calls mutation_table's own four source-only ledger validators."""
import sys
sys.path.insert(0, "tests")
import json
import mutation_table as mt
budgets = json.load(open(mt.BUDGETS))
probs = []
probs += mt.triage_problems(budgets.get("survivor_triage", {}))
probs += mt.ledger_form_problems(budgets)
probs += mt.layout_problems()
sites = mt.inventory()
probs += mt.completeness_problems(budgets, sites)
print(f"inventory sites: {len(sites)}")
print(f"unpinned: {len(mt.unpinned_sites(budgets, sites))}")
if probs:
    print("LEDGER VALIDATOR PROBLEMS:")
    for p in probs:
        print("  - " + p)
    sys.exit(1)
print("LEDGER VALIDATORS CLEAN (triage + form + layout + completeness)")
