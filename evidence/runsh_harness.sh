# $1 = tree, $2 = variant label
cd "$1"
PYTHON=python3; JOBS=${JOBS:-1}; LANE=main; step=0; WAIT_UNRUN=""
WORKDIR=$(mktemp -d); export HPO_GATE_LOCK_DIR=$(mktemp -d)/lock
eval "$(sed -n '/^scope_script() {/,/^}/p' tests/run.sh)"
eval "$(sed -n '/^leased() {/,/^}/p' tests/run.sh)"
eval "$(sed -n '/^run_always() {/,/^}/p' tests/run.sh)"
python3 tests/gate_lock.py take --label other-holder --owner-pid $$ >/dev/null 2>&1 || python3 tests/gate_lock.py take --label other-holder
fake=$(mktemp); printf 'print("STRESS RAN")\n' > $fake
# scope_script keys on a tests/*.py argument: pass it as a no-op extra arg
run_always python3 "$fake" tests/stress.py
echo "--- manifest:"; cat $WORKDIR/main.manifest
echo "--- held: $(python3 tests/gate_lock.py status 2>&1 | head -2)"
