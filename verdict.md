Fix review: blocked 9951f224a9e652fb7323784e05d86b4b35f16e55 carry-missing: not carried to R10-ARCHSCORE-COVERAGE (#2259 item 2, #2373): the card_dead_definitions census registration and the ledger strike owed at #2373's merge are in this PR's body and RCA §5.3 only; the group's roster brief and carry on origin/main name neither

bus-nonce: 9e706e565b088baabddcc43f3c4b61c3

PR #2415, R10-RCA-STRUCTURE-BLIND. **Review round 1**: the PR has no earlier `Fix review:` comment. I reviewed from a detached worktree at head `9951f224a9e652fb7323784e05d86b4b35f16e55`. The merge base is `55dc8d9c2c59c2ab614cb7c5d4b0ae9807401b50` and origin/main is `c8cc75ea9`. `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so my contract is current. Every figure below was taken at this head, in a full clone, unless I say otherwise. All the evidence is in `ev/`.

## What holds (re-derived by me)

- **Ratchet.** `tests/structure.py` prints `ok name_kept_members 38 <= 38`, `RESULT name_kept_members=38 count` and `STRUCTURE RATCHET PASSED`, rc=0 (`structure_head.txt`).
- **The hand-added budget row equals `--record`.** I ran `--record` in a scratch worktree. It changes only `recorded_at`, from `e5f7e169d` to the merge base `55dc8d9c2`, and keeps `name_kept_members: 38` (`record_diff.txt`). The body's claim holds.
- **Plant harness, both ends** (`plant_head.txt`, `plant_main.txt`).
  - At the head: `clean_refused=0`, `plant_refused=1 (name_kept_members)`, `null_refused=1 (dead_methods)`, `typed_refused=0`. name_kept is 38, 39, 38, 38.
  - On main's `structure.py` and budgets: `plant_refused=0` with `plant_name_kept=39`, and `null_refused=1`. The defect reproduces on main, and the control fails at both ends.
  - This harness is the RCA seat's own and says so in its docstring. A root-cause record has no finder harness for its countermeasure, so I also ran independent on-disk plants with my own instrument (below), plus the finder's D7 and D14 harnesses (F4, F5).
- **My own plants, on disk, outside the harness's anchor** (`mutants_structure.txt`, `F3b_structure_on_diskplant.txt`).
  - A live `_RevKept.to_dict` in `coordinator.py`, kept only by an untyped `x.to_dict()`: `FAIL name_kept_members 39 > 38 (+1)`.
  - A property `to_dict` kept by an attribute-only `x.to_dict`: the same FAIL.
  - The harness's `diagnostics.py` plant written to disk: the same FAIL.
- **Mutants on `tests/structure.py`, each restored after its run:**
  - M1, the row dropped from `measure()`: `FAIL name_kept_members: in the budget table but never measured`, rc=1.
  - M2, the row hard-coded to 0: `1 STRUCTURE BUDGET(S) IMPROVED AND NOT YET RECORDED`, rc=2.
  - M3, `owners = None` in `dead_members` (line 2192): `3 COUNTING RULE(S) BROKEN`, rc=1.
  - All three match the body.
- **Census arm** (`census_head.txt`, `selftest_head.txt`, `F6_census_mainstructure.txt`, `mutants_census.txt`).
  - At the head, `--only census` prints `read=3 ... refused=0`. Each census is refused on its own row: `0 -> 1`, `1 -> 2` and `38 -> 39`. It ends `FIELD COVERAGE ok`.
  - With main's `structure.py` and budgets, `name_kept_members` is `REFUSED` because its count line cannot be read.
  - With the row uncapped (9999): `BLIND ... UNGATED, 38 -> 39 ... no FAIL on name_kept_members`, ending `FIELD COVERAGE REFUSED`.
  - `--self-test` prints `FIELD COVERAGE SELF-TEST ok`. Removing each of the three new `censusRun` branches (UNGATED, the gate-less census, the census red unplanted) fails exactly its own self-test arm.
- **RCA figures.**
  - **F1:** the tag series reads `v6.7.14 124`, `v6.7.15 132`, `v6.7.16 132`, `v6.7.17 141`, `v7.0.0 152`. It matches the RCA (`F1_series.txt`).
  - **F3:** the arch-score delta on the harness plant reads `dS 0`, `rises []`, `NULL`. It matches (`F3_archscore_plant.txt`).
  - **F4:** the finder's `namekept_receivers.py` reads `candidates_with_zero_typed_hits=6`. It matches.
  - **F5:** the finder's D14 `enumerate.py` reads `seams=10`, `instances=5`. Its rule-E row is the literal at line 132, as RCA §3 item 3 says (`F5_enumerate_head.txt`).
  - **F8:** five tags from `2b6c5b87`; `16551007` first at `v6.7.15`; `fee38809` first at `v6.7.13`; 54 tags in the window. All match.
  - **F9:** I re-derived #2311's span only, from 2026-10-15T19:29:59Z to its merge at 2026-10-16T14:29:26Z: 19.0 h. That matches.
  - **Cost-test arithmetic:** (2.1×2 + 9.5 + 17.6×2)/5 = 9.78 h, 4/5 = 0.8, and 7 × 25 min = 2.9 h. It is consistent.
- **The class (step 6).** The D14 enumerator's ten seams are each dispositioned in RCA §1 or §3, or in the new barrier's "Not reached" list:
  - `max_class_loc` (#2340);
  - name-kept (this PR);
  - the card `.js` (#2373);
  - `is_any` and returned_keys (#2293);
  - the hub engine (#2311);
  - the annotation grammar ("Not reached").
- **Other checks.**
  - `env -u BASH_ENV tests/entities.py` prints `ALL 2347 ENTITY CHECKS PASSED`, rc=0 (`entities.txt`).
  - `fold_ledger.py check` reports `0 violation(s)`.
  - `harness_headers.py` prints `ALL 109 HARNESS HEADER CHECKS PASSED`.
  - `VERSION`, the manifest, `RELEASE_NOTES.md` and both claim files are untouched. No package file changes, so `env_drift` has no fixture that could move.
  - `git merge-tree --write-tree origin/main 9951f224` exits 0 (tree `0c1df9905`, `merge-tree.txt`).
- **Head (step 7).** The body names `9951f224` as the head, with `ba9653fa0` as the authored code head plus a delivery-row commit. `git log` agrees.
- **CI (step 11).** There are 46 check-runs at this head, all completed, and every one is success or skipped. None is red, so no red check is owed an answer (`check_runs.txt`). The two local reds the body answers (`stress.py`, `harness_headers.py`) are named with their detector answers.

## Why blocked

**Step 10: the forward-carry to #2373 is not at its destination.** The body's `## Forward-carry` and RCA §5.3 say that two things are owed when #2373 merges:

1. `card_dead_definitions` registers as a `field_coverage.mjs` census, with its plant and the `arch-score` gate as its refusal.
2. The ledger's "Not reached" entry for the card `.js` is struck.

RCA §5.3 assigns both to "#2259's item-2 group, not to this RCA". This PR's own `bugclasses.json` barrier keeps the card in "Not reached" *until #2373 merges*. That stage has not merged, and the carry changes what it must deliver.

Neither item is in that stage's brief:

- On origin/main, `dev/programme/rosters/wave-r10-groups.json`'s R10-ARCHSCORE-COVERAGE `brief` and `carry` name neither `field_coverage` nor the ledger strike. `git grep field_coverage` over `dev/programme/` returns nothing for that group.
- #2373's body and its three review comments do not mention it either.
- The finding lives only in this PR's body and its RCA record. `finding-propagation.md` says that records it but does not propagate it.

**Remedy (the orchestrator's, and the head need not move).** Add a carry to R10-ARCHSCORE-COVERAGE's roster entry, and to its out-of-tree brief if one is live, carrying the control. For example:

"From R10-RCA-STRUCTURE-BLIND (#2415): when part 4 lands `card_dead_definitions`, register it in `tools/policy/field_coverage.mjs` CENSUSES with `gate` set to the arch-score row and a plant of one unused top-level card function. The census must read `n -> n+1, refused on <row>`; with the row uncapped it must read `UNGATED`. Then strike the card `.js` from N-structure-blind's `barrier` "Not reached" in `dev/audit/config/bugclasses.json`."

With that carry on origin/main, a re-dispatch at this same head would be `merge` from me, provided nothing else moves.

## Noted, not blocking

- The PR body names the branch `r10-rca-structure-blind`, but the PR's head ref is `fix/r10-rca-structure-blind`. This is cosmetic.
- The census tree's unplanted `dead_top_level_symbols` reads 1, against 0 in the full tree. This was already so before this PR, and the arm reads `1 -> 2` correctly.
- The questions the body routes to the orchestrator and to tvofi (RCA §8) are open questions, not carries, so they are not judged here.

## Not verified by me

- #2293's and #2340's fix spans (F9).
- The local scoped-gate and `stress.py` figures, and `score.py --diff origin/main`. CI's `arch-score` runs at this head are green.


RESULT plant_refused_head=1 count
RESULT plant_refused_main=0 count
RESULT null_refused_both_ends=1 count
RESULT census_read=3 count
RESULT mutants_killed=6 of 6 (M1, M2, M3, and the census branches UNGATED, no-gate, red-unplanted)
RESULT red_checks_at_head=0 count
