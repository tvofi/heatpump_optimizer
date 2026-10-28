#!/bin/bash
# Reviewer's own drive of #2910's two prepr pins over mutated copies of prepr.sh.
P=$1
pin1() { case "$(grep -F 'PREDICT_LINE=$(predict_line origin/main' "$1")" in *'"${1:-}" "" record)'*) echo 0 ;; *) echo 1 ;; esac; }
pin2() { case "$(sed -n '/^predict_line() {/,/^}/p' "$1")" in *'[ -n "${5:-}" ] && rec="--record-self-tests"'*'$only $rec 2>&1'*) echo 0 ;; *) echo 1 ;; esac; }
T=$(mktemp -d)
cp "$P" $T/clean; sed 's/"${1:-}" "" record)/"${1:-}")/' "$P" > $T/w1
grep -v 'rec="--record-self-tests"' "$P" > $T/w2
sed 's/\$only \$rec 2>&1/$only 2>\&1/' "$P" > $T/w3
for m in clean w1 w2 w3; do echo "RESULT prepr=$m pin6d=$(pin1 $T/$m) pinmap=$(pin2 $T/$m) changed=$(cmp -s $P $T/$m && echo no || echo yes)"; done
