#!/bin/bash
# repro_po.sh <cloud_relay.sh> : reviewer-built reproduction of P-O (a relayed probe whose confirm failed, then the next pass)
# plus null controls: an already-posted review is not confirmed; an undispatched review is owed once, not every pass.
R=$(readlink -f "$1"); t=$(mktemp -d); export RELAY_T=$t
git init -q --bare "$t/o.git"; git init -q "$t/w"; cd "$t/w"; git remote add origin "$t/o.git"
git -c user.name=x -c user.email=x@x commit -q --allow-empty -m init; git push -q origin HEAD:refs/heads/main
export GIT_AUTHOR_NAME=x GIT_AUTHOR_EMAIL=x@x GIT_COMMITTER_NAME=x GIT_COMMITTER_EMAIL=x@x
h=0123456789abcdef0123456789abcdef01234567; n=0123456789abcdef0123456789abcdef
export HPO_STATE_DIR=$t/state HPO_BUS_STATE=$t/bus; mkdir -p $t/bus $t/state
printf '#!/bin/sh\n' > $t/none.sh; chmod +x $t/none.sh; export HPO_RELAY_PRS=$t/none.sh
cat > $t/push.sh <<'EOF'
#!/bin/bash
s=$(mktemp -d "$RELAY_T/p.XXXX"); mkdir -p "$s/w/evidence"; cp "$2" "$s/w/VERDICT.md"; cp -R "$3"/. "$s/w/evidence/"
gd=$(git rev-parse --absolute-git-dir)
tree=$(cd "$s/w" && GIT_DIR="$gd" GIT_INDEX_FILE="$s/i" GIT_WORK_TREE="$s/w" git add -A -f . && GIT_DIR="$gd" GIT_INDEX_FILE="$s/i" git write-tree)
p=$(git ls-remote origin "refs/heads/review/$1" | awk 'NF{print "-p "$1;exit}'); [ -z "$p" ] || git fetch -q origin "refs/heads/review/$1"
c=$(git commit-tree "$tree" $p -m "verdict #$1") && git push -q origin "$c:refs/heads/review/$1" && echo "review/$1 $c"
EOF
cat > $t/confirm.sh <<'EOF'
#!/bin/bash
echo "$1 $2" >> "$RELAY_T/calls"
[ -f "$RELAY_T/fail" ] && { echo "BUS refused $1 $2: the poster refused: HTTP 502"; exit 1; }
echo "$1 $(git rev-parse "$2^{tree}")" >> "$HPO_BUS_STATE/posted-signed"; echo "BUS posted $1 $2"
EOF
chmod +x $t/push.sh $t/confirm.sh; export HPO_RELAY_PUSH=$t/push.sh HPO_RELAY_CONFIRM=$t/confirm.sh
mkprobe() { rm -rf $t/pr; git init -q $t/pr; mkdir $t/pr/ev; echo "$1 $RANDOM" > $t/pr/ev/e
  printf 'Fix review: merge %s\n\nbus-nonce: %s\n' $h $n > $t/pr/verdict.md
  git -C $t/pr add -A; git -C $t/pr commit -qm "verdict $1 $h"; git -C $t/o.git fetch -qf $t/pr "HEAD:refs/heads/probe/rev-$1-${n:0:8}"; }
calls() { grep -c "^$1 " $t/calls 2>/dev/null || echo 0; }
LOG=$t/relay.log
# P-O: probe 61 dispatched; confirm fails on the relay's own pass, then works
mkprobe 61; echo "61 $h cloud $n" >> $t/bus/dispatched
touch $t/fail; bash "$R" pass --confirm --log $LOG > $t/p1.out 2>&1; echo "PASS1 rc=$? calls61=$(calls 61)"
rm -f $t/fail; bash "$R" pass --confirm --log $LOG > $t/p2.out 2>&1; echo "PASS2 rc=$? calls61=$(calls 61)"
grep -h 'already relayed\|POSTED\|OWED' $t/p2.out | sed 's/^/  p2: /'
echo "RESULT po_posted=$(grep -c "^POSTED .* 61 " $LOG)"
# null 1: already posted review (66), posted by hand before any confirm pass
mkprobe 66; echo "66 $h cloud $n" >> $t/bus/dispatched; bash "$R" pass --log $LOG >/dev/null 2>&1
tip66=$(git ls-remote origin refs/heads/review/66 | cut -f1); git fetch -q origin refs/heads/review/66
echo "66 $(git rev-parse $tip66^{tree})" >> $t/bus/posted-signed
bash "$R" pass --confirm --log $LOG >/dev/null 2>&1; echo "RESULT null_posted_calls66=$(calls 66) owed66=$(grep -c 'review/66 ' $LOG.level 2>/dev/null)"
# null 2: relayed but undispatched now (dispatch record for another head), two passes
mkprobe 62; echo "62 $h cloud $n" >> $t/bus/dispatched; bash "$R" pass --log $LOG >/dev/null 2>&1
sed -i '/^62 /d' $t/bus/dispatched
for k in 1 2 3; do bash "$R" pass --confirm --log $LOG > $t/u$k.out 2>&1; done
echo "RESULT null_undispatched_calls62=$(calls 62) level_lines62=$(grep -c 'review/62 .*undispatched' $LOG.level 2>/dev/null) log_owed62=$(grep -c 'OWED.*62' $LOG)"
# retry bound: confirm always fails for 63 -> at most 3 calls over 5 passes
mkprobe 63; echo "63 $h cloud $n" >> $t/bus/dispatched; touch $t/fail
for k in 1 2 3 4 5; do bash "$R" pass --confirm --log $LOG >/dev/null 2>&1; done
echo "RESULT bound_calls63=$(calls 63) level63=$(grep 'review/63 ' $LOG.level 2>/dev/null | sed 's/^OWED [^ ]* //')"
rm -rf "$t"
