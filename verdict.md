Fix review: merge 7f6d7e72260ca64e98ec13c3b7c46c5e01af62a6

bus-nonce: 2b1ddd8f170885a89e93ce2bbbbb73f8

## Summary

Round 3 of this group's fix review (fixer.md: from the fourth round a re-cut is owed, not a repair). Range `d1662cf7b..7f6d7e72`. The authored commit is `fcbf8ec95`; the rest are an automatic main merge and the bot's `ci: pin killed mutants`. Measured at head `7f6d7e72260ca64e98ec13c3b7c46c5e01af62a6`, merge base `d052f80f7f81d42db5c57a55ebaef7056c7ce01a` (origin/main), from detached worktrees, with the finder's harness. Both earlier blocks are answered in the code and the tests. The verdict is merge on the code. The PR body has not been brought up to round 3; that is a body edit (Findings).

## Findings

- The PR body does not record round 3 (`fcbf8ec95`). `## Mutation proof` and `## Figures` still describe round 2: 28 FR checks, and no U6 or U7 entry. `## Red checks` attributes `tests / fast (3.14)` and `tests / mutation-autofix` only to round 1 (`e2b12a17`). It does not answer the separate red both checks carried at `d1662cf7b`. The cause there was the `tests/entities.py` `_svc_fr_record` stub returning None; it is named only in the commit message. The cheaper detector was running `tests/entities.py` whole on Linux before the handoff: about 25 s on CI, 8 min in this container. The round-2 verdict asked for that answer in the body. The fix is a body edit, which moves no head: add round 3's mutation proof (U6 and U7 killed by the two new checks, the two equivalent `return None` triages), the 31-check figure, and a `## Red checks` entry for the `d1662cf7b` red with that detector. The `pr-contract` run at the head the train merges then checks it. Carry: R10-FACTORY-RESET
- The head moved while I measured. The PR head is now `2df0b81ed2fb9726a4b8d52de072fdb64520ded1`, one `github-actions[bot]` commit (`ci: pin killed mutants`) that adds 13 `tests/mutation_ledger/killed_by/` records and no production or test line. `tools/audit/seat/review_carry.py 7f6d7e72 2df0b81e` prints `FRESH-REVIEW`, because ledger files count as branch-only content (ev/review_carry.txt). So this verdict does not carry to `2df0b81e` by the tool. Every figure below concerns code and tests that commit leaves unchanged, so they all hold at `2df0b81e`. The orchestrator owes the call on re-confirming at `2df0b81e`, and on `gate` and `pr-contract` there. Neither concluded at `7f6d7e72` (Evidence, CI). Carry: R10-FACTORY-RESET

## Evidence

Contract and head: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so fix-review.md is current. The body's `## Head` names `7f6d7e72260ca64e98ec13c3b7c46c5e01af62a6`, the head I measured. The review packet (ev/review-packet.md) reports no refusals and no advisories, and carry_audit at the head reads 3 routed, 0 unrouted.

Harness: the finder's. That is `ev/` of probe/rev-3047-30905b88 (round 1: the section-extract recipe, run.py, list2.py) and `ev/` of probe/rev-3047-0dec8285 (round 2: run2.py, list4.py, list5.py, full.py). I re-extracted the R10-FACTORY-RESET section from this head's `tests/features.py`, lines 13167..13774, with the module header and `_li_state_of` as the round-2 file carries them (ev/fr_section_head.py). Unmutated it reads `ALL 31 FR CHECKS PASSED` (ev/sec_head.txt). The only changes to the drivers are their paths to the worktree (ev/run.py, ev/run2.py, ev/full.py; ev/list45.py is list4 plus list5 concatenated for full.py).

Block (1), verdict/3047 round 1, the void list:
- RESULT void-entry mutants: 21 killed, 0 survived (ev/mut_void.txt). This is the finder's list2.py verbatim, each entry deleted in turn and run through the section. `_FACTORY_VOID` at this head has 21 entries: 14 thermal, 3 stores whole (`dhw_profile`, `dhw_draws`, `price_model`), 4 accuracy. The brief's figure of 22 does not match the tree. Round 2 counted 21 too.
- `dhw_draws` is written to disk by the test. Its `None -> ()` mutant is killed by 3 checks.
- The kills come from "a learners reset drops every learned key, key by key, and keeps every fact", per learner, against the test-owned `_FR_FACTS` list.
- The entry_config GUARD_OFF (T1, T2), the coordinator RETURN_DEL (C1), and P1..P4, R1..R7, S1/S2/S4, U1..U5, N1/N2, SV1/SV2 and T3..T6 are all killed in the section (ev/mut_list4.txt).
- The two humidity CMP_BOUND mutants (C2, C3) and the DHW-probe guards (C4, C5) survive the section, as in round 2. Each is killed by the whole of `tests/features.py`: C2 and C3 `1 of 4713 FEATURE CHECKS FAILED`, C4 and C5 `3 of 4713` (ev/mutants-full-features.txt). Unmutated, the whole file reads `ALL 4713 FEATURE CHECKS PASSED`, rc 0 (ev/features_head_unmutated.txt).

Block (2), round 2 at `d1662cf7b`, the learner flush and `tests/entities.py`:
- RESULT U6 (`await _async_save_restored(coord)` deleted from `_async_store_documents`): KILLED, `FAIL the undo restores what the learners knew at the reset, learning since the last save included: COP scale 1.21  [restored True, COP scale 1.13]` (ev/mut_list4.txt).
- The null control, with the flush present, is the new check "learning since the last save is in memory only before the reset: COP scale 1.21 held, 1.13 stored (the control)". It passes, and so does the restore check (ev/sec_head.txt). The control shows the 1.21 is unsaved state when the reset starts, so the undo restoring 1.21 is earned by the flush.
- RESULT U7 (`undo_target` taking any undo point in the ring): KILLED, by "after an unhealthy snapshot newer than the undo point, the restore takes neither: nothing qualifies, the reset stays".
- `tests/entities.py` at this head: `ALL 2499 ENTITY CHECKS PASSED`, rc 0, including "factory_reset hands that entry's coordinator its scope and reports both" (ev/entities_head.txt). Its printed `FAIL` lines are the script's own planted-negative self-tests, each followed by its `ok` arm. CI agrees: `tests / fast (3.14)` concluded success at this head.

Lane sites: the lane's exact operators, through the section and the whole file (ev/mut_list5.txt, ev/mutants-full-features.txt):
- 358 GUARD_OFF, 369 GUARD_OFF and 373 RETURN_DEL are killed in the section; 9955 GUARD_OFF is killed by the whole file.
- `entry_config.py:360 RETURN_DEL` and `coordinator.py:9957 RETURN_DEL` survive the whole file (`ALL 4713 FEATURE CHECKS PASSED`). Each deletes a function's trailing `return None`, which is an equivalent mutant. Both are recorded by hand under `tests/mutation_ledger/survivor_triage/` in `fcbf8ec95`, and I agree with both records.

Mutation lane at this head (tests / mutation 124914587936):
- It reads `MUTATION TABLE REFUSED -- 3551 unpinned site(s) against 3551 at the ratchet base d052f80f7, 14 of them added by this diff`. Every one of the 14 is in the body's `## Unpinned sites`, each marked mutation-autofix. That list also carries 6 sites that are already pinned or triaged, so it is a superset, not an omission.
- The three `tests / mutation-pins` shards measured 5 + 4 + 4 = 13 anchors (shard 1: `PIN KILLED: 6 pinned, 0 left unpinned`). The bot commit `2df0b81e` adds exactly 13 killed_by records, one per anchor. `CMP_BOUND*2` is one anchor.

Carry-over, re-checked for drift:
- Undo exact pins, refused-unload messages, FACTORY_KEPT, learner scope, and the undo point taken before the heat-loss void call: all mutants above are killed, as in round 2. The null control "unconfirmed, nothing changes" passes, and N1 is killed.
- The delivery row `dev/programme/delivery/3047.md` is in the three-dot diff.
- Claim files: `card_claimed_drift.txt` is byte-identical to origin/main. `claimed_drift.txt` differs on its one `config_flow` line only, which carries this branch's claim. That is expected for a branch that claims a drift (claim-files.md), and it is why the file is not byte-identical.
- `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all d052f80f7` reads `CLAIMED config_flow: 4 leaves moved`, `NO UNCLAIMED DRIFT: 56 scenario(s)`, `NO STALE FIXTURE: 56`, rc 0 (ev/envdrift_head.txt). `claims-for: 7.1.0` equals VERSION 7.1.0. VERSION, manifest.json and RELEASE_NOTES.md are untouched.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`, `seam_cut_total 423 <= 423` (ev/structure_head.txt).
- Scoped gate: `tests/closure.py select --diff d052f80f7` prints `MODE: SCOPED -- 31 script(s) run, 2 scoped out.`

Raise (step 14), `seam_cut_total` 422 -> 423 (ev/raise_plants.txt):
- Removing the `coord._snapshot_store` wait gives `seam_cut_total=422`, so the +1 is the crossing the body names.
- Re-spelling the read as `_ctx_of(coord)._snapshot_store` gives 423, so the instrument does not reward a re-spelling.
- The body's third payment, refusing while `_snapshots_loaded` is false, measures 422, as the body says (+0). I judge it as the body does. It turns a load window into a user-facing refusal, and the existing `factory_reset_not_applied` text would then state the wrong cause. That is not a sounder change.
- No other existing owner waits on the snapshot read for the learning seam, so I found no payment the body missed. This part is analysis, not a built variant.
- `python3 tools/audit/archscore/score.py --diff d052f80f7` reads `Architecture score: dS +0.0030 IMPROVES`, `coord_footprint 2387 -> 2382` (ev/archscore_head.txt). The dS matches the body. The footprint pair differs from the body's `2389 -> 2384` because the body measured against older merge bases (`8fec54ee`, `92588d58`), as it states.
- This verdict does not approve the raise. The approval is the owner's review under budget-raise-gate.

Merge: `git merge-tree --write-tree origin/main 7f6d7e72` exits 0, tree f0a037f0 (ev/merge-tree.txt). No claim file conflicts, so the claimnotes driver did not run.

CI at this head (ev/check-runs-head.txt, ev/classify-log.txt):
- Concluded red: `tests / mutation`, whose 14 added sites are pinned by the bot commit, and `budget-raise-gate / budget-raise-gate`, red until the owner's approving review (`REFUSED: no decisive review by tvofi`). The body names both.
- Every other concluded check is success, `tests / fast (3.14)` and `tests / typing` among them.
- `gate` and `pr-contract` never ran at this head. The bot push to `2df0b81e` superseded it first, and new runs started there at 17:53 UTC. `merge_train.py classify 7f6d7e72` returned 3 (WAIT, `pending: gate`) on every run from 17:01 to 17:59 UTC. So the classifier is unreadable for this head: it can never reach GREEN or RED. I stopped the wait.
- Because no `pr-contract` run checked the body at this head, the body's red-check record is unverified here. That is the first Finding.
