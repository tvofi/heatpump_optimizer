#!/bin/bash
# spoofs.sh <shimdir> <stubdir> <tree gh_comment.py> : parent-check spoofs and the gh_comment.py control, offline
O=$(cd "$(dirname "$0")" && pwd); S=$1; ST=$2; G=$3
POST="import subprocess,sys; sys.exit(subprocess.run(['gh','api','-X','POST','repos/o/r/issues/201/comments','-f','body=x']).returncode)"
t() { local L=$1 E=$2; shift 2; local log=$O/logs/sp_$L.log; mkdir -p $O/logs; : > $log
  env -i HOME=$O/home HPO_STATE_DIR=$O/state STUBLOG=$log PATH=$S:$ST:/opt/hpo/venv-ci/bin:/usr/bin:/bin bash -c "$*" >/dev/null 2>$log.err; rc=$?
  n=$(wc -l < $log); if [ $E = refuse ]; then [ $n = 0 ] && r=OK || r=FAIL; else [ $rc = 0 ] && [ $n -ge 1 ] && r=OK || r=FAIL; fi
  echo "$r expect=$E rc=$rc stublines=$n :: $L"; }
printf 'Seat state: fixture-mandate-0000 is in force.\n' > $O/home/seat-rev/body.txt
t X-value refuse "python3 -X gh_comment.py -c \"$POST\""
t other-basename refuse "python3 $O/other/gh_comment.py post --repo o/r --issue 201 --body-file $O/home/seat-rev/body.txt"
t hardlink-other-name refuse "python3 $O/other/hard_gh_comment.py post --repo o/r --issue 201 --body-file $O/home/seat-rev/body.txt"
t python-c refuse "python3 -c \"$POST\""
t bash-c refuse "gh api -X POST repos/o/r/issues/201/comments -f body=x; true"
t c-naming refuse "python3 -c \"$POST\" $G"
t m-module refuse "cd $(dirname $G) && python3 -m gh_comment post --repo o/r --issue 201 --body-file $O/home/seat-rev/body.txt"
t exec-a-argv0 refuse "exec -a 'python3 $G' bash -c 'gh api -X POST repos/o/r/issues/201/comments -f body=x; true'"
t control-abs pass "python3 -I $G post --repo o/r --issue 201 --body-file $O/home/seat-rev/body.txt"
t control-rel pass "cd $(dirname $G) && python3 -I gh_comment.py post --repo o/r --issue 201 --body-file $O/home/seat-rev/body.txt"
t control-symlinked-dir pass "python3 -I $O/sl/prdir/gh_comment.py post --repo o/r --issue 201 --body-file $O/home/seat-rev/body.txt"
