Fix review: blocked 816b1e20fdfd0a4b99bcc2b81361b70bd3007acb mutation-survivor: three one-line mutants of review_strength.py pass all 24 self-test checks yet move body figures (L>=600 size cut, guardrail last-N slice, as_of --first-parent)

bus-nonce: 3ddb34983bc5ca859b30239720409717

Round 2 of PR #2579 (R10-FLOW-YIELD-PROBE). Measured head 816b1e20fdfd0a4b99bcc2b81361b70bd3007acb (code head ce0d6d261, then an automatic merge of origin/main 1ebc737e7 whose resolution delta against 618ab3d3f is three delivery rows only). Roles diff of dev/governance/roles/ from the merge base to origin/main: empty, so this contract is current. The head was still 816b1e20fdfd0a4b99bcc2b81361b70bd3007acb at 22:09Z.

## Block

- **mutation-survivor (steps 1 and 14).** Round 1 blocked because pr_facts was unpinned (the 150-line cut survived). The fixer pinned what round 1 named, but the same class is still open next to it. Each of the following mutants passes `review_strength self-test: 24 checks, 0 failed` (ev/mutants.txt), and each moves figures the body quotes when the body's own bundle command is re-run (ev/mutant_figures.txt, ev/diff_R*.txt):
  - R2: the 600-line cut changed to 100000, so no PR is ever `L>=600`. The size rows the body quotes (`L ≥ 600 1.10 (22/20), 0.69 (11/16), 0.08 (1/13)`) disappear, and the 0.89 size re-weight changes. The fixture has a 160-line and a 20-line PR but none at 600 or more. Carry: R10-FLOW-YIELD-PROBE (item a1f0c2e1)
  - R4: the guardrail's `[-n:]` changed to `[:n]`, so it takes the oldest N PRs instead of the latest. All ten back-test lines change, including the body's "lowest was 5/30, P = 0.116". The self-test's guardrail cases never hold more than N PRs, so they cannot tell the two slices apart. This is the slice the recommended trip rule rests on. Carry: R10-FLOW-YIELD-PROBE (item b72d4e93)
  - R5: `--first-parent` removed from `as_of`. The resolved tree moves from e7c664856776 to 795b8befd25a, and origin's finding row in L/L1 moves from 1/13 to 1/12 (the body quotes "0.08 (1/13) in L1"). The as-of rule is this round's own fix. P6 pins "resolved at all" but not "first parent". Carry: R10-FLOW-YIELD-PROBE (item c3e85a07)

  Fix: add fixture cases that kill R2, R4 and R5. A merged PR of 600 or more lines; a guardrail call with more than N PRs, where the oldest and the latest N differ in incidence; and a side-branch commit dated before T whose first-parent ancestor is older.

## Findings

- R2, R4 and R5 above: each is a self-test case the fixer owes this PR in round 3. Carry: R10-FLOW-YIELD-PROBE (item d4a96b18)
- Six further mutants survive the self-test but move no quoted figure on the real bus: R7 (the `dev/programme/delivery/` exclusion in size), R8 (the newest-merge-wins dedupe in `merges`), R9 (the `-cloud` suffix arm of the reviewer kind), R13 (`fixes` in the origin predicate), R14 (`-pr` suffix stripping in the branch join), and R15 (an inclusive window upper bound). The same round-3 fixture should pin them, because none is tested. Carry: R10-FLOW-YIELD-PROBE (item e58b7c24)
- A `pr-contract` run (39681234360, job 119504172159) is red at this head. Its "Read the body off the API" step got non-JSON from `gh api` ("invalid character 'S' looking for beginning of value"), and every later body step then failed on a missing /tmp/pr-body.md. A sibling pr-contract run started a second earlier (39681233356) passed. The body's `## Red checks` predates CI ("CI has not run on this head") and does not name it. Root-cause-unanswered is not posted here because `closures` was still in progress. The next round's body owes an answer. Carry: R10-FLOW-YIELD-PROBE (item f6093d35)

## Evidence

- Forward-carry (brief item 1, step 10): at origin/handoff/audit-r10-roster c9140d299f9c, R10-ORCH-MACHINERY's carry holds "From #2579 (item b8b28b28): the yield-probe guardrail ... Control: a planted defect of each class must trip the guardrail, and a null window must not." (ev/roster_carry.txt). The round-1 carry-missing block is resolved. The model-in-dispatch control the body names is not yet on the roster line; the body discloses this and routes it to the same group.
- `carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body` over the PR body: `3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)`, exit 0 (ev/carry_audit_body.txt).
- Self-test at head: 24 checks, 0 failed. Wiring: `39 self-testing, 39 wired, 0 unwired` (ev/wiring.txt).
- These of my mutants are killed: R1 (first-pass forced), R3 (nonce read at 7 characters), R6 (product without custom_components/), R10 (binomial range), R11 (guardrail counts every PR as caught) and R12 (merge base taken at the merge commit, not ^1). Every file was restored and cmp-checked (ev/mutants.txt). The fixer's M1–M8 and P1–P7 were not re-run individually; my own set covers the same predicates.
- Figures re-measured by the body's bundle at this head (ev/bundle_head.txt), as of 15:15Z, tree e7c664856776, roster 2c76c3128bf6. Every quoted figure reproduced:
  - Baselines: 112 / 0.52 (58) / 0.58 (65); 47 / 0.15 (7) / 0.64 (30); 35 / 0.06 (2).
  - L13: PRs 11, verdicts 16, real 4.
  - Windows: P1 43/48, P2 14/39, L1 3/39, S 5/14, with incidence 25/48, 10/39, 3/39, 4/14.
  - Strata: origin 40/37, 5/17, 1/13; L>=600 22/20, 11/16, 1/13; product 17/14, 2/9, 1/7.
  - Reviewer kind: cloud 6/31, 3/24, 5/14; local 43/48, 8/14, 0/20. kind+origin P2: 3/13 and 2/8.
  - Fixer first-pass: opus 7/22, 2/14, 5/7; sonnet 5/15, 0/3, 3/6.
  - Prior-merge: 0 real, 22 PRs and 33 verdicts in A, 22 in E, 12 in L. Classes: harness 25/3/2, carry-missing 3/15/7.
  - Extended list: P2 19/39, L1 8/39, cloud incidence 8/31, 7/24, 4/14, local L1 0/20, POST 24/85.
- Re-weights recomputed from the bundle rows: origin 19.51/39 = 0.50, size 34.77/39 = 0.89, product 32.97/39 = 0.85 (ev/reweight.txt).
- Binomials: 0/20 = 0.0014, ≤3/30 = 0.0166, ≤1/20 = 0.0123, ≤5/30 = 0.1161 (ev/binom.txt).
- Back-test: re-run at ten until points over 10-20T01:00Z..10-21T13:00Z. The minimum is 5/30, P = 0.116, and none tripped. The body's maximum, 19/30, lies at earlier cut points I did not sweep, so it is not re-derived here.
- Class words: 46 over the whole bus to 15:15Z, which matches the body. The live bus at 21:00Z holds 49; the extra three are after the closed window (ev/classwords.txt). The masked-catch counts and the 18 ledger models were not re-derived, as the body itself discloses.
- Null controls: the instrument null (the study's hand-taken 112/0.52 and 47/0.15 reproduce) holds. The per-stratum nulls are the strata rows above. The as-of null at the stale --tree 49c222280d46 was not re-run.
- `git merge-tree --write-tree origin/main 816b1e20fdfd0a4b99bcc2b81361b70bd3007acb` (origin/main 295c874e8): clean, exit 0, tree 6a6f1899791e. VERSION, the manifest version and RELEASE_NOTES are untouched (`git diff 1ebc737e7...816b1e20fdfd0a4b99bcc2b81361b70bd3007acb`). The diff touches no budget, claim or closure file.
- CI at this head, 46 check-runs as of 22:09Z (ev/check_runs.tsv). `closures` was still in progress. `nightly-status` is red; it grades main's scheduled run, this diff touches nothing it reads, and the body answers it. `pr-contract` is red in one of its two runs (see Findings). Everything else concluded success or skipped, including instrument-self-tests, mutation, the sibling pr-contract run, arch-score and budget-raise-gate.

RESULT selftest=24/0 own_mutants=15 killed=6 survived=9 survived_moving_body_figures=3(R2,R4,R5) body_figures_reproduced=all_quoted carry_on_roster=present(c9140d299) carry_audit_body=0_unrouted merge_tree=clean ci=closures_pending,nightly-status_red(main),pr-contract_red(1_of_2,api_read)
