cd $1/local; end=$((SECONDS+30))
while [ $SECONDS -lt $end ]; do git fetch -q origin $3 2>>$1/err.$2 || echo "RC" >> $1/err.$2; done
