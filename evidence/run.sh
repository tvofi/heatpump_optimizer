#!/bin/bash
B=/home/user/rev2469
n=$1; d=$B/mut/wt-$n; R=/home/user/heatpump_optimizer
git -C $R worktree add -q --detach $d 98fe31c26da80c46441a32bde66c2c3ef9ac5bc1 2>/dev/null
cd $d; U=tools/audit/seat/update_pr.sh; C=tools/audit/seat/cloud_relay.sh
case $n in
  lock|unlock|stop|drain|pgrp|holdgrp) grep -v "# mut:$n\$" $U > $U.x && cat $U.x > $U && rm $U.x ;;
  shellfd) python3 - $U <<'P'
import sys; p=sys.argv[1]; s=open(p).read()
a='python3 -I -c \'import fcntl, os, subprocess, sys, time\nf = open(sys.argv[1], "a")'
assert a in s
s=s.replace(a,'exec 9>>"$WT.lock"\npython3 -I -c \'import fcntl, os, subprocess, sys, time\nf = os.fdopen(9, "a")',1)
open(p,'w').write(s)
P
  ;;
  oldfd) git show 49577add8c4df47aa24124727fd2f6e250f3434f:$U > $U ;;
  mainupd) git show origin/main:$U > $U ;;
  relay-body) sed -i 's|bd=$(mktemp -d "$state/cloud-body.XXXXXX")|bd=${TMPDIR:-/tmp}/cb$$; body=$(mktemp "${TMPDIR:-/tmp}/cloud_body.XXXXXX")|; /^    body=\$bd\/BODY.md$/d' $C ;;
  relay-rm) python3 - $C <<'P'
import sys; p=sys.argv[1]; s=open(p).read()
a='    fi\n    rm -rf "$bd"\n'; assert s.count(a)==1; s=s.replace(a,'    fi\n',1); open(p,'w').write(s)
P
  ;;
  relay-75) grep -v 'if \[ "$urc" = 75 \]' $C > $C.x && cat $C.x > $C && rm $C.x ;;
esac
git diff > $B/mut/$n.diff
case $n in relay*) bash $C --self-test > $B/mut/$n.out 2>&1 ;; *) bash tools/audit/seat/pr_args.sh --self-test > $B/mut/$n.out 2>&1 ;; esac
echo "rc=$?" >> $B/mut/$n.out
