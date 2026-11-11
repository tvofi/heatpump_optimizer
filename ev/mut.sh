#!/bin/bash
# reviewer's own mutation driver: apply each mutant at the head, run the file's self-test, restore
W=$1; cd $W/wt
CG=dev/audit/rounds/round6/D11/fix/codeowners_gap.py; PP=tools/pr/prepr.sh
cgm() { name=$1; shift; python3 - "$CG" "$@" <<'PY'
import sys; p,a,b=sys.argv[1:4]; s=open(p).read(); assert a in s,(a); open(p,'w').write(s.replace(a,b))
PY
  out=$(python3 -I $CG --self-test 2>&1); rc=$?; git checkout -q -- $CG
  w=$(echo "$out"|grep -c '^  WRONG\|WRONG'); echo "CG $name rc=$rc $(echo "$out"|tail -1)"; echo "$out" | grep -i wrong | head -5; }
ppm() { name=$1; shift; python3 - "$PP" "$@" <<'PY'
import sys; p,a,b=sys.argv[1:4]; s=open(p).read(); assert a in s,(a); open(p,'w').write(s.replace(a,b))
PY
  out=$(HPO_GATE_PRIORITY=0 bash $PP --self-test 2>&1); rc=$?; git checkout -q -- $PP
  echo "PP $name rc=$rc $(echo "$out"|grep -E 'passed|failed'|tail -1)"; echo "$out" | grep '^ *FAIL' | head -5; }
cgm M1-admission-off 'or bool(source) and' 'or False and'
cgm M2-any-input 'inputs\.restore_source|needs' 'inputs\.\w+|needs'
cgm M3-gate-dropped '(?:prelude|gate)' '(?:prelude)'
cgm M4-step-dropped '|steps\.source\.outputs\.sha) ' ') '
cgm M5-sep-optional ') \|\| ")' ')")'
cgm M6-match-to-search 'PINNED_SOURCE.match(val)' 'PINNED_SOURCE.search(val)'
cgm NULL-isnotnone 'bool(source) and' 'source is not None and'
out=$(HPO_GATE_PRIORITY=0 bash $PP --self-test 2>&1); echo "PP BASELINE rc=$? $(echo "$out"|grep -cE '^ *ok') ok-lines; $(echo "$out"|grep -E 'passed|failed'|tail -1)"
ppm PM1-both-src 'PINNED:[[:space:]]*\$\{\{ ((inputs\.restore_source|needs\.(prelude|gate)\.outputs\.restore_source|steps\.source\.outputs\.sha) \|\| )?github\.event\.pull_request\.base\.sha( \|\| github\.event\.merge_group\.base_sha)?( \|\| \(' 'PINNED:[[:space:]]*\$\{\{ github\.event\.pull_request\.base\.sha( \|\| github\.event\.merge_group\.base_sha)?( \|\| \('
ppm PM2-pr-src 'PINNED:[[:space:]]*\$\{\{ ((inputs\.restore_source|needs\.(prelude|gate)\.outputs\.restore_source|steps\.source\.outputs\.sha) \|\| )?github\.event\.pull_request\.base\.sha( \|\| github\.event\.merge_group\.base_sha)?( \|\| format' 'PINNED:[[:space:]]*\$\{\{ github\.event\.pull_request\.base\.sha( \|\| github\.event\.merge_group\.base_sha)?( \|\| format'
ppm PM6-src-any-leader '((inputs\.restore_source|needs\.(prelude|gate)\.outputs\.restore_source|steps\.source\.outputs\.sha) \|\| )?github\.event\.pull_request\.base\.sha( \|\| github\.event\.merge_group\.base_sha)?( \|\| \(' '([a-z_.]+ \|\| )?github\.event\.pull_request\.base\.sha( \|\| github\.event\.merge_group\.base_sha)?( \|\| \('
ppm PM5-step-both 'restore_source|steps\.source\.outputs\.sha) \|\| )?github\.event\.pull_request\.base\.sha( \|\| github\.event\.merge_group\.base_sha)?( \|\| \(' 'restore_source) \|\| )?github\.event\.pull_request\.base\.sha( \|\| github\.event\.merge_group\.base_sha)?( \|\| \('
echo DONE
