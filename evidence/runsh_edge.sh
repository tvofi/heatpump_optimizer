cd "$1"
PYTHON=python3; JOBS=1; LANE=main; step=0; WAIT_UNRUN=""
WORKDIR=$(mktemp -d); export HPO_GATE_LOCK_DIR=$(mktemp -d)/lock
eval "$(sed -n '/^scope_script() {/,/^}/p' tests/run.sh)"
eval "$(sed -n '/^leased() {/,/^}/p' tests/run.sh)"
eval "$(sed -n '/^run_always() {/,/^}/p' tests/run.sh)"
sleep 300 & HOLD=$!
python3 tests/gate_lock.py take --label seat --owner-pid $HOLD >/dev/null 2>&1
python3 tests/gate_lock.py take --label w --owner-pid $HOLD > $WORKDIR/w.out 2>&1 &   # W queues behind the seat
sleep 2
export HPO_GATE_LOCK_LABEL=seat
fake=$(mktemp); printf 'print("RAN")\n' > $fake
run_always python3 "$fake" tests/stress.py
run_always python3 "$fake" tests/harness_headers.py
echo "--- manifest:"; cat $WORKDIR/main.manifest
kill $HOLD
