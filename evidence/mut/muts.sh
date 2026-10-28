#!/bin/bash
# muts.sh: each mutant in a fresh detached worktree at the head; runs the named self-tests
W=$1; H=a01627177715d6f363eee2f8add5b19f7a97945d; R=/home/user/heatpump_optimizer
export PREPR_SKIP_CLOSURES=1
T=tools/audit/seat/train.sh; C=tools/audit/seat/cloud_relay.sh; P=tools/audit/seat/pr_args.sh
run() { # name file old new tests...
  local name=$1 f=$2 old=$3 new=$4; shift 4
  local d=$W/mwt/$name out=$W/ev/mut/$name.txt
  git -C $R worktree add -q --detach $d $H
  { echo "MUTANT $name in $f"; echo "  old: $old"; echo "  new: $new"; } > $out
  if [ "$name" != M0 ]; then python3 -I $W/tools/mut.py $d/$f "$old" "$new" >> $out 2>&1 || { echo "ANCHOR FAIL" >> $out; git -C $R worktree remove --force $d; return; }; fi
  git -C $d diff >> $out
  for t in "$@"; do
    case $t in
      train) c="bash $T --self-test" ;; relay) c="bash $C --self-test" ;; pa) c="bash $P --self-test" ;;
    esac
    echo "== $c" >> $out
    (cd $d && timeout 900 $c > $W/mwt/$name.$t.log 2>&1; echo "rc=$?" >> $W/mwt/$name.$t.log)
    grep -E 'FAIL|fail|refus|self-test:|rc=' $W/mwt/$name.$t.log | grep -v '^  ok' | tail -12 >> $out
  done
  git -C $R worktree remove --force $d
  echo "RESULT $name: $(grep -cE '^rc=0' $out) of $# self-tests rc 0" >> $out
}
run M0 $T x x train relay pa
run TR-TRAP $T $'PR_AFTER_REAP=\'rm -f "$pidfile"\'\npr_exit_trap\n' $'PR_AFTER_REAP=\'rm -f "$pidfile"\'\n\n' train
run TR-AFTER $T $'PR_AFTER_REAP=\'rm -f "$pidfile"\'\n' $'\n' train
run TR-LEAD $T $'PR_REAP_LEAD=$!\nrc=0; wait "$PR_REAP_LEAD" || rc=$?' $'LEADX=$!\nrc=0; wait "$LEADX" || rc=$?' train
run TR-FG $T $') >> "$log" 2>&1 &\n' $') >> "$log" 2>&1\n' train
run TR-EXEC $T '  exec python3 -u tools/audit/seat/merge_train.py batch' '  python3 -u tools/audit/seat/merge_train.py batch' train relay pa
run F-TR-RC $T 'rc=0; wait "$PR_REAP_LEAD" || rc=$?' 'rc=0; wait "$PR_REAP_LEAD" || :' train
run PA-LEAD $P $'  pr_lead_stop  # mut:lead\n' $'\n' train relay pa
run PA-LEADTERM $P $'  pr_kill TERM "$PR_REAP_LEAD"\n' $'\n' train relay pa
run PA-LEADWALK $P '*) return 0 ;; esac  # mut:leadwalk' '*) ;; esac  # mut:leadwalk' pa
run F-PA-TENTHS $P '"${PR_REAP_LEAD_TENTHS:-300}"' '"${PR_REAP_LEAD_TENTHS:-0}"' train relay pa
run CR-LEAD $C 'PR_REAP_LEAD=$!; wait "$PR_REAP_LEAD" || urc=$?' 'wait $! || urc=$?' relay
run F-CR-ELSEFG $C $'else bash "$HERE/update_pr.sh" "$br" "$hs" "$body" $iss >&2 & fi' $'else bash "$HERE/update_pr.sh" "$br" "$hs" "$body" $iss >&2; fi' relay pa
run F-CR-ELSELEAD $C $'else bash "$HERE/update_pr.sh" "$br" "$hs" "$body" $iss >&2 & fi\n    PR_REAP_LEAD=$!; wait "$PR_REAP_LEAD" || urc=$?' $'else bash "$HERE/update_pr.sh" "$br" "$hs" "$body" $iss >&2 & fi\n    if [ -n "${HPO_RELAY_UPDATE:-}" ]; then PR_REAP_LEAD=$!; fi; wait $! || urc=$?' relay
echo ALLDONE
