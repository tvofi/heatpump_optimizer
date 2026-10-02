cd /Users/timmalmstrom/hpo-seats/1857-review/wt
export PATH=/Users/timmalmstrom/hpo-seats/bin:$PATH
mkdir -p ../ev2
run() { PYTHONPATH=tests/hastub:../pylib python3 tests/entities.py > ../ev2/mut-$1.txt 2>&1; echo "$1: $(git diff --numstat | tr '\n' ' ') -> $(grep -E 'ENTITY CHECKS' ../ev2/mut-$1.txt | tail -1)"; grep -E '^  FAIL (a pinned|and stays|the closures job tees|every status)' ../ev2/mut-$1.txt | cut -c1-140; git checkout -q -- tests/closure.py tests/entities.py .github/workflows/tests.yml; }
Y=.github/workflows/tests.yml
py() { python3 - "$@"; }
run H
py <<'P'
from pathlib import Path; p=Path("tests/closure.py"); t=p.read_text()
o='        disagree = check_txt.is_file() and any('; assert t.count(o)==1
p.write_text(t.replace(o,'        disagree = False and any('))
P
run M1-guard
py <<'P'
from pathlib import Path; p=Path("tests/closure.py"); t=p.read_text()
o='"changed", "skip-clean", "skip-not-allowed", "skip-not-under-scoped"),'; assert t.count(o)==1
p.write_text(t.replace(o,'"changed", "skip-clean", "skip-not-allowed", "skip-not-under-scoped", "skip-classifier-disagrees"),'))
P
run M3-quiet
py <<'P'
from pathlib import Path; p=Path("tests/closure.py"); t=p.read_text()
o='l.startswith("UNDER-SCOPED: ")'; assert t.count(o)==1
p.write_text(t.replace(o,'"UNDER" in l'))
P
run M8-loose-predicate
py <<'P'
from pathlib import Path; p=Path("tests/closure.py"); t=p.read_text()
o='        return "skip-classifier-disagrees" if disagree else "skip-not-under-scoped"'; assert t.count(o)==1
p.write_text(t.replace(o,'        return "skip-classifier-disagrees"'))
P
run M9-always-disagree
sed -i '' '1708s/^          set -o pipefail$/          true/' $Y; run M2a-thisstep-pipefail
sed -i '' -e '835s/^          set -o pipefail$/          true/' -e '954s/^          set -o pipefail$/          true/' -e '1007s/^          set -o pipefail$/          true/' $Y; run M2c-decoy-other-three
sed -i '' '1710s/ 2>&1 | tee "\$RUNNER_TEMP\/closures\/check.txt"$//' $Y; run M2b-scoped-arm-tee
sed -i '' '1708s/set -o pipefail/# set -o pipefail/' $Y; run M6-pipefail-commented
sed -i '' -e '1708d' $Y; sed -i '' '1712a\
          set -o pipefail
' $Y; run M7-pipefail-after-fi
sed -i '' -e '1708d' $Y; sed -i '' '1708a\
            set -o pipefail
' $Y; sed -n 1706,1712p $Y; run M10-pipefail-inside-then
py <<'P'
from pathlib import Path; p=Path("tests/entities.py"); t=p.read_text()
o=', inert={"DISCLAIMER.md"})'; assert t.count(o)==1
p.write_text(t.replace(o,')'))
P
run M11-fixture-without-inert
git status --short; echo ALLDONE
