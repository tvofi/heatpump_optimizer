#!/usr/bin/env bash
# run every probe sequentially, keep full output in probes/out/<key>.txt, print a one-line summary each
cd /root/audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1/wave/D3-g43/probes || exit 1
mkdir -p out
for f in probe_*.py; do
  k=${f#probe_}; k=${k%.py}
  python3 $f > out/$k.txt 2>&1
  echo "$k | $(grep -E 'scenarios=' out/$k.txt | head -1) | $(grep -E 'RESULT .*(max_abs_diff|scenarios_moved|parity_mutant|parity_baseline)' out/$k.txt | sed 's/RESULT //' | tr '\n' ' ')"
done
