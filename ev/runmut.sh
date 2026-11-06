# each run writes its OWN log; the last line is "RESULTLINE <name> rc=<n>"
W=/tmp/tmp.DAQU6SMXEC
d=$1
(cd $W/$d && PYTHONPATH=tests/hastub timeout 5400 python3 tests/features.py > $W/ev/features-$d.log 2>&1; echo "RESULTLINE $d rc=$?" >> $W/ev/features-$d.log)
