Fix review: merge 2d010b0913cabbbfc72ace3fc8d203bfb65744f7

bus-nonce: 22f38dfbae6110059a91a1cf89f2d120

## Round

Second fix-review round of PR 3297 (the first blocked 9cf0b6108 mutation-vacuous). I reviewed the whole fix again plus the repair delta (9cf0b6108..385073c4f, `tests/features.py` only, +46/-2), from a detached worktree at 2d010b0913cabbbfc72ace3fc8d203bfb65744f7. The roster has no committed harness for this hotfix, so the finder's harness is the brief's null control plus the R10-HOTFIX-COP-UNMEASURED section of `tests/features.py`. I built the section-block driver (`ev/mkprelude.py`, `ev/mutants.py`, `ev/whole.py`) myself; it is mine, not the finder's.

## Evidence

- RESULT head=2d010b0913cabbbfc72ace3fc8d203bfb65744f7 merge-base=aaaec2128e5d2efc2e0ad8ffe4918eec6cbb7f98. `## Head` in the body names this head, a merge of the code head 385073c4f, so it is current.
- RESULT merge-tree: `git merge-tree --write-tree origin/main 2d010b09` rc=0, no conflict (`ev/merge_tree.txt`).
- RESULT roles: `git diff $(merge-base)...origin/main -- dev/governance/roles/` shows one line changed in fix-review.md ("Evidence names differ beyond case"). I followed the main copy.
- RESULT CI: `merge_train.py classify 2d010b09 --pr 3297` returned `GREEN ... pending: none red: none`, rc=0 (`ev/classify.txt`). All 56 check runs at this head are listed in `ev/check_runs_head.txt`. The one concluded red is the edit-run `gate` (job 128631241009, 04:57Z), and it failed on one line only: "FAIL run(s) [42447989984] at this head are still being judged; their gate decides". That is a GATE DEFERRAL. The code-run gates 128642035569 and 128642815635 are both success (05:43Z and 05:45Z). `pr-contract / pr-contract` (128641734924, 05:39Z–05:40Z) started after that last red concluded and is success, so the body check stands. Under the brief's deferral rule this red needs no body answer. `tests / mutation` is success and prints `MUTATION TABLE PASSED`, with every diff site killed (`ev/ci_mutation_summary.txt`).
- RESULT features at head: `PYTHONPATH=tests/hastub python3 tests/features.py` gives `ALL 4915 FEATURE CHECKS PASSED`, rc=0 (`ev/features_head_summary.txt`). This matches the body.
- RESULT section block (158 checks, as the body states): unmutated it gives `ALL 158 FEATURES BLOCK PASSED`, rc=0. This is the null control for every mutant below.
- RESULT mutants on the repair delta, each against the section block (`ev/mutants_block.txt`):
  - G, the measured_cop provenance gate removed: rc=1. It fails "a last COP stored before measured provenance does not load as measured; one stored since round-trips".
  - The CUSUM load replaced by `pass`: rc=1. It fails "a COP health CUSUM stored since measured provenance loads with its state".
  - DOMAINS `cop_health_cusum_measured/stat` floor 0.0→1.0: rc=1. It fails the store-domains check.
  - DOMAINS `cop_baseline_measured/*/1` floor 1→2: rc=1. It fails the store-domains check.
  - All three of the body's repair claims reproduce.
- RESULT mutants on the first-round production lines, re-run at this head:
  - Killed by the section block: M1, M3, M4, M5, M7. My added mutant M5b (the loader also reading the old `cop_health_cusum`) is killed too.
  - Also killed by the section block, each from my own list:
    - power side only / heat side only in `cop_measured`
    - `_estimated` without its estimate arm / without its meter arm
    - the heat counter no longer outranking an estimated thermal power
    - `heat_sees_dhw` forced off
    - `cop_observability`'s `estimated` forced False
    - `cop_observability`'s no-heat guard deleted
    - the `COP_REFUSED_NO_HEAT` refusal removed
  - Survive the block but are killed by the whole `tests/features.py`, 1 of 4915 each (`ev/whole_*.txt`):
    - M6, `machine_score`'s `if not measurable` deleted: killed by "a fresh install grades nothing ... with no heat reading the heat pump is never graded".
    - `machine_score(..., cop_measured(False))` → `True`: killed by the same check.
    - `_FACTORY_VOID` reverted to the old keys: killed by "a learners reset drops every learned key ...", which names `cop_baseline_measured`.
  - One survivor, `cop_measured` without `and self.cop_electric()`, is under `## Findings`.
- RESULT null control (the brief's): the section's no-heat check shows the inference equal to `compute_cop_dhw(8.0, 48.0)` with nothing recorded and `_cop_samples == 1`. The Tuya check shows heat over power observing the fitted COP on every interval with nothing recorded, and the same install set to `meter` records. M1 turns both red, so the control moves under its own perturbation. I did not re-transplant the section onto the base. The base reading is the first round's (the body says "the review reproduced this at the merge base aaaec2128"), and production code is unchanged since then (`git diff --stat 9cf0b6108 385073c4f` lists `tests/features.py` alone).
- RESULT drift: `python3 tests/env_drift.py --all aaaec2128` gives `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE`, rc=0 (`ev/env_drift.txt`). The claim lines are the five coord_* reason-string edits plus config_flow, and `card_claimed_drift.txt` claims score_open. I did not re-run `card_drift.mjs`; I cite CI's green `tests / browser`.
- RESULT ratchet: `python3 tests/structure.py` gives `STRUCTURE RATCHET PASSED`, rc=0 (`ev/structure.txt`). The three-dot diff touches no `*_budgets.json`, `VERSION` (7.1.5), `manifest.json` or `RELEASE_NOTES.md`.
- RESULT bookkeeping: the delivery row `dev/programme/delivery/3297.md` is in the diff. The only new tracked files are that row and nine `tests/mutation_ledger/killed_by/*.json` pins, and `governance`/`tests / closure-scope` are green on them.
- RESULT archscore: `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD) HEAD` gives `Architecture score: dS -0.0023 WORSENS (inadmissible: coord_footprint 2491->2495)`, rc=0 (`ev/archscore_diff.txt`). This is the body's figure, re-derived.
- Judgement on the +4: `metrics/footprint.py` charges logic statements in the coordinator class and in every function handed the coordinator. So the module function `machine_score`, which takes only `baseline`, and its new guard are not charged. The charge falls inside `_fold_cop_evidence`:
  - the `cop_sample(...) is None` refusal and its return
  - the `if measured:` that now guards the already-counted `record` and `_observe_cop_health` calls
  - the score-path argument
  The decision itself already lives off-coordinator, in `InstallCapability.cop_measured` and `cop_sample`, so the move the coordinator suggested is made. I looked for a payment the fixer missed:
  - Pushing the guard into `MeasuredCop.record` leaves `_observe_cop_health` as a coordinator method, so it is still charged.
  - Encoding the refusal as a return value of `cop_sample` keeps one branch per outcome.
  - Moving the `machine_score`/`_watched_cop_buckets` block out of `coordinator.py` would change nothing, because the metric does not charge it.
  None of these is a sounder in-seam payment. The +4 is justified, and no budget is raised.
- RESULT class rule: `git grep -n -e "_measured_cop.record(" -e "_observe_cop_health(" -- custom_components` returns only the two calls inside `if measured:`. The loader grep returns the three keys, each with a pre-fix arm and a since-fix arm, killed above. I also checked for leftover uses of the old keys: `git grep '"cop_baseline"' '"cop_health_cusum"' -- custom_components tools` returns only the comment at coordinator.py:385.
- RESULT store: `store.off_domain` is diagnostic only (`_log_off_domain`), so a pre-fix payload's undeclared `cop_baseline` key does not quarantine the store. It drops on the next save, because `_save_thermal_learning` rebuilds the dict.
- RESULT entities: I did not re-run `tests/entities.py` at the head. I cite CI's `tests / fast`, `tests / coverage` and `gate` green. Under the R-electric mutant it gives `3 of 2645 ENTITY CHECKS FAILED`: the coverage-job reuse, release-ZIP and Pages-workflow checks, the same three environment failures the body names (`ev/entities_R-electric_tail.txt`).
- Forward-carry: the body says `none`, and I found no stage-changing finding beyond the one below.

## Findings

- Follow-up: `custom_components/heatpump_optimizer/thermal_model.py` `InstallCapability.cop_measured`, the conjunct `and self.cop_electric()`, is unpinned. Deleting it passes the whole `tests/features.py` (ALL 4915) and leaves `tests/entities.py` at its three environment failures (`ev/whole_R-electric.txt`, `ev/whole_R-electric_entities.txt`). On the sample paths it is equivalent: a heat-counter span with no electric delta refuses `unaligned_meters` in `heat_energy.close_span`, and a thermal power with no power entity refuses `no_power` first. It is reachable at one point, the score call `machine_score(..., cop_measured(False))`. On an install with a heat counter and no electric counter (the config flow allows that), the mutant would publish `cop_watch_learning` ("not enough data yet") forever instead of `cop_unmeasurable`, which is the user-visible symptom this hotfix removes. The grade is None either way, and the production line is correct, so this does not block a hotfix. What is owed: one fresh-install check that a heat counter with no electric counter grades `cop_unmeasurable`. Carry: R10-HOTFIX-COP-UNMEASURED

## Friction

- The brief asks for handoff-wip pushes at milestones, but the dispatch prompt says to push nothing but the probe ref. I followed the dispatch prompt and pushed no handoff-wip. Carry: dismissed: dispatch instruction conflict, resolved by the outer prompt
- `tools/audit/seat/features_block.py` needs a hand-built `--prelude` for this section (32 statements). The body states the count but not the statements. I derived them with my own AST script (`ev/mkprelude.py`). Carry: dismissed: seat convenience, no defect in this PR
