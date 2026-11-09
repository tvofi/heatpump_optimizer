Fix review: merge fe9b0b2036650c7e9c5abf3eef8318bcfff064a9

bus-nonce: 2ee2325dd4c4b52b3af35aee48dbea85

Round 3 (rounds 1 and 2 blocked earlier heads). Head measured: fe9b0b2036650c7e9c5abf3eef8318bcfff064a9 (= code head 0e751cc72e56b153ed6483074358c50407fbd5cf plus an empty-diff merge commit; `git diff 0e751cc fe9b0b2036650c7e9c5abf3eef8318bcfff064a9 --name-only` is empty).

## Evidence

- RESULT merge-tree: `git merge-tree --write-tree origin/main fe9b0b2036650c7e9c5abf3eef8318bcfff064a9` exit 0, prints a tree id only, no CONFLICT and no MERGE-CLAIM line.
- RESULT role-contract drift: main's fix-review.md changed after the merge base (step 13 wording, "block on main only on a real conflict"); read and applied, it does not affect this head.
- RESULT version/claims: the diff touches no VERSION, manifest, RELEASE_NOTES, golden, claim, budget, closures or INERT file; no budget raise, so steps 4, 5 and 14 have nothing to move. standing-tick.md is a 4-line policy edit; the body states it waits on the owner's approving review.
- RESULT self-tests at head (each rc 0): carry_audit 402/0 failed, body_push 36/0, bus 161/0, ledger 101/0, cloud_dispatch 129/0, roster_edit 242/0, carry_fold 6/0, cloud_relay 393/0. These match the body's figures.
- RESULT mutation proof, re-run by me (ev/m1-m4.txt): (1) landed() source read against the brief too -> carry_audit "402 checks, 1 failed" (FAIL #3234 before); (2) blocked_rounds without `sort -u` -> bus FAIL "five re-posts at one head count as one round"; (3) carry_fold_arm foldonly test reduced to the kept-body test -> cloud_relay 393 checks, 6 failed (the mixed-block and no-refusal arms); (4) body_push landed exit 4 -> 1 -> FAIL "REFUSE landed: exit code (4)". Every mutant killed; each restored to a clean tree and baseline cloud_relay is 393/0 (ev/relay.txt).
- RESULT null controls present in the diff and passing: source in carries lands; three distinct blocked heads refuse without a Re-cut note; CARRY-LANDED plus BODY-LINT folds nothing.
- RESULT carry_audit at head (review packet): 2 finding items, 2 routed, 0 unrouted; figure_lint 11 resolved, 0 not verified. Forward-carry destinations (roster carries 5 to 11) sit on the group's existing roster, not in this diff; the body dismisses them as already carried.
- Step 11, red checks: the packet read at 01:35Z shows gate digest green. Two earlier `gate` check runs (ids 128917068063, 128919827773) failed in edit-kind workflow runs with "run(s) [42539741632] at this head are still being judged; their gate decides". That is the documented deferred-gate behaviour (merge_train.py R10-HOTFIX-TRAIN-DEFER-WAIT), not a failure of this diff. The deciding code run 42539741632 has `gate` id 128928008769 success (completed 01:28:58Z), with every other check in that run success or skipped; `pr-contract / pr-contract` success. The round-2 red (instrument-self-tests) is answered in the body and its ledger fix verified here (ledger self-test 101/0).
- CI classify: `merge_train.py classify fe9b0b2036650c7e9c5abf3eef8318bcfff064a9 --pr 3325` exits 1 (RED, red: gate) at 01:35Z because it counts those two deferred edit-run gates beside the green one. I judge the head GREEN on the grounds above, but the orchestrator should know classify itself printed RED. I did not re-run the gate or mutation lane (cited CI's: mutation success, run 42539741632).
- Not re-derived: the body's "mutation proof" for roster_edit C6 (`r10_roster_ops_mutants.py C6`, rc=1 fails=3) was not re-run by me; the roster_edit self-test passes 242/0 at the head. HPO_BUS_TRAIN_STATE is unset here, so the packet's hot-file advisory reads unboarded.
- Class check (step 6): the body's issue names carries 0 to 14, each with an explicit disposition; no enumeration rule is named, and none of the seams is a repeated site of one predicate, so I treat it as a bundle of independent fixes rather than a class.

## Findings

none
