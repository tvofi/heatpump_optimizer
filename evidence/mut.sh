cd /Users/timmalmstrom/hpo-seats/1857-review/wt
export PATH=/Users/timmalmstrom/hpo-seats/bin:$PATH
run() { PYTHONPATH=tests/hastub:../pylib python3 tests/entities.py > ../ev/mut-$1.txt 2>&1; echo "rc=$?" >> ../ev/mut-$1.txt; echo "$1: $(git diff --numstat | tr '\n' ' ') -> $(grep -E 'ENTITY CHECKS' ../ev/mut-$1.txt | tail -1)"; grep '^FAIL' ../ev/mut-$1.txt | cut -c1-150; git checkout -q -- tests/closure.py .github/workflows/tests.yml; }
Y=.github/workflows/tests.yml
run H
python3 - <<'P'
from pathlib import Path; p=Path("tests/closure.py"); t=p.read_text()
o='        disagree = check_txt.is_file() and any('; assert t.count(o)==1
p.write_text(t.replace(o,'        disagree = False and any('))
P
run M1-guard
sed -i '' '1492s/^          set -o pipefail$/          true/' $Y; run M2a-thisstep-pipefail
sed -i '' -e '835s/^          set -o pipefail$/          true/' -e '954s/^          set -o pipefail$/          true/' $Y; run M2c-decoy-other-two
sed -i '' '1494s/ 2>&1 | tee "\$RUNNER_TEMP\/closures\/check.txt"$//' $Y; run M2b-scoped-arm-tee
sed -i '' '1492s/set -o pipefail/# set -o pipefail/' $Y; run M6-pipefail-commented
sed -i '' -e '1492d' $Y; sed -i '' '1496a\
          set -o pipefail
' $Y; sed -n 1488,1498p $Y; run M7-pipefail-after-fi
python3 - <<'P'
from pathlib import Path; p=Path("tests/closure.py"); t=p.read_text()
o='"changed", "skip-clean", "skip-not-allowed", "skip-not-under-scoped"),'; assert t.count(o)==1
p.write_text(t.replace(o,'"changed", "skip-clean", "skip-not-allowed", "skip-not-under-scoped", "skip-classifier-disagrees"),'))
P
run M3-quiet
python3 - <<'P'
from pathlib import Path; p=Path("tests/closure.py"); t=p.read_text()
o='l.startswith("UNDER-SCOPED: ")'; assert t.count(o)==1
p.write_text(t.replace(o,'"UNDER" in l'))
P
run M8-loose-predicate
git status --short
