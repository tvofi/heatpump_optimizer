#!/usr/bin/env bash
# Box D3-g23: write results/<key>.json (write_record.py) and checkpoint the moment each gates/<key>.json lands.
W="$(cd "$(dirname "$0")" && pwd)"; TR="$HOME/audit-r11-D3-s1"
export PATH="$HOME/venv-ci/bin:$PATH" PYTHONPATH=tests/hastub
while true; do
  for g in "$W"/gates/*.json; do
    k=$(basename "$g" .json); [ "$k" = null ] && continue
    [ -f "$W/results/$k.json" ] && continue
    (cd "$TR" && python3 "$W/write_record.py" "$k") >> "$W/autorecord.log" 2>&1 || echo "write_record failed: $k" >> "$W/autorecord.log"
    bash "$HOME/gate_wave.sh" ckpt >> "$W/autorecord.log" 2>&1
    echo "$(date -u +%FT%TZ) recorded+ckpt $k" >> "$W/autorecord.log"
  done
  grep -q "RUN-EXIT" "$HOME/gates.log" 2>/dev/null && [ "$(ls "$W"/results/*.json 2>/dev/null | wc -l)" -ge 16 ] && exit 0
  sleep 60
done
