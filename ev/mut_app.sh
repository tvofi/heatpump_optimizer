#!/bin/bash
# mutant name, sed expr on tools/pr/app_push.sh; run self-test + planted harness; restore
cd /tmp/claude-0/rv/wt
run() { local n=$1 e=$2; cp tools/pr/app_push.sh /tmp/claude-0/rv/app.orig; sed -i "$e" tools/pr/app_push.sh
  if cmp -s tools/pr/app_push.sh /tmp/claude-0/rv/app.orig; then echo "$n: MUTANT DID NOT APPLY"; return; fi
  local st=$(bash tools/pr/app_push.sh --self-test 2>&1 | grep -E '^FAIL|self-test:' | tr '\n' ' ')
  local pl=$(bash ../harness/plant.sh tools/pr/app_push.sh 2>&1 | grep -c '^FAIL')
  cp /tmp/claude-0/rv/app.orig tools/pr/app_push.sh; echo "$n | selftest: $st | planted FAILs: $pl"; }
run M1-no-ancestor 's/git -C "\$wt" merge-base --is-ancestor "\$c" "\$RV_HEAD" 2>\/dev\/null \\/true \\/'
run M2-no-firstparent 's/rev-list --first-parent refs\/remotes\/origin\/main 2>\/dev\/null | grep -x "\$mb" >\/dev\/null \\/true \\/'
run M3-no-treediff 's/\[ -z "\$d" \] || {/true || {/'
run M4-no-commitcount 's/\[ "\$n" = 0 \] || {/true || {/'
run M5-many-trailers 's/grep -c .)" = 1 \]/grep -c .)" -ge 1 ]/'
run M6-reuse-skips-rowchecks 's/\[ "\$reused" = 0 \] || row_only_checks/true || row_only_checks/'
run M7-verdict-always 's/reuse_verdict "\$wt" "\$listing" "\$br" >\/dev\/null \&\& reused=1/reused=1/'
git status --short
