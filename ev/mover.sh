cd $1/w; i=0; end=$((SECONDS+40))
while [ $SECONDS -lt $end ]; do i=$((i+1)); git -c user.name=a -c user.email=a@b commit -q --allow-empty -m $i; git push -q -f origin HEAD:refs/heads/train-hold HEAD:refs/heads/b$((i%30+1)) 2>/dev/null; done
