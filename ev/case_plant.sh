#!/bin/bash
# reviewer's own plant: the finder's harness (agreement_py.py --run) with each end's guard,
# unperturbed and under one shell case-arm writer appended to tools/audit/seat/merge_pr.sh. Run from a head worktree.
set -u
AG=tools/policy/agreement.mjs; MP=tools/audit/seat/merge_pr.sh
T=$(mktemp -d); cp $AG $T/ag; cp $MP $T/mp
run() { python3 -I tools/policy/agreement_py.py --run 2>&1 | grep -E 'merge call|REFUSED +merge-subject|RESULT' | sed -e 's/^ *//' -e 's/ seconds=[0-9.]*//' -e 's/.*commit(s) past [0-9a-f]*, //' | tr '\n' ' '; echo; }
for ref in e73424f247781b8d5e55abe52f54d7005cb51f39 683dd52cbb938ad00b38857117710791f5581f4b d0d35231c633ca447acf04770f9034281417b72d; do
  git show $ref:$AG > $AG
  cp $T/mp $MP; echo "$ref unperturbed: $(run)"
  printf '\n%s\n' 'case "${DRY:-}" in' '  never) gh pr merge "$n" --squash --subject "Merge pull request #$n (x)" ;;' 'esac' >> $MP
  echo "$ref case-arm plant: $(run)"
  cp $T/mp $MP
  printf '\n%s\n' 'case "${DRY:-}" in' '  (never) gh pr merge "$n" --squash --subject "Merge pull request #$n (x)" ;;' 'esac' >> $MP
  echo "$ref (never) control plant: $(run)"
  cp $T/mp $MP
done
cp $T/ag $AG; rm -rf $T; git status --short -- $AG $MP
