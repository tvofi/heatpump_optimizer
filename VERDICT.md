Fix review: blocked 4a81d718e03564dc1b0de06ee5a68edc98d13096 carry-missing: G1-G3 not carried to R10-FLOW-JIDOKA or R10-POLICY-LINT-FAMILY

bus-nonce: 1d103dab1b2a39330189057d035e8fb1

## Block

fix-review.md step 10. The body's `## Forward-carry`, and section `## Forward-carry` of `dev/audit/rca/R10-RCA-BODY-CHECK-PARITY.md`, say G1, G2 and G3 "land in dev/programme/rosters/wave-r10-groups.json". They do not. Neither the `brief` nor the `carry` list of R10-FLOW-JIDOKA or R10-POLICY-LINT-FAMILY holds any of them, either at origin/main `50af6174f` or at the roster handoff `handoff/audit-r10-roster` `717f7e582`. A carry that exists only in this PR's body and in a record no seat is dispatched to read is not propagation (`finding-propagation.md`, "A comment is not propagation").

- **G3's destination has already finished.** R10-POLICY-LINT-FAMILY merged as #2669 (head `0506a55b2`, an ancestor of `50af6174f`, merged 2026-10-23T19:12Z). The roster handoff ref records it as `done` (pr 2669). #2669's own `## Forward-carry` is `none`, and it did not unify `isNone` and `NONE_ITEM`. A carry to that group reaches no seat. The record's status line "Neither carry destination has started ... both at `resume.stage: not-started`" reads a stale stage on main's copy of the roster. That stage is not the group's state, so the status section misstates G3's owner as pending.
- **G1 and G2 are not in JIDOKA's brief.** The only parity requirement JIDOKA holds, P-Q on `717f7e58` (not on main), scopes the test to "the checks pr-contract.yml runs on a body". That is exactly the scope G1 calls insufficient, because P-F's grader is in `budget-raise-gate.yml` and `gate.py --body` is in `arch-score.yml`. Nothing there names a twin table or argv pin (G2), or the G2/G1 demonstration mutants.

To repair: `roster_edit.py append-carry R10-FLOW-JIDOKA` for G1 and G2, each with its control (section 4's demonstrations), and route G3 to a live group, or record that it is dismissed. Then correct the record's status line and the body's figure line on the stages.

## Findings

- G1 (parity test must enumerate every workflow step that reads the PR body: pr-contract.yml, arch-score.yml, budget-raise-gate.yml) and G2 (twin table pinning each body step's CI argv against the twin's, with the mutant editing one carry-step argument) are absent from R10-FLOW-JIDOKA's brief and carry at origin/main and at handoff/audit-r10-roster 717f7e582. Carry: R10-FLOW-JIDOKA
- G3 (one parser must own `## Forward-carry`; policy_lint isNone/path demand against carry_audit NONE_ITEM/seg_dests) is addressed to R10-POLICY-LINT-FAMILY, which merged as #2669 without it; it needs a live owning group. Carry: R10-POLICY-LINT-FAMILY
- The status section of R10-RCA-BODY-CHECK-PARITY.md and the body's `## Figures` state both groups are not-started; R10-POLICY-LINT-FAMILY is merged (#2669) and JIDOKA is in-progress on the roster handoff. The line must be corrected in this PR. Carry: R10-FLOW-JIDOKA

## Evidence

- Round: first review this seat holds of #2691.
- Head reviewed: `4a81d718e03564dc1b0de06ee5a68edc98d13096` (ev/HEAD.txt). PR head at review time: the same. The body's `## Head` names this SHA, plus the authored head `16500c740` one commit back, which holds only `dev/programme/delivery/2691.md`.
- Diff (three-dot from `50af6174f`): 3 files, 469 insertions, all markdown. `VERSION`, the manifest, `RELEASE_NOTES.md`, `tests/golden` and both claim files are untouched.
- `git merge-tree --write-tree origin/main 4a81d718e03564dc1b0de06ee5a68edc98d13096`: rc 0, tree `5c54aae1f` (ev/merge-tree.txt). There is no conflict.
- CI on the head: 52 check runs, each `success` or `skipped`, none `failure`. That includes pr-contract (two runs), gate, closures, entities and arch-score. `## Red checks: none` agrees with the checks.
- Mutation proof (step 1) is n/a. The diff writes no production line, so the mutation lane draws no mutant. Null control: `git ls-tree 50af6174f dev/audit/rca/R10-HANDOFF-PREPR-BOUNCE.md` prints nothing at base. The three citations the body names (`body_push.sh:17`, `INSTRUMENTS.md:127`, `bugclasses.json:2336`) each cite R10-HANDOFF-PREPR-BOUNCE at base, and the file resolves at head.
- Provenance: `R10-HANDOFF-PREPR-BOUNCE.md` at head equals `git show 5fa9ffce0:` of the same path, plus only an inserted 29-line status section (ev/handoff-record-vs-5fa9ffce0.diff). `5fa9ffce0` is 3959 commits behind `50af6174f`, matching the body. `R10-RCA-BODY-CHECK-PARITY.md` sections 1-4 match `BODY.md` at `4fd3eef16` line for line except heading level (### to ##) (handoff-body/r10-rca-body-check-parity).
- Figures re-derived at `50af6174f` (ev/figures.txt): harness siblings 102, 139 inert_reads, 35 and 15 closures commits, `rederive` 0, `predict|prepr` 2, `carry_audit` 0 and 0, `isNone` at policy_lint.mjs:6244, `NONE_ITEM` at carry_audit.py:94, prepr.sh:3130 line present. All match the body.
- Not re-derivable: "99 handoff refs" is a live `ls-remote` count, not a figure of the tree, and it reads 108 now. It cannot be re-taken at the measurement moment, so I have not verified it.
- The "not-started" stage figure is literally true of main's roster file, and false as the groups' state (see Block).
- Figures the records label as the original seat's measurements (the 14 reds, 43.1 min, 58 of 176, timings) were not re-run, and the records say so.
- The record's statement that a full prepr now runs carry_audit through `ci_predict.py --body` (U9d, prepr.sh:3142) was not independently checked by this seat.
