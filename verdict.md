Fix review: merge 82b63f10988b6450c6d0779eb93b07b500bd1cc1

bus-nonce: 9638dd4a14223262dea4400f75941fa9

## Scope

Review scope: delta, a later round over the reviewed head 34466736f2f4e9b7d2e7e448652904c6e9d65d4f, whose verdict was merge. The delta 34466736f2..82b63f1098 is two merges of origin/main, which bring in #3566, #3626, #3629 and #3634. The PR's own three-dot diff still touches the same four files. Three of them have blob ids identical to the reviewed head: fix-review.md, the RCA record and delivery/3638.md. Only `dev/governance/roles/fixer.md` differs, as the conflict resolution against main's rewrite of step 5 and its removal of the gate-lease paragraph. No `custom_components/` line moves, so nothing widens the scope. This verdict does not stand in for the owner's approving review that a policy change needs.

## Evidence

- RESULT own-diff delta: the only change from the reviewed own diff is in fixer.md step 5. Main replaced "(`ci-autofix.md`'s wait starts at the PR)" and the following lines with its "Prepr runs scoped" text. The branch keeps main's text and re-attaches its own clause "(a red `UNDER-SCOPED` or `INHERITED CLAIMS` is answered by naming it)" after "before the handoff". The step 3 latch sentence and the removed "Before you hand off" section are unchanged from the reviewed head (ev/own-diff-delta.txt).
- RESULT the resolution is faithful. Main's prepr-scoped ruling text is kept verbatim, and the PR's clause survives with the same meaning. It drops nothing main added and restores nothing main removed (the gate-lease paragraph stays removed, and the 0011 citation stays at main's new location in step 6).
- RESULT policy at the head: policy_lint reports 0 errors across 51 files. Budgets: fixer.md 313/315 lines and 5203/5216 tokens; fix-review.md 138/140 lines and 2775/2775 tokens; corpus ~65925 against cap 65926 + band 500. check-wave-script: 223 passed, 0 failed. rules_sync: ok. review_packet self-test: 133 checks, 0 failed. Role files show no drift against main. No VERSION, manifest, RELEASE_NOTES, custom_components, tests or tools file appears in the three-dot diff (ev/policy-checks.txt).
- Mutation M4: deleting the re-attached clause leaves policy_lint, check-wave-script and the review_packet self-test green. No instrument pins it, so it is policy wording for the owner's review. It does not block (ev/mutants.txt).
- RESULT merge with main: `git merge-tree --write-tree origin/main 82b63f1098` rc=0 (ev/merge-tree.txt).
- RESULT PR head read live (refs/pull/3638/head) equals 82b63f10988b6450c6d0779eb93b07b500bd1cc1.
- CI: `merge_train.py classify 82b63f10988b6450c6d0779eb93b07b500bd1cc1 --pr 3638` printed `GREEN 82b63f10988b6450c6d0779eb93b07b500bd1cc1 pending: none red: none` (ev/classify.txt). The packet digest's `gate` failure was the provisional red while the run was pending; classify decides.
- The previous verdict's single finding was a wording note, dismissed for the owner's review at merge. The delta leaves step 2 untouched, so the note stands as carried.

## Findings

- Note: wording: step 2 loses "printing your own `RESULT` lines". This is carried from the previous round and unchanged by the delta. Carry: dismissed: the obligation survives in the closing paragraph and the owner reviews policy wording at merge

## Red checks

none at the head (classify GREEN).
