#!/bin/bash
# live.sh <checkout> <ack file>...: the two live boards of 2026-10-28 (boards/), each read one
# minute after its provenance time against one fresh state, with the session's own queue and
# seat ledger as the ack files; then the null control, every key acknowledged at the second board.
set -uo pipefail
W=$1; shift; T=$W/tools/audit/seat/owed_unactioned.py; B=$(cd "$(dirname "$0")" && pwd)/boards
S=$(mktemp -d); trap 'rm -rf "$S"' EXIT
A=(); for f in "$@"; do A+=(--acks "$f"); echo "ack file $(basename "$f"): $(grep -c 'OWED-ACK' "$f") OWED-ACK line(s)"; done
for b in tick-1904 tick-1912; do
  at=$(head -1 "$B/$b.txt" | sed -E 's/.*, ([0-9T:-]+)\..*/\1Z/')
  now=$(python3 -c "import datetime as d,sys;print((d.datetime.fromisoformat(sys.argv[1].replace('Z','+00:00'))+d.timedelta(minutes=1)).strftime('%Y-%m-%dT%H:%M:%SZ'))" "$at")
  echo "== $b at $now"; python3 -I "$T" --tick "$B/$b.txt" --state "$S/live.json" "${A[@]}" --now "$now" | cut -c1-160; echo "rc=${PIPESTATUS[0]}"
done
echo "== null control: tick-1912 again, every key acknowledged at $now"
python3 -I - "$T" "$B/tick-1912.txt" "$now" > "$S/acks.md" <<'PY'
import importlib.util, sys
s = importlib.util.spec_from_file_location("ou", sys.argv[1]); ou = importlib.util.module_from_spec(s); s.loader.exec_module(ou)
for k, v in ou.board(open(sys.argv[2]).read())[1].items():
    print(f"OWED-ACK {sys.argv[3]} {k} {(v['shas'] or ['-'])[0]} ttl=1 null control: named next action")
PY
python3 -I "$T" --tick "$B/tick-1912.txt" --state "$S/live.json" --acks "$S/acks.md" --now "$now" | head -1; echo "rc=${PIPESTATUS[0]}"
