Fix review: merge e14a378c12e5d292c1f564bc9100ecb0de39bd76 [carry: the round-3 carry-missing block is discharged by roster R10-BRIEFS-FOLD carry "From #2373 review r3" at main eae8c4ca4; head unmoved, CI 45/45 concluded none red, merges clean with origin/main c8cc75ea9]

bus-nonce: 4b065d9eea004cce6a617a3a50583568

PR #2373, R10-ARCHSCORE-COVERAGE part 4. **Review round 4.** Earlier rounds:
- round 1 (`a19384631`) blocked at `28d6a60bb`;
- round 2 (`d21d3b132`) blocked at `c06c9e84b`;
- round 3 blocked at this same head with `carry-missing`, and said a roster carry alone would unblock it, with no head move.

The head has not moved since round 3, so the fixer made no repair this round. `fixer.md`'s rule that a re-cut is owed from the fourth round is therefore not triggered.

This is a cloud reviewer seat. I measured from detached worktrees in `/tmp/seat/rev2373/{head,base,merged}`:
- head: `e14a378c1`;
- base: the merge base `42e6dedb2`;
- merged: a probe commit of `git merge-tree` against origin/main `c8cc75ea9`.

`git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so the contract is current. Before writing this verdict I re-read `refs/pull/2373/head`, and it is still `e14a378c12e5d292c1f564bc9100ecb0de39bd76`.

## The round-3 block: discharged (step 10)

Round 3 asked for one thing: amend the R10-BRIEFS-FOLD carry to state the general limit, namely that a drop is credited only when the copies are actually gone from the source. That carry is now on origin/main.

- **Where it is:** `dev/programme/rosters/wave-r10-groups.json`, group `R10-BRIEFS-FOLD`, `carry[8]`. It was added by `eae8c4ca4` (`roster_edit append-carry R10-BRIEFS-FOLD`), and `ev/roster_carry_r3.txt` holds the text.
- **It supersedes the stale clause.** It names `carry[6]`'s "Unless #2373 closes them" clause and replaces it.
- **It states the general limit.** Both censuses normalise a finite list of spellings, and any other indirection of the same value reads as a removed copy. It gives both of round 3's figures.
- **It is a precondition.** A drop is "credited only when the copies are actually gone from the source, never on the metric alone".
- **It carries a control:** "re-plant both spellings at your merge base with tools/audit/archscore/score.py and confirm the drop is not credited".
- **It reaches its stage in time.** The destination group is `resume.stage: not-started`, with `after: [R10-ARCHSCORE-COVERAGE, R10-D15-GRADER]`. The carry therefore lands before that stage's fixer is dispatched.
- **Its figures are mine too.** My own plant script (`ev/plants_r4.py`, written by me and disclosed as mine; it is not the finder's) prints these at this head:
  - `P6_class_attr literal_clone_copies=186->182`
  - `P7_const_expr literal_clone_copies=186->182`
  - `NULL_unchanged 186->186`

  Evidence: `ev/plants_r4_head.txt`. The carry quotes both figures, so they are verified.
- **ABOUT.md gap.** ABOUT.md's not-seen list (lines 259-265) still does not name the class attribute or the constant expression. Round 3 called that addition optional, so it does not block. The carry's "a spelling not listed there" covers it.

## Re-derived at this head (RESULT lines)

**Finder harness**, ARCH2-s5 `arch_delta.py` at `3930b421a`:
- The harness sha1 is `4fa94bb4…`. All five patch sha1s equal the body's.
- Run as `--base 9061fbd3d`, `PYTHONPATH=tests/hastub`, at both ends (`ev/finder_*_{base,head}.txt`).
- Base:
  - `F1 RESULT delta_S=+0.0000`, `admissible=1`.
  - `C1-C4 RESULT delta_S=+0.0000`.
- Head:
  - `F1 RESULT delta_S=+0.4701`, `literal_clone_copies=186->134`.
  - `C1-C4 RESULT delta_S=+1.0958`, `card_dead_definitions=1->0`, `card_clone_copies=108->101`.
- Perturbation, all four runs: `perturbed_delta_S=+0.0000` and `perturbed_vector_equals_baseline=1`.
- All of these equal the body's figures.

**Today's tree** (`ev/measure3.py`):
- At the head: `RESULT tree=head literal_clone_copies=186 card_dead_definitions=0 card_clone_copies=108`.
- **On the merge with current origin/main `c8cc75ea9`**: `RESULT tree=merged ... 186 / 0 / 108`.
  - Since the merge base, main has touched `coordinator.py`, `store.py`, `price_model.py` and six other package files.
  - The merged tree still reads exactly the three new `tests/ci_budgets.json` rows, so main's forced-full `ci-ratchet` will not go red on merge.

**Mutation proof**, my own runner (`ev/mutate_r4.sh`):
- It runs `calibrate.py --only` over the 17 part-4 cases (`ev/part4_ids.txt`).
- **M0:** `RED TEAM 8/8 attempts read NULL or inadmissible; IMPROVES: none`, and no part-4 case MOVED.
- **M10** (`drop_noops` not called):
  - `rt_44b_card_noop_split` NULL -> IMPROVES (0.1557, equal to the body);
  - `rt_44c_card_empty_statement` NULL -> IMPROVES (0.0844). This is expected: 44c's statement is also dropped by `drop_noops`.
  - No other case moves.
- Restored with `git checkout`, and the tree is clean.
- The `MOVED ... now None` lines in both logs are the cases outside `--only`.

**Cheap checks at the head** (`ev/cheap_checks_head.txt`, `ev/entities_head.txt`, `ev/arch_score_head.txt`):
- `closure.py select --diff 42e6dedb2`: `MODE: SCOPED -- 4 script(s) run, 29 scoped out`.
- `brief_lint.mjs`: `TOTAL: 0 error(s) across 47 file(s)`.
- `tests/doc_claims.py`: `ALL 169 checks PASSED`.
- `env -u BASH_ENV tests/entities.py`: `ALL 2346 ENTITY CHECKS PASSED`.
- `tests/arch_score_head.py`: `ALL 16 ARCHITECTURE SCORE HEAD CHECKS PASSED`.
- `env_drift.py --claims-only 42e6dedb2`: `claims hygiene ... ok`.
- `score.py --diff`: `Architecture score: dS +0.0000 NULL`.
- Agreement:
  - `agreement.mjs` is byte-identical to main;
  - the run prints `RESULT divergent=0 unregistered=0 dead=0 refused=0` and `AGREEMENT ok`;
  - the `_IDENT` grep finds `metrics/card.py:53` plus the other group's `r10_deeplink_mutants.py:217`, exactly as the body says.

**Step 5:** `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched (`git diff --quiet` rc 0).

## Merge (step 13)

`git merge-tree --write-tree origin/main e14a378c1` exits 0 with tree `3299efe96` (`ev/merge_tree.txt`). Its stderr carries `LEDGER-MERGE: resolved tests/closures.json`, merged as sets for three closures. It has no `MERGE-CLAIM` line, and the claim files are not in the diff.

## CI (step 11)

I read the head's own check-runs API (`ev/check_runs_head.tsv`):
- 45 runs, all `completed`: 30 success and 15 skipped;
- 0 non-success and non-skipped;
- `pr-contract`, `briefs`, `arch-score`, `closures` and `budget-raise-gate` are among them.

No red check is owed an answer at this head. The earlier red at `2183ab58f` (`briefs`, `pr-contract`) is answered in the body's `## Red checks`, as round 2 confirmed.

## Owed to tvofi at merge (mandate 6175172275), not blocking

- **`tests/ci_budgets.json`** gains three new rows against the merge base `42e6dedb2`:
  - `archscore.literal_clone_copies` 186;
  - `archscore.card_dead_definitions` 0;
  - `archscore.card_clone_copies` 108.

  No existing row moves.
- **`calibration/expected.json`** gains 17 cases and deletes none.

## Not verified by me

- The full `calibrate.py --record` and the full corpus re-measure, which are heavy and CI's to run. CI's `arch-score` is green at this head.
- Mutants M1-M9 and M11-M16, and the ablations. I re-ran only M0 and M10 this round; rounds 1-3 re-ran M1, M3, M4, M7, M13 and M15.
- The body's own figures taken at earlier SHAs (`45da9204f`, `033998cb5`, `21dd4a3e5`), beyond the ones re-derived above.

## Friction

My first wait loop used `pgrep -f "<script>"`. It matched its own command line, so it never exited, and the mutant run started about 25 minutes late. A wait loop should key on a sentinel file, not on `pgrep -f` of a pattern it carries itself.
