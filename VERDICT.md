Fix review: merge 9292cdd99338222df30454039c6ea4cfcfbe9963

bus-nonce: 483cf9709390edbff85f86b740d48cc1

## Round

Round 3 (delta review after the blocked round-2 verdict, review/2772, carry-missing). The brief scopes this round to the carry; the rest of round 2's evidence is carried.

## Findings

- None this PR leaves open. The roster carry is in place, and the round-2 block (carry-missing) is settled. Carry: dismissed: no open item; the carry is verified at the roster tip.

## Evidence

- RESULT carry: the tip of origin/handoff/audit-r10-roster is 2124781cf86064c9bba6639755f73d60b5d54627, which is the Roster SHA the body names. R10-FLOW-AUTOTRAIN's carry list there has 10 entries. Index 9 is the text added at 2381e112129c, which is an ancestor of the tip. It is 562 characters long, matching the body's "562/562". It states exactly the four items: (1) the queue builder at b3dceb5ca has no policy exclusion, so P84's "lift the exclusion" has nothing to lift; (2) `Train.admit_add` in tools/audit/seat/merge_train.py is the admission seam; (3) `launch_detached` replaces launch_train; (4) the live-train check reads `queue.open` as well as `train.pid`. It also states its control as a precondition: re-measure against the merged train, not the b3dceb5ca base (finding-propagation.md). It is prose, not a host path. ev/carry.txt
- RESULT bare-path: the tracked dev/programme/rosters/wave-r10-groups.json has 0 host-path matches and 0 carry entries that are just a path, in all groups, at both the roster tip and origin/main 662a3809ced4. The bare-path entry from 4937d60fe is gone from the file at the tip, and 4937d60fe is not in origin/main's ancestry. ev/carry.txt
- RESULT code: the three-dot diff (merge-base...head) at 9292cdd99338222df30454039c6ea4cfcfbe9963 is byte-identical to the one at 94da32128301, the head round 2 verified. 9292cdd99 adds only a merge of origin/main 662a3809c. Six paths changed: the harness, delivery row 2772, tests/closures.json, INSTRUMENTS.md, merge_train.py and train.sh. VERSION, the manifest and RELEASE_NOTES are untouched. ev/code-and-merge.txt
- RESULT merge: `git merge-tree --write-tree origin/main 9292cdd99338222df30454039c6ea4cfcfbe9963` exits 0 with tree d377f27b8f72. ev/code-and-merge.txt
- Carried from round 2 without re-taking them: the mutation proof (28 run, 0 not as required), the self-test counts, harness headers, the closure scope, and the red-checks answers for `tests / fast (3.14)`, `pr-contract` and `gate`. The code is unchanged, so this delta did not re-run them, following the tvofi 2026-09-30 rule to cite CI's heavy runs.
- CI at this head: when I read it, every workflow was still queued (prelude, refresh and cancel-superseded in two runs; arm was skipped). No check had concluded red, so step 11 had no new red to answer. I did not observe a green gate at this head. ev/checks.txt
- Head check (step 12): the PR's head.sha was 9292cdd99338222df30454039c6ea4cfcfbe9963 when I read it, and it matches the body's `## Head`.
