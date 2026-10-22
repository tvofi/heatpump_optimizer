#!/bin/bash
# muts.sh: each mutant <name> <file> <python-replace old new> <self-test command>; restore after
cd "$1"; E=$2; export PREPR_SKIP_CLOSURES=1
mut() { local name=$1 f=$2 old=$3 new=$4; shift 4
  python3 - "$f" "$old" "$new" <<'PY' || { echo "MUTANT $name: anchor not found exactly once" | tee "$E/$name.txt"; return; }
import sys; f,o,n=sys.argv[1:]; s=open(f).read(); c=s.count(o)
assert c==1, c; open(f,"w").write(s.replace(o,n))
PY
  git diff > "$E/$name.diff"; s=$(date +%s)
  timeout 900 "$@" > "$E/$name.log" 2>&1; rc=$?
  echo "MUTANT $name rc=$rc secs=$(( $(date +%s)-s )) :: $(grep -E 'self-test: [0-9]+ checks' "$E/$name.log" | tr '\n' ' ') :: FAILS: $(grep -cE '^\s*FAIL' "$E/$name.log")" | tee "$E/$name.txt"
  grep -E '^\s*FAIL' "$E/$name.log" | head -8 >> "$E/$name.txt"
  git checkout -q -- .; test -z "$(git status --short)" || echo "DIRTY after $name"; }
mut M0 tools/audit/seat/pr_args.sh 'pr_exit_trap() {' 'pr_exit_trap() {' bash tools/audit/seat/pr_args.sh --self-test
mut A_apppush_trapcleanup tools/pr/app_push.sh $'\npr_exit_trap cleanup\n' $'\ntrap cleanup EXIT\n' bash tools/pr/app_push.sh --self-test
mut B_grace tools/audit/seat/pr_args.sh 'for p in "${PR_REAP_PIDS[@]}"; do pr_kill KILL "$p"; done  # mut:grace' ':  # mut:grace' bash tools/audit/seat/pr_args.sh --self-test
mut C_exitreap tools/audit/seat/pr_args.sh $'  trap "${first}"\'pr_reap; eval "${PR_AFTER_REAP:-:}"\' EXIT  # mut:exitreap' '  :  # mut:exitreap' bash tools/audit/seat/pr_args.sh --self-test
mut D_handoff_fg tools/audit/seat/handoff_push.sh '> "$B.push.log" 2>&1 &' '> "$B.push.log" 2>&1' bash tools/audit/seat/pr_args.sh --self-test
mut E_relay_trap tools/audit/seat/cloud_relay.sh '. "$HERE/pr_args.sh"; pr_exit_trap' '. "$HERE/pr_args.sh"' bash tools/audit/seat/cloud_relay.sh --self-test
mut F_train_kill tools/audit/seat/merge_train.py $'                p.terminate()' $'                p.kill()' python3 tools/audit/seat/merge_train.py --self-test
mut G_sigign tools/audit/seat/pr_args.sh "  trap '' TERM INT HUP  # mut:sigign" "  :  # mut:sigign" bash tools/audit/seat/pr_args.sh --self-test
mut H_remerge_fg tools/audit/seat/remerge_main.sh '> "$PL" 2>&1 &' '> "$PL" 2>&1' bash tools/audit/seat/pr_args.sh --self-test
mut I_update_reapspare tools/audit/seat/pr_args.sh '  PR_REAP_SPARE=$LKP' '  :' bash tools/audit/seat/pr_args.sh --self-test
echo ALLDONE
