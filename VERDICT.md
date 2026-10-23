Fix review: merge 91e37c0964e6c203108ae53814dcf1f0a0761bf1

bus-nonce: 1d6b263f3cd8c61f9744e55b6ce5008e

Re-review of #2651 (roster ops only, no group), measured at head 91e37c0964e6c203108ae53814dcf1f0a0761bf1 (PR head re-read via ls-remote: unchanged). Reviewed against the PR body. Previous verdict: merge at 2bb638af. Roles dir unchanged vs main since merge base.

RESULT (1) three-dot roster diff vs origin/main: 61 insertions / 10 deletions. Diff 2bb638af..head on the roster is exactly three added carry lines (+ trailing-comma edits): R10-FLY-CARRY-DISPOSITION (3c8cf18ca), R10-FLOW-DESIGN-STAGES (ad0c114f5), R10-FLY-RELAY-REVIEW-FF (bb7c6eb27). Each carry's text matches the body's description (P-G narrowed 8 to 1 with null control, heading allow-list rejected; stub pinning the dispatch commit SHA; tick_loop stale-checkout restart, no in-place ff). All three groups are resume.stage not-started (not done, not absorbed). Note: the body has no literal "### Triage" headings; it summarises each op, and the roster text begins "Triage ... verbatim". Matched against those summaries.
RESULT (2) groups 167 -> 168, removed [], new [R10-FLY-NO-FOOTERS-EMITTERS], 9 changed. Stage counts done 91 / in-progress 10 / not-started 60 / queued 6 / absorbed 1, as the body says. Null control: git diff --exit-code 8de7e22ac a243a79f4 on the roster rc 0.
RESULT (3) 13 ops: git rev-list --count origin/main..bb7c6eb27 = 13; numstat 61 10 on the roster; the head's two-file diff adds delivery/2651.md (+1).
RESULT (4) brief_lint: TOTAL: 0 error(s); ref_privacy --check: 0 refused; carry_audit pr 2651: 0 finding items, 0 unrouted, 0 bad destinations.
RESULT (5) check-runs, one bulk read at this head: 44 runs: 29 success, 13 skipped, 1 neutral, 1 in_progress (instrument-self-tests, still running at read time; no red, no failure). pr-contract, nightly-status, delivery-status, budget-raise-gate all success.
Merge: git merge-tree --write-tree origin/main head rc 0, no conflicts (origin/main a243a79f4).
VERSION, manifest and notes heading untouched. No production code: mutation proof n/a (body states it). Forward-carry: none claimed and none needed; the carries are roster content. Red checks: none at this head.
Not re-derived / caveat: instrument-self-tests had not concluded; the diff is roster JSON only, so I judge it outside what that check reads, but I did not see it conclude.
Round: re-review, not past the fourth.
