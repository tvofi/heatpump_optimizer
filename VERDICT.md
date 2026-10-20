Fix review: merge 8864a760ee0fa0ec7bdfbffa77bf04d4826f89c2

bus-nonce: 2fd04c73ee84f19c5d988c7fcd21667c

RESULT merge: parents are a3f7c328 and d1db05df; git merge-tree --write-tree a3f7c328 d1db05dfc exits 0 and gives tree cc9eaf81, equal to the head's tree.
RESULT pr-diff: git diff d1db05df 8864a760ee0fa0ec7bdfbffa77bf04d4826f89c2 and git diff 4a3cbcf6 (merge-base of main and a3f7c328) a3f7c328 are identical apart from index lines (10 files, 154 insertions, 18 deletions in both); nothing new.
RESULT main: git merge-tree --write-tree origin/main 8864a760ee0fa0ec7bdfbffa77bf04d4826f89c2 exits 0 against current main d5cd0031 (main has moved past d1db05df; still clean).
RESULT ci: 49 check-runs at the head via the API, none red or pending.
Round: delta review after the a3f7c328 pass.
