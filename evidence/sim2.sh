#!/bin/bash
# Reviewer's bypass hunt on the head grader: real commits, aged merges.
set -u
GRADER_SRC=$(realpath "$1"); SRC_REPO=$2; HEADSHA=$3
R=$(mktemp -d); trap 'rm -rf $R' EXIT
git clone -q --shared --no-checkout "$SRC_REPO" $R/r; cd $R/r; git checkout -q -B main $HEADSHA
git config user.name sim; git config user.email sim@invalid
GR=tools/policy/agreement.mjs; SOLE=tools/policy/zzrev_1.mjs; P=tools/policy/zzrev_2.mjs; Q=tools/policy/zzrev_3.mjs
src='export const ZZ = /^zzrev-grammar-(\d+)-k$/'
src2='export const YY = /^yyrev-grammar-(\d+)-k$/'
NOW=$(git log -1 --format=%ct HEAD); OLD=$((NOW-8*86400))
grade(){ out=$(node $GR --only discovery 2>&1); rc=$?
  echo "$1: rc=$rc $(echo "$out" | grep -E '^RESULT' | sed 's/ seconds=[^ ]*//')"
  echo "$out" | grep -E 'zzrev-grammar|yyrev-grammar' | sed 's/^ */      /'; }
ci(){ base=$2; pr=$3; git checkout -q --detach $base; git merge -q --no-ff --no-edit -m "Merge pull request #9 from t/$pr" $pr
  git checkout $base -- $GR; grade "$1"; git reset -q --hard; git checkout -q main; }
mergeat(){ git checkout -q main; GIT_COMMITTER_DATE="@$2 +0000" GIT_AUTHOR_DATE="@$2 +0000" git merge -q --no-ff --no-edit -m "Merge pull request #9 from t/$1" $1; }
addentry(){ python3 - "$GR" "$1" "$2" <<'EOF'
import sys,json; f,k,v=sys.argv[1:]; s=open(f).read(); a='const SHARED_GRAMMARS = {\n'
open(f,'w').write(s.replace(a, a+'  %s: %s,\n'%(json.dumps(k),json.dumps(v)),1))
EOF
}
cp $GRADER_SRC $GR; echo "$src" > $SOLE; echo "$src2" > tools/policy/yyrev_1.mjs; git add -A; GIT_COMMITTER_DATE="@$((OLD-100)) +0000" git commit -q --no-verify -m base
git checkout -q -b a; addentry 'zzrev-grammar-(\d+)-k' "identical:synthetic (awaits $P)"; GIT_COMMITTER_DATE="@$OLD +0000" git commit -qam "PR A"
mergeat a $OLD
git checkout -q -b u main; echo x > docs/zzrev.md; git add -A; git commit -q -m U; mergeat u $NOW
grade "B0 control: entry 8 days old, main push"
git tag expired
# B1: an unrelated second entry naming the same awaited path re-dates the first
git checkout -q -b b1 main; addentry 'yyrev-grammar-(\d+)-k' "identical:other (awaits $P)"; git commit -qam "PR B1"
ci "B1 PR graded by base" main b1; mergeat b1 $NOW; grade "B1 main push after a second entry awaiting the same path"
# B1c: a comment line holding the needle
git checkout -q -B main expired; git checkout -q -b b1c; sed -i "0,/^const SHARED_GRAMMARS = {/s||// note (awaits $P)\nconst SHARED_GRAMMARS = {|" $GR; git commit -qam "PR B1c"
mergeat b1c $NOW; grade "B1c main push after a comment holding '(awaits $P)'"
# B1r: re-point the clause at a fresh never-existed path
git checkout -q -B main expired; git checkout -q -b b1r; sed -i "s|(awaits $P)|(awaits $Q)|" $GR; git commit -qam "PR B1r"
mergeat b1r $NOW; grade "B1r main push after renaming the awaited path"
