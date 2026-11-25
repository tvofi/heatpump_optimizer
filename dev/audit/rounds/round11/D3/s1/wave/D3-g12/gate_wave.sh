#!/usr/bin/env bash
# PROTOTYPE (out of tree, shipped on each dispatch/finder-r11-D3-g<NN> ref): the full-gate driver of
# one D3 u1 wave box. Owner ruling 2026-11-22: every u1 full-net survivor gets the full gate.
# It runs D3-top6's procedure (dev/audit/rounds/round11/D3/s1/fullgate.py: apply the one-line mutant,
# commit, take the gate_lock lease, GATE_SCOPE=full GOLDEN_MODE=drift GATE_JOBS=1 ./tests/run.sh,
# record, reset to the baseline) down this box's keys.tsv, one gate at a time.
#
#   gate_wave.sh null      the box's null control gate (once; restored from the checkpoint on a re-fire)
#   gate_wave.sh run       every key of keys.tsv not yet gated, in order; resumable; obeys STOP
#   gate_wave.sh ckpt      copy the box's wave dir (and REPORT.{json,md} once written) into the seat
#                          dir and checkpoint it through box_comms.sh
#   gate_wave.sh restore   on a re-fire: copy the checkpointed wave dir back into the tree
#   gate_wave.sh status    one line: gated / left / verdict counts
#
# Env (from $HOME/.boxcomms.env): BOX, ROUND. Paths: tree $HOME/audit-r11-D3-s1 (baseline worktree),
# its D3 dir S1, the box's wave dir $S1/wave/$BOX, the seat dir $HOME/d3wave-seat (what checkpoints).
# A gate is bounded at GATE_CAP seconds (default 14400): past it the gate gets SIGINT, fullgate.py's
# finally resets the tree and releases the lease, and the key is recorded TIMEOUT, never KILLED.
set -u
. "$HOME/.boxcomms.env"
export PATH="$HOME/venv-ci/bin:$PATH" PYTHONPATH=tests/hastub
BASE=92d38ecb640bd462f2e19c0814d0f0b7df1ee692
TR="$HOME/audit-r11-D3-s1"
S1="$TR/dev/audit/rounds/round11/D3/s1"
W="$S1/wave/$BOX"
SEAT="$HOME/d3wave-seat"
ST="$HOME/.boxcomms-r${ROUND}-${BOX}"
CAP="${GATE_CAP:-14400}"
hb() { bash "$HOME/box_comms.sh" heartbeat "$*" >/dev/null 2>&1 || echo "heartbeat failed: $*"; }

ckpt() {
  mkdir -p "$SEAT/wave/$BOX"
  cp -R "$W/." "$SEAT/wave/$BOX/"
  for f in REPORT.json REPORT.md; do [ -f "$W/$f" ] && cp "$W/$f" "$SEAT/$f"; done
  bash "$HOME/box_comms.sh" checkpoint D3-s1 "$SEAT" >/dev/null 2>&1 || echo "checkpoint failed"
}

clean_tree() { # the tree must be at the baseline with no staged or committed mutant
  local h; h=$(git -C "$TR" rev-parse HEAD)
  if [ "$h" != "$BASE" ]; then git -C "$TR" reset -q "$BASE"; echo "RESET HEAD $h -> baseline"; fi
  git -C "$TR" checkout -q "$BASE" -- custom_components/heatpump_optimizer
}

null_gate() {
  mkdir -p "$W/gates" "$S1/state/gates"
  if [ -f "$W/gates/null.json" ]; then cp "$W/gates/null.json" "$S1/state/gates/null.json"; echo "null: already taken"; return 0; fi
  # earlier boxes' gate records are evidence, not this box's null: set them aside once
  if [ ! -d "$S1/state/gates-prior" ]; then mv "$S1/state/gates" "$S1/state/gates-prior"; mkdir -p "$S1/state/gates"; fi
  clean_tree
  hb "null gate started"
  (cd "$TR" && timeout -s INT "$CAP" python3 "$S1/fullgate.py" null 2>&1 | grep -E 'RESULT|REFUSE|Error')
  clean_tree
  [ -f "$S1/state/gates/null.json" ] || { echo "NULL-MISSING"; return 1; }
  cp "$S1/state/gates/null."{json,log} "$W/gates/"
  ckpt; hb "null gate done: $(python3 -c "import json;d=json.load(open('$W/gates/null.json'));print('gate_rc',d['gate_rc'],'failed',d['failed_scripts'])")"
}

run_keys() {
  [ -f "$W/gates/null.json" ] || { echo "run: take the null first (gate_wave.sh null)"; return 1; }
  cp "$W/gates/null.json" "$S1/state/gates/null.json"
  local key src n=0 left
  while IFS=$'\t' read -r key src _rest; do
    case "$key" in ''|key) continue;; esac
    [ -f "$W/gates/$key.json" ] && continue
    while [ -f "$ST/stop" ]; do echo "STOPPED waiting"; hb "STOPPED before $key"; sleep 240; done
    clean_tree
    echo "START $key $(date -u +%FT%TZ)"; hb "gate started: $key"
    (cd "$TR" && timeout -s INT -k 300 "$CAP" python3 "$S1/fullgate.py" run --src "$src" --key "$key" 2>&1 | grep -E 'RESULT|VERDICT|REFUSE|Error')
    # a capped gate can leave run.sh's children (or a leaking mutant's solver workers) behind
    pkill -f 'tests/run.sh' 2>/dev/null; pkill -f 'process_worker.py' 2>/dev/null; true
    clean_tree
    if [ -f "$S1/state/gates/$key.json" ] && python3 -c "import json,sys;sys.exit(0 if 'verdict' in json.load(open('$S1/state/gates/$key.json')) else 1)"; then
      cp "$S1/state/gates/$key."{json,log} "$W/gates/"
    else
      python3 - "$W/gates/$key.json" "$key" "$src" "$CAP" <<'PY'
import json, sys
out, key, src, cap = sys.argv[1:]
json.dump({"key": key, "src": src, "verdict": "TIMEOUT", "cap_s": int(cap), "provisional": True,
           "note": "gate exceeded the box cap or ended without a record; never read as KILLED"}, open(out, "w"), indent=1)
PY
      [ -f "$S1/state/gates/$key.log" ] && cp "$S1/state/gates/$key.log" "$W/gates/"
    fi
    n=$((n+1)); ckpt
    left=$(status_line)
    hb "gate done: $key $(python3 -c "import json;print(json.load(open('$W/gates/$key.json'))['verdict'])") | $left"
  done < "$W/keys.tsv"
  echo "GATES-DONE $(status_line)"
}

status_line() {
  python3 - "$W" <<'PY'
import json, sys
from pathlib import Path
w = Path(sys.argv[1])
keys = [l.split("\t")[0] for l in (w / "keys.tsv").read_text().splitlines()[1:] if l.strip()]
v = {}
for k in keys:
    p = w / "gates" / f"{k}.json"
    if p.exists():
        r = json.loads(p.read_text()).get("verdict", "?")
        v[r] = v.get(r, 0) + 1
done = sum(v.values())
print(f"gated {done}/{len(keys)} left {len(keys) - done} " + " ".join(f"{k}={n}" for k, n in sorted(v.items())))
PY
}

restore() {
  local src="$ST/tree/seats/D3-s1/wave/$BOX"
  [ -d "$src" ] || { echo "restore: nothing checkpointed"; return 0; }
  mkdir -p "$W"; cp -R "$src/." "$W/"
  mkdir -p "$SEAT"; cp -R "$ST/tree/seats/D3-s1/." "$SEAT/"
  echo "restore: $(status_line)"
}

case "${1:-}" in
  null) null_gate;;
  run) run_keys;;
  ckpt) ckpt;;
  restore) restore;;
  status) status_line;;
  *) echo "usage: gate_wave.sh null|run|ckpt|restore|status" >&2; exit 2;;
esac
