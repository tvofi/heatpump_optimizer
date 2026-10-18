Fix review: merge 87c579404df187dc426960c2ac79f10a553be468

bus-nonce: 855ab27b434327d4a6e5952a9dc9b27d

PR #2415, R10-RCA-STRUCTURE-BLIND. **Review round 2.** Round 1 blocked `9951f224` with `carry-missing` (comment 6253266283). I reviewed from a detached worktree at head `87c579404df187dc426960c2ac79f10a553be468`, in a full clone. Its merge base with origin/main is `176851e95`, and origin/main was `106af95a3` when I read it. `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so my contract is current. All evidence is in `ev/`, and `ev/HEAD` names the head.

## What changed since round 1, and how it is judged

- **The head moved by an origin/main merge only.** `87c57940` merges `176851e95` into `9951f224`. I redid that merge myself with `git merge-tree --write-tree 9951f224 176851e95` and got tree `efc067565`. It differs from the head's tree in nothing (`ev/resolution_delta.txt` is empty). So the resolution delta is empty, and no authored file changed. Round 2 judges that delta and the round-1 blocker. I also re-took the cheap figures below at this head.
- **The carry (round 1's blocker) is resolved at its destination.** I judged it at the roster ref `handoff/audit-r10-roster` = `9a487b7320d72bbc16309121128c3c6bd3324e9e`, as the dispatch directs.
  - Commits `2e7aad8e3` (`append-carry`) and `9a487b732` (`edit-brief`) write it into R10-ARCHSCORE-COVERAGE's `carry` list and its `brief` (`ev/carry_roster.txt`).
  - It is stated as a precondition: "part 4 (#2373) is not done until …".
  - It carries the control: `--only census` must read `n -> n+1 … refused on <row>`, and with the row uncapped it must read `UNGATED` and end `FIELD COVERAGE REFUSED`. A census that cannot be read, or that moves with no refusal, "is not delivery".
  - It requires the card `.js` to be struck from the barrier's "Not reached" clause in the same PR, and tells the receiving seat to re-measure `n` at its own base.
  - `field_coverage` occurs 2 times in the roster at that ref and 0 times on origin/main.
  - With that roster file placed in an origin/main checkout, `node tools/policy/brief_lint.mjs` prints `TOTAL: 0 error(s) across 47 file(s)`, rc=0 (`ev/brief_lint_roster.txt`).
  - The carry reaches origin/main only when roster PR #2417 lands. That landing, and relaying the carry to #2373's live seat, are the orchestrator's, owed before this PR merges, as the body says.

## Re-taken at this head

- **Ratchet.** `ok 56 counting rules hold`, `ok name_kept_members 38 <= 38`, `RESULT name_kept_members=38 count`, `STRUCTURE RATCHET PASSED`, rc=0 (`ev/structure_head.txt`).
- **Plant arms, at both ends** (`ev/plant_head.txt`, `ev/plant_main.txt`).
  - At the head: `clean_refused=0`, `plant_refused=1 (name_kept_members)`, `null_refused=1 (dead_methods)`, `typed_refused=0`. name_kept reads 38, 39, 38, 38.
  - On origin/main's `structure.py` and budgets: `plant_refused=0` with `plant_name_kept=39`, `null_refused=1`, `row_in_budgets=False`. The defect reproduces on main, and the null control behaves the same at both ends.
- **Mutants**, each restored afterwards (`ev/mutant_M1.txt`, `ev/mutant_M2.txt`, `ev/census_uncapped.txt`):
  - M1, the row dropped from `measure()`: `FAIL name_kept_members: in the budget table but never measured -- re-record`, rc=1.
  - M2, the row hard-coded to 0: `1 STRUCTURE BUDGET(S) IMPROVED AND NOT YET RECORDED`, rc=2.
  - The census row uncapped (9999): `BLIND census structure.py name_kept_members: UNGATED, 38 -> 39 with one planted member and no FAIL on name_kept_members`, ending `FIELD COVERAGE REFUSED`, rc=1.
  - Round 1's M3 and the census-branch mutants were not re-run, because `structure.py` and `field_coverage.mjs` are byte-identical to round 1's head.
- **Census and self-test.** `--only census` prints `read=3 … blind=0 … refused=0`, with `name_kept_members: 38 -> 39 … refused on name_kept_members`, and ends `FIELD COVERAGE ok`. `--self-test` prints `FIELD COVERAGE SELF-TEST ok`.
- **Ledger.** `fold_ledger: 0 violation(s)`.
- **Earned (step 14).** The diff adds only `name_kept_members: 38` to `tests/structure_budgets.json`, and one INERT READS entry to `tests/closures.json` for the new harness. M1 shows the row exists only because of the mechanism. `recorded_at` is unchanged, and budget-raise-gate is green.
- **Untouched.** `VERSION`, the manifest, the `RELEASE_NOTES.md` heading and both claim files are unchanged against the merge base. No package file changes.
- **Merge.** `git merge-tree --write-tree origin/main 87c57940` exits 0. The `LEDGER-MERGE: resolved tests/closures.json` line is the ledger driver's set merge (`ev/merge-tree.txt`).
- **Head (step 7).** The body names `87c579404df1…` as the head, and its branch ref still points there when this verdict is written.
- **CI (step 11).** The commit's check-runs API lists 48 runs, all completed: 33 success and 15 skipped, none red (`ev/check_runs.txt`). There is no red check to answer. The two local reds the body names (`stress.py`, `harness_headers.py`) are answered with their detector reasoning.

## Not re-verified this round

- The RCA's historical figures (F1, F3–F5, F8, F9, and the cost-test arithmetic) and the class enumeration. Round 1 verified them at `9951f224`. No file they read changed, because the resolution delta is empty.
- `score.py --diff`: I cite CI's two green `arch-score` runs at this head.

RESULT resolution_delta_files=0 count
RESULT carry_at_destination=1 (brief + carry, roster 9a487b732)
RESULT brief_lint_errors=0 count
RESULT plant_refused_head=1 count
RESULT plant_refused_main=0 count
RESULT null_refused_both_ends=1 count
RESULT mutants_killed=3 of 3 (M1, M2, census uncapped)
RESULT red_checks_at_head=0 of 48
