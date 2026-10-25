# usage: pins_shard.sh <worktree> <k> <n>
S=<scratch>/
cd "$1"; k=$2; n=$3; i=0
for f in $(git diff --name-only 5c0ee109305fc4f377c9326c712156b9ceb0e638...274e6975c1b7a4334d181879c4ad2bef532c4134 -- tests/mutation_ledger/killed_by); do
  i=$((i+1)); [ $(( (i-1) % n )) -eq $k ] || continue
  a=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['anchor'])" "$f")
  grep -qF "######## $a" $S/pins_part0.log && grep -A30 -F "######## $a" $S/pins_part0.log | grep -q "PIN RE-VERIFICATION" && continue
  echo "######## $a"
  env -u BASH_ENV PYTHONPATH=tests/hastub timeout 1500 python3 tests/mutation_table.py --anchor "$a" --scripts tests/_rv_prefix.py --jobs 1 2>&1 | grep -v "^  [0-9]* unpinned site" | tail -12
done
