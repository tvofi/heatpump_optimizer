#!/bin/bash
# Probe: a transport file introduced by a merge commit's own resolution (in neither parent).
set -u
. "$1"
R=$(mktemp -d); cd "$R"; git init -q -b main .; git config user.name p; git config user.email p@p
echo a > code; git add -A; git commit -qm base
git checkout -q -b br; echo b > code; git commit -qam br
git checkout -q main; echo m > other; git add -A; git commit -qm main2
git checkout -q br; git merge -q --no-commit main
mkdir -p tools/audit/handoff/t; echo body > tools/audit/handoff/t/BODY.md; git add -A; git commit -qm "merge main"
base=$(git rev-parse main~1)   # merge base of the original branch point
echo "case 1, base=old base:"; transport_in_ancestry "$base" br; echo "rc=$?"
echo "case 2, base=main tip (merge-base after the merge):"; transport_in_ancestry "$(git merge-base main br)" br; echo "rc=$?"
echo "tree at head carries:"; git ls-tree -r --name-only br -- tools/audit/handoff
echo "combined-diff variant:"; git log --full-history -c --diff-filter=ACMRT --name-only --format='@%h' "$(git merge-base main br)..br" -- tools/audit/handoff/ handoff/
rm -rf "$R"
