#!/bin/bash
# usage: run.sh label tree mode inproc runs
l=$1; t=$2; m=$3; i=$4; r=$5
cmd="cd /home/user/rev2964 && PATH=/root/v314/bin:\$PATH PYTHONPATH=tests/hastub /root/v314/bin/python dev/audit/harnesses/r10_fly_nightly_hb.py --tree $t --mode $m --inproc $i --runs $r --out /root/ev/fly/$l"
echo "$cmd" > /root/ev/fly/$l.txt
bash -c "$cmd" >> /root/ev/fly/$l.txt 2>&1
echo "EXIT $?" >> /root/ev/fly/$l.txt
