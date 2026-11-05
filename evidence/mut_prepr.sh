#!/bin/bash
cd /tmp/claude-0/rv/wt2
run() { local n=$1 f=$2 e=$3; cp "$f" /tmp/claude-0/rv/mp.orig; sed -i "$e" "$f"
  if cmp -s "$f" /tmp/claude-0/rv/mp.orig; then echo "$n: MUTANT DID NOT APPLY"; return; fi
  local st=$(bash tools/pr/prepr.sh --self-test 2>&1 | grep -E '^ *FAIL|passed, .* failed' | tr '\n' ' ')
  cp /tmp/claude-0/rv/mp.orig "$f"; echo "$n | $st"; }
P=tools/pr/prepr.sh
#run P1-no-merged-steps $P 's/^merged_steps "\${1:-}" "\$UNPINNED_SITES"$/: merged_steps_dropped/'
#run P2-no-dirty-check $P 's/\[ -z "\$(git status --porcelain --untracked-files=no 2>\/dev\/null)" \] \\/true \\/'
run P3-no-early-rm $P 's/^  rm -f "\$(receipt_file)" 2>\/dev\/null$/  :/'
run P4-skipcode-writes $P 's/\[ "\$v" = PREPR_SKIP_CLOSURES \] || \[ -z "\${!v}" \]/[ "$v" = PREPR_SKIP_CLOSURES ] || [ "$v" = PREPR_SKIP_CODE ] || [ -z "${!v}" ]/'
run P5-no-rc-check $P 's/\[ "\$1" = 0 \] || { say skip "receipt" "rc=/true || { say skip "receipt" "rc=/'
run P6-trailer-any-sha tools/audit/seat/body_push.sh 's/\[ "\$s" = "\$2" \] \&\& \[/[ -n "$s" ] \&\& [/'
run P7-predict-not-merged $P 's/^  \[ -n "\${PREPR_SKIP_CODE:-}" \] || return 0$/  return 0/'
git status --short
