#!/usr/bin/env bash
# box D3-g05: after each gate record lands, write results/<key>.json and checkpoint once.
W=$HOME/audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1/wave/D3-g05
while true; do
  out=$(python3 /tmp/claude-0/-home-user-heatpump-optimizer/3447f893-53f4-5840-8607-7f6a1e09d573/scratchpad/build_results.py 2>&1)
  if [ -n "$out" ]; then echo "$out"; if echo "$out" | grep -q '^WROTE'; then bash $HOME/gate_wave.sh ckpt && echo "CKPT ok $(date -u +%FT%TZ)" || echo "CKPT FAILED"; fi; fi
  n=$(ls $W/results/*.json 2>/dev/null | wc -l)
  [ "$n" -ge 16 ] && { echo "ALL-RESULTS $n"; break; }
  sleep 60
done
