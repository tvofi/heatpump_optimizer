#!/bin/bash
# Null control for the -c variant: main itself adds a transport file, the branch merges main cleanly.
set -u
. "$1"
R=$(mktemp -d); cd "$R"; git init -q -b main .; git config user.name p; git config user.email p@p
echo a > code; git add -A; git commit -qm base
git checkout -q -b br; echo b > code; git commit -qam br
git checkout -q main; mkdir -p tools/audit/handoff/m; echo x > tools/audit/handoff/m/BODY.md; git add -A; git commit -qm "main carries transport"
git checkout -q br; git merge -q --no-edit main
base=$(git rev-parse main~1)
echo "stale base:"; transport_in_ancestry "$base" br; echo "rc=$?"
echo "fresh base:"; transport_in_ancestry "$(git merge-base main br)" br; echo "rc=$?"
rm -rf "$R"
