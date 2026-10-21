#!/usr/bin/env bash
# REVIEWER'S OWN harness (not the finder's: none is committed; not the fixer's
# r10_roster_push_race.sh). Deterministic interleave instead of a sleep:
# run A blocks inside its lint gate (after its commit, before its push) until
# run B has finished end to end; then A proceeds. Same shape as 2026-10-21.
#   reviewer_race.sh <tree> <shared|separate|solo> <samegroup|diffgroup>
set -u
TREE=$1 MODE=$2 KIND=${3:-diffgroup}
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 GIT_AUTHOR_NAME=r GIT_AUTHOR_EMAIL=r@x GIT_COMMITTER_NAME=r GIT_COMMITTER_EMAIL=r@x
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
R=dev/programme/rosters/wave-r9-groups.json
git init -q -b main $T/seed; mkdir -p $T/seed/tools/policy $T/seed/dev/programme/rosters
cat > $T/seed/tools/policy/brief_lint.mjs <<'J'
import fs from 'fs';
if (process.env.LINT_MARK) fs.writeFileSync(process.env.LINT_MARK, 'in');
const w = process.env.LINT_WAIT;
while (w && !fs.existsSync(w)) await new Promise(r => setTimeout(r, 50));
console.log('TOTAL: 0 error(s) across 1 file(s)');
J
python3 - $T/seed/$R <<'P'
import json,sys
g=lambda n:{"group":n,"lane":"L1","issues":[],"fixes":[],"after":[],"brief":n,"carry":[],"resume":{"stage":"not-started","branch":"handoff/x"}}
open(sys.argv[1],"w").write(json.dumps({"repo":"x","groups":[g("R9-A"),g("R9-B")]},indent=1))
P
git -C $T/seed add -A; git -C $T/seed commit -qm seed
git clone -q --bare $T/seed $T/origin.git; git clone -q $T/origin.git $T/drvA; git clone -q $T/origin.git $T/drvB
CB=$T/drvB; [ "$MODE" = shared ] && CB=$T/drvA
ed(){ python3 $TREE/tools/audit/seat/roster_edit.py "$3" "$4" "$5" --checkout "$1" --roster-ref main --branch handoff/roster --worktree "$2" --lint-cwd $T/seed --push; }
ed $T/drvA $T/wt0 set-stage R9-A seeded >$T/s.log 2>&1 || { cat $T/s.log; exit 1; }
before=$(git -C $T/origin.git rev-parse handoff/roster)
GB=R9-B; [ "$KIND" = samegroup ] && GB=R9-A
LINT_MARK=$T/inA LINT_WAIT=$T/goA ed $T/drvA $T/wtA append-carry R9-A carry-from-A >$T/A.log 2>&1 & PA=$!
for i in $(seq 600); do [ -e $T/inA ] && break; sleep 0.1; done
[ -e $T/inA ] || { echo "A never reached lint"; cat $T/A.log; exit 1; }
RB=-
if [ "$MODE" != solo ]; then ed $CB $T/wtB append-carry $GB carry-from-B >$T/B.log 2>&1; RB=$?; fi
touch $T/goA; wait $PA; RA=$?
tip=$(git -C $T/origin.git rev-parse handoff/roster); ro=$(git -C $T/origin.git show handoff/roster:$R)
fsck=$(git -C $T/origin.git log --format=%H $before..$tip | wc -l)
chk(){ sha=$(sed -n 's/^pushed [^ ]* at \([0-9a-f]\{40\}\)$/\1/p' $3|tail -1); on=none
  [ -n "$sha" ] && { git -C $T/origin.git merge-base --is-ancestor $sha $tip 2>/dev/null && on=yes || on=NO; }
  grep -q "$4" <<<"$ro" && e=yes || e=no; echo "RUN $1 rc=$2 reported_on_origin=$on edit_on_origin=$e"; }
chk A $RA $T/A.log carry-from-A
[ "$MODE" != solo ] && chk B $RB $T/B.log carry-from-B
echo "RESULT tree=$(git -C $TREE rev-parse --short HEAD) mode=$MODE kind=$KIND A_rc=$RA B_rc=$RB commits=$fsck"
grep -h 'lost a race\|REFUSED' $T/A.log $T/B.log 2>/dev/null | cut -c1-160 | sed 's/^/  note| /'
