#!/bin/bash
# probe.sh <worktree> <SIG> <prepr|group>: reviewer's own reap probe. The fake recorder forks
# a subshell lane that itself forks a grandchild `sleep 301`; liveness read from /proc/<pid>/stat
# field 3 (absent or Z = gone). Independent of the self-test's alive()/reap_arm.
WT=$1; SIG=$2; HOW=$3; T=$(mktemp -d)
git -C "$WT" worktree list >/dev/null
git clone -q "$WT" "$T/r" 2>/dev/null
cat > "$T/rec.sh" <<EOF
#!/bin/bash
( ( sleep 301 ) & echo "\$!" > "$T/gc"; wait ) & echo "\$!" > "$T/lane"
echo "\$\$" > "$T/rec"
wait
EOF
chmod +x "$T/rec.sh"
{ echo "cd '$T/r' || exit 9"
  echo "eval \"\$(awk '/^rc=0\$/{exit} {print}' '$WT/tools/pr/prepr.sh')\""
  echo "exit_on_signals"
  echo "say() { :; }; step() { :; }; unset PREPR_SKIP_CLOSURES; BASE=\$(git rev-parse HEAD~1)"
  echo "export PREPR_RECORD='$T/rec.sh' PREPR_RECORD_CLOSURES=1"
  awk '/^# --- 6b\./{f=1} f&&/^if /{p=1} p{print} p&&/^fi$/{exit}' "$WT/tools/pr/prepr.sh"
} > "$T/drv.sh"
# give the clone a scoped diff for closures_line to record: touch one test script
( cd "$T/r" && echo "# probe" >> tests/layout.py && git -c user.name=p -c user.email=p@p commit -qam probe )
st() { local s; s=$(awk '{print $3}' /proc/$1/stat 2>/dev/null); [ -n "$s" ] && [ "$s" != Z ] && echo alive || echo gone; }
( set -m; bash "$T/drv.sh" </dev/null >"$T/drv.out" 2>&1 & echo $! > "$T/drv.pid" ); D=$(cat "$T/drv.pid")
for i in $(seq 1 1200); do [ -s "$T/gc" ] && [ -s "$T/rec" ] && break; sleep 0.1; done
R=$(cat "$T/rec" 2>/dev/null); L=$(cat "$T/lane" 2>/dev/null); G=$(cat "$T/gc" 2>/dev/null)
[ -z "$G" ] && { echo "PROBE $SIG $HOW unstarted"; tail -5 "$T/drv.out"; kill -KILL -- -$D; exit 1; }
if [ "$HOW" = group ]; then kill -$SIG -- -$D; else kill -$SIG $D; fi
sleep 5
echo "PROBE $(basename $WT) $SIG $HOW prepr=$(st $D) recorder=$(st $R) lane=$(st $L) grandchild=$(st $G)"
kill -KILL -- -$R -$D 2>/dev/null; kill -KILL $R $L $G $D 2>/dev/null; rm -rf "$T"
