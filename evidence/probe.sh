#!/bin/bash
# Reviewer's probe (builder: fix-review seat, not the finder's): op_host_refusal at the head, verbatim,
# over a throwaway repo whose branch touches one given path; p2.log holds only a self-test REFUSE row.
set -u; here=$(cd "$(dirname "$0")" && pwd); . "$here/fn.sh"
run() { # <path the branch changes> -> HOST (left open) | HEAD (closed)
  local t; t=$(mktemp -d); git init -q -b main "$t/o"; cd "$t/o"
  mkdir -p tools/pr tools/policy; echo a > tools/pr/prepr.sh; echo a > tools/policy/policy_lint.mjs; echo a > README.md
  git add -A; git -c user.name=x -c user.email=x@x commit -qm base
  git clone -q "$t/o" "$t/wt" 2>/dev/null; cd "$t/wt"; git checkout -qb fix/r
  echo broken >> "$1"; git -c user.name=x -c user.email=x@x commit -qam "branch change to $1"
  WT=$t/wt; D=$t; printf '  ok       figures               fine\n  REFUSE   self-test             FAIL policy-rot row\napp_push: REFUSE: the body did not pass tools/pr/prepr.sh\n' > $D/p2.log
  if op_host_refusal; then r=HOST-left-open; else r=HEAD-closed; fi; echo "$1: $r"; cd /; rm -rf "$t"
}
for p in tools/pr/prepr.sh tools/policy/policy_lint.mjs README.md; do run $p; done
