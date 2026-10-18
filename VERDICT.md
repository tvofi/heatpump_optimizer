Fix review: blocked 28d6a60bb80a5c6bdb6c565e65e1b6b7fceab4f5 carry-missing: three planted games read IMPROVES on the new metrics (literal module alias, keyword respelling, card no-op split) and are carried nowhere; attempt 44 still respells card._IDENT
bus-nonce: 35c8c31b10248f1a52ac3b75a9bd395a

PR #2373, R10-ARCHSCORE-COVERAGE part 4. Round 1. Reviewed from detached worktrees: head `28d6a60bb80a5c6bdb6c565e65e1b6b7fceab4f5`, base at the merge base `52f698905868c9140ed213ea542c44053fca7096`. The role contract matched origin/main `9a1ce39c3` (the roles diff was empty). Before posting I re-read `refs/pull/2373/head`, and it was still `28d6a60bb80a5c6bdb6c565e65e1b6b7fceab4f5`.

## What holds (every figure re-derived by me)

- **Finder harness**: ARCH2-s5 `arch_delta.py` from `git archive 3930b421a`, sha1 `4fa94bb4…` as in the body, `--base 9061fbd3d`. The five patch sha1s match the body.
  - Base instrument: F1 `RESULT delta_S=+0.0000`. C1-C4 `RESULT delta_S=+0.0000`.
  - Head instrument: F1 `RESULT delta_S=+0.4761` with `literal_clone_copies=184->132`. C1-C4 `RESULT delta_S=+1.0958` with `card_dead_definitions=1->0` and `card_clone_copies=108->101`. All four runs are `admissible=1`.
  - Perturbation at both ends: `perturbed_delta_S=+0.0000` and `perturbed_vector_equals_baseline=1`.
  - Evidence: `finder_*_{base,head}.txt`.
- **Today's tree** (`measure_head_*.txt`): `card_dead_definitions=0`, `card_clone_copies=108`, `literal_clone_copies=184`. These equal the three new `ci_budgets.json` rows. origin/main has not touched `custom_components/` or `tools/audit/archscore/` since the merge base.
- **Mutation proof** (my own runner, `mutants.sh`; `calibrate.py --only` on the twelve cases):
  - M0: all twelve cases classify as recorded.
  - M1 (`dead_definitions` returns `[]`): `a3_card_dead_definitions_control` and `_fix` both move to NULL.
  - M4 (`is_spec` returns False): `a3_literal_clone_copies_fix` moves to NULL, and the control stays WORSENS through `dead_members` and `unread_private_globals`.
  - M3 (the union never joins): the attempt-44 locator refuses (CalledProcessError).
  - M7 (`doc_claims._tokens` returns an empty set): `1 of 169 checks FAILED`. Unmutated: `ALL 169 checks PASSED`.
  - All of these match the body. I did not re-run M5, M6 or the ablations.
- **Calibration rows**: `expected.json` has 0 deleted lines and gains exactly the twelve cases. In `corpus_vectors.json`, the same 87 trees gain only the three new keys, and no existing value changed (I checked this with my own script).
- **Agreement**: `tools/policy/agreement.mjs` is byte-identical to origin/main, and the agreement run printed `unregistered=0`, `AGREEMENT ok`. The single-owner import route is accepted, as the brief directed.
- **Other cheap checks**:
  - `score.py --diff`: `dS +0.0000 NULL`.
  - `closure.py select`: `MODE: SCOPED -- 4 script(s) run, 29 scoped out`.
  - `merge-tree` against origin/main exits 0.
  - `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched.
  - `HA_CONVENTION_METHODS`/`is_ha_method` (the deleted names) have no reader left. The round harnesses read `tests/structure.py`'s copy.
- **Closing keywords**: the body says only "Part of #2259" and "Part of #2235". `closingIssuesReferences` is `[]`, and no commit message in the range has a closing keyword. #2259 stays open, as the brief requires.
- **Checks**: all 45 check-runs at the head concluded success, skipped or neutral. `ci-ratchet` is skipped because it runs on pushes to main only. The non-green runs at `c12f2f524` were all `cancelled` (superseded), so no red check is owed an answer.

## Why blocked

1. **The new counters can be gamed, and nothing carries it** (step 14, step 10). On the head tree I planted the diff's own kind of move with nothing improved, then scored it with the full vector (`plants.py`, `plants_ds.py`, `plants_*.txt`):
   - **P1, module alias.** Three copies of `_number(1, 24, 1, slider=True)` in `config_flow.py` read `_LAST_HOUR_<i>` instead, each a module-level `= 24`. C21 inlines locals only. Result: `literal_clone_copies 184->180`, `delta_S=+0.0315 IMPROVES`.
   - **P2, keyword respelling.** The same three copies pass `step=` / `maximum=` / `minimum=` by keyword. C20 sorts keywords but never binds positionals. Result: `184->180`, `delta_S=+0.0315 IMPROVES`.
   - **P3, card no-op split.** A distinct `void <n>;` follows every second card `const`/`let` line (685 statements; `node --check` passes). Result: `card_clone_copies 108->98`, `delta_S=+0.1388 IMPROVES`.

   The credited moves themselves (F1, C1-C4) are real deduplications, so this is an instrument finding, not `metric-gamed`. But the body's `RED TEAM ... IMPROVES: none` holds only for the attempts that were written. Part 3's equivalent limits went into R10-BRIEFS-FOLD's carry ("must state what the layering counters do not see"). Part 4 has no carry there: the main roster's BRIEFS-FOLD carries name none of the three new metrics. The body leaves the roster carry to the orchestrator, but the destination does not hold it yet. Remedy, in either order:
   - close the gaps (fold single-bound module constants like C21; bind positionals to the callee's signature where it resolves in-package; drop no-op statements before windowing);
   - or record P1-P3 as KNOWN-OPEN red-team attempts;
   - then carry the residual limits to R10-BRIEFS-FOLD (`dev/governance/dimensions/D7.md`).
2. **The body claims more than the tree shows.** "Attempt 44 and `tests/doc_claims.py`'s card-token reader both import it, so no second spelling exists" is false. `planted/redteam/44_card_rename_locals.py:25` still spells the grammar inside `r"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)"` (`git grep -nF '[A-Za-z_$][\w$]*'`). The agreement lane matches only standalone spellings, so it passes. The fix is a few lines: build the pattern from `K._IDENT.pattern`, or reword the claim to what the lane checks.
3. **Minor, not blocking**: `tests/doc_claims.py`'s `_tokens` runs `sys.path.insert` on every call (once per package file). The file's module-level path setup at line 62 is where that insert belongs.

## Owed to tvofi (noted, not blocking)

- `tests/ci_budgets.json` gains three new rows: `archscore.literal_clone_copies` 184, `archscore.card_dead_definitions` 0 and `archscore.card_clone_copies` 108. It also changes `reason` and sets `recorded_at` to `4b17a5419`. No existing row moves. These are budget rows (0013), so tvofi approves them, or the orchestrator does under mandate 6175172275 as the body states.
- `tools/audit/archscore/calibration/expected.json` gains 12 cases (72 insertions, 0 deletions).

## Not verified by me

- The full `calibrate.py --record`, `--measure-corpus` and the heavy gate scripts. These are CI's to run (heavy-script rule). CI's `arch-score`, `closures` and `fast` runs at this head are green.
- M5, M6 and the C20/C21/C22 ablation figures.

Evidence: /Users/timmalmstrom/hpo-seats/r10s3/review-2373/evidence
