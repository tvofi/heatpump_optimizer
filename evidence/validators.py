import sys, json
sys.path.insert(0, "tests")
import mutation_table as mt
budgets = mt.load_budgets()
triage = budgets.get("survivor_triage", {})
sites = mt.inventory()
for name, probs in (
    ("completeness_problems", mt.completeness_problems(budgets, sites)),
    ("ledger_form_problems", mt.ledger_form_problems(budgets)),
    ("layout_problems", mt.layout_problems()),
    ("triage_problems", mt.triage_problems(triage)),
):
    print(f"{name}: {len(probs)} problem(s)")
    for p in probs[:10]:
        print(f"    - {p}")
print(f"inventory sites: {len(sites)}")
