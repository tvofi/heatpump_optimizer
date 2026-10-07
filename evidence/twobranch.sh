cd /Users/timmalmstrom/hpo-seats/review-2040/t
for pair in "a b" "a c" "a d" "d e" "a f"; do set -- $pair; git checkout -q -f $1; git merge --no-commit --no-ff $2 >$E/m-$1$2.out 2>$E/m-$1$2.err; rc=$?; echo "$1+$2 rc=$rc $(grep -o 'LEDGER-MERGE: [a-z]*' $E/m-$1$2.err|head -1) U=$(git diff --name-only --diff-filter=U|tr '\n' ,)"
 [ $rc -eq 0 ] && python3 -c "
import json;d=json.load(open('dev/audit/config/bugclasses.json'));print('  P1',d['P1']['total'],len(d['P1']['instances']),'P2',d['P2']['total'],len(d['P2']['instances']),'rca',[k for k in d['_rca']][-3:])"
 git merge --abort 2>/dev/null; git reset -q --hard; done
