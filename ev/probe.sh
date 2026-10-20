#!/bin/bash
# probe: does a git process that `gc --auto` detaches inherit update_pr.sh's fd 9 lock?
X=$1; cd $X; rm -rf r2 l3.lock; git init -q r2
find $X/blobs -type f | git -C r2 hash-object -w --stdin-paths > /dev/null
echo "loose: $(git -C r2 count-objects)"
bash $X/run2.sh $X/l3.lock $X/r2
for i in 1 2 3 4; do
  python3 -I -c 'import fcntl,sys;f=open(sys.argv[1],"a")
try: fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB); print("probe: lock free")
except BlockingIOError: print("probe: lock HELD after the run exited")' $X/l3.lock
  for p in $(pgrep -x git); do echo "  live git pid $p: $(tr '\0' ' ' < /proc/$p/cmdline) holds: $(ls -l /proc/$p/fd 2>/dev/null | grep -o 'l3.lock')"; done
  sleep 1
done
