Fix review: blocked bb3933b18fc35aea81c755dceb5e59eb07d3224d mutation-vacuous: rv3-folded-skip-topic-only rv3-wt-not-removed

bus-nonce: e36568a705823d5440a97e9bf44b31c9

## Block

This is round 3, a delta review over the blocked head c562b07972c71226a8cb54d0efd4376c76921c1c. I measured handoff tip bb3933b18fc35aea81c755dceb5e59eb07d3224d. It was still `handoff/r10-review-dispatch-residue-p1`'s tip after the runs (`ev/head-recheck.txt`). The body is BODY.md at handoff-body 8e1d2e995d (`ev/handoff-body-8e1d2e99.md`). The delta is in `tools/audit/seat/cloud_relay.sh` only: the `cloud-folded` skip at :834 is rewritten as one line, the memo write is dropped, the comment is updated, and the self-test gains three checks. No `custom_components/` code changes, so the scope is not widened.

Both mutants that round 2 named are settled. `rv-privref-not-deleted` is KILLED, and `rv-folded-memo-no-entry` no longer has a site because the write is deleted. `r3-folded-skip-off` is KILLED. The full set, which is round 2's spec less the deleted site plus four mutants of my own (`ev/mutants.json`), leaves two survivors (`ev/mutants.txt`):

- `rv3-folded-skip-topic-only` is the one this block turns on. At `cloud_relay.sh:834`, the line this round rewrote, I replaced `grep -qxF "$topic $bsha"` with `grep -q "^$topic "`, so the skip keys on the topic alone and ignores the body. It SURVIVES. Under it, a topic that was folded once and later blocked `CARRY-LANDED` again on a new kept body (`handoff-wip/<topic>-body` moved) is never folded again, so its carries never land. The arm's comment and the body both say the skip is keyed on "(topic, body)". The round's new check moves only the wip ref, and the existing "moved body ref is judged again" null control covers the memo, not this skip. Cure: after cf-a's fold, move `handoff-wip/cf-a-body` and assert that `carry_fold.py` ran a second time for cf-a. That check is the null control for the existing "not folded again" check.
- `rv3-wt-not-removed`: at `cloud_relay.sh:863` I replaced `git worktree remove --force "$wt"` with `true`. It SURVIVES. This line is outside the round-3 delta: the PR moved it from base line 841, and it has not changed since round 1. Its effect is bounded, because the next fold runs `rm -rf "$wt"; git worktree prune` before its `worktree add` (:850). Without the remove, the relay checkout keeps a registered `cloud-fold-code` worktree after every pass that folds. Round 2 blocked `rv-privref-not-deleted`, the private-ref leak, on the same reasoning. I list it so that the survivor list is complete in one round, as the dispatch requires. Cure: either extend the existing post-pass check to assert that `git worktree list` names no `cloud-fold-code`, or record in the body why the leak is accepted.

Under fix-review.md's closing line, a fourth round owes a re-cut (`fixer.md`). Both cures are one self-test line each.

## Evidence

- RESULT named mutants at bb3933b18f (`ev/mutants-named.txt`): NULL SURVIVED. KILLED: rv-privref-not-deleted, r3-folded-skip-off. rc=0.
- RESULT full set at bb3933b18f (`ev/mutants.txt`, driver `tools/audit/seat/mutant_run.py --copy-tree --cmd 'bash tools/audit/seat/cloud_relay.sh --self-test'`): NULL SURVIVED. 16 KILLED: foldref-fetch-head, foldtip-assert-off, foldmemo-drops-line, foldmemo-no-skip, foldttl-never-retry, foldttl-always-retry, foldtip-wide-lsremote, rv-memo-key-ignores-body, rv-blocked-never-stands, rv-memo-not-saved, rv-stub-outside-wt, rv-real-bodypush-outside-wt, rv-privref-not-deleted, rv-nohandoff-not-on-level, r3-folded-skip-off, rv3-folded-not-recorded. 2 SURVIVED: rv3-folded-skip-topic-only, rv3-wt-not-removed. On the body's own 15-mutant set the result is 15 KILLED and NULL SURVIVED, which matches the body.
- RESULT head self-test: `cloud_relay self-test: 444 checks, 0 failed`, rc=0 (`ev/selftest-head.txt`). This matches the body.
- RESULT failing-test-first, re-derived on the head tree with merge-base f24d107bd7's `carry_fold_arm` spliced in: `444 checks, 15 failed`, rc=1 (`ev/selftest-red.txt`). The body's `443 checks, 15 failed` is stated at d6a35eb044. bb3933b18f adds one check, and the base arm passes it because it has the same skip. The two figures agree.
- `cloud_relay.sh` is byte-identical at a7628041dc and f24d107bd7. The base line figures 805, 818, 821 (skip), 838 (`FETCH_HEAD`), 843 and 849 re-derive at f24d107bd7.
- Structure: `STRUCTURE RATCHET PASSED` (`ev/structure.txt`). Archscore: `dS +0.0000 NULL` (`ev/archscore.txt`). Gate scope: `MODE: SCOPED -- 1 script(s) run, 32 scoped out.` (`ev/scope.txt`). `tests/doc_claims.py`: `ALL 315 checks PASSED` (`ev/doc_claims.txt`). All match the body.
- Three-dot diff against the merge base: `dev/programme/delivery/3448.md` and `tools/audit/seat/cloud_relay.sh`. VERSION, the manifest, RELEASE_NOTES.md, both claim files and every `*_budgets.json` are untouched.
- merge-tree: `git merge-tree --write-tree origin/main bb3933b18f` gave rc=0 with origin/main at 0e28afd38b (`ev/merge-tree.txt`). It merges cleanly.
- CI: no pull request carries this head yet; #3448's head is still c562b07972. There is no review packet and no CI run at bb3933b18f, so no red is owed an answer at this head. The owed-reds set is in `ev/owed-reds.txt`. The two reds the dispatch names, `tests / fast (3.14)` (PR #3466's combi census) and `governance / instrument-self-tests` (R10-HOTFIX-PUSHER-CENSUS), are main's.
- Live-relay cost figures (27-33 s, about 181 s a pass) come from the triage. They cannot be re-derived in a cloud seat and are not verified here.

## Findings

none

## Friction

none
