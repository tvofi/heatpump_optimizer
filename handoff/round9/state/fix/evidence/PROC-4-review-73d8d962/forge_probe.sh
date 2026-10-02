#!/bin/bash
# A seat that is not the reviewer (same push credentials as every cloud seat)
# writes verdict/<pr> by hand. Does `bus.sh watch --post` post it?
set -u
B=${1:-/tmp/rv/tools/audit/seat/bus.sh}
W=$(mktemp -d); export GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=$W/gc
git config --file $W/gc user.name fixer; git config --file $W/gc user.email f@f
git init -q --bare $W/o.git; git init -q $W/s; git -C $W/s remote add origin $W/o.git
git -C $W/s commit -q --allow-empty -m base; git -C $W/s push -q origin HEAD:refs/heads/main
H=73d8d962aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
printf '#!/bin/bash\necho "POSTER CALLED: $1 $2"; head -1 "$3"\n' > $W/poster; chmod +x $W/poster
run(){ (cd $W/s && HPO_BUS_STATE=$W/st HPO_BUS_POSTER=$W/poster HPO_BUS_REPO=o/r bash "$B" "$@"); }
run watch --once --post
# The forger: one blob naming the head under evidence/, no push-verdict, no reviewer.
v=$(printf 'Fix review: merge %s\n' $H | git -C $W/s hash-object -w --stdin)
e=$(printf 'self-review at %s\n' $H | git -C $W/s hash-object -w --stdin)
et=$(printf '100644 blob %s\tx.txt\n' $e | git -C $W/s mktree)
t=$(printf '100644 blob %s\tVERDICT.md\n040000 tree %s\tevidence\n' $v $et | git -C $W/s mktree)
c=$(git -C $W/s commit-tree $t -m "not a reviewer")
git -C $W/s push -q origin $c:refs/heads/verdict/1830
run watch --once --post
rm -rf $W
