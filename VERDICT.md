Fix review: merge 82e14f6d8fb87fc65dd993d1cadbd35883090f07

bus-nonce: c031750fec06e0044b9779cb6716b333

Round: third review (repair round 2), delta scope over the blocked head bbad7959ae2bacf68d01f190f28e87f849932179. Measured head: 82e14f6d8fb87fc65dd993d1cadbd35883090f07, still the tip of handoff/r10-card-collapse at return time (`ev/ls_remote_final.txt`). Reviewed from a detached worktree at that head.

## Findings

none

## Evidence

- Previous block (probe/rev-3441-69316311, `root-cause-unanswered` at bbad7959), item by item:
  - **Stale base / env_drift refusal: cured.** The delta is a single merge of origin/main ceb3070ccb49fe6dfc9d403458e8a3cc03c5595e into bbad7959. `git show --remerge-diff` of the merge is empty (`ev/remerge_diff.txt`), so no line was hand-resolved. `CLAIM_HEAD=82e14f6… PYTHONPATH=tests/hastub python3 tests/env_drift.py --all origin/main` at the head: `NO UNCLAIMED DRIFT: 56 scenario(s) checked against origin/main`, `NO STALE FIXTURE: 56 committed fixture(s)…`, rc=0 (`ev/env_drift_all.txt`; origin/main was 50e4b1aa at the run).
  - **`## Red checks` read none: cured.** The body now names `tests / fast (3.14)` and answers the trigger: the failing check is `tests/features.py`'s `combi_type_branch census`, main's own red, so no cheaper detector exists for this branch; its cause is owned by #3466. Reviewer's control: `PYTHONPATH=tests/hastub GOLDEN_MODE=drift python3 tests/features.py` prints the same `FAIL combi_type_branch census` line and `1 of 5237 FEATURE CHECKS FAILED`, rc=1, both at the head (`ev/features_head_fail.txt`, `ev/features_head.tail.txt`) and at the merge base ceb3070 (`ev/summary_rest.txt`, `ev/features_base.tail.txt`). This matches the dispatch's statement that main is red on the combi census, fixed by #3466. I checked that the trigger is answered, not the answer itself (fix-review step 11).
  - **pr-contract refusal for the same omission.** It cannot be re-read here: see CI below. The body text the refusal objected to is replaced.
- CI: there is no PR head at 82e14f6 yet. The commit's check-runs API returns `total_count` 0 (`ev/check_runs.tsv`, empty). So there is no review packet and no CI to wait on before the PR head moves to this tip. Every check, `pr-contract` included, runs then; the train re-proves it. `merge_train.py owed-reds` (`ev/owed_reds.txt`) is the set those runs are judged against.
- Merge with main: `git merge-tree --write-tree origin/main 82e14f6…` against 50e4b1aa exits 0 and prints `MERGE-CLAIM: resolved tests/golden/card_claimed_drift.txt` (`ev/merge_tree.txt`). There is no conflict and the claim driver resolved the claim file.
- Delta scope, not widened: `git diff bbad7959..82e14f6` adds only main's content. In the card file that is the setup diagram's combi caption strings (en/sv/de) and the combi buffer-to-DHW pipe in `setupSvgHtml` (`ev/delta_card_js.diff`). Both are disjoint from the fold code (`_folds`, `headlineHtml`, the fold click handler), so reviewed functionality is not at non-obvious risk.
- Mutation proof, re-run at the head by the reviewer's own driver (`ev/mut_driver.sh`, `ev/mut_go.sh`). It uses sed edits on the card file at the anchors recorded in `ev/folds_lines.txt`, runs `PYTHONPATH=tests/hastub node tests/card.mjs` after `tests/plan_view.py`, and runs `git checkout` after each edit. The worktree was clean afterwards (`status-after: 0 dirty`, `ev/mutants.txt`; failing names in `ev/mutant_fails.txt`):
  - NULL (` // null` on the fold handler's focus line): SURVIVED, rc 0, 0 FAIL.
  - R1 (`_folds` reset added to the card's `set hass`): KILLED, 1 FAIL, `collapse: a hass refresh rebuilds the card and keeps each fold as it was`.
  - M4 (fold handler's `again.focus()` line deleted): KILLED, 2 FAIL, `collapse: focus returns to the rebuilt header` and `collapse: focus returns to the dialog's copy of the pressed header`.
  - M2 (the `this._folds = {...}` toggle line deleted): KILLED, 21 FAIL, the first being `headline shows every narrative line`.
  - All four match the body's round-2 figures. The other mutants (M1, M3, M5-M12, R2-R10) were settled at bbad7959 by the previous review. The merge changes no fold line, so they were not re-run.
- Body `## Figures` re-derived at the head:
  - `node tests/card.mjs`: `ALL CARD CHECKS PASSED`, rc 0 (`ev/card_head.txt`).
  - `tests/closure.py select --diff ceb3070…`: `MODE: SCOPED -- 12 script(s) run, 21 scoped out.` (`ev/closure_select.txt`).
  - `tests/structure.py`: `STRUCTURE RATCHET PASSED` (`ev/structure.txt`).
  - `archscore/score.py --diff ceb3070…`: `Architecture score: dS +0.0000 NULL` (`ev/archscore.txt`).
  - VERSION, RELEASE_NOTES.md and manifest untouched in the three-dot diff (`ev/version_untouched.txt`).
  - `card_drift.mjs`: `card_drift: 44 state(s) moved and claimed, 1 identical`, rc 0 (`ev/card_drift.tail.txt`). Every moved card state is claimed.
- Not re-derived by me: the body's `tests/card_browser.mjs` / `docs/img/card` figures, measured at d7c39135. The fold code is unchanged since then, and CI's `tests / browser` runs that lane on the PR. The body's `closure.py selftest` and `env_drift --claims-only` lines were also not re-run.
- Body `## Head` names 82e14f6d8fb87fc65dd993d1cadbd35883090f07, the handoff tip I measured.
- Role contracts unchanged between the head's merge base and origin/main (`git diff …...origin/main -- dev/governance/roles/` empty).
