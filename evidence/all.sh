R=tvofi/heatpump_optimizer; W=/Users/timmalmstrom/hpo-seats/1857-review/wt; E=/Users/timmalmstrom/hpo-seats/1857-review/ev
export PATH=/Users/timmalmstrom/hpo-seats/bin:$PATH
ext(){ awk -v s="$2" 'NR>s && /##\[endgroup\]/ && !g {g=1; next} g && /##\[error\]|##\[group\]/ {exit} g' "$1" | sed -E 's/^[0-9T:.-]+Z //' | sed 's/\x1b\[[0-9;]*m//g'; }
for run in 37020572769 37019499517 37018136984 37007942153 37007613365; do
  d=$E/r$run; mkdir -p $d; cd $d
  sha=$(gh api repos/$R/actions/runs/$run --jq .head_sha)
  gh api repos/$R/actions/runs/$run/jobs?per_page=100 --jq '.jobs[]|select(.name=="closures" or .name=="closures-autofix")|"\(.name) \(.id) \(.conclusion)"' > jobs.txt
  cj=$(awk '$1=="closures"{print $2}' jobs.txt); aj=$(awk '$1=="closures-autofix"{print $2}' jobs.txt)
  gh api --allow-escape-sequences repos/$R/actions/jobs/$cj/logs > c.log; gh api --allow-escape-sequences repos/$R/actions/jobs/$aj/logs > a.log
  L=$(grep -n '##\[group\]Run # --partial' c.log | head -1 | cut -d: -f1); ext c.log $L > check.txt
  pin=$(grep -a 'PINNED: ' a.log | head -1 | sed 's/.*PINNED: //' | tr -d '\r\033'); real=$(grep -a 'AUTOFIX: ' a.log | grep -v print | sed 's/.*AUTOFIX: //' | head -1)
  art=$(gh api repos/$R/actions/runs/$run/artifacts --jq '.artifacts[]|select(.name=="closure-recordings")|.id')
  gh api repos/$R/actions/artifacts/$art/zip > rec.zip && rm -rf rec && mkdir rec && unzip -q rec.zip -d rec && rm rec.zip
  git -C $W cat-file -e "${sha}^{commit}" 2>/dev/null || git -C $W fetch -q origin $sha
  git -C $W show "${sha}:tests/closures.json" > closures.json
  git -C $W cat-file -e "${pin}^{commit}" 2>/dev/null || git -C $W fetch -q origin $pin
  mkdir -p p/tests pf/tests; git -C $W show "${pin}:tests/closure.py" > p/tests/closure.py; cp p/tests/closure.py pf/tests/; (cd pf && patch -s -p1 < $E/fix.patch)
  us=$(grep -c '^UNDER-SCOPED: ' check.txt)
  echo "RUN $run ${sha:0:8} pinned=${pin:0:8} ci_status=$real check_US_lines=$us"
  for T in p pf; do for C in check.txt -; do echo -n "  $T check=$C: "; (cd $W && PYTHONPATH=tests/hastub python3 $E/real.py $d/$T $d/rec $d/closures.json $([ $C = - ] && echo - || echo $d/check.txt) $W 2>&1 | tail -1); done; done
  rm -rf rec
done
