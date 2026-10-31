Fix review: merge c85c5f9b314477ed02df421f2d40381574d8fb7b

bus-nonce: fd5e7da01a2f13ec678dd6a187fd4217

## Summary
Round 1 of PR #3043, a record PR (triage s9 batch 91: P329 ACCEPT narrowed, P330 ACCEPT narrowed). The diff is two files (`dev/programme/triage/s6-batch91.md`, `dev/programme/delivery/3043.md`); no production code, VERSION or claim file. Reviewed head c85c5f9b314477ed02df421f2d40381574d8fb7b.

## Findings
- The P329 carry is not on the roster yet. At `handoff/audit-r10-roster` tip e7cc45559, `R10-FLY-RELAY-REVIEW-FF` has 15 carries and none cites `s6-batch91.md#P329` or holds the approval-sentence text. This is by construction, since `roster_edit.py` needs the ruling on main before it accepts the cite (the body calls the roster ops "held"). The `append-carry` for P329 (and P330 on R10-FLY-TRAIN-DEFAULTS) is owed right after this merges, and the body's `## Forward-carry: none` does not say so. Carry: R10-FLY-RELAY-REVIEW-FF | #3043 | O1 | dismissed: owed by the merge seat after this PR merges, because the triage gate cannot accept the cite before the ruling is on main
- The body's "69 flagged items, 19 with a Carry marker" is not re-derivable. Over all 485 `verdict/*` refs now (484 at the ruling), my count of flagged items in non-bulleted prose or a `Summary` section outside `## Evidence` is 47, with 11 holding a `Carry:` marker. The ruling's definition is not given, so only the direction is confirmed: routed findings do sit in such prose. Carry: R10-TRIAGE-S6 | #3043 | O2 | dismissed: the rejection of arm (a) stands on the named examples and on the 11 routed items under my count, so a different definition does not change the ruling
- The delivery row `dev/programme/delivery/3043.md` names PR #3043 and its state, not a head SHA. It is in the three-dot diff. Carry: R10-TRIAGE-S6 | #3043 | O3 | dismissed: delivery rows record the PR, not a head, until merge

## Evidence
- RESULT (a): examples confirmed in the verdict refs. #2549 `01ce8b81` (Residual, not blocking), #2217 `aab127ea` (Observation, no block) and #2386 `97a3b64e`/`e414e101` (numbered under a lead) are flagged non-Evidence prose. Exactly two items are flagged under a `Summary` heading: #3013 `fccf8846` and #3038 `7dba2920`. #3005 `e963066e` sits under `## Round`.
- RESULT (a) prototype: the ruling's two regexes, applied to #3013 fccf8846, #3005 e963066e, #2997 a7dc6fe0 and #3004 fdeb7c52, take each from flagged to clear. The fixture "approving review is required at merge. This review does not block on it." goes clear. The null rows "...A defect in y is left in place, not blocking." and "x.py is code-owned and a defect in it does not block." stay flagged. #2281 e9ead054 and #2867 fe436106/9132bbad carry no approval sentence.
- RESULT (c): `roster_edit.ruling_verdict` reads P329 and P330 as ACCEPT, and `triage_refusal` returns None for both cites. With the verdict flipped to REJECT it refuses: "s6-batch91.md#P329 is not an ACCEPT ruling (REJECT)", and the same for P330. With the file absent: "not on the roster branch or origin/main".
- RESULT budgets: `policy_lint.mjs --budgets` shows standing-merge.md 36/37 lines and 501/507 tokens, and fix-review (briefs) 137/140, as the body says. `carry_audit.py` is not in the table.
- RESULT merge: `git merge-tree --write-tree origin/main HEAD` exits 0, with no conflict.
- RESULT scope: the three-dot diff holds only the two files, so VERSION, the manifest, the release notes and the claim files are untouched.
- RESULT CI: `merge_train.py classify c85c5f9b314477ed02df421f2d40381574d8fb7b` exits 0, GREEN (pending none, red none).
- Not verified: the 30-verdict figures (11 flagged, 5 without a marker), the 7 PARK lines in the train log (orchestration dir, not reachable here), and the P330 sequencer facts (`seq3.sh`/`seq4.sh`, scratch files off the tree).
- Round 1; head not moved since measured.
