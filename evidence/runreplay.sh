M=$(cat /Users/timmalmstrom/hpo-seats/review-2040/clone/dev/audit/rca/bugclasses/merges.txt)
for arm in without with; do bash /Users/timmalmstrom/hpo-seats/review-2040/clone/dev/audit/rca/bugclasses/replay.sh $arm $M > $E/replay-$arm.log 2>&1; done; echo done > $E/replay.done
