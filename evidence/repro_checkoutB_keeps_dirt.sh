# scratch repo: a branch br on origin, a worktree on it detached and left with a tracked edit
git init -q --bare o.git && git clone -q o.git m && cd m
git -c user.name=a -c user.email=a@a commit -q --allow-empty -m init
echo a>f && git add f && git -c user.name=a -c user.email=a@a commit -qm f && git push -q origin HEAD:refs/heads/br
git worktree add -q -B br ../wt origin/br && cd ../wt && git checkout -q --detach && echo EDIT>>f
(git fetch -q origin br && git reset -q --hard origin/br); echo "A reset --hard: head=$(git symbolic-ref -q HEAD || echo detached) dirty=[$(git status --porcelain)]"
echo EDIT>>f
(git fetch -q origin br && git checkout -q -B br origin/br); echo "B checkout -B: head=$(git symbolic-ref -q HEAD || echo detached) dirty=[$(git status --porcelain)]"
git diff --quiet || git -c user.name=a -c user.email=a@a commit -qam "claims: drop"; echo "B then the arm's commit -qam: $(git show --stat --format=%s HEAD | head -3 | tr '\n' ' ')"
git checkout -q --detach; git reset -q --hard origin/br; echo EDIT>>f
git checkout -q -f -B br origin/br; echo "C checkout -f -B: head=$(git symbolic-ref -q HEAD) dirty=[$(git status --porcelain)]"
