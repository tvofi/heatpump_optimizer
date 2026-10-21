#!/bin/bash
source /etc/profile.d/hpo-toolchain.sh
W=$1; m=$2; cd $W/m/$m
case $m in
  MC*|MX6) PYTHONPATH=tests/hastub python3 tests/plan_view.py >/dev/null 2>&1; node tests/card.mjs > $W/ev/mut-$m.log 2>&1; rc=$?;;
  *) PYTHONPATH=tests/hastub python3 tests/features.py > $W/ev/mut-$m.log 2>&1; rc=$?;;
esac
echo "RESULT mutant=$m rc=$rc fails=$(grep -c '^ *FAIL' $W/ev/mut-$m.log)"
