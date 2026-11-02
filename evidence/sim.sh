#!/bin/bash
# Reviewer's own two-PR simulation (not the fixer's harness): real commits in a
# throwaway clone of the reviewed head; every PR run is the merge of the PR into
# its base with tools/policy/agreement.mjs restored from the base and NOT
# committed, as governance.yml's policy-docs job does (fetch-depth 0, restore,
# then node tools/policy/agreement.mjs). Grader: $1. Entry for PR A: $2.
# Prints the verdict line(s) on the synthetic key and the RESULT line.
set -u
GRADER_SRC=$(realpath "$1"); ENTRY="$2"; SRC_REPO=$3; HEADSHA=$4
R=$(mktemp -d); trap 'rm -rf $R' EXIT
git clone -q --shared --no-checkout "$SRC_REPO" $R/r; cd $R/r; git checkout -q -B main $HEADSHA
git config user.name sim; git config user.email sim@invalid
GR=tools/policy/agreement.mjs; SOLE=tools/policy/zzrev_1.mjs; P=tools/policy/zzrev_2.mjs; Q=tools/policy/zzrev_3.mjs
KEY='zzrev-grammar-(\\d+)-k'
src='export const ZZ = /^zzrev-grammar-(\d+)-k$/'
grade(){ out=$(node $GR --only discovery 2>&1); rc=$?
  echo "$1: rc=$rc $(echo "$out" | grep -E '^RESULT' | sed 's/ seconds=[^ ]*//')"
  echo "$out" | grep -F 'zzrev-grammar' | sed 's/^ */      /'; }
ci(){ base=$2; pr=$3; git checkout -q --detach $base; git merge -q --no-ff --no-edit -m "Merge pull request #$4 from t/$pr" $pr
  git checkout $base -- $GR; grade "$1"; git reset -q --hard; git checkout -q main; }
merge(){ git checkout -q main; GIT_COMMITTER_DATE="${3:-}" git merge -q --no-ff --no-edit -m "Merge pull request #$2 from t/$1" $1; }
addentry(){ python3 - "$GR" "$1" "$2" <<'EOF'
import sys,json; f,k,v=sys.argv[1:]; s=open(f).read(); a='const SHARED_GRAMMARS = {\n'
assert a in s; open(f,'w').write(s.replace(a, a+'  %s: %s,\n'%(json.dumps(k),json.dumps(v)),1))
EOF
}
cp $GRADER_SRC $GR; echo "$src" > $SOLE; git add -A; git commit -q --no-verify -m main1
git tag m1; grade "main1 push (one reader, no entry)"
git checkout -q -b a; addentry 'zzrev-grammar-(\d+)-k' "${ENTRY//\{P\}/$P}"; git commit -qam "PR A"
ci "PR A graded by main1" main a 1; merge a 1; grade "main2 push (entry, one reader)"
git checkout -q -b b main; echo "$src" > $P; git add -A; git commit -q -m "PR B"
ci "PR B graded by main2 (pinned restore)" main b 2; merge b 2; grade "main3 push (two readers)"
git checkout -q -b d main; git rm -q $P; git commit -q -m "PR D"
ci "PR D graded by main3 (reader leaves)" main d 3
