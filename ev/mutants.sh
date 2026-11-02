#!/bin/bash
# Reviewer's mutants on card.py in ~/wt-mut; each applied, measured, restored.
cd ~/wt-mut
F=tools/audit/archscore/metrics/card.py
run() {
  echo "=== $1"
  PYTHONPATH=tests/hastub python3 ~/rv/run_crs.py ~/wt-mut 2>&1 | grep -E "FAIL|RESULT|RAISED"
  python3 tools/audit/archscore/calibrate.py --only rt_46_card_rule_respelled 2>&1 | grep -E "rt_46|MOVED|PASS|FAIL|exit" | head -4
  for p in finder3 null_unrelated null_distinct_rule null_identical_stmt null_comment null_docstring null_string; do python3 ~/rv/plant.py ~/wt-mut ~/wt-head $p; done
  python3 ~/card_measure.py ~/wt-mut ~/wt-head
}
run NULL-unmutated
sed -i '498s/owners\[key\].add(site)/pass  # MUTANT A/' $F; git diff --stat; run "MA drop the one-statement arm (owners[key].add(site) -> pass)"; git checkout -q -- $F
sed -i '464s/key.append(v)/key.append(" ".join(part[m:e]))  # MUTANT B/' $F; git diff --stat; run "MB exact text only (values kept as spelled, not numbered)"; git checkout -q -- $F
sed -i '466s/if len(key) < RULE_TOKENS or not content or not any(len(r) >= 2 for r in readers.values()):/if not key:  # MUTANT C1/' $F; git diff --stat; run "MC1 widen: any run of a chain is a rule (token, content, one-value predicates dropped)"; git checkout -q -- $F
sed -i '466s/if len(key) < RULE_TOKENS or not content or not any(len(r) >= 2 for r in readers.values()):/if not key:  # MUTANT C2/; 421s/len(operands) >= 2 and all(operands)/any(operands)/; 495s/range(a + 2,/range(a + 1,/' $F; git diff --stat; run "MC2 widen: any statement (a single operand) is a rule"; git checkout -q -- $F
git status --porcelain; echo "restored rc=$?"
