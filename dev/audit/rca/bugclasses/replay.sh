#!/bin/bash
# replay.sh <arm: without|with> <merge-sha>...: re-run each merge with real `git merge`
# in a standalone clone; report whether the register conflicted and, when it
# merged, whether its JSON equals the resolution the merge commit recorded.
# S: a scratch dir holding a STANDALONE clone at $S/clone (never a worktree:
# .git/info/attributes would route every sibling) with
#   git config merge.bcmerge.driver "python3 $S/ledger_merge.py --merge %O %A %B %L dev/audit/config/bugclasses.json"
# and $S/ledger_merge.py a copy of the driver under test.
S=${S:?set S to the scratch dir}; cd "$S/clone" || exit 2
ARM=$1; shift
if [ "$ARM" = with ]; then
  printf 'tools/audit/bugclasses.json merge=bcmerge\ndev/audit/config/bugclasses.json merge=bcmerge\n' > .git/info/attributes
else
  : > .git/info/attributes
fi
conf=0; same=0; differ=0; n=0
for m in "$@"; do
  n=$((n+1))
  git checkout -q -f --detach "$m^1" 2>/dev/null || { echo "CHECKOUT-FAIL $m"; continue; }
  git merge -q --no-commit --no-ff "$m^2" >/dev/null 2>$S/merge.err
  f=$(git diff --name-only --diff-filter=U | grep bugclasses.json)
  path=$(git ls-tree -r --name-only "$m" | grep -E '(^tools/audit|^dev/audit/config)/bugclasses.json$')
  if [ -n "$f" ]; then conf=$((conf+1)); echo "CONFLICT ${m:0:8}"
  else
    if python3 -c "import json,sys;a=json.load(open(sys.argv[1]));b=json.loads(sys.stdin.read());sys.exit(a!=b)" "$path" < <(git show "$m:$path"); then
      same=$((same+1)); r=same; else differ=$((differ+1)); r=DIFFERS; fi
    cmp -s "$path" <(git show "$m:$path") && b=bytes-equal || b=bytes-differ
    echo "merged   ${m:0:8} json-vs-recorded=$r $b $(grep -o 'LEDGER-MERGE: [a-z]*' $S/merge.err | head -1)"
  fi
  git merge --abort 2>/dev/null; git reset -q --hard
done
echo "ARM=$ARM merges=$n conflicted=$conf merged-equal-to-recorded=$same merged-differing=$differ"
