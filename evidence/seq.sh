#!/bin/bash
W=/tmp/tmp.0yIqpWX7DG; E=$W/ev; cd $W/head
export HOME=$(mktemp -d)
bash tools/audit/seat/cloud_relay.sh --self-test > $E/cloud_relay.selftest.log 2>&1; echo "RESULT cloud_relay-selftest rc=$? $(tail -1 $E/cloud_relay.selftest.log)" >> $E/RESULT.txt
python3 -I tools/audit/seat/ledger.py --self-test > $E/ledger.selftest.log 2>&1; echo "RESULT ledger-selftest rc=$? $(tail -1 $E/ledger.selftest.log)" >> $E/RESULT.txt
python3 dev/audit/harnesses/r10_seat_selftests_mutants.py M0 cloud_relay-29 cloud_relay-30 cloud_relay-31 cloud_relay-32 cloud_relay-33 ledger-1 pr_args-1 > $E/mutants.log 2>&1; echo "RESULT mutant-harness rc=$? $(grep RESULT $E/mutants.log)" >> $E/RESULT.txt
git status --porcelain >> $E/RESULT.txt
for d in head prev; do (cd $W/$d && bash $W/grpkill.sh tools/audit/seat/pr_args.sh 15 > $E/grpkill-$d.log 2>&1); echo "RESULT grpkill $d $(grep -c ' 0 live' $E/grpkill-$d.log) zero-sessions, $(grep -cE ' [1-9][0-9]* live' $E/grpkill-$d.log) nonzero" >> $E/RESULT.txt; done
echo SEQDONE >> $E/RESULT.txt
