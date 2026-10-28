#!/bin/bash
export PATH=/opt/hpo/venv-ci/bin:$PATH
H=39e5a3df4aa76b5d13099fe2ef20dcdbd66f2295; MB=b6f6ceca4f0323b24171c45a2a2372ba2e2cbaaa
R=/home/user/heatpump_optimizer
cd $R
echo "== diff of records"; git diff $MB...$H -- tests/structure_budgets.json tests/closures.json tests/entities.py dev/programme/delivery/2912.md
echo "== triage row"; cat /tmp/rv-head/tests/mutation_ledger/survivor_triage/config_flow.py/*421708f2~2.json
echo "== entities_errors full"; sed -n '/async def _entities_errors/,/^    async def _metering_errors/p' /tmp/rv-head/custom_components/heatpump_optimizer/config_flow.py
cd /tmp/rv-head
echo "== structure"; python3 tests/structure.py 2>&1 | tail -3; echo rc=$?
echo "== entities"; PYTHONPATH=tests/hastub python3 tests/entities.py 2>&1 | tail -2
echo "== archscore"; python3 tools/audit/archscore/score.py --diff $MB 2>&1 | grep -iE 'Architecture score|duplication' | head -5
echo "== when= lines"; grep -c 'when=' custom_components/heatpump_optimizer/config_flow.py
echo "== env_drift"; git -C /tmp/rv-head diff --quiet $MB -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt && echo claim files identical to base
echo "== golden drift"; GOLDEN_MODE=drift PYTHONPATH=tests/hastub python3 tests/golden.py 2>&1 | grep -E 'NO |UNCLAIMED|STALE|config_flow' | head -5
echo "== ci_predict"; python3 -I tools/pr/ci_predict.py --base origin/main 2>&1 | tail -5
echo "== closure select"; W=$(mktemp -d); python3 tests/closure.py select --diff $MB --workdir $W 2>&1 | grep -E 'MODE'
