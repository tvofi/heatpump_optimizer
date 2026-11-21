#!/bin/bash
# mutant driver: copy head tree per mutant, apply single-site edit, run tests/card.mjs
H=ef157f1551c0ec3981ad4286fd81f00ab00d3796
F=custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
run() { name=$1; d=$HOME/m_$name; rm -rf $d; mkdir -p $d; git -C /home/user/heatpump_optimizer archive $H | tar -x -C $d
  [ -n "$2" ] && python3 - "$d/$F" "$2" "$3" <<'PY'
import sys
p,a,b=sys.argv[1:4]; s=open(p).read(); assert s.count(a)==1,(a,s.count(a)); open(p,'w').write(s.replace(a,b))
PY
  (cd $d && PYTHONPATH=tests/hastub python3 tests/plan_view.py > $HOME/ev/planview_$name.txt 2>&1; PYTHONPATH=tests/hastub node --max-old-space-size=6144 tests/card.mjs > $HOME/ev/card_$name.txt 2>&1; echo "$name rc=$? ok=$(grep -c '^ok' $HOME/ev/card_$name.txt) FAIL=$(grep -c 'FAIL' $HOME/ev/card_$name.txt)") | tee -a $HOME/ev/mutants_card_mjs.txt
  grep 'FAIL' $HOME/ev/card_$name.txt | head -5 >> $HOME/ev/mutants_card_mjs.txt
}


run typescaleconst '(px / DIALOG_FONT_PX_MIN).toFixed(4)' '"1.0000"'
echo DONE
