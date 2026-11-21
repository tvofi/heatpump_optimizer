#!/bin/bash
H=ef157f1551c0ec3981ad4286fd81f00ab00d3796
F=custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
for name in nosubgrid unmutated; do d=$HOME/b_$name; rm -rf $d; mkdir -p $d; git -C /home/user/heatpump_optimizer archive $H | tar -x -C $d
  [ $name = nosubgrid ] && python3 - "$d/$F" <<'PY'
import sys
p=sys.argv[1]; s=open(p).read(); a='display: grid; grid-template-rows: subgrid; row-gap: 0;'; assert s.count(a)==1; open(p,'w').write(s.replace(a,'display: block; row-gap: 0;'))
PY
  (cd $d && PYTHONPATH=tests/hastub python3 tests/plan_view.py >/dev/null 2>&1; node tests/card_browser.mjs > $HOME/ev/browser_$name.txt 2>&1; echo "browser $name rc=$?") | tee -a $HOME/ev/mutants_browser.txt
  grep -E 'tile and stat rows|FAILED|PASSED|misaligned' $HOME/ev/browser_$name.txt | head -8 >> $HOME/ev/mutants_browser.txt
done; echo DONE
