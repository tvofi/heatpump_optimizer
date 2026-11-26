#!/bin/bash
# usage: run.sh name cmd...
cd $HOME/wt
n=$1; shift
timeout 900 bash -c "$*" > $HOME/w/ev/$n 2>&1
echo "EXIT=$?" >> $HOME/w/ev/$n
