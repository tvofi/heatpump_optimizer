set -u
H=b7ea3bd28c718b6844575c70ec1d234cc90e84fe
git cat-file -t $H || git fetch -q origin $H
echo "--- log handoff"; git log --oneline -4 origin/handoff/r9-f10-merge-queue-2
echo "--- parents"; git log -1 --format='%H %P %an <%ae>%n%s' $H
echo "--- handoff vs H"; git diff --stat $H origin/handoff/r9-f10-merge-queue-2
MT=$(git merge-tree --write-tree 8a0ca90ab2b948236424a4346abe7682b5760500 283accde7c04e8dcddeaf3809c217017d7c43f06 | head -1); echo "merge-tree=$MT rc"
echo "--- MT vs H tree"; git diff --stat $MT $H^{tree}
echo "--- authored stage2 vs main-merge content"
B=$(git merge-base 8a0ca90a 283accde); echo base=$B
git diff $B 283accde > /tmp/claude-0/-home-user/3641f72f-e6e6-5960-a9aa-131dcae989d4/scratchpad/a.diff
git diff 8a0ca90a $H > /tmp/claude-0/-home-user/3641f72f-e6e6-5960-a9aa-131dcae989d4/scratchpad/b.diff
git diff --stat $B 283accde | tail -1; git diff --stat 8a0ca90a $H | tail -1
diff <(git diff --name-only $B 283accde) <(git diff --name-only 8a0ca90a $H) && echo SAME-FILES
diff <(grep -E '^[+-]' /tmp/claude-0/-home-user/3641f72f-e6e6-5960-a9aa-131dcae989d4/scratchpad/a.diff | grep -vE '^(\+\+\+|---)' ) <(grep -E '^[+-]' /tmp/claude-0/-home-user/3641f72f-e6e6-5960-a9aa-131dcae989d4/scratchpad/b.diff | grep -vE '^(\+\+\+|---)') && echo SAME-PM-LINES
echo "--- files changed on both sides"; comm -12 <(git diff --name-only $B 8a0ca90a|sort) <(git diff --name-only $B 283accde|sort)
