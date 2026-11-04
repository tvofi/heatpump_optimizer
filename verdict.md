Fix review: merge 558c54a0f0f0617678caa9acc87a426a8ddb19bc

bus-nonce: 30d66647d3bb53686472274b09d40c2a

Round 4 of PR #3174 (R10-REPLAY-COST-BUDGET, issue 3129). This is a delta review of the r3 merge verdict at 8e47d727. It was judged from a detached worktree at head 558c54a0f0f0617678caa9acc87a426a8ddb19bc against merge base b8e823699 (the three-dot diff touches tests/replay.py and dev/programme/delivery/3174.md only). The body carries a `## Re-cut note`, as the fourth round requires. dev/governance/roles/ is unchanged between the merge base and origin/main. The harness is the finder's from r3: the CI lanes' own `cost` lines graded through the production `class_budget` + `cost_offenders` (ev/grade.py).

## Findings

- Residual: no control re-derives a band's edges from `COST_CLASS_READINGS`. The rule is min/1.05 to max x1.05, and every edge at this head matches it (Evidence). But a band widened into a gap, short of a refused ruler, passes all 33 controls:
  - W24u: ref24 to (22.64, 28.0).
  - W24d: ref24 to (12.0, 25.53).
  - W53u: ref53 to (49.60, 90.0).
  - Emptying `COST_RULERS_REFUSED` (RF-EMPTY) also survives.
  
  So the pin for "never widen a band to fit a runner" covers only the two named foreign rulers and the gap midpoints, not the edge rule the comment states. A widened band would grade an unsampled ruler on a neighbour's budget, which is the 28.01-on-ref30 blind spot the body explains. It does not hide anything at this head, and any edit is a code-owned change to tests/replay.py. The countermeasure is a control asserting each band equals its readings' widened extremes. Carry: R10-REPLAY-COST-BUDGET
- Residual: ref24's band and budgets rest on one job (125461180429), disclosed in the body. A later ref24 clean `cpu_ratio` under 1.815, or a `ref_ms` outside 22.64-25.53, reads as a named red (`cannot see a 2x cycle` or `runner class unknown`), never a silent pass. The first ref24 runs after merge owe their `cost` lines appended to `COST_CLASS_READINGS`. Carry: R10-REPLAY-COST-BUDGET
- The r3 carry that the owner fixture is unread on the ref53 nightly class is unchanged by this round. The owner `cpu_ratio` 337.8 is untouched, and ref24's owner reading 269.8155 is WITHIN it. Carry: dismissed: already carried by the r3 verdict on R10-REPLAY-COST-BUDGET; this round neither settles nor worsens it

## Evidence

- **Head.** `git ls-remote` reads fix/r10-replay-cost-budget at 558c54a0f0f0617678caa9acc87a426a8ddb19bc at 2026-11-04T05:34Z, the head the PR API and the body's `## Head` name (ev/HEAD.txt). It did not move during the review.
- **Merge.** `git merge-tree --write-tree origin/main 558c54a0` exits 0 against current origin/main c3a279e32 (tree fa123f50). There is no conflict and no claim-file driver involvement.
- **CI.** `merge_train.py classify 558c54a0... --pr 3174` exited 0 twice, printing `GREEN 558c54a0f0f0617678caa9acc87a426a8ddb19bc pending: none red: none` (ev/classify-1.txt, ev/classify-2.txt).
  - The PR's check-runs at this head: total_count 55, all on one page of 100, all completed. pr-contract (125552025626, 125550586826) and gate (125552986776, 125550977172) are success.
  - The one concluded failure is `governance / delivery-status` (125528941954). Its log names `overdue #3065` and states that it is NOT a required context. It grades main's record, not this PR's row, so it is not this PR's by fix-review step 11.
  - `## Red checks` names the reds at the prior head acec536b (tests / replay 125461180429, pr-contract 125483440211, gate) but not this delivery-status red. pr-contract run 125552025626 started at 21:07:51Z, after delivery-status concluded at 20:26:04Z, and passed on this body. Under step 11 that run is the evidence and is not re-derived.
- **This head's own replay lane** (job 125530195186, ref46, ref_ms 46.56) printed `ALL 181 replay checks PASSED`, with all 33 controls ok, including `class_budgets`, `runner_class_unknown`, `away:covered_names_are_committed` and `recorder:unsupported_scheme_refusal_prints_none_of_the_url`.
  - Synthetic clean 2.3273 is WITHIN 3.357. The cpu-doubled arm 4.6962 is over 3.357, and the loop-doubled arm 0.1913 is over 0.1278.
  - Owner 241.6526 is WITHIN 337.8.
- **Ask (1): fail closed.** At the head, `class_budget` refuses by name with `runner class unknown: ref_ms X lies in no band ...; no budget is assumed`, returning budget None. It does so for NaN, 0, -1, inf, and each edge plus or minus 0.01 (22.63, 25.54, 28.71, 32.70, 42.98, 49.52, 56.79). It also refuses the gap 49.55 and the two refused rulers 28.01 and 34.35 (ev/finder_harness_head.txt).
  - The control `runner_class_unknown` pins it: M4 (fall back to ref46) and FALLBK (return the default COST_BUDGETS) both turn it red (ev/mutants_r4.txt).
  - LANE-FALLBK swaps run_fixture's `refused or` for a default-budget fallback. It survives the controls, but the default synthetic budget has no `cpu_ratio`, so the lane would still read `no recorded budget` (red). No silent pass exists on that path.
  - Bands not widened to fit 23.8: ref30, ref46 and ref53 are byte-identical to r3. ref24 re-derives from its own job's four `ref_ms` (23.77-24.31) as floor(23.7732/1.05)=22.64 and ceil(24.3138x1.05)=25.53, matching the committed values. The bands are disjoint, since 25.53 < 28.72.
  - I opened job 125461180429 myself. Its `cost` lines read: clean 2.5671 and loop 0.1282 at ref_ms 23.83; cpu doubled 5.2086 at 23.99; memory doubled 3860.7 at 24.31; loop doubled 0.2603 at 23.77; owner 269.8155 at 24.06. Its `record:` line printed `cpu_ratio=3.63 ... loop_cpu_ratio=0.1813`. Each tuple in `COST_CLASS_READINGS` for ref24 matches.
  - Budgets: sqrt(2) x 2.5671 = 3.6304 and sqrt(2) x 0.1282 = 0.1813, each reading at 70.7 % of its budget (ev/rederive.txt). The 28.01 ruler sits 2.47 % under ref30's floor, and its doubled 3.8922 < 3.934, which confirms why widening ref30 would hide a 2x.
- **Ask (2): a planted 2x per class.** Using the finder's harness at the head (ev/finder_harness_head.txt), every class's clean reading is WITHIN and every doubled arm is over its own class budget:
  - ref24: cpu 5.209 over 3.63; loop 0.2603 over 0.1813; memory 3861 over 2686.
  - ref30: 5.701 and 5.532 over 3.934.
  - ref46: 4.647, 4.777 and 4.696 over 3.357.
  - ref53: 2.885, 2.841 and 2.925 over 2.081.
  - The refused rulers read `runner class unknown` on both clean and doubled.
  
  Base-vs-base control at acec536b (ev/finder_harness_base_acec536b.txt): the ref24 job reads `runner class unknown`, reproducing CI's 4 reds, and every other class reads identically to the head.
  
  Mutants re-planted at this head (ev/mutants_r4.txt, the tree restored and clean):
  - Killed by `class_budgets`: K24, K24L, K24B, K30, K46 and K53. K24B also turns `runner_class_unknown` red.
  - Killed by `runner_class_unknown`: M4, FALLBK, W30, W30u and W46.
  - Survived: W24u, W24d, W53u and RF-EMPTY (see Findings).
  - The null edit reads 33 of 33 ok.
- **Ask (3): earlier pins.** `away:covered_names_are_committed` and the recorder unsupported-scheme pin are ok locally (33/33 controls) and in CI job 125530195186. The owner `cpu_ratio` 337.8 and `loop_cpu_ratio` 0.249 are unchanged from r3, and the CI owner readings 241.65 (ref46) and 269.82 (ref24) are WITHIN.
- **Ask (5): untouched paths.** The three-dot diff names no `*_budgets.json`, claim file, VERSION, manifest or RELEASE_NOTES.md. No host path appears in the added lines. `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. `python3 tests/closure.py select --diff b8e823699`: `MODE: SCOPED -- 3 script(s) run, 30 scoped out.` The delivery row dev/programme/delivery/3174.md is in the three-dot diff.
- **Figures not re-derived.** I did not re-derive the body's "census of 22 jobs" in full. I re-graded 12 cited jobs (the 9 `COST_CLASS_READINGS` jobs, both refused rulers, and this head's lane). The 22.16 nightly job 121370544228 and the remaining census jobs were not opened. I did not re-run the body's `prepr.sh` or the scoped scripts beyond `structure.py` and the closure select.
- **Instrument.** The harness is the finder's from r3 (CI `cost` lines through the production grading functions). ev/grade.py is my own script that applies it, and ev/controls.py runs `replay.controls()`. Both are disclosed per fix-review step 9.
