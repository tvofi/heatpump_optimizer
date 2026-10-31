cd $1/w; i=0; end=$((SECONDS+30))
while [ $SECONDS -lt $end ]; do i=$((i+1)); git -c user.name=a -c user.email=a@b commit -q --allow-empty -m m$i; git push -q -f origin HEAD:refs/heads/main 2>/dev/null; done
