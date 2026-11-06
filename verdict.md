Fix review: merge b4951a08c98c98c94d3050ca4c0bbb627c6f5401

bus-nonce: 5db5bd851a770cd4c6be119c3720517a

## Round

Round 1, first-round adversarial fix review of #3251 (R10-REF-PRIVACY-CLOUD), measured at head b4951a08c98c98c94d3050ca4c0bbb627c6f5401, merge base 57958d6a44c4f489384705ba64e8f65a8507f6b7. Roles diff merge-base...origin/main is empty, so the contract is current.

## Findings

none. Both roster carries are answered by built changes with controls, every mutant I planted was killed, and no seam is left open.

## Evidence

- RESULT carry-1 at base: `ref_privacy.py --check` refuses 2 roster lines (17201, 17209) with HOME=/root and 3 (17201, 17209, 17390) with HOME=/nonexistent, uid 0. That reproduces the carry. File: ev/check_base_head.txt.
- RESULT carry-1 at head: I ran the head's predicate over the base's same added range (80 lines since 4b7e1770ba81). It refuses 0 lines under both HOMEs. `scrub` dry-run on the roster: 0 of 1 file(s) would change under both HOMEs. At the head's own range: 0 refused. Files: ev/head_predicate_on_base.txt and ev/scrub_dry.txt.
- The finder's harness here is the carry's own command, `ref_privacy.py --check` on a uid-0 seat. I ran it myself at both ends on this cloud seat (uid 0, HOME=/root), not through the fixer's self-test.
- Null control: an ad hoc host with HOME=/home/alice and USER=alice still refuses `see /home/alice/x` as home-directory, account-name and host-path, and passes `/root/x`. So the predicate drops only public or placeholder homes. File: ev/null_and_identity.txt.
- Self-tests at the head, under HOME=/root and HOME=/home/runner: ref_privacy 113 checks, 0 failed; heartbeat 8 checks, 0 failed; gh_comment SELF-TEST PASSED; cloud_dispatch 127 checks, 0 failed; cloud-setup 19 checks, 0 failed; structure.py STRUCTURE RATCHET PASSED. These match the body's figures. File: ev/selftests_head.txt.
- Mutants, my own, each restored and the tree clean afterwards (ev/mutants.txt):
  - M1, the of_host filter dropped: 2 failed, the two uid-0 arms. This matches the body.
  - M2, `_public_home` always True: the /Users null control, the heartbeat home arm and the gh_comment wiring arm all fail.
  - M3, NO_HOMES emptied (my mutant, not in the body): the nonexistent arm fails with account-name.
  - M4, the public-home regex widened to any name (my mutant, a widening attack): the /Users null control fails.
  - M5, identity reverted to `seat` in both files: cloud_dispatch reports 127 checks, 1 failed (the value pin), and cloud-setup stays 0 failed. This matches the body's stated gap.
- Carry 2: cloud-setup.sh already exports GIT_AUTHOR_* and GIT_COMMITTER_* from SEAT_NAME and SEAT_EMAIL. Its self-test makes a commit under the exports and checks the author, with a conflicting user.name in config (cloud-setup.sh:158-161). It also has the unset-environment null control at :154-157. The head changes the values to hpo-fixer / 70032254+tvofi@users.noreply.github.com in both sources, and cloud_dispatch's agreement check plus the new value pin bind them. This seat's own environment still reads `seat` because the session-start hook ran on the pre-checkout tree (main), not on this head.
- Class: the body's rule is a git grep for `of_host(`, `ref_privacy.py guard` and identity-less imports. The two arms it found that depend on the real $HOME (heartbeat, gh_comment) are repaired with planted homes and null controls. Mutants M1 and M2 show those arms still bite.
- Merge: `git merge-tree --write-tree origin/main(9cbd7dd0d) b4951a08` rc=0, tree b5083c84f. No conflict. ev/merge_and_scope.txt.
- Untouched: VERSION, RELEASE_NOTES.md and custom_components/ show 0 paths in the three-dot diff. No `*budgets*.json` changed. The delivery row dev/programme/delivery/3251.md is in the three-dot diff.
- I could not re-derive the body's `closure.py select` figure (MODE: SCOPED). Run locally on this detached checkout it prints MODE: FULL with "no changed files could be determined". CI's tests / closure-scope and tests / closures are green at this head.
- CI: `merge_train.py classify b4951a08... --pr 3251` reads GREEN, pending: none, red: none, rc=0 (ev/classify.txt). All 81 check-runs for the head are on one page. The only concluded non-success is governance / instrument-self-tests id 128120413665, cancelled at its 30-min timeout. That is the owner's standing line (R10-PROCESS-SLIM, #3245), and the body names it. The latest pr-contract / pr-contract (128120945847, 19:58Z) concluded success after that cancel (19:51Z).
- The gate failures the body lists (128118470802, 128118465772) are no longer in the head's check-run listing, which now shows gate success. Naming them over-discloses but does no harm.
- `## Head` names b4951a08c98c98c94d3050ca4c0bbb627c6f5401, the head I measured.
- Forward-carry: none named, and none owed. Both carries close here.
