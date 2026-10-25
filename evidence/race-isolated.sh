#!/bin/bash
# reviewer's own instrument: the holder of pr_branch_lock (pr_args.sh at the reviewed head) with
# its mut:drain line deleted, as the self-test's mutant arm builds it; its parent exits at once.
# The arm's wait (poll 50 ms until the mark reads drain, or the lock is free) is then followed by
# one lockstate read, exactly as sigrun does. Prints how often that read says held (the arm fails).
# usage: race.sh <pr_args.sh> <trials> <with-detach: 1|0>
src=$1; n=$2; det=$3; d=$(mktemp -d); git init -q "$d/r" && git -C "$d/r" -c user.email=a@b -c user.name=a commit -q --allow-empty -m x
py=$(awk '/^  python3 -I -c .import fcntl, os, signal, sys, time$/{f=1; sub(/^  python3 -I -c ./,""); print; next} f&&/^sys.exit\(0\)/{print "sys.exit(0)"; exit} f{print}' "$src" | grep -v '# mut:drain$')
lockstate() { python3 -I -c 'import fcntl, sys
f = open(sys.argv[1], "a")
try: fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError: print("held"); sys.exit()
print("free")' "$1"; }
held=0
for i in $(seq "$n"); do
  lf=$d/l$i.lock; git -C "$d/r" checkout -q -B fix/t 2>/dev/null
  if [ "$det" = 1 ]; then bash -c 'python3 -I -c "$1" "$2" detach "$3" </dev/null >/dev/null 2>&1 & sleep 0.3' x "$py" "$lf" "$d/r"
  else bash -c 'python3 -I -c "$1" "$2" </dev/null >/dev/null 2>&1 & sleep 0.3' x "$py" "$lf"; fi
  k=0; while [ "$(cut -d' ' -f3 "$lf" 2>/dev/null)" != drain ] && [ "$(lockstate "$lf")" = held ] && [ $k -lt 600 ]; do sleep 0.05; k=$((k + 1)); done
  [ "$(lockstate "$lf")" = held ] && held=$((held + 1))
  while [ "$(lockstate "$lf")" = held ]; do sleep 0.05; done
done
echo "RESULT detach=$det trials=$n held_at_read=$held"
rm -rf "$d"
