#!/bin/bash
cd $HOME/wt; E=$HOME/w/ev
C1='PYTHONPATH=tests/hastub:custom_components:tests python3 tests/doc_claims.py'
C3='PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py'
C4='PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/rounds/round3/D5/option_doc_coverage.py'
A=docs/architecture.md
fin(){ git checkout -- . ; echo "status after $1: [$(git status --porcelain)]" >> $E/mut_status.txt; }
# M1
sed -i 's/^    if _hit:$/    if False:/' dev/audit/rounds/round4/D6/claims.py
$E/run.sh mut_M1_claims.txt "$C3"; fin M1
# M2
sed -i 's/pages_ok += 1/pages_ok += 0/' dev/audit/rounds/round3/D5/option_doc_coverage.py
$E/run.sh mut_M2_option.txt "$C4"; fin M2
# M3
sed -i '1295a _ABSENT_QUANTITIES = frozenset()' tests/doc_claims.py
$E/run.sh mut_M3_doc_claims.txt "$C1"; fin M3
# M4
sed -i 's/knows nothing about Home Assistant: fewer than half of the modules import the/knows nothing about Home Assistant: 105 modules, of which 36 import the/' $A
$E/run.sh mut_M4_doc_claims.txt "$C1"; $E/run.sh mut_M4_claims.txt "$C3"; fin M4
# M5
sed -i 's/^\(These modules import `homeassistant` at module level: `__init__`,\)/\1 `__init__`,/' $A
$E/run.sh mut_M5_claims.txt "$C3"; fin M5
# M6
sed -i 's/^\(These modules import `homeassistant` at module level: `__init__`,\)/\1 `nosuch_module`,/' $A
$E/run.sh mut_M6_claims.txt "$C3"; fin M6
# M8
sed -i 's/fewer than half of the modules import the/most modules import the/' $A
$E/run.sh mut_M8_doc_claims.txt "$C1"; $E/run.sh mut_M8_claims.txt "$C3"; fin M8
echo DONE >> $E/mut_status.txt
