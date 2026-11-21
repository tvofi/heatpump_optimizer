#!/bin/bash
D=$HOME/audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1/state
end=$(date -j -u -f "%Y-%m-%dT%H:%M:%SZ" "2026-11-17T18:36:00Z" +%s)
while [ "$(ls $D/results/c2 | wc -l | tr -d ' ')" -lt 12 ] && [ "$(date +%s)" -lt "$end" ]; do sleep 20; done
ls $D/results/c2 | wc -l; date -u +%TZ
