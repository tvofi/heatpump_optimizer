Fix review: blocked 4c875cad33394e55efacc65ffa85ff061eda182e head-moved: measured 4c875cad33394e55efacc65ffa85ff061eda182e, head is c8287e3601643394af397718cf54ddbeee2a9b28

bus-nonce: 697e209e6d0164f95947120da857e6cc

## Block

The dispatched head 4c875cad is no longer the head of #3844. The record beat re-derived the branch twice during this review: review_packet.py first read the head as 9a152f17, and the PR's head is now c8287e36, which the body's `## Head` names. 9a152f17 does not descend from 4c875cad, and `review_carry.py 4c875cad 9a152f17` prints `FRESH-REVIEW` ("force-push: 9a152f177 is not a descendant of 4c875cad3; 2 of 2 branch-only commit(s) carry code"). A verdict on 4c875cad cannot carry to the live head. Re-dispatch at c8287e36, or let `record_row.py --automerge-check` approve it, as the body's `## Approval` provides.

## Evidence

- At 4c875cad, each of the 14 rows that changed state (#3728 #3729 #3735 #3737 #3814 #3821 #3832 #3836 #3839 #3840 #3842 #3843 #3846 #3851) names a short SHA. Each SHA resolves to `Merge pull request #<N>` for that same N, and each is an ancestor of origin/main. #3844's own row is `open`. All 14 rows are correct at that head.
- `git merge-tree --write-tree origin/main 4c875cad` rc=0 (ev/merge_tree.txt): it merges cleanly.
- At render, the packet's gate digest for 4c875cad was green on every required context (ev/review-packet.md). Classify was not waited on, because the head had already moved.
- At render, the packet's refusals were `moved-head` (head 9a152f17) and `head-note`. carry_audit at the head: 0 items. figure_lint: 1 resolved.
- ev/HEAD.txt: the reviewed head and the live `refs/pull/3844/head` at write time. ev/review_carry.txt: the carry check's output.

## Findings

none
