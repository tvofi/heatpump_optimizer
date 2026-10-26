Fix review: merge e088bf833707542cfa027c1878b086e4e05ddd9e

bus-nonce: a6ea4142c4fa063f7b02d3ab0462b254

Delta review of #2819 (R10-ARCH-SHAPES), round 5 (a delta review after the round-4 merge at 6f91e6d05450ba32fe1cfa102b00a9763235d412, comment 6405240420). Measured head: e088bf833707542cfa027c1878b086e4e05ddd9e, still the PR head at 2026-10-26T02:59Z. Reviewed from a detached worktree at that head. Roles diff `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty (merge base 7d2056970e08135bdc7c2cab4063427a2efa1c30 = origin/main).

## Findings

- The body's unpinned-site figure is stale at this head. It says `ci_predict.py --base origin/main` "lists the same 71 unpinned sites as at 6f91e6d05". At this head `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` prints `CI PREDICT: 12 unpinned site(s) the diff adds`. CI `tests / mutation` (job 121357722191) prints `MUTATION TABLE REFUSED -- 3892 unpinned site(s) against 3943 at the ratchet base 7d2056970..., 13 of them added by this diff`. The drop comes from the bot's `ci: pin killed mutants` commit 54e3920f7, which is inside the delta and pins 60 records. All 12 are in the body's 71-line list, so no site goes unlisted; only the count overstates. The 12/13 sites still left are probably survivors, and their pin or survivor triage is still owed before `tests / mutation` goes green. Carry: R10-ARCH-SHAPES

## Evidence

- CHECK 1, structure_budgets.json. The conflicted merge is b5049f3fd (6f91e6d05 x 5261ba841, merge base c78df2b86). The ledger driver's output tree 7664fd70a printed `class_excess_loc: 18102 + both deltas = 18081` and `max_class_loc: 8311 + both deltas = 8234`. b5049f3fd differs from it only in `functions_cc_over_15 29 -> 28` and `recorded_at -> 5261ba841`. e088bf833 is exactly the automatic merge of eff0486fb x 7d2056970 (an empty tree diff; ev/resolution_delta.txt). Three-way per changed leaf (merge base c78df2b86 / 6f91e6d05 / 5261ba841=origin/main values / head):
  - class_excess_loc 18102 / 18090 / 18093 / 18081;
  - duplication_copies 16 / 15 / 16 / 15;
  - functions_cc_over_15 30 / 29 / 29 / 28 (the driver gave 29, the fixer re-recorded 28);
  - max_class_loc 8311 / 8297 / 8248 / 8234;
  - methods_over_150 17 / 17 / 16 / 16;
  - seam_cut_total 419 / 419 / 424 / 424.
  
  A re-measure with `python3 tests/structure.py` at the head (ev/structure_head.txt) gives class_excess_loc 18081, duplication_copies 15, functions_cc_over_15 28, max_class_loc 8234, methods_over_150 16, seam_cut_total 424, and `STRUCTURE RATCHET PASSED`. Every budget equals the re-measure and none is above origin/main. max_class_loc is a base-plus-both-deltas sum here, but the sum equals the measured largest class (8234), because both sides shrank the same class in disjoint lines. The value is measured, not carried, so the 2753 defect does not recur.
- CHECK 1, closures.json: the driver merged it. `inert_reads.tests/harness_headers.py` reads 883 at 6f91e6d05, 881 at origin/main and 885 at the head. That is exactly the set union, and all 885 paths exist in the head tree. No other leaf differs from both sides. (The body's 884 is the b5049f3fd figure. The later automatic merge with 7d2056970 added one.)
- CHECK 2: `cmp` of `tests/golden/claimed_drift.txt` and `tests/golden/card_claimed_drift.txt` at origin/main and at the head: both identical (ev/claim_cmp.txt). The three-dot diff touches nothing under tests/golden/, nor VERSION, manifest.json or RELEASE_NOTES.md.
- CHECK 3, Closes: the delta 6f91e6d05..e088bf833 changes no production code. Its non-main content is the bot's 60 mutation pin records plus the two-line budget re-record, so the closing claims settled at round 4 stand. Spot re-run at the head of `dev/audit/rounds/round10/catchup/arch-s2/probe_coercion_reach.py`: `1e6`, `1e400` and `inf` give silent_cap_kw 4.2 (the `unknown` arm, not p_max 6.0), `RESULT inf_changes_decision=0`, `RESULT perturbed_1e400_equals_unknown=1`. The finite absurd 1e6 reading does not reach p_max, so the #2236 claim holds. `r10_finite_float_census.py . .` gives `RESULT coercers=1` (`const.py::finite_float`), so the #2239 claim holds. Neither claim overreaches.
- CHECK 4: `git log 6f91e6d05..e088bf833 --not origin/main` shows only 54e3920f7 (github-actions bot, mutation pins), b5049f3fd (merge #2817), eff0486fb and e088bf833 (merges). There is no authored commit outside what the body's `## Head` section describes. dev/programme/delivery/2819.md is in the three-dot diff. `git merge-tree --write-tree origin/main e088bf833` exits 0 (ev/merge_tree_main_head.txt).
- CHECK 5, CI at the head from the check-runs API (ev/check_runs_0300Z.txt, 02:59Z). There are two reds:
  - `tests / mutation`: the body's `## Red checks` names and answers it (red as predicted, the pin run owed, ci_predict named every site before the push). Its count is stale, as under Findings.
  - `governance / delivery-status`: OVERDUE rows for other PRs (#2798, #2799, ...). The log says it is not a required context and a red there blocks no merge. This diff does not reach what it reads, so it is not this PR's.
  
  Every other run that completed is green: fast (3.14), closures, coverage, typing, replay, browser, arch-instrument, mutation-pins (2), (3) and lane-proofs among them. Two were still in progress at 02:59Z: `tests / mutation-pins (1)` (started 01:52Z) and the `CI edit` run's `prelude` (started 01:47Z). So no pr-contract body check on this head had run by then. I post no root-cause verdict on that account.
- Carries 1-8 were answered at round 4. The delta changes no code they read, so none is re-opened.
- I re-ran no heavy gate or mutation table (I cite CI). I built no harness of my own.
