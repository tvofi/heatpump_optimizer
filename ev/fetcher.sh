cd $1/local; end=$((SECONDS+40))
while [ $SECONDS -lt $end ]; do git fetch -q origin '+refs/heads/*:refs/remotes/origin/*' 2>>$1/err.$2 || echo "RC=$?" >> $1/err.$2; done
