Fix review: merge 6cc0273f6b0693c775f2295576ac40fa2f4ab08d

bus-nonce: 793c4ec6d04aed3bf0ae0c8079b18bf3

## Scope

Round 3, a delta review of #2822 (triage batch 26, `dev/programme/triage/s6-batch26.md`) from round 2's head e40e45eeb9509e44bb93d43373cf777cc62f40d8 (block: comment 6400669887) to 6cc0273f6b0693c775f2295576ac40fa2f4ab08d. This is the third round, so `fixer.md`'s re-cut rule does not apply yet.

## Evidence

- RESULT delta: `git diff e40e45eeb..6cc0273f6` changes 1 file, `dev/programme/triage/s6-batch26.md`, 3 lines changed (3 insertions, 3 deletions). The 3 changed lines are P139's design-verdict times. There is one commit, 6cc0273f6, and it changes nothing else (`ev/delta.diff`).
- RESULT times: fabd19b8a 2026-10-25T17:40:56+01:00 = 16:40:56Z; 636a85b36 17:48:41+01:00 = 16:48:41Z; ad376684f 17:51:54+01:00 = 16:51:54Z. The new text says 16:40Z, 16:48Z and 16:51Z, an exact match. All three commits are ancestors of `origin/design-verdict/R10-HEAT-METER`, and their subjects match the round and verdict stated in P139 (revise 04de6ae7f r1, revise e23ace899 r2, approve 21f4fbfe9 r3) (`ev/p139_times.txt`).
- RESULT P139's other time: 04de6ae7f 17:34:27+01:00 = 16:34:27Z, matching the stated 2026-10-25T16:34Z. It is an ancestor of `origin/design/R10-HEAT-METER`. P139 holds no other `Z` time.
- The body says every other timestamp in the file is already UTC. That is outside this brief's scope, but I checked it anyway. Line 105 says #2671 merged at 2026-10-23T23:20:07Z, and its merged_at is 23:20:07Z. Line 164 says #2524 merged at 2026-10-22T20:16:54Z, and its merged_at is 20:16:54Z (the merge commit fd9914851's committer time is 20:16:53Z, so the stated time is the API's merged_at). Line 175 says `dispatch/fixer-r10-pusher-reap` is at 2026-10-22T18:32Z, and its tip 4347a0b74 was committed at 18:32:48Z (`ev/ci_checkruns.txt`).
- `## Head` names 6cc0273f6b0693c775f2295576ac40fa2f4ab08d on merge base da12aa37dee15b9e9567bd6c848493436f2592dd, which equals `git merge-base origin/main 6cc0273f6b0693c775f2295576ac40fa2f4ab08d`. It describes only the delta: round 2's head plus the one UTC commit.
- Against the merge base, the PR changes 2 files: `dev/programme/delivery/2822.md` (+1) and `dev/programme/triage/s6-batch26.md` (+204). There is no VERSION, manifest or RELEASE_NOTES change. Neither the diff nor the body contains a host or home path (grep for `/home/`, `/Users/`, `/root/` and `/tmp/` found nothing).
- RESULT merge: `git merge-tree --write-tree origin/main 6cc0273f6b0693c775f2295576ac40fa2f4ab08d` gives rc=0, tree 6f3a0bdbc5fd4c2e2f46eccff18fd83a409fdad9 (`ev/merge_and_scope.txt`).
- `dev/governance/roles/` is unchanged between the merge base and origin/main, so the contract I applied is current.
- CI at this head, from the check-runs API: 4 runs. cancel-superseded, refresh and prelude are queued (held), and arm was skipped. None has concluded red, so no red check needs an answer, which matches the body's `## Red checks: none`. Whether those held runs pass will be shown on the head once they run.
- Mutation proof: n/a. The diff writes no production or check code, only a ruling record.

## Findings

- The PR title reads "Merge remote-tracking branch 'origin/main' into triage/s6-batch26", which is a merge commit's subject rather than a description of the triage batch. It is cosmetic, and no gate I read keys on it. Carry: dismissed: cosmetic title, the orchestrator may retitle at merge
