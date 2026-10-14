#!/bin/bash
# usage: mut.sh <tree> <name> <file> <perl-subst>
T=$1; N=$2; F=$3; P=$4; S=$(cd $(dirname $0) && pwd)
cp "$T/$F" "$S/evidence/.bak"
perl -0pi -e "$P" "$T/$F"
if cmp -s "$T/$F" "$S/evidence/.bak"; then echo "RESULT mutant=$N applied=NO"; exit; fi
(cd $T && node tools/policy/check-wave-script.mjs > "$S/evidence/mut-$N.out" 2>&1); rc=$?
cp "$S/evidence/.bak" "$T/$F"
fails=$(grep -E '^\s+FAIL ' "$S/evidence/mut-$N.out" | grep -v 'probe, expected' | sed 's/^ *FAIL *//' | cut -c1-110 | tr '\n' '|')
echo "RESULT mutant=$N rc=$rc $(tail -1 $S/evidence/mut-$N.out) fails=[$fails]"
