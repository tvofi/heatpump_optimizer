#!/usr/bin/env bash
# Reviewer's instrument (builder: the fix reviewer, round 5), run in a scratch worktree at
# 822a3556df06781ed7a0a1e8cecd74be0a1ffd01. Re-records tests/doc_claims.py's closure under four trees.
set -u
cd "$1"
H=822a3556df06781ed7a0a1e8cecd74be0a1ffd01
run() { # label
  echo "=== $1"
  timeout 900 ./tests/derive_closures.sh --single tests/doc_claims.py > /tmp/rev_derive.$$ 2>&1; rc=$?
  tail -12 /tmp/rev_derive.$$ | cut -c1-400
  echo "RESULT $1 derive_rc=$rc closures_json_diff_vs_head=$(git diff $H -- tests/closures.json | grep -c '^[+-] ') has_line=$(grep -c 'instruments/cloud_dispatch.py.md' tests/closures.json)"
  git diff $H -- tests/closures.json | grep '^[+-] ' | cut -c1-200
  git checkout -q $H -- . 
}
run A_head
git checkout -q e1ab25dcff6b99e83d088bb6bcf3cedf187528f2 -- tests/closure.py tests/closures.json
run B_null_delta_reverted
sed -i '/"tools\/audit\/seat\/instruments\/cloud_dispatch.py.md",/d' tests/closure.py
run M1_inert_except_line_removed
sed -i '/"tools\/audit\/seat\/instruments\/cloud_dispatch.py.md",/d' tests/closures.json
run M2_closures_json_line_removed
# step 14: remove the mechanism -- the page's citation of the instrument page
sed -i 's#tools/audit/seat/instruments/cloud_dispatch.py.md#tools/audit/seat/cloud_dispatch.py#' dev/README.md
grep -c 'instruments/cloud_dispatch.py.md' dev/README.md
run M3_citation_removed_from_page
echo DONE
