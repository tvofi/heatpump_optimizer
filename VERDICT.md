Fix review: blocked 468781122d076f5396f4a27c171b78f64f1c5537 carry-missing: not carried to R10-ORCH-MACHINERY

Round 1 (first review) of PR #2579, R10-FLOW-YIELD-PROBE. Measured head 468781122d076f5396f4a27c171b78f64f1c5537 (code head 7864970031c4, merge 81d617cec of main 49c222280). Pack spec: dev/programme/flow-study/roster/groups/R10-FLOW-YIELD-PROBE.json is byte-identical at pin 30c57744a and at the body's 78117030 (an ancestor). Roles diff against main: empty, so this contract is current.

## Blocking

- **carry-missing (step 10).** The body's two forward-carries name R10-ORCH-MACHINERY (the guardrail threshold, the extended class list, the seat-family arm and the planted-defect calibration; and the unrecorded reviewer model), and the body says the seat "edited neither file". At origin/handoff/audit-r10-roster 23ef06dc6cc7, R10-ORCH-MACHINERY's carry and brief hold no text about review strength, the yield probe, p0 or the reviewer model, and the body names no roster SHA. A carry that exists only in this PR's body is the case step 10 blocks: by finding-propagation.md it must be written into that group's carry/brief, stating its control as a precondition, before merge. The roster write can be the orchestrator's (roster_edit.py append-carry), and the body then names that roster SHA. Carry: R10-ORCH-MACHINERY (item b8b28b28)
- **mutation-survivor (step 1 and step 14), pr_facts is unpinned.** The 17 self-test checks never call pr_facts, so origin, size, product and fixer, which explanation 2 and the PR-mix null control rest on, have no test. Three mutants applied together all survive (`review_strength self-test: 17 checks, 0 failed`): the origin label swapped finding->group, the size threshold changed 150->15, and the product predicate forced False (ev/pr_facts_mutant.txt). The fixer owes a fixture: a roster plus a delivery row plus a merged and an unmerged PR, checked for each fact. Carry: dismissed: blocking here, the fixer owes it this PR (item 3f84a1e7)
- **figures not closed under the stated rule (step 8).** The body says "Every window is closed ... the figures are a function of the refs, not of main's tip". That is false for the fact strata. pr_facts takes each PR's last verdict over the whole bus, not the last in the window, and reads delivery rows and merges at --tree (default origin/main). So a verdict after 15:24Z moves a PR's stratum. PR 2529 has a merge verdict at 18:50Z on 8f026328d. That verdict moves 2529 from product False to True, so L1's product row now reads 0.12 (1/8) where the body and record say 0.14 (1/7), and the product re-weight reads 0.86 where they say 0.85 (ev/product_cutoff.txt). With the verdicts cut at 15:24Z, the body's 1/7 reproduces, so the figure was honest when it was taken, but the reproduction command no longer reproduces it. Fix one of two ways: compute facts as of the window's until (or an --as-of with --tree pinned), or withdraw the closure claim and pin the bus/tree SHAs in the record. Carry: dismissed: blocking here, the fixer owes it this PR (item 9cdf8918)

## Not blocking

- **"5 of its 7 real blocks"**: for the window that reproduces the study exactly (L, end 14:50Z: 47 PRs, 7 real (0.15), 30 book (0.64)), the 13:00Z sample holds 4 of the 7 (ev/fig_13_1450.txt). It holds 5 only at the 15:00Z end, which gives 48 PRs (ev/end_sweep.txt). The fixer should reword this in the same round. Carry: dismissed: wording fix, rides this PR's next round (item 65976a91)
- **Not re-derived (step 8):** the masked-catch counts 0/8, 1/31, 0/20, 0/5 (the body says these came from an out-of-tree one-off regex, so no tree instrument re-derives them); the 18 ledger-recorded reviewer models (wip-sync/orchestrator-scratch, not read). Neither is reported as confirmed. Carry: dismissed: disclosed in body, not load-bearing (item 7e8a0c64)

## Verified

- Mutation proof: M1–M8 reproduce exactly the failing checks the body lists. My own M9 (window lower bound), M10 (first-pass), M11 (binomial coefficient) and M12 (nonce read) each fail 1–2 checks, and every file was restored (ev/mutation.txt). Removing the wiring step gives `39 self-testing, 38 wired, 1 unwired`; restored, it reads 39/39/0. The body's 38 was taken before the main merge brought in one more self-testing instrument.
- Figures re-measured with the tool at this head (ev/*.txt):
  - Baselines: 112 PRs 0.52 (58) / 0.58 (65); 47 PRs 0.15 (7) / 0.64 (30); 35 PRs 0.06 (2).
  - Windows: P1 0.90 43/48, P2 0.36 14/39, L1 0.08 3/39, S 0.36 5/14, with incidence 25/48, 10/39, 3/39, 4/14.
  - Kind: cloud 6/31, 3/24, 5/14; local 43/48, 8/14, 0/20. kind+origin P2: 3/13 and 2/8.
  - Origin: 1.08 (40/37) to 0.08 (1/13). Size: L>=600 1.10 (22/20) to 0.08 (1/13).
  - Re-weights: origin 0.50 and size 0.89, both at the body's roster 802b38503eb5 and tree e7c664856.
  - Fixer first-pass: opus 7/22, 2/14, 5/7; sonnet 5/15, 0/3, 3/6 (body refs).
  - Prior-merge: 33 verdicts on 22 PRs, 22 in E, 12 in L, 0 real. Classes: harness 25/3/2, carry-missing 3/15/7.
  - Extended list: P2 19/39, L1 8/39, cloud incidence 8/31, 7/24, 4/14, local L1 0/20, POST 24/85.
  - Binomials: 0.0014, 0.017, 0.050, 0.012. Back-test over twelve cut points: minimum 5/30 (P = 0.116), maximum 19/30, no trip.
  - Class words: 46 used, 16 on the study list, 9 extended, 21 left.
  - Self-test: 17 checks, 0 failed.
- git merge-tree --write-tree origin/main 468781122d076f5396f4a27c171b78f64f1c5537: clean, exit 0 (ev/merge_tree.txt). The diff touches no VERSION, manifest, notes heading, budget or claim file.
- CI at this head (check-runs API, 49 runs): the only red is nightly-status. Its log grades main's scheduled run 39563978649 (head c77f89d, mutation-nightly and slow). This diff adds only a governance.yml self-test step, and nightly-status does not read it. The body's `## Red checks` answers it. pr-contract's last run (17:15Z) started after every other workflow had concluded, and it passed.

RESULT review_strength_selftest=17/0 mutants_named=8/8_killed own_mutants=4/4_killed pr_facts_mutants=3/3_survived merge_tree=clean red_checks=nightly-status(main) carry_on_roster=absent

bus-nonce: 7393693a92be42bdd7be868ccfb0840e
