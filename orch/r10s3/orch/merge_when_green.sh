#!/bin/bash
# merge PR $1 at head $2 via REST once no check-run is in progress; give up after 90 min
for i in $(seq 1 36); do
  n=$(gh api repos/tvofi/heatpump_optimizer/commits/$2/check-runs --paginate -q '[.check_runs[]|select(.status!="completed")]|length' | paste -sd+ - | bc)
  if [ "$n" = "0" ]; then gh api -X PUT repos/tvofi/heatpump_optimizer/pulls/$1/merge -f sha=$2 -f merge_method=merge 2>&1 | head -2; exit 0; fi
  sleep 150
done; echo TIMEOUT
