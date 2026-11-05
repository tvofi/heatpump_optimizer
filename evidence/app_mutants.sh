#!/bin/bash
# Reviewer's mutants on tools/pr/app_push.sh's reuse path; each run against the
# file's own self-test AND the reviewer's planted-receipt harness, then restored.
M=/home/user/m2; F=$M/tools/pr/app_push.sh; cd $M
eval "$(bash /home/user/heatpump_optimizer/.claude/hooks/session-start.sh --env-lines)" >/dev/null 2>&1
mut() { # name line sed-expr
  git checkout -q -- "$F"; sed -i "$2s$3" "$F"
  if git diff --quiet; then echo "MUTANT $1: NOT APPLIED"; return; fi
  st=$(timeout 900 bash tools/pr/app_push.sh --self-test 2>&1 | grep -E '^FAIL|self-test:' | head -4 | tr '\n' ' ')
  pl=$(bash /home/user/w/ev/plant_rv.sh $M 2>&1 | grep -c '^RESULT: FAIL')
  echo "MUTANT $1 (line $2): self-test: $st | plant FAIL rows: $pl"
  git diff | grep '^[-+][^-+]' | sed 's/^/    /'
}
mut A1-tree-check 283 '#= "$t" \]#= "$(git -C "$wt" rev-parse "$c^{tree}" 2>/dev/null)" ]#'
mut A2-ancestor 285 '#merge-base --is-ancestor "$c" "$RV_HEAD"#rev-parse "$c"#'
mut A3-clean-merge 303 '#2>/dev/null) \\#2>/dev/null); true \\#'
mut A4-tree-equals-merge 309 '#\[ -z "$d" \] ||#true ||#'
mut A5-own-commits 313 '#\[ "$n" = 0 \] ||#true ||#'
mut A6-always-skip 564 '#if \[ "$reused" = 1 \]; then export#if true; then export#'
git checkout -q -- "$F"; git status --short
