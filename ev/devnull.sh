set -uo pipefail
gen(){ printf 'a/x\n'; i=0; while [ $i -lt 20000 ]; do printf 'handoff/f%d\n' $i; i=$((i+1)); done; }
gen | grep -vE '^handoff/' >/dev/null; echo "grep -v >/dev/null PIPESTATUS=${PIPESTATUS[*]}"
gen | grep -vE '^handoff/' >"$1"; echo "grep -v >file PIPESTATUS=${PIPESTATUS[*]}"
gen | grep -vqE '^handoff/'; echo "grep -vq PIPESTATUS=${PIPESTATUS[*]}"
