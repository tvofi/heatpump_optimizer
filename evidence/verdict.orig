Fix review: merge bd8011e9231944317162ffbde7824ffcad89ff2e

bus-nonce: 59142f3e0143987162ae84de7fe21e7f

PR #2415, R10-RCA-STRUCTURE-BLIND. **Review round 2.** Round 1 (`9951f224a`) returned `blocked ... carry-missing: not carried to R10-ARCHSCORE-COVERAGE`. I reviewed from a detached worktree at `bd8011e9231944317162ffbde7824ffcad89ff2e` (`ev/HEAD`), on this Linux cloud runner (Python 3.14.7, node 22.22.0), with a full clone. The merge base is `913ce1ff5`, and origin/main is `abb397938`, 34 commits ahead. `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so my contract is current. The evidence is in `ev/`.

## Round-1 blocker: cleared

- The carry is now on origin/main, landed by `2e7aad8e3` ("roster_edit append-carry R10-ARCHSCORE-COVERAGE: #2415 census + barrier strike precondition").
- R10-ARCHSCORE-COVERAGE has one `carry` entry naming #2415, and its `brief` names #2415 and `field_coverage` (`ev/roster_carry_main.txt`).
- The carry states its control as a precondition, as `finding-propagation.md` requires:
  - `--only census` must print `card_dead_definitions: n -> n+1 ... refused on <row>`;
  - with that row uncapped it must print `UNGATED` and end `FIELD COVERAGE REFUSED`;
  - the card `.js` is to be struck from the barrier's "Not reached" clause in the same PR.
- The group is live: its `resume.stage` reads in-progress.

## Authored delta since round 1: none

- `git diff <mb>...9951f224a` and `git diff <mb>...bd8011e9` differ only in hunk offsets, index lines and neighbouring context (`ev/r1_diff.patch`, `ev/head_diff.patch`).
- The rest of the context differences are main's: a different neighbouring `closures.json` INERT entry, and `structure_budgets.json`'s `recorded_at` and `seam_cut_total`.
- The PR's own additions are byte-identical.

## Re-taken at this head

**Ratchet.** `tests/structure.py` prints `ok name_kept_members 38 <= 38`, `RESULT name_kept_members=38 count` and `STRUCTURE RATCHET PASSED`, rc=0 (`structure_head.txt`).

**Plant harness, both ends** (`plant_head.txt`, `plant_main.txt`). The harness is the RCA seat's own and says so. Round 1 established that a root-cause record has no finder harness for its countermeasure, so I also ran the finder's D7 and D14 harnesses and my own plant.
- At the head: `clean_refused=0`, `plant_refused=1 (name_kept_members)`, `null_refused=1 (dead_methods)`, `typed_refused=0`, `row_in_budgets=True`.
- On main's `structure.py` and budgets: `plant_name_kept=39` but `plant_refused=0`, with `null_refused=1` and `row_in_budgets=False`. The defect reproduces on main, and the control fires at both ends.

**Mutants on `tests/structure.py`, each restored** (`mutants_structure.txt`):
- M1, the row dropped from `measure()`: `FAIL name_kept_members: in the budget table but never measured -- re-record`, rc=1.
- M2, the row hard-coded to 0: `1 STRUCTURE BUDGET(S) IMPROVED AND NOT YET RECORDED`, rc=2.
- P1, my own on-disk plant outside the harness: a new class in `coordinator.py` whose `as_dict` only an untyped `x.as_dict()` reaches. It gives `FAIL name_kept_members 39 > 38 (+1)`, rc=1. It also trips `dead_top_level_symbols`, because of my plant's module-level helper.

**Census arm** (`census_head.txt`, `census_uncapped.txt`, `selftest_head.txt`, `mutants_census.txt`):
- `--only census` prints `read=3 ... refused=0`: `dead_methods 0 -> 1`, `dead_top_level_symbols 1 -> 2` and `name_kept_members 38 -> 39`, each refused on its own row. It ends `FIELD COVERAGE ok`.
- With the row uncapped (9999), in a separate worktree: `BLIND ... name_kept_members: UNGATED, 38 -> 39 with one planted member and no FAIL on name_kept_members`, ending `FIELD COVERAGE REFUSED`, rc=1.
- `--self-test` prints `FIELD COVERAGE SELF-TEST ok`.
- Each new `censusRun` branch, removed alone, fails exactly its own self-test arm, `1 FAILED` each time: C1 UNGATED, C2 no-gate, C3 red-unplanted.

**Finder's harnesses** (step 6):
- D7 `namekept_receivers.py` reads `candidates_with_zero_typed_hits=6`.
- D14 `sweep-N-structure-blind/enumerate.py` reads `seams=10` and `instances=5` (`F4_*`, `F5_enumerate_head.txt`).
- Each of the five instances is either in the diff or dispositioned:
  - `max_class_loc`: #2340;
  - `name_kept`: this PR;
  - the card `.js`: the carry above;
  - `is_any` and `returned_keys`: #2293 and #2311.
- The other five rows are `guarded` or `not applicable`.

**Other checks:**
- `fold_ledger.py check` reports `0 violation(s)`.
- `score.py --diff origin/main` reads `Architecture score: dS +0.0000 NULL`.
- `tests/entities.py` prints `ALL 2349 ENTITY CHECKS PASSED`.
- `harness_headers.py` prints `ALL 109 HARNESS HEADER CHECKS PASSED`.
- `ci_predict.py --base origin/main` prints `no closures or fast red predicted`.

**Untouched (step 5).** `VERSION`, `manifest.json`, `RELEASE_NOTES.md`, both claim files and every file under `custom_components/` are unchanged in the three-dot diff (`untouched.txt`, 0 paths). No fixture can move, so `env_drift` has nothing to claim.

**Step 14.** The only metric movement is a new `MAX` key, recorded at the measured value. M2 shows it is earned: the row is live, and hard-coding it reads as a change. The INERT READS entry in `closures.json` registers the new harness.

**Body figures:**
- `fa16596c3..913ce1ff5` touches only `dev/programme/delivery/` (9 files).
- The diff has 0 `custom_components` paths.
- `DEFAULT_ROSTER_REF` has no reader.
- `git grep card_dead_definitions origin/main -- tools/policy dev/audit/config` prints nothing, while `tests/ci_budgets.json` on main does carry `archscore.card_dead_definitions: 0`.
- #2373 is empty: `merge-tree origin/main <#2373 head>` gives tree `a76f4c26d`, which is origin/main's own tree (`body_figures.txt`).

**`tests/stress.py` on Linux** (the body's local red):
- At this head: `ALL 110 STRESS CHECKS PASSED`, `ok shoulder: cheaper than holding the setpoint`, rc=0 (`stress_head.txt`).
- At main `abb397938` with `GOLDEN_REF=HEAD^1`: `ALL 110 STRESS CHECKS PASSED`, with the same `ok shoulder`, rc=0 (`stress_main_ref_parent.txt`).
- The body's `FAIL shoulder [4.67 vs 3.96]` does not reproduce on Linux at either end, which is consistent with its attribution to the seat's platform.
- My first main run, with the default reference, read 7 reds. Every one says `origin/main IS this commit` (a self-compare), not a real failure (`stress_main.txt`).

**Merge (step 13).** `git merge-tree --write-tree origin/main bd8011e9` exits 0, tree `0c8b19cf0`, with no conflict and no driver marker (`merge-tree.txt`).

**CI (step 11).** The check-runs API shows 48 runs at this head, all completed: 33 success, 15 skipped, none red (`check_runs.txt`). This includes `closures`, `fast (3.14)`, `mutation` and `pr-contract` (two runs, both success). No red check is owed an answer. The diff writes no production line, so `mutation` draws no mutant.

**Head (steps 7, 12).** The body names `bd8011e9` as merging code head `2a01f9ee2`, and the graph agrees. `refs/pull/2415/head` is still `bd8011e9` at verdict time.

## Noted, not blocking

- The body says `git diff --name-only 45ecca4f9 HEAD` names none of the authored files. It names `dev/audit/config/bugclasses.json`, but only through main's `1a4c7ef56` (R10-RCA-TRAIN-RAISE-HOLD) brought in by the merge. The PR's own `bugclasses.json` hunk is unchanged, so the figures the sentence protects hold.
- The barrier text and the carry both say "until #2373 merges". #2373 will never merge: it is empty against main, and #2401 landed `card_dead_definitions` without the census. The body flags this as the orchestrator's to re-point. The carry still binds R10-ARCHSCORE-COVERAGE, which is live, but its wording names a dead PR.
- `stress.py` at this head read `shoulder/tariff+pv+cycle` at 266.7x against a 268x budget, with three heavy jobs running in parallel on 4 cores. It passed, but with little margin.

## Not verified by me

- The RCA's historical figures (124 -> 152, fix spans, cost test). Round 1 re-derived them, and the RCA file is unchanged since.
- The local scoped-gate run the body quotes. CI's `closures` and `fast` are green at this head instead.

RESULT plant_refused_head=1 count
RESULT plant_refused_main=0 count
RESULT null_refused_both_ends=1 count
RESULT census_read=3 count
RESULT census_uncapped=UNGATED (FIELD COVERAGE REFUSED)
RESULT mutants_killed=6 of 6 (M1, M2, P1 plant, C1, C2, C3)
RESULT stress_linux_head=110/110 pass
RESULT stress_linux_main=110/110 pass
RESULT red_checks_at_head=0 of 48
RESULT merge_tree_rc=0
