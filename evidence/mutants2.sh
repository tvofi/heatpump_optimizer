#!/bin/bash
cd ~/wt-mut
F=tools/audit/archscore/metrics/card.py
run() {
  echo "=== $1"; git diff -U0 | grep '^[+-] ' 
  PYTHONPATH=tests/hastub python3 ~/rv/run_crs.py ~/wt-mut 2>&1 | grep -E "FAIL|RESULT|RAISED"
  python3 tools/audit/archscore/calibrate.py --only rt_46_card_rule_respelled 2>&1 | grep -E "^rt_46"
  python3 ~/card_measure.py ~/wt-mut ~/wt-head
}
O='if len(key) < RULE_TOKENS or not content or not any(len(r) >= 2 for r in readers.values()):'
sed -i "466s/$O/if len(key) < RULE_TOKENS or not content:  # MUTANT C1a/" $F; run "MC1a drop the one-value (readers) predicate"; git checkout -q -- $F
sed -i "466s/$O/if not content or not any(len(r) >= 2 for r in readers.values()):  # MUTANT C1b/" $F; run "MC1b drop RULE_TOKENS"; git checkout -q -- $F
sed -i "466s/$O/if len(key) < RULE_TOKENS or not any(len(r) >= 2 for r in readers.values()):  # MUTANT C1c/" $F; run "MC1c drop the content predicate"; git checkout -q -- $F
sed -i '466s/if len(key) < RULE_TOKENS/if len(key) < 3/' $F; run "MC1d RULE_TOKENS 7 -> 3"; git checkout -q -- $F
git status --porcelain; echo "restored rc=$?"
