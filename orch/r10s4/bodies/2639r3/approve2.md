Agent approval for the code-owned `.github/workflows/governance.yml` line in this PR. The orchestrator gives it under mandate 6329234399 (scope all), at head 84900f1e0fe7eee17451478edbd13573bd163d76.

Basis: `Fix review: merge 1cf9ca11b30c639c7608f549ba94a08e9b3f10b1` (round 3, BUS 93fcf88f), carried to 84900f1e by the merge train's main merge. I checked the carry: 84900f1e's parents are 1cf9ca11 and main a243a79f, and `git merge-tree --write-tree 1cf9ca11 a243a79f` equals the head's tree. The merge adds nothing beyond main.
