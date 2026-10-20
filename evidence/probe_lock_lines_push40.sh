pr_refuse(){ echo "REFUSE: $*" >&2; exit 1; }
WT=/tmp/tmp.9Po3VvKNr8/sk/upd-x; BR=x
python3 -I -c 'import fcntl, os, sys, time
f = open(sys.argv[1], "a")
try: fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError: sys.exit(75)
p = os.getppid(); f.truncate(0); f.write("%d %d\n" % (p, os.getpid())); f.flush()
while os.getppid() == p: time.sleep(2)' "$WT.lock" </dev/null >/dev/null 2>&1 & LKP=$!
trap '{ kill "$LKP"; wait "$LKP"; } 2>/dev/null || :' EXIT  # mut:unlock
k=0; while kill -0 "$LKP" 2>/dev/null && [ "$(cat "$WT.lock" 2>/dev/null)" != "$$ $LKP" ] && [ $k -lt 400 ]; do sleep 0.05; k=$((k + 1)); done
upd_unlocked() { # the holder did not take the lock: BUSY (75) when another holder has it
  local rc=0 o; kill -0 "$LKP" 2>/dev/null && pr_refuse "the lock holder for $WT.lock did not report within 20 s"
  wait "$LKP" || rc=$?; o=$(cut -d' ' -f1 "$WT.lock" 2>/dev/null || :)
  [ "$rc" = 75 ] || pr_refuse "could not take the per-branch lock $WT.lock (its holder exited $rc)"
  if [ -n "$o" ] && kill -0 "$o" 2>/dev/null; then o="another update_pr.sh run (pid $o)"; else o="the lock holder of run ${o:-unknown}, which has ended (the holder exits within 2 s),"; fi
  echo "update_pr: BUSY: $o holds $BR's worktree $WT; nothing was changed, run again when it ends" >&2; exit 75
}
[ "$(cat "$WT.lock" 2>/dev/null)" = "$$ $LKP" ] || upd_unlocked  # mut:lock
echo LOCKED $$; sleep 40; echo PUSH-DONE
