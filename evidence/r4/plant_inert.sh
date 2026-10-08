#!/usr/bin/env bash
# Reviewer harness (review-2061 r2): a harness-only diff -- does 6d predict INERT READS,
# what rc, and which closures arm (affected case) would CI take? Arg: source worktree.
set -u
D=$(mktemp -d); trap 'rm -rf "$D"' EXIT
git clone -q --shared "$1" "$D/r" && cd "$D/r" || exit 9
G="git -c user.name=r -c user.email=r@x -c commit.gpgsign=false"
$G checkout -q --detach; git update-ref refs/remotes/origin/main HEAD
src=$(git ls-files 'dev/audit/harnesses/*.py' | head -1)
cp "$src" dev/audit/harnesses/zz_planted.py; $G add -A; $G commit -qm plant
PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main > "$D/p.txt" 2>&1; rc=$?
grep -E '^PREDICT|^CI PREDICT' "$D/p.txt"; echo "RESULT predict rc=$rc"
git diff --name-only origin/main...HEAD > "$D/c.txt"
python3 tests/closure.py affected --files-from "$D/c.txt" --workdir "$D/a" >/dev/null 2>&1
echo "RESULT closures arm case=$(cat "$D/a/affected.case") (skip = fast arm: no recording, no INERT READS check, no autofix)"
