#!/bin/bash
# D3.M3 quiet-window gate for one mutant (or the baseline): commit the mutant in
# the seat worktree so HEAD moves off the baseline, take the gate lease, run
#   GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF=<baseline> GATE_JOBS=1 ./tests/run.sh
# record survived/killed, killing checks and load1, reset to the baseline and
# release. Usage: quiet_gate.sh <selector|BASELINE>. Never run beside U1 workers.
set -u
WT=/Users/timmalmstrom/hpo-orch/r10s6/r11/audit-r11-D3-s1
BASE=92d38ecb640bd462f2e19c0814d0f0b7df1ee692
P=$WT/dev/audit/rounds/round11/D3/s1
G=$P/state/gates
mkdir -p $G
SEL=$1
cd $WT || exit 2
export PYTHONPATH=tests/hastub
PY=/Users/timmalmstrom/.local/state/hpo/venv-ci/bin/python3
export PATH="$(dirname $PY):$PATH"
stamp() { date -u +%Y-%m-%dT%H:%M:%SZ; }
load1() { sysctl -n vm.loadavg | awk '{print $2}'; }
if pgrep -f "prescreen.py run" > /dev/null; then echo "REFUSE: U1 workers running"; exit 3; fi
[ "$(git rev-parse HEAD)" = "$BASE" ] || { echo "REFUSE: HEAD is not the baseline"; exit 3; }
git config user.name hpo-fixer; git config user.email 70032254+tvofi@users.noreply.github.com
if [ "$SEL" = BASELINE ]; then
  KEY=baseline; FILE=""
  git commit -q --allow-empty -m "D3-s1 quiet gate: baseline marker (no change)"
else
  out=$($PY $P/r2/mutant.py apply "$SEL" $WT) || exit 4
  KEY=$(echo "$out" | cut -f1); FILE=$(echo "$out" | cut -f2)
  git commit -q -m "D3-s1 quiet gate: mutant $KEY" -- "$FILE"
fi
L0=$(load1); T0=$(date +%s)
python3 tests/gate_lock.py take --label D3-s1-r11 --owner-pid $$ > $G/$KEY.lease 2>&1
export HPO_GATE_LOCK_LABEL=D3-s1-r11
GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF=$BASE GATE_JOBS=1 ./tests/run.sh > $G/$KEY.log 2>&1
rc=$?
T1=$(date +%s); L1=$(load1)
python3 tests/gate_lock.py release --label D3-s1-r11 >> $G/$KEY.lease 2>&1
git reset -q $BASE
[ -n "$FILE" ] && git checkout -q $BASE -- "$FILE"
failed=$(grep -E '^>>> (FAILED|ENDED BEFORE ITS SUMMARY):' $G/$KEY.log | sed -E 's/^>>> [A-Z ]+: //; s/ \(exit.*//' | tr '\n' ';')
mode=$(grep -m1 -E '^MODE:' $G/$KEY.log)
printf '%s\t%s\t%s\trc=%s\tfailed=%s\twall=%ss\tload1=%s..%s\t%s\n' "$(stamp)" "$KEY" "$SEL" "$rc" "${failed:--}" "$((T1-T0))" "$L0" "$L1" "$mode" >> $G/gates.tsv
echo "$(stamp) GATE $SEL key=$KEY rc=$rc failed=${failed:--} wall=$((T1-T0))s load1=$L0..$L1" >> $P/r2/PROGRESS.log
[ "$(git rev-parse HEAD)" = "$BASE" ] || echo "$(stamp) WARN HEAD not reset" >> $P/r2/PROGRESS.log
