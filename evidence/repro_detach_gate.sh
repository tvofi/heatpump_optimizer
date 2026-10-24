#!/bin/sh
# Scratch repo: app_push.sh's committed-tip predicate (HEAD == refs/heads/br, porcelain empty), and the ruling's update-arm re-attach.
S=$(mktemp -d); cd $S && git init -q -b main o && cd o && git -c user.name=a -c user.email=a@b commit -q --allow-empty -m 0 && echo a>f && git add f && git -c user.name=a -c user.email=a@b commit -qm 1 && git branch br && cd .. && git clone -q o m && cd m && git branch -q br origin/br && git worktree add -q ../wt br && cd ../wt
gate(){ head=$(git rev-parse HEAD); tip=$(git rev-parse --verify refs/heads/br); [ "$head" = "$tip" ] && [ -z "$(git status --porcelain)" ] && echo PASS || echo REFUSE; }
git checkout -q --detach; echo "RESULT detached-at-tip gate=$(gate)"
git -c user.name=a -c user.email=a@b commit -q --allow-empty -m row; echo "RESULT detached-then-row-commit gate=$(gate)"
git checkout -q --detach origin/br; echo x>>f; git checkout -q -f -B br origin/br && git reset -q --hard origin/br; echo "RESULT ruling-update-arm sym=$(git symbolic-ref -q HEAD) porcelain=[$(git status --porcelain)] gate=$(gate)"
git checkout -q --detach; echo y>>f; git reset -q --hard origin/br; echo "RESULT todays-update-arm sym=$(git symbolic-ref -q HEAD || echo DETACHED)"
