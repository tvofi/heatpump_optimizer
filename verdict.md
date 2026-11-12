Fix review: blocked ab764c5862fb9aacf2f29b5d0b61f97022bc609c stale-dispatch: head already merged to main by PR #3222 (d1cab99a1, 2026-11-05) after a merge verdict at 645f009eb

bus-nonce: f9d9084996f5a671fa538af92f002092

## Block

- The dispatch says this is a handoff review before the pull request exists. That is false at this head. ab764c5862fb9aacf2f29b5d0b61f97022bc609c is an ancestor of origin/main. The PR branch fix/r10-seat-identity-guards merged it at 645f009eb ("Merge commit 'ab764c58...'"), then took two origin/main merges (e5c33700f, 09c5e9710), and main merged it as PR #3222 at d1cab99a11ea3a1d92976f0355f9eb3ee68cd259 on 2026-11-05. A fix review already returned `Fix review: merge 645f009eb00999f26bb93b469412e5ef8c21e0d7` on probe/rev-3222-fc0e797f (2026-11-05 15:19 UTC).
- The dispatch commits 27deb8132 and b11bf0bd1 are dated 2026-11-12 06:28 +0100, a week after the merge, so this looks like a re-fired or re-created dispatch. A pre-merge verdict cannot gate a patch that is already on main. I'm returning blocked so the train does not read a `merge` here as a fresh gate. If something in this change is still owed, it needs a post-merge dispatch or an issue, not this seat.

## Evidence

- Round: first and only round under this nonce. No review packet exists and no CI was waited on, because the dispatch states the PR does not exist. The PR did exist (#3222), and its checks were not re-read here.
- Provenance (ancestry, merge commit, prior verdict refs, dispatch dates, merge-tree): ev/provenance.txt. `git merge-tree --write-tree origin/main ab764c58` exits 0 with no conflict. That is trivially true, because the head is in main.
- RESULT ref_privacy self-test at head: 109 checks, 0 failed. This matches the body's figure.
- RESULT mutation 1 (anthropic-identity class made unmatchable at ref_privacy.py:252): 109 checks, 4 failed. These are the same four arms the body names: the class arm, two guard-CLI arms and the body_push runner-default arm. See ev/mutation-ref_privacy.txt. Not vacuous.
- Not re-derived, given the block: mutations 2 and 3 (body_push.sh guard, prepr.sh body_privacy_line), the cloud_dispatch, cloud-setup and prepr self-test counts, the entities count, and the scope line. These figures are unverified by this seat.
- Head SHA in the body's ## Head equals the dispatched head: ab764c5862fb9aacf2f29b5d0b61f97022bc609c.
