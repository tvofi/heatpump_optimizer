Fix review: blocked c3bc47e86272bc57df9aa387892b7f5dac6f9cbf carry-missing: not carried to R10-ORCH-DISPATCH-REG; both roster append-carry ops are unpushed, absent from handoff/audit-r10-roster 2381e1121 and main 9d0ddf8af, and the body names no roster SHA

bus-nonce: 7b49cb673b455c418b4be91970678345

Round: second review of #2765. The first was review/2765, `blocked 4df5a42f1 carry-missing`.

## Block

The round-1 block asked for each carry to be written into the live group's roster carry on `handoff/audit-r10-roster`, with that SHA named in the body. Round 2 paid it only in part:

- **Paid.** The owner's-call carry and round-1 finding 2 are now in this PR's tree, as two new entries of `dev/programme/carries/carry-201.json` (ev/round2_diff.txt). Each has `from`, `effect`, `control`, `remeasure` and `brief`. The `stage` field now names the owner's decision. `brief_lint.mjs` prints `TOTAL: 0 error(s) across 48 file(s)`.
- **Not paid.** The two carries that change what dispatch must do are the model arm and the planted-defect audit dispatch. Their destination is R10-ORCH-DISPATCH-REG, which is live (`resume.stage: not-started`). Neither carry is in any tree. I read R10-ORCH-DISPATCH-REG's group at origin/main `9d0ddf8af`, at `handoff/audit-r10-roster` `2381e112129c3b02ddaca687874cddcd10d9d979`, and at `handoff/r10-roster-freeze-b`, `-freeze-b-r2`, `-runq` and `-sync-carries-open`. None of them mentions `2765` or `review_strength` (ev/roster_search.txt). The body says this itself: "Not yet in the tree: the roster seat must land them, and the roster branch SHA is owed to this body before merge."

finding-propagation.md and fix-review.md step 10 require the carry to be in the tree before the producing PR merges. A lint-clean local commit on a fixer's machine is not in the tree. The second carry's precondition also points at the carry-201 entry, which lands with this PR. The roster half is still missing, so a DISPATCH-REG seat that starts today would never read either constraint.

To clear the block: get the roster seat to land both `append-carry R10-ORCH-DISPATCH-REG` ops on `handoff/audit-r10-roster`, then name that SHA in the body's `## Forward-carry`. Nothing else in the PR needs to change. The production code and the harness are byte-identical to the round-1 head, whose mutation proof and sweep round 1 verified.

## Findings

- The friction item routes `Carry: R10-FLY-YIELD-GUARD`. The body's own Round 2 section says that group "ends at this merge, so the review's `Carry: R10-FLY-YIELD-GUARD` would reach no seat after it", and moves finding 2 off it for that reason. The friction item, which says carry (2) reads "first-pass merges" where the statistic is incidence, is still addressed to the ending group. `carry_audit.py` accepts it because the group is `in-progress` today. Route it to whoever owns the yield-probe record's carry text, or close it as recorded friction. Carry: R10-FLY-YIELD-GUARD
- The round-1 instrument gap is still open: `carry_audit.py` reads an `absorbed` group as a live destination. This PR does not settle it, and the body correctly leaves it to round 1's routing. In the same way, `carry_audit.py` cannot see whether a roster carry's text is actually in the destination group. This round's body passes `5 routed, 0 bad destination(s)` while two of its carries are absent from the roster (ev/carry_audit.txt). Carry: R10-ORCH-ROSTER-SCHEMA

## Evidence

- Head: PR #2765's head is `c3bc47e86272bc57df9aa387892b7f5dac6f9cbf` (REST pulls API at review time), matching the body's `## Head` (ev/HEAD.txt). Merge base with origin/main is `9d0ddf8af`. `git merge-tree --write-tree origin/main c3bc47e86` exits 0, tree `ecda1cf58`. `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- No production line moved since round 1. `git diff 4df5a42f1 c3bc47e86 -- tools/audit/seat/review_strength.py dev/audit/harnesses/r10_review_strength_mutants.py` is empty (ev/prod_unchanged_since_r1.txt). The authored round-2 commit `b66cbf0be` touches only `dev/programme/carries/carry-201.json`. Round 1's finder's-harness sweep at the code head (`RESULT mutants=3090 killed=3036 survived=54 disposed=54 undisposed=0 stale=0`) therefore still describes this head. I did not re-run it.
- M0 at the head: `review_strength self-test: 114 checks, 0 failed` (ev/selftest_head.txt).
- I re-ran the body's mutants at the head, each restored and checked with `cmp` (ev/hand_mutants_r2.txt):
  - M1, trip forced to False: 5 failed.
  - M7, P0 changed to 0.24: 4 failed.
  - M8, local arm dropped: 1 failed.
  - My own: local N set to 19, 1 failed; cloud N set to 21, 1 failed.
  - All match the body or are killed.
- Round-2 figures re-derived on the bus, fetched at the time in ev/bus_fetch_time.txt (813 verdicts, 0 outside the grammar; the body's fetch had 812). Files: ev/guard_1024T1000.txt and ev/round2_figures.txt.
  - At 10-24T10:00Z: all 3/30, P = 0.0166, would-trip; cloud 3/20, P = 0.1466; local 0/20, P = 0.0014, would-trip.
  - At 10-25T06:00Z: all 2/30, P = 0.0041; cloud 2/20, P = 0.0526, ok; local 0/20.
  - Null cut at 10-20T12:00Z: all 8/30, P = 0.5282; cloud 7/20; local 8/20; every arm ok.
  - The unclassified line has 41 words at 10-24T10:00Z and 51 at 10-25T06:00Z.
  - Widening REAL by the nine words leaves the lines unchanged. Widening by all 41 gives all 6/30, P = 0.2238, ok; cloud 6/20; local 0/20, would-trip.
  - Every figure matches the body and the carry-201 entries.
- carry_audit.py at the head, with the body fetched from the REST API: `CARRY-AUDIT: 5 finding item(s): 5 routed, 0 unrouted, 0 bad destination(s)`, with the roster ref set to origin/main and to `handoff/audit-r10-roster` (ev/carry_audit.txt). So the carry text resolves and R10-ORCH-DISPATCH-REG is an open destination. The block above concerns the content not being in the roster, which this tool does not read.
- VERSION, the manifest version, RELEASE_NOTES.md and the golden and claim files are untouched by the three-dot diff. `tests/structure.py`: STRUCTURE RATCHET PASSED.
- CI on the head, from the check-runs API: 8 runs. `.github/dependabot.yml` succeeded, `arm` was skipped, and prelude, refresh and cancel-superseded (two each) are queued (ev/checks_head.txt). No check is red, so step 11 is not engaged. The head's workflows have not concluded, and there is no mutation or pr-contract run to cite.
- I built no instrument for this review. Every command is in ev/.
