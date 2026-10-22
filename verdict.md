Fix review: blocked eb9f7e89d0b258ca66a8d9757df0156a776b7332 mutation-survivor: the nine named mutants are killed, but new one-line mutants of review_strength.py (guardrail ordered by PR number, origin without findings, the 600 cut moved to 650 or 700) pass all 31 checks and move figures the body quotes

bus-nonce: 0e359fb8bd15567e4ab97a86c4e27758

This is round 3 of PR #2579 (R10-FLOW-YIELD-PROBE), so the next round is the fourth, and `fixer.md` owes a re-cut there, not a repair. I measured head eb9f7e89d0b258ca66a8d9757df0156a776b7332 (code head aba00fbf2, plus an automatic merge of origin/main 46e368127) from a detached worktree. I diffed `dev/governance/roles/` from the merge base to origin/main: empty, so this contract is current. The head was still eb9f7e89d0b258ca66a8d9757df0156a776b7332 at 00:44Z.

## Block

- **mutation-survivor (steps 1 and 14).** Round 2's mutants are all killed now (see Evidence). The class it named is still open beside them, though: a one-line mutant that passes `review_strength self-test: 31 checks, 0 failed` (ev/mutants.txt) and moves figures the body quotes when the body's own bundle command is re-run (ev/survivor_figures.txt, ev/bundle_N*.txt):
  - N3: the guardrail sorts by PR number, not by first verdict (`sorted(first, key=lambda p: first[p])` becomes `sorted(first)`). The body's back-test incidence `8, 8, 8, 8, 7, 7, 6, 5, 5, 5` becomes `10, 9, 7, 7, 7, 7, 5, 5, 5, 5`, and the window bounds move. The new case "the LATEST N by first verdict (5, 6, 7)" cannot tell these orders apart, because in the fixture first-verdict order and PR-number order agree. This ordering is what the recommended trip rule rests on. Carry: R10-FLOW-YIELD-PROBE (item 7a3c91e2)
  - N6: `or grp.get("findings")` is removed from the origin predicate. The body's `finding` rows `0.29 (5/17), 0.08 (1/13)` become 5/15 and 1/11. P2 `cloud+finding 3/13` becomes 3/11. The origin re-weight 0.50 becomes about 0.44 (11×40/37 + 20×3/11, over 39). Round 3 pinned the sibling arm `fixes` (R13) but not `findings`; no fixture group lists `findings`. Carry: R10-FLOW-YIELD-PROBE (item 8b4d02f3)
  - N1 and N2: the 600-line cut is moved to 700 or to 650. The body's `L>=600 1.10 (22/20), 0.69 (11/16), 0.08 (1/13)` becomes 21/19, 10/15, 1/11 under N1, and 21/19, 11/16, 1/12 under N2. The fixture's PRs are 20, 160 and 700 lines, so the new PR 7 case pins the cut only to somewhere in (160, 700]. Nothing in the fixture sits on either side of 600. Carry: R10-FLOW-YIELD-PROBE (item 9c5e13a4)

  Fix: add fixture cases that kill N3, N6 and N1/N2. First, a guardrail set whose first-verdict order differs from PR-number order, with a higher-numbered PR reviewed earlier. Second, a roster group that lists `findings` alone. Third, PRs of 599 and 600 lines, so each side of the cut is pinned.

## Findings

- N3, N6 and N1/N2 above: each is a self-test case owed in the round-4 re-cut. Carry: R10-FLOW-YIELD-PROBE (item ad6f24b5)
- Four further mutants survive the self-test but move no quoted figure on the real bus: N4 (the guardrail's `v["t"] < until` becomes `<=`), N7 (pr_facts' `v["t"] < until` becomes `<=`), N8 (the `blueprints/` arm of product is dropped) and N9 (the merge parent count `== 2` becomes `>= 2`). No fixture case tests any of them, so the round-4 fixture should pin them too. Carry: R10-FLOW-YIELD-PROBE (item be7035c6)

## Evidence

- Mutation proof (step 1), my own runner over exact one-occurrence replacements, with the file `filecmp`-identical afterwards (`restored identical: True`, ev/mutants.txt). Unmutated: `review_strength self-test: 31 checks, 0 failed`. Every row of the body's mutation table reproduces, with the same failing checks: R2, R4, R5, R7, R8, R9, R13, R15 (1 failed each) and R14 (2 failed). So round 2's three named mutants (R2, R4, R5) are each killed now, as the brief asked. Round 2's killed R1, R3, R6, R11 and R12 are still killed. My own N5 (the `cloud` id prefix), N10 (the 150 cut moved to 200), N11 (roster not resolved as of T) and N12 (the probe arm) are killed.
- Finder's harness (step 2): the brief's quoted rates, 0.52 over 112 PRs and 0.15 over 47. At this head the tool prints `PRs 112 verdicts 257 real 58 (0.52/PR) book 65 (0.58/PR)` and `all L PRs 47 ... real 7 (0.15/PR) book 30 (0.64/PR)` (ev/bundle_head.txt). At the merge base the tool does not exist; the baseline end is the brief's own hand count, which this matches.
- Figures re-derived at this head with the body's bundle (ev/bundle_head.txt), as of `2026-10-21T15:15Z: tree e7c664856776 roster 2c76c3128bf6`, 358 verdicts on the bus, 0 outside the grammar. All re-derived and all match:
  - Baselines: 112 / 0.52 (58) / 0.58 (65); 47 / 0.15 (7) / 0.64 (30); 35 / 0.06 (2).
  - L13: PRs 11, verdicts 16, real 4.
  - `all` rows: P1 43/48, P2 14/39, L1 3/39, S 5/14, with incidence 25/48, 10/39, 3/39, 4/14.
  - Strata: finding 40/37, 5/17, 1/13; L>=600 22/20, 11/16, 1/13; product True 17/14, 2/9, 1/7.
  - Re-weights: 0.50, 0.89, 0.85 (ev/reweight.txt).
  - Reviewer kind: cloud 6/31, 3/24, 5/14; local 43/48, 8/14, 0/20. P2 cloud+finding 3/13, local+finding 2/8.
  - Fixer first-pass: opus 7/22, 2/14, 5/7; sonnet 5/15, 0/3, 3/6.
  - Prior-merge: 0 real everywhere, 22 verdicts in E and 12 in L; A gives 22 PRs and 33 verdicts.
  - Classes: harness 25/3/2; carry-missing 3/15/7.
  - Extended list: P2 19/39, L1 8/39; cloud incidence 8/31, 7/24, 4/14; local L1 0/20; POST 24/85.
  - Back-test: 8, 8, 8, 8, 7, 7, 6, 5, 5, 5 of 30, every line ok, lowest 5/30 at P = 0.116.
  - Self-test: 31 checks, 0 failed.
  - The "+27 lines" is net: `git diff 889c39e59 573d5cbff` shows +31/-4.
  - The local Red-checks figures (2382 entity checks, 73 wired and so on) were not re-run; CI's runs on this head are cited instead.
- Null controls (step 3): M0 above holds. The instrument null (the hand-taken baselines reproduce) holds. Each new case does separate its named mutant (R2, R4, R5, R7, R8, R9, R13, R14, R15 all fail).
- Step 14: the `tests/closures.json` +1 is an `inert_reads` entry for `tests/entities.py`, made by `ci_predict.py --apply-inert`'s sibling rule. It only widens what runs when the file is touched, and `closure-scope` is green on this head. No budget, score, ledger or claim file moves.
- Step 4/5: VERSION, the manifest version, RELEASE_NOTES.md and both claim files are untouched by `git diff 46e368127...eb9f7e89d0b258ca66a8d9757df0156a776b7332`.
- Step 7: the body's `## Head` names eb9f7e89d0b258ca66a8d9757df0156a776b7332, the head I measured. Merge structure checked:
  - 38534c764 merges aba00fbf2 into 816b1e20f.
  - 889c39e59 merges 5a755f53e into 816b1e20f.
  - eb9f7e89d merges 46e368127 into 38534c764.
  - Against main, the head's governance.yml differs only by the added review-strength step.
- Merge-tree (step 13): `git merge-tree --write-tree origin/main eb9f7e89d0b258ca66a8d9757df0156a776b7332` (origin/main 46e368127) is clean, exit 0, tree f2a1c4fc3aac (ev/merge_tree.txt).
- Carry audit (rule 19): `carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body` over the body prints `CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)`, rc=0 (ev/carry_audit_body.txt). Roster origin/handoff/audit-r10-roster is 743463c61f6a.
- My own verdict's carries (ev/carry_audit_verdict.txt): read as a verdict comment, it gives `0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)`. The Block and Findings items, re-read under a forward-carry heading, give `1 routed, 0 unrouted, 0 bad destination(s)`, so the destination R10-FLOW-YIELD-PROBE resolves on the roster.
- Forward-carry (step 10): at roster 743463c61f6a, R10-ORCH-MACHINERY's carry still holds "From #2579 (item b8b28b28) ... Control: a planted defect of each class must trip the guardrail, and a null window must not". R10-FLY-GH-READ-RETRY's carry names #2579's pr-contract read failure, run 39681234360 (ev/roster_carry.txt).
- Red checks (step 11), 41 check-runs at this head as of 00:44Z (ev/check_runs.tsv): 23 success, 13 skipped, 1 neutral (CodeQL), and 3 in progress (fast (3.14), coverage, Analyze (python)).
  - `nightly-status` is red. It grades main's scheduled run, this diff touches nothing it reads, and the body answers it. It is not this pull request's.
  - Both `pr-contract` runs are success, as are instrument-self-tests, closure-scope, mutation, arch-score, budget-raise-gate and delivery-status.
  - The intermediate commits aba00fbf2, 573d5cbff and 38534c764 carry no check-runs (ev/check_runs_range.txt).
  - No gate check is red, so no root-cause answer is owed.

RESULT selftest=31/0 named_mutants=9/9_killed own_mutants=12 own_killed=4 own_survived=8 survived_moving_body_figures=4(N1,N2,N3,N6) body_figures_reproduced=all_quoted carry_audit_body=0_unrouted merge_tree=clean ci=3_in_progress,nightly-status_red(main) round=3
