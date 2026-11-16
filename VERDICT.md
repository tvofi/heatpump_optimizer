Fix review: blocked 87a315a355faa219065ed906ed3adbd4d589aacd mutation-survivor: apply() ceiling taken from editCeiling() instead of applyEnd survives every card check

bus-nonce: ff5cb03a2451b37138d30b67c1630afb

## Block

- The PR's stated design point is not pinned by any test. The body says the apply ceiling "does not use `editCeiling`, which also takes the zoomed visible end into account, so a zoomed-in view does not change what is applied", and the new test block's header says it pins "the published window (`applyEnd`), not the zoomed visible end `editCeiling` also carries". Mutant M5 replaces `const hi = this.ceilingParts().applyEnd - APPLY_CLOCK_SKEW_MS;` with `const hi = this.editCeiling() - APPLY_CLOCK_SKEW_MS;` at `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:11590`, and `node tests/card.mjs` still prints `ALL CARD CHECKS PASSED` (ev/card-M5.txt). The test harness never sets the host's geometry, so `geomAt()` is null, `visibleEnd` is Infinity, and on the extended 48 h plan `editCeiling()` equals `applyEnd`: the test cannot tell the two apart.
- The mutant is not equivalent. I added a reviewer probe check to the same block (ev/reviewer-zoom-probe.diff): it zooms in so the visible end is 3 h before the window (`c.geomAt = () => ({ windowStart: 0, windowEnd: at(-3) })`) and expects the dhw payload `[[-4,-3],[-2,0.5]]`. It passes at the head (ev/card-probe-head.txt) and fails under M5 (ev/card-probe-M5.txt: `FAIL REVIEWER PROBE zoomed view does not change the applied dhw runs`). Under M5, a user who zooms in before pressing "Apply this plan" silently loses every run past the visible end.
- What would settle it: a check in the #3636 block with a zoomed `geomAt()` that kills M5. The probe above is one way to write it.

## Findings

- Residual: upper side of the clock-skew allowance unpinned: mutant M8 (`APPLY_CLOCK_SKEW_MS = 2 * PLAN_STEP_MS`) survives all card checks (ev/card-M8.txt). The checks pin that a run starting within one step of the window is held back, but none pins that a run starting just over one step before the window is still sent. So a wider allowance, which holds back runs the server would accept, passes. A space or dhw run starting about two steps before the ceiling, expected in the payload, would kill it. Carry: R11-OUTSIDE-APPLY-PLAN-CEILING
- Follow-up: there is no committed finder's harness (fix-review.md step 9). #3636 is an outside report, and the body says so. The reporter's repro is encoded as the committed #3636 card checks, which fail 3 of 6 at the merge base and pass at the head; that harness is the fixer's, not a finder's. Carry: dismissed: outside report with no finder harness; disclosed in the body and encoded as committed card checks

## Evidence

- Round: first review round of this PR (review scope full, no prior reviewed head).
- Head reviewed: 87a315a355faa219065ed906ed3adbd4d589aacd (ev/HEAD.txt). The PR body names it as head. The body's earlier measurement head 9f66f1cc43563528dbf526bc5e2ba83c696210fb is an ancestor, and `review_carry.py 9f66f1cc… 87a315a3…` prints `CARRY` (only a main merge and the delivery row since).
- Merge with main: `git merge-tree --write-tree origin/main 87a315a3…` exit 0, tree 6ec9b1cfb6a2b535fbb633abb575e14bcb39590e. No conflict.
- Role files current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
- Mutation proof at the head, HPO_PLANDATA from `tests/plan_view.py` at the head (ev/plan_view.txt), then `node tests/card.mjs` (ev/mutants-summary.txt, ev/card-M*.txt):
  - RESULT unmutated: ALL CARD CHECKS PASSED (ev/card-head.txt)
  - RESULT M1 (predicate `r.start < hi` removed): 3 CARD CHECK(S) FAILED, the three checks the body names. Killed, as claimed.
  - RESULT M2 (`APPLY_CLOCK_SKEW_MS = 0`): 1 failed (the clock-skew check). Killed, as claimed.
  - RESULT M3 (`r.start <= hi`): 1 failed. Killed.
  - RESULT M4 (`applyEnd + APPLY_CLOCK_SKEW_MS`): 1 failed. Killed.
  - RESULT M5 (`hi` from `editCeiling()`): ALL CARD CHECKS PASSED. Survivor; see Block.
  - RESULT M6 (`const [lo] = this.bounds();`): ALL CARD CHECKS PASSED. Equivalent mutant: `bounds()[0]` is `editFloor()`.
  - RESULT M7 (`r.end <= hi` in place of `r.start < hi`): 1 failed (straddling run). Killed.
  - RESULT M8 (skew = 2 steps): ALL CARD CHECKS PASSED. Survivor; see Findings.
- Failing test first: the head's tests/card.mjs on merge-base e30408f7881cd5602a2c4d7ea9517b0d765652f6 code gives 3 CARD CHECK(S) FAILED. Those are the three #3636 checks the body names; the other three #3636 checks pass (ev/card-base-newtest.txt). Matches the body.
- Null control: `a plan wholly inside the window sends the same payload (#3636)` and `the captured plan ends inside the window (#3636)` pass at the head. They pass under M1 and M2 too (ev/card-M1.txt, ev/card-M2.txt), as the body says.
- Backend consistency: `build_override` (custom_components/heatpump_optimizer/manual_plan.py) refuses a slot only when its start is strictly after `now + MANUAL_PLAN_WINDOW_HOURS`. The card holds back starts at or after `applyEnd - PLAN_STEP_MS`. That is strictly inside the server's acceptance for any browser clock at most one step fast, and only drops runs on a slow clock. The body's reasoning holds.
- Class enumeration: `git grep -n '"apply_manual_plan"' -- custom_components/heatpump_optimizer/www` returns one site, heatpump-optimizer-card.js:11615 inside `ManualPlan.apply()`, which is in the diff (ev/seam-grep.txt). A one-seam class.
- Figures re-derived at the head: `MODE: SCOPED -- 9 script(s) run, 24 scoped out.` (ev/closure-select.txt); `STRUCTURE RATCHET PASSED` (ev/structure.txt); `Architecture score: dS +0.0000 NULL` (ev/archscore.txt); `ALL 2723 ENTITY CHECKS PASSED` rc 0 (ev/entities.txt). All match the body. The features count (`ALL 5710 FEATURE CHECKS PASSED`) is not re-derived: my run was still in progress at the push (partial log in ev/features.txt); it rests on CI's green `tests / fast`.
- VERSION, the manifest version and the RELEASE_NOTES heading: untouched. The three-dot diff touches only the card JS, tests/card.mjs and dev/programme/delivery/3649.md.
- Claim files: untouched by the diff. No golden or claim drift applies to a card-only change with no fixture movement.
- No figure the diff moves (no budget, closures, ledger or score change).
- CI: `merge_train.py classify 87a315a3… --pr 3649` printed WAIT from 00:49 and exited 0 (GREEN) at 01:14:41 UTC, last line: `GREEN 87a315a355faa219065ed906ed3adbd4d589aacd pending: none red: none` (ev/classify-rc.txt, ev/classify.txt). The review packet's `introduced-red` refusal came from `governance / instrument-self-tests` still in progress at render; classify at GREEN supersedes it.
- Red checks: none. Classify reads `red: none` at the head, so no `## Red checks` answer is owed.
- Forward-carry: the body states none; this change alters no later stage.
