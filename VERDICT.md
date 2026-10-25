Fix review: blocked 9d5c6afe928445223aaec2504bfee9a4d7489875 carry-missing: friction item R10-PIN-DRIVE-INCONCLUSIVE names R10-FLOW-JIDOKA, which does not hold it, and the body names no roster SHA

bus-nonce: dc8005df956a622de462866290b9fbef

This is review round 5 for #2712. Four earlier `Fix review:` verdicts blocked 5fb0a083b, a126c8b3f, f0a975b0a and 7afd9452b. The brief calls this fixer round r6. As the brief asks, I judge the delta since round 4's verdict on 7afd9452b: the round-5 code (305f284bd, 438b14cf4, 3fd107bd7, 08105c13e, fe96b2289), the r6 ledger pins (f7ee98672), and the merges 427be9080 and 9d5c6afe9.

I measured head 9d5c6afe928445223aaec2504bfee9a4d7489875. `git ls-remote` still showed it as the PR head when I wrote this (`ev/HEAD.txt`). I read fix-review.md from origin/main b89fea13e, and the roles diff against the merge base is empty. Every mutant ran in its own fresh detached worktree at the head.

The orchestrator's three requirements are met:
- `tests/structure.py` exits 0 at this head.
- The five coordinator.py sites are pinned, and each is killed.
- The fast (3.14) and mutation entries are answered.

One block remains.

## Block

- **carry-missing (step 10).** The body's `## Friction` item `R10-PIN-DRIVE-INCONCLUSIVE ... Carry: R10-FLOW-JIDOKA` is not in R10-FLOW-JIDOKA's brief, either on `handoff/audit-r10-roster` at dbd592fe41c8c45b0b2f1677e0b9fc9c24971caa or on origin/main. I searched every field of that group for `INCONCLUSIVE`, `demand-overbook` and `2712` and found 0 matches (`ev/carries.txt`).
  - R10-FLOW-JIDOKA's scope is prepr's quick-check replay (`files: tools/pr/prepr.sh`). The owner's ruling, quoted in the group, excludes any mutation run from that scope. Even if the text were written there, that group would not act on a `tests/mutation_table.py --pin-killed` baseline defect.
  - The body names no roster-branch SHA. `finding-propagation.md` says "The body names the file, the stage and (a roster carry) the branch SHA".
  - This is the same class of block that rounds 2, 3 and 4 of review raised on this PR's friction items.
  - Repair: write the item into a live group that owns `tests/mutation_table.py`. R10-MUTANT-SKIP (in-progress) and R10-FLY-LEDGER-SAMPLE (not-started) both list that file. Point the marker at that group, and cite the roster SHA in the body.
  - The four `## Forward-carry` markers are correct and land: R10-UX-HEALTH holds 1, R10-BUFFER-STORE holds 2 (the DP lead and the `dhw_temp_trajectory` tank seed), and R10-LEARNER-DEFAULT holds 1. They are on the roster branch and on origin/main. Round 4's mismatch on those lines is repaired.

## Findings

- **The `failed=N` figure in every `killed_by` reason recorded on `tests/features.py` is one too high.** This is the fourth review round to find it (rounds 2, 3 and 4 recorded it as `failed=2` against 1). The cause is in the instrument:
  - `tests/mutation_table.py` `failing_count` returns `n + int(_TRACEBACK in run.stderr)`.
  - The unmutated `tests/features.py` already prints `Traceback (most recent call last):` at log lines 106, 740 and 1207, from its own negative controls (`ev/mut_unmutated.features.log`).
  - So every red features.py run is counted one higher. At this head: BOOLOP 8f67bdf0 records 4 and fails 3. RETURN_DEL 7cca5f1c records 8 and fails 7. GUARD_OFF 73ca1d75 records 2 and fails 1. GUARD_OFF 5bbf06c9 records 8 and fails 7. legionella GUARD_OFF c97515c6 records 2 and fails 1.
  - The kills are real. Only the recorded tally is wrong.
  - It is a recurring error, so it owes a `root-cause.md` seat rather than another note.
  - Carry: R10-FLY-LEDGER-SAMPLE
- **Two behaviours on lines this diff rewrites are pinned by nothing in `tests/features.py`.** Neither gap is this PR's own; both survive on origin/main b89fea13e too.
  - The published `dhw_hours_since_legionella` value: `dhw_hours_since_legionella=hours` -> `=None` gives `ALL 4388 FEATURE CHECKS PASSED`. On main, the same mutant of `=self._legionella.hours_since()` gives `ALL 4374 PASSED` (`ev/mut_h_hoursnone.txt`, `ev/mut_main_h.txt`).
  - The `check_ceiling()` call: deleting it from `LegionellaGuard.async_observe` gives `ALL 4388 PASSED`. Deleting it from main's coordinator gives `ALL 4374 PASSED` (`ev/mut_l_noceil.txt`, `ev/mut_main_l.txt`).
  - The new `return self.hours_since()` (RETURN_DEL 32cb48eb) is killed only statically. `tests/typing_ruler.py` fails it on `by_code[return] did not grow [recorded 0, measured 1]`, while `tests/features.py` passes it (`ev/mut_g_obsret.*`). The ledger accepts a static kill, so the pin stands. But no value check follows the hours from the guard to the published payload.
  - A coordinator-level check that a hot tank's reset shows up in the published hours would close all three.
  - Carry: R10-DEMAND-OVERBOOK
- **`## Red checks` names `tests / fast (3.14)` red at 0b03e095f, but not the same red at the next head d9f8e2d16** (run 40180441420, job 121130499831). It also does not name `pr-contract` red at both heads. I re-ran `tests/structure.py` at d9f8e2d16: `FAIL seam_cut_total 424 > 418 (+6)`, rc=1 (`ev/structure_d9f8e2d16.txt`). That is the cause the body gives for 0b03e095f, and d9f8e2d16 does not contain fe96b2289 either. So the answer the body gives covers it, but the head is not named.
  - Whether the step-11 trigger is final cannot be judged yet, because `tests / mutation` is still in progress and `pr-contract` has not reported on this head.
  - Carry: R10-DEMAND-OVERBOOK

## Evidence

- RESULT structure, `PYTHONPATH=tests/hastub python3 tests/structure.py` (`ev/structure_head.txt`, `ev/structure_origin_main.txt`):
  - At the head: `STRUCTURE RATCHET PASSED`, rc=0, with `seam_cut_total 419 <= 419`, `max_class_loc 8311 <= 8311`, `class_excess_loc 18102 <= 18102` and `duplication_copies 16 <= 16`.
  - At origin/main b89fea13e: 420 / 8343 / 18103 / 17, passed.
  - Against main, the budget file moves 420->419, 8343->8311, 18103->18102 and 17->16, and raises nothing (`ev/budget_diff.txt`). The deltas match the body's −1/−32/−1/−1. Its absolute values were taken against f40142d66.
  - Round 3's and round 4's block (424 > 418) is paid in code: `_track_dhw` is gone, its body moved into `LegionellaGuard.async_observe`, and `_async_learn_interval` holds the learner sequence.
- The merge warning the brief quotes. `git merge-tree --write-tree origin/main 9d5c6afe9` exits 0 against b89fea13e (`ev/merge_tree.txt`). It also exits 0 against main 0825aee64, which landed during the review (tree a6b34a6f0). There its stderr is `LEDGER-MERGE: resolved tests/closures.json ... re-run the gate that owns this file before pushing`, with no claim-file conflict (`ev/merge_tree_new.*`). I re-ran `tests/structure.py` on that merged tree: `STRUCTURE RATCHET PASSED`, with `seam_cut_total 419 <= 419` and `max_class_loc 8311 <= 8311` (`ev/structure_merged_new_main.txt`). So it holds.
- The closure gate:
  - `tests/closure.py select --diff <merge-base>` prints `MODE: SCOPED -- 28 script(s) run, 5 scoped out.`, the body's figure (`ev/closure_select.txt`).
  - The heavy closure lane is cited from CI, not re-run (step 11): `tests / closures` is success on this head (job 121180713136), and so is `tests / fast (3.14)` (job 121180713214).
  - The one new file the diff adds, `dev/audit/harnesses/r10_demand_overbook.py`, is listed in `tests/closures.json`.
- Step 14 (seam map). The diff maps `_async_learn_interval` and `coordinator._propagated_slab` to `learning`. To see what the counter does under other choices, I remapped `_async_learn_interval` to `core` and to `dhw`. Those give 422 and 440, both breaches, against 419 (`ev/seam_map_perturb.txt`). `learning` is its honest seam, since the method calls only the house, lower-floor and COP learners. Its name carries the prefix of the other `_async_learn_*` entries. The −1 is earned by moving the DHW block out of the coordinator, not by the map.
- Spent prose. Most of the −32 `max_class_loc` comes from shortening coordinator-class comments: the v5.3.0 docstring paragraph, the lower-zone history and the learner-order note. The invariants are kept in shorter form: the cycle follower runs regardless of a reading (the `async_observe` docstring), and the baseline reader runs first (the `_async_learn_interval` docstring). Round 1 of review ruled spent prose an allowed payment.
- RESULT mutation (step 1) at the head, `PYTHONPATH=tests/hastub python3 tests/features.py`. Summaries are in `ev/mutants_summary.txt` and diffs plus output in `ev/mut_*.txt`:
  - Unmutated: `ALL 4388 FEATURE CHECKS PASSED` rc=0. `harness_headers.py`: `ALL 112 HARNESS HEADER CHECKS PASSED`. `typing_ruler.py`: all passed. The body's 4385 was taken at f7ee98672; main has since added 3 checks.
  - `_async_learn_interval` BOOLOP (`and`->`or` on the COP save): rc=1, 3 failed, the buffer/learner save-count checks.
  - `_async_learn_interval` RETURN_DEL: rc=1, 7 failed, including `D12-s1-01: ... slab seed follows the previous plan` and `#2499: the slab rises with the metered draw ...`.
  - `_update_current_state` BOOLOP 73ca1d75 (`tank is not None or ...`): `features.py` rc=1. The cycle raises `'<=' not supported between instances of 'float' and 'NoneType'` (ConfigEntryNotReady). `harness_headers.py` gives `15 of 112 FAILED`, matching the pin's 15. This is a crash kill, so it is real.
  - GUARD_OFF 73ca1d75: rc=1, 1 failed, `#2499: a tank reading reaches the DHW learner ...`.
  - GUARD_OFF 5bbf06c9 (`if seed is not None` -> `if False`): rc=1, 7 failed.
  - legionella GUARD_OFF c97515c6: rc=1, 1 failed, `#2499: a tank at the disinfection temperature resets the legionella timer ... [hot=None cool=None none=None]`.
  - legionella RETURN_DEL 32cb48eb: `features.py` passes; `typing_ruler.py` rc=1 (see Findings).
  - My own mutants: `slab_unsensed=False`: rc=1, 7 failed. Reading `prior_at` after the house learner (`self._last_house_sample_time` at the return): rc=1, 3 failed, including `a metered pump that drew nothing leaves the slab cooling [slab=25.000]`. This pins the order the docstring claims. Deleting `async_track_cycle`: rc=1, 30 failed.
  - Null control, a comment on the `check_ceiling()` line: `ALL 4388 FEATURE CHECKS PASSED` rc=0.
  - The five coordinator.py sites that r5 left unpinned are all pinned at this head, and each is killed by its named script. The two legionella sites are pinned too.
- Behaviour of the r5 move. Per reading, `async_observe` keeps main's order: tracker on a reading, `disinfect.observe`, `async_track_cycle` on the reading or `None`, `check_ceiling`, `hours_since`. The publish now runs after the await, which 3fd107bd7 says fixes a stale-context overwrite. The `prior` state is captured before the copy and passed through; `prior_at` is read before `_async_learn_house_heat_loss` overwrites it. That is the delta's only reorder, and the mutant above pins it.
- r6 changes no production line. The PR's own patch on `custom_components` and `tests/features.py` is the same at fe96b2289 (against its merge base) and at f7ee98672 (against f40142d66), checked by comparing the +/- lines of the two diffs. 427be9080 and 9d5c6afe9 are automatic merges.
- Class (step 6). `grep -n "_open_loop_plan_value("` at the head returns three sites (`ev/class_census.txt`). coordinator.py:1016 is the slab fallback in `_propagated_slab`, which is closed. :1975 is the definition. :6379 is the tank seed, carried to R10-BUFFER-STORE. That matches every earlier round.
- Architecture (step 15). `score.py --diff b89fea13e HEAD` prints `dS +0.3255 WORSENS (inadmissible: coord_footprint 2446->2447)`, with `duplication_copies 39 -> 38`. That is the body's dS. Its footprint absolutes (2463->2464) were taken against f40142d66. The body explains the +1 under `## Architecture score`, and `arch-score` is green on this head (`ev/archscore.txt`). `_async_learn_interval` and `async_observe` orchestrate and delegate, with no arithmetic added to the coordinator. I found no step-17 breach.
- Versions and claims (steps 4, 5). `VERSION`, the manifest, `RELEASE_NOTES.md` and both claim files are untouched against merge base b89fea13e (`ev/untouched.txt`). No golden fixture is in the diff.
- Harness (steps 2, 9). I did not re-run `dev/audit/harnesses/r10_demand_overbook.py`. The slab path's production code (`_propagated_slab`, `draw_range.space_draw_kw`) is unchanged since round 1 of review re-ran it at both ends; that run verified directions and null arms, and values as directions only. It is the fixer's own instrument, as the body discloses.
- Head (step 7). The body's `## Head` names 9d5c6afe9, made by merging f7ee98672 and then origin/main b89fea13e. The commit graph matches.
- CI (step 11; `ev/ci_checkruns_head.txt`). Every concluded run on this head is success or skipped. `tests / mutation` (job 121180600924) and the edit-run `prelude` are in progress, and `pr-contract` and `gate` have not reported. The body names its two red-check entries with a cheaper detector each:
  - fast (3.14): `tests/structure.py`, 17 s per push.
  - mutation: `tools/pr/ci_predict.py`, a static read.

  I re-derived the fast cause at d9f8e2d16 (see Findings).
- The body's figures I could not re-derive at this head, because they name another tree (f40142d66 / f7ee98672 / a22eece4e): the predictor control's `7 unpinned site(s)` at a22eece4e, `4385` checks, and the absolute budget and footprint values. Their deltas reproduce where I could measure them.
