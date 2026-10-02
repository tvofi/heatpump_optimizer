#!/bin/bash
# Round-2 provenance: can a seat with the shared push credential (no key)
# re-post an EARLIER confirmed verdict after a later one superseded it?
# Same PR, same head: round 1 confirmed "merge H", round 2 confirmed
# "blocked H". The forger copies round 1's tree and signed message onto a new
# commit on verdict/<pr>. app_approve.sh acts on the NEWEST approver verdict.
set -u
B=${1:-/tmp/rv2/tools/audit/seat/bus.sh}
W=$(mktemp -d); export GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=$W/gc
git config --file $W/gc user.name t; git config --file $W/gc user.email t@t
git init -q --bare $W/o.git; git init -q $W/s; git -C $W/s remote add origin $W/o.git
git -C $W/s commit -q --allow-empty -m base; git -C $W/s push -q origin HEAD:refs/heads/main
mkdir -p $W/ap; openssl genrsa -out $W/ap/identity-approver.pem 2048 2>/dev/null
H=3333333333333333333333333333333333333333; PR=1829
mkdir -p $W/ev; echo "measured at $H" > $W/ev/run.log
printf '#!/bin/bash\necho "POSTED: $(head -1 "$3")" >> %s/posts\n' $W > $W/poster; chmod +x $W/poster
run(){ (cd $W/s && HPO_BUS_STATE=$W/st HPO_BUS_POSTER=$W/poster HPO_BUS_REPO=o/r HPO_IDENTITY_DIR=$W/ap bash "$B" "$@") 2>&1; }
run watch --once --post >/dev/null
# round 1: merge
n=$(run dispatch $PR $H reviewerA); printf 'Fix review: merge %s\n\n%s\n' $H "$n" > $W/v1.md
r=$(run push-verdict $PR $W/v1.md $W/ev | awk '{print $2}'); run confirm $PR $r
v1=$(git -C $W/s ls-remote origin refs/heads/verdict/$PR | cut -f1)
run watch --once --post >/dev/null
# round 2: same head, reviewer retracts with blocked
n=$(run dispatch $PR $H reviewerA); printf 'Fix review: blocked %s harness: retracted\n\n%s\n' $H "$n" > $W/v2.md
r=$(run push-verdict $PR $W/v2.md $W/ev | awk '{print $2}'); run confirm $PR $r
run watch --once --post >/dev/null
echo "--- posts before the replay"; cat $W/posts
# forger: no key, only push
git -C $W/s fetch -q origin verdict/$PR
tip=$(git -C $W/s rev-parse FETCH_HEAD)
c=$(git -C $W/s log -1 --format=%B $v1 | git -C $W/s commit-tree "$v1^{tree}" -p $tip)
git -C $W/s push -q origin $c:refs/heads/verdict/$PR
echo "--- watch --post after the replay"; run watch --once --post
echo "--- posts after"; cat $W/posts
rm -rf $W
