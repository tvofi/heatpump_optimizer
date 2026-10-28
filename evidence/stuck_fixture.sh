#!/bin/bash
# reviewer's own STUCK harness: extracts STUCK_PY from the real cloud_relay.sh ($1) and stuck_arm,
# runs them against fixture locks held by a real flock holder; prints RESULT lines.
F=$1; tag=$2; t=$(mktemp -d); export HPO_STATE_DIR=$t/state; mkdir -p $t/state/pr
eval "$(awk '/^STUCK_PY=/{p=1} p{print} p&&/print\(n\[4:-5\]/{exit}' "$F")"
eval "$(grep "^relay_log()" "$F")"
eval "$(awk '/^level_line\(\)/{print} /^level_set\(\)/{p=1} p{print} p&&/^}/{exit}' "$F")"
eval "$(awk '/^stuck_arm\(\)/{p=1} p{print} p&&/^}/{exit}' "$F")"
LOG=$t/log
now=$(date +%s)
printf '111 222 %s\n' $((now-901)) > $t/state/pr/upd-fix-old.lock
printf '333 444 %s\n' $((now-899)) > $t/state/pr/upd-fix-young.lock
printf '555 666 %s drain\n' $((now-5000)) > $t/state/pr/upd-fix-gone.lock
# mtime: touched "later" = now (written now). Also one whose mtime is OLD but recorded start fresh:
printf '777 888 %s\n' $((now-10)) > $t/state/pr/upd-fix-oldmtime.lock; touch -d @$((now-5000)) $t/state/pr/upd-fix-oldmtime.lock
python3 -I -c 'import fcntl,sys,time
fs=[open(p,"a") for p in sys.argv[2:]]
[fcntl.flock(f,fcntl.LOCK_EX) for f in fs]; open(sys.argv[1],"w").close(); time.sleep(30)' $t/held $t/state/pr/upd-fix-old.lock $t/state/pr/upd-fix-young.lock $t/state/pr/upd-fix-oldmtime.lock & hp=$!
while [ ! -e $t/held ]; do sleep 0.05; done
out=$(stuck_arm 2>&1); echo "$out" | sed "s/^/[$tag] /"
r(){ echo "RESULT $tag $1 $2"; }
grep -qE '^cloud_relay: STUCK fix-old 111 90[12]s$' <<<"$out" && r held901 reported || r held901 NOT-reported
grep -q fix-young <<<"$out" && r held899 reported || r held899 not-reported
grep -q fix-gone <<<"$out" && r released5000 reported || r released5000 not-reported
grep -q fix-oldmtime <<<"$out" && r oldmtime-freshstart reported || r oldmtime-freshstart not-reported
grep -qE 'push-stuck fix-old 111 STUCK fix-old 111 90[12]s$' $LOG.level 2>/dev/null && r level push-stuck-line || r level NO-line
kill -KILL $hp; wait $hp 2>/dev/null
out2=$(stuck_arm 2>&1); [ -z "$out2" ] && ! grep -q push-stuck $LOG.level && r all-released nothing-reported || r all-released REPORTED:"$out2"
rm -rf $t
