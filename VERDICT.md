Fix review: merge 07b83e9b28ab3a21e3a1ad8d9b38eea27ee707e0
bus-nonce: e738724dcd211079d8fd05c95c62c121

Review round 2 of #2683 (R10-INPUT-STALENESS, Closes #2234), at head `07b83e9b28ab3a21e3a1ad8d9b38eea27ee707e0`. The head is unchanged since round 1 (review/2683 486e987d5), so every round-1 measurement stands at this head: the finder's harness (power 39, mode 47, polling 0 at the base, all three 0 at the head), the six instance probes and my disclosed humidity arm, the failing-test-first run, mutants M1–M4 killed, plants P1 and P2 caught, and the structure −8 earned. Evidence is under `evidence/` (round-1 files carried over).

## Round-1 blocker resolved: forward-carry in the tree (step 10)

`origin/handoff/audit-r10-roster` at `93007df25c205508cf1802cd38e78271db0fe033` has both `8d6527c07` and `57bb4b33e` as ancestors (`git merge-base --is-ancestor`).

- **R10-HEAT-METER** has one `carry` entry starting "From R10-INPUT-STALENESS (#2683". It states the constraint: a new `INPUT_MAX_AGE_MINUTES` key needs its on-change decision, either `math.inf` for a total_increasing counter or a reasoned `_r10st_same` entry. It states the control: the head passes, a planted undeclared key fails 1 check, and a reverted power limit fails 3, both measured in round 1. It states the precondition: a dead-meter test must re-report before going silent, and an old `last_updated` alone now reads fresh on an unbounded key. It says it supersedes the older carry and gives the re-measurement instruction at the merge base.
- **R10-ARCH-SHAPES** has one `carry` entry with the same prefix. It states the constraint: route a new reader through `InputReader` and `age_limit_for`, and never read stamps directly. It states the control: the P2 `state_age` registry fails at the base and passes at the head. It says the `_RANGE_KEYS` comment item is already done, with the grep to re-run. It gives the re-measurement instruction.

Both entries are in the groups' `carry` lists, written by `roster_edit.py append-carry`. Neither group's `brief` string repeats them. `carry_audit.py pr 2683`: `7 finding item(s): 7 routed, 0 unrouted, 0 bad destination(s)`.

## Body (steps 7, 10, non-blocking note 1)

The live PR body is the same text as handoff-body ref `39cb37f13`. Both forward-carry items name their roster SHA (8d6527c07, 57bb4b33e). Lines 5 and 45–47 state that the countermeasure departs from the RCA's numeric quiet-interval form. `## Head` still names `07b83e9b2`.

No `pr-contract` run has seen the patched body. The last two ran at 02:34:06Z and 02:36:54Z; the body ref was committed at 02:45:00Z. I ran the same steps locally on the live body:
- `node tools/policy/policy_lint.mjs --pr-body … --head 07b83e9b2 --base d05a44c63 --paths-file … --existing-file …` printed `PR-BODY: 0 error(s)`, rc 0. Its red-history arm skipped because no token was set.
- `node tools/policy/figure_lint.mjs` printed `FIGURES: 17 resolved, 13 not verified, 0 refused`, rc 0.

(evidence/policy_lint-body.out)

## Checks at the head (step 11)

Every check run on `07b83e9b2` concluded success or skipped; none failed. `tests / mutation` finished success at 02:34:03Z (`mutation-autofix` and `mutation-pins` skipped). Both `pr-contract / pr-contract` runs and both `gate` runs are success, as are `prelude`, `fast (3.14)`, `closures`, `arch-score` and `budget-raise-gate`. No commit in `d05a44c63..07b83e9b2` has a failed run (`a23179207`'s runs were cancelled as superseded). The body's `## Red checks` answers the one locally predicted red, `mutation` from prepr step 6d, which was repaired before the handoff.

## Carried notes

- Non-blocking note 2 from round 1 stands as written there. Carry: dismissed: unmeasured heartbeat-source observation; finding-propagation.md carries only a measured finding
