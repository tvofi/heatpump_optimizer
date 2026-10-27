#!/bin/bash
# Isolate the derivation loop's cost: one `python3 -I -c` per link target, then
# the same loop normalising in shell. Whole-tree copy, so every target exists and
# no archive runs: the difference is the interpreter spawn, nothing else.
set -uo pipefail
REPO=$1
cd "$REPO" || exit 2
python3 -I dev/audit/rounds/round4/D6/claims.py --print-link-targets > /tmp/rev2853r2/lt.txt 2>/dev/null
echo "targets: $(wc -l < /tmp/rev2853r2/lt.txt)"
T=$(mktemp -d)
git archive HEAD | tar -x -C "$T"
echo "== per-target python3 -I -c (the step's shape) =="
/usr/bin/time -p bash -c '
while IFS= read -r t; do
  [ -n "$t" ] || continue
  rel=$(python3 -I -c '"'"'import os, sys
p = os.path.normpath(sys.argv[1])
print("" if os.path.isabs(p) or p == ".." or p.startswith("../") else p)'"'"' "$t") || continue
  [ -n "$rel" ] || continue
  [ -e "$1/$rel" ] && continue
done < /tmp/rev2853r2/lt.txt' _ "$T" 2>&1 | awk '/^real/{r=$2}/^user/{u=$2}/^sys/{s=$2}END{print "  real",r,"cpu",u+s}'
echo "== the same normalisation in shell =="
/usr/bin/time -p bash -c '
while IFS= read -r t; do
  [ -n "$t" ] || continue
  p=${t#./}
  case $p in /*|..|../*) continue;; esac
  while :; do case $p in *//*) p=${p//\/\//\/};; *) break;; esac; done
  [ -e "$1/$p" ] && continue
done < /tmp/rev2853r2/lt.txt' _ "$T" 2>&1 | awk '/^real/{r=$2}/^user/{u=$2}/^sys/{s=$2}END{print "  real",r,"cpu",u+s}'
rm -rf "$T"
echo "== one spawn =="
/usr/bin/time -p python3 -I -c 'pass' 2>&1 | awk '/^real/{r=$2}/^user/{u=$2}/^sys/{s=$2}END{print "  real",r,"cpu",u+s}'
