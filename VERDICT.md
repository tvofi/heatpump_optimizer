Fix review: blocked 4df5a42f137bbc9392bb41e79f0d9d08ae956a5b carry-missing: not carried to R10-ORCH-LEDGER or R10-ORCH-DISPATCH-REG; the three forward-carries name R10-ORCH-MACHINERY, which is absorbed, and none is in the roster at main or at handoff/audit-r10-roster 1558cf55f

bus-nonce: 9669ebea5a4ff23f24908b07c7625f2f

Round: first review of #2765 (no earlier verdict on the bus for this PR).

## Block

fix-review.md step 10 and finding-propagation.md's Enforcement section say the producing PR does not merge until the carry is in the tree. For a roster carry, the body names the roster branch SHA. The body's `## Forward-carry` routes three items to `dev/programme/rosters/wave-r10-groups.json` with `Carry: R10-ORCH-MACHINERY`. I checked them as follows:

- At origin/main `0810d5b8f`, R10-ORCH-MACHINERY has `resume.stage: absorbed`. Its note reads "Closed, superseded by the re-cut ... the concerns now sit in R10-ORCH-LEDGER, R10-ORCH-DISPATCH-REG, R10-ORCH-BEATD, R10-ORCH-PLANPAGE and R10-ORCH-ROSTER-SCHEMA ... This group keeps only the no-build records and residuals as carries." Nothing dispatches an absorbed group, so a carry addressed there reaches no seat.
- No R10-ORCH-* group's carries or brief mention the guardrail, the planted-defect audit or the reviewer's model. I checked this at origin/main and at `handoff/audit-r10-roster` `1558cf55fb9073f3d3dbe72c536a186906657775`, and also at `handoff/r10-roster-runq` and `handoff/r10-roster-sync-carries-open` (ev/roster_search.txt).
- The body names no roster branch SHA. The PR has no comments.

Two of the carries change what a later stage must do:

- A model arm needs the ledger or dispatch to write the reviewer's model onto the bus. That is R10-ORCH-LEDGER's or R10-ORCH-DISPATCH-REG's work.
- A trip names a planted-defect audit that nothing dispatches. That is R10-ORCH-DISPATCH-REG's work.

The third, "the guardrail would trip on today's bus", is the owner's call under R13. It belongs on #201, or in a carry file, as the owner's decision. To clear the block, write each carry into the live group's roster carry, with its control as a precondition, on `handoff/audit-r10-roster`, and name that SHA in the body.

`carry_audit.py check` passes this body (`4 routed, 0 bad destination(s)`) because `roster_lib.DONE_STAGES` is `("done", "rca-done")` and leaves out `absorbed`. That instrument gap is carried below.

## Findings

- `tools/audit/carry_audit.py` treats an `absorbed` group as a live destination. `roster_lib.DONE_STAGES = ("done", "rca-done")`, so a carry to a group closed by a re-cut passes `pr-contract` and the train's pre-flight while it reaches no seat. This PR's three carries are the instance. Perturbation: `stage: done` on R10-ORCH-MACHINERY makes the same body a bad destination. Carry: R10-ORCH-ROSTER-SCHEMA
- The `unclassified` line at 10-24T10:00Z lists 41 words. Several of them read as engineering catches: `mutant-survived`, `unpinned-site`, `mutation-unpinned`, `null-control-unpinned`, `figure-wrong`, `body-false`, `spec-unmet`, `closures-under-approximated`, `docs-code-mismatch`. The guardrail is right to route them for classifying rather than count them. Until someone classifies them, k is a lower bound. Sensitivity: widening REAL by those nine leaves every arm's line at 10-24T10:00Z unchanged (all 3/30, cloud 3/20, local 0/20; ev/sensitivity_unclassified.txt), so today's trip does not rest on them. Classifying them belongs to whoever owns REAL's list. Carry: R10-FLY-YIELD-GUARD

## Evidence

- Head: PR #2765's head is `4df5a42f137bbc9392bb41e79f0d9d08ae956a5b`, matching the body's `## Head` and my measurements (ev/HEAD.txt). Merge base with origin/main is `0810d5b8f`. `git merge-tree --write-tree origin/main HEAD` exits 0, tree `88fa271e3`. `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so this contract is current.
- VERSION, the manifest version, RELEASE_NOTES.md and the golden and claim files are untouched by the three-dot diff. `tests/structure.py`: STRUCTURE RATCHET PASSED. `tests/closure.py select`: `MODE: SCOPED -- 0 script(s) run, 33 scoped out.`
- M0: `review_strength self-test: 114 checks, 0 failed` (Python 3.14.7).
- Binomial figures, re-derived independently in float and in exact `Fraction(28,100)` (ev/binom.txt). n=30: k=3 0.0166, k=4 0.0495, k=5 0.1161. n=20: k=1 0.0123, k=2 0.0526, k=3 0.1466. All match the body and the docstring. Null control: at p = 24/85 exactly, n=20 k=2 reads 0.0503, still above ALPHA, and n=30 k=4 reads 0.0468, still below it. The arms' lines therefore do not depend on rounding 24/85 to 0.28. `(1-0.28)^20 = 0.0014` matches.
- Back-test: all nine `all`-arm points reproduce (13, 19, 9, 8, 5, 5, 7, 8 and 3 of 30, with `would-trip` only at 10-24T10:00Z, P = 0.0166). The local arm reads 10, 15, 15, 8, then 0/20 from 10-21T06:00Z. The cloud arm is insufficient before 10-19, with lowest 3/20 (P = 0.1466). Bus fetched 2026-10-24 ~21:15Z (ev/guard_1024T1000.txt, ev/backtest.txt).
- My own hand mutants on the new code, each restored and confirmed with `cmp` (ev/hand_mutants.txt). Every one is killed:
  - family filter dropped: 2 failed
  - `[-n:]` changed to `[:n]`: 4 failed
  - insufficient `<` changed to `<=`: 8 failed
  - first-verdict `min` changed to `max`: 2 failed
  - until cut dropped: 2 failed
  - trip inverted: 7 failed
  - unclassified keeping real words: 3 failed
  - tie-break dropped: 1 failed
  - real counted only on merge: 2 failed
  - local N set to 21: 1 failed
  - ALPHA set to 0.053: 1 failed
  - until taken as the min of the windows: 1 failed
- Finder's harness at the head (`dev/audit/harnesses/r10_review_strength_mutants.py --jobs 4`): `--list` prints `RESULT mutants=3090`, matching the body. The full run at the head prints `RESULT mutants=3090 killed=3036 survived=54 disposed=54 undisposed=0 stale=0`, rc=0, 21:15Z to 22:15Z, with M0 at `114 checks, 0 failed` (ev/sweep_head.txt), matching the body's head figure. I did not re-run the base sweep (`mutants=2612 ... undisposed=0`), so that figure is the body's, not re-derived. The four new DISPOSED entries were read and their reasons hold: no CDF at N in {20, 30} and P0 = 0.28 equals 0.05 (ev/binom.txt), argparse order affects only `--help`, and `until` is a pure read of `wins`.
- REAL_EXTRA equals the record's nine words (yield-probe.md, "Nine block words outside it"). The self-test pins this word for word.
- The friction item (carry (2) says "first-pass merges" where the statistic is incidence) is correct. yield-probe.md's threshold and back-test read incidence.
- CI on the head, read from the check-runs API: arch-score, prelude and refresh succeeded. governance, tests, codeql, validate, kernel-points and hassfest were skipped, because the PR is a draft. budget-raise-gate, cancel-superseded and a second prelude/refresh were queued. No check was red, so step 11 is not engaged. No `mutation` or `pr-contract` run exists on this head to cite.
- I built no instrument for this review. The sensitivity run and the binomial check are command lines, in ev/.
