#!/bin/bash
# VD3L AT HEAD: in the evidence tree (e3cb5c019b), apply each mutant on disk at its head line,
# run tests/guard_pins.py and tests/features.py (GATE_JOBS-free, sequential), record rc and the
# FAILED summary, restore the file with git checkout. Null: the unmutated tree once.
H=/home/user/audit-r11-verify-D3-late; O=$HOME/vout/D3-vlate/athead; mkdir -p $O; cd $H
P=custom_components/heatpump_optimizer
apply() { python3 - "$1" "$2" "$3" "$4" <<'PY'
import sys
f,l,old,new=sys.argv[1],int(sys.argv[2]),sys.argv[3],sys.argv[4]
L=open(f).read().split("\n")
assert L[l-1].strip()==old.strip(), (f,l,L[l-1])
ind=L[l-1][:len(L[l-1])-len(L[l-1].lstrip())]
L[l-1]=ind+new.strip(); open(f,"w").write("\n".join(L))
PY
}
one() { # id file line old new
  local id=$1 f=$P/$2
  [ -f $O/$id.done ] && return
  if [ "$id" != null ]; then apply $f $3 "$4" "$5" || { echo "$id APPLY-REFUSED" > $O/$id.sum; touch $O/$id.done; return; }; fi
  for s in guard_pins features; do
    PYTHONPATH=tests/hastub timeout 1500 python3 tests/$s.py > $O/$id.$s.out 2>&1; echo "$id $s rc=$? $(grep -E '[0-9]+ of [0-9]+ .*FAILED|passed' $O/$id.$s.out | tail -1)" >> $O/$id.sum
  done
  git checkout -q -- $P
  touch $O/$id.done
}
one null x 0 x x
one 02 tariff.py 744 "if x.size == 0 or k <= 0:" "if x.size == 0 or k < 0:"
one 62 grid_fee.py 173 "if not sep:" "if False:"
one 63 grid_fee.py 355 "if abs(rule.rate) > worst:" "if abs(rule.rate) >= worst:"
one 64 grid_fee.py 383 "if rule.rate < lowest:" "if rule.rate <= lowest:"
one 65 flow_lift.py 47 "FLOW_BIAS_ALPHA = 0.1" "FLOW_BIAS_ALPHA = 0.2"
one 66 flow_lift.py 188 "if self.samples < FLOW_BIAS_MIN_SAMPLES:" "if self.samples <= FLOW_BIAS_MIN_SAMPLES:"
one 67 thermal_model.py 169 "if not spec:" "if False:"
one 68 thermal_model.py 2618 ") / max(dt_hours, 1e-6)" ") / min(dt_hours, 1e-6)"
one 69 dhw_planner.py 1559 "shortfall_price = 1000.0 * (float(np.max(np.abs(prices))) + 1.0)" "shortfall_price = 1000.0 * (float(np.min(np.abs(prices))) + 1.0)"
one 70 coordinator.py 8774 "if tariff.enabled and factor > 0.0:" "if tariff.enabled or factor > 0.0:"
one 71 price_model.py 163 "if not np.all(np.isfinite(values)) or float(np.mean(values)) <= 1e-6:" "if not np.all(np.isfinite(values)) or float(np.mean(values)) < 1e-6:"
echo ATHEAD DONE > $O/ALL.done
