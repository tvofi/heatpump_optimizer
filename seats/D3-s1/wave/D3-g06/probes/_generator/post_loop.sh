#!/usr/bin/env bash
# Step 3 driver: each gated key's record the moment its gate is recorded, then a checkpoint.
. "$HOME/.boxcomms.env"
W="$HOME/audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1/wave/$BOX"
SEAT="$HOME/d3wave-seat"
while true; do
  for g in "$W"/gates/*.json; do
    k=$(basename "$g" .json); [ "$k" = null ] && continue
    [ -f "$W/results/$k.json" ] && continue
    python3 -c "import json,sys;sys.exit(0 if 'verdict' in json.load(open('$g')) else 1)" 2>/dev/null || continue
    echo "POST $k $(date -u +%FT%TZ)"
    python3 "$HOME/probe-gen/build_result.py" "$k" 2>&1 | tail -3
    mkdir -p "$SEAT/wave/$BOX/probes" && cp "$HOME/probe-r11/dev/audit/rounds/round11/D3/s1/wave/$BOX/probes/"probe_*.py "$SEAT/wave/$BOX/probes/"
    echo "CKPT $k $(cd "$REPO" && bash "$HOME/gate_wave.sh" ckpt 2>&1 | tail -1)"
  done
  if grep -q GATES-DONE "$HOME/run.log" 2>/dev/null; then
    n=$(ls "$W"/results/*.json 2>/dev/null | wc -l); [ "$n" -ge 16 ] && { echo "POST-DONE $n"; exit 0; }
  fi
  sleep 60
done
