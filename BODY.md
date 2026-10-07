Closes #1939

Leaves #201 open.

Successor of `705c3be37fe94feb37be1600b57403e129c382f8`. That commit merged the pin `19391406563cf785e723be51ceb7b9b34a850511` with `origin/main` `6001b09a557259f37319b400d219cf83e02c563f`. This commit points the env-matrix at `tools/policy/policy_lint.mjs`.

Merge `origin/main` `1b1bbaad57bc4bb5fa710efe2c510b0b4bc64872` into `058a5f8018e87cb7861477c8e7382ba9c7daada8`. `f07cd253c52f1012427d9869a808f1df39dafb93` is an ancestor of that tip; the commits above it add `docs/delivery/2000.md` only.

The mermaid and the D6 census keep both additions. Main adds the Model Restart Advisor (60 sensors). This branch adds the finalize button (5 buttons). The platforms construct 77 entities. The claim list kept is `config_flow`. `coord_all_features`, `coord_dhw`, `coord_grid_fee`, `coord_minimal` and `coord_two_zone` are origin/main's list; those fixture files match origin/main, and a `coord_minimal` capture differs from that file only in value leaves. `tests/structure.py` measures `max_class_loc` at the ledger sum, so the cap is not raised.

_Requested by **tvofi**_.

## Head

`a8d2e78ec189a5a8bb547df8ab7c23a426ec55ff`

## Mutation proof

`configured_specs` in `quiet_windows.py` ends with `return out`. Replacing that line with `pass` and running `PYTHONPATH=tests/hastub python3 tests/manual_plan.py` printed `FAIL configured_specs returns the stored rows and the not-enforced marker  [got None]` and `1 of 129 manual plan checks FAILED`. The line was restored before the commit.

`python3 tests/mutation_table.py --pin-killed --base origin/main --jobs 1 --scripts tests/manual_plan.py` pinned `custom_components/heatpump_optimizer/quiet_windows.py:370 RETURN_DEL`, killed by `tests/manual_plan.py`. The row is `tests/mutation_ledger/killed_by/quiet_windows.py/configured_specs.RETURN_DEL.a8227ccf.json`. Its reason text says `failed=2`. On this tree, replacing `return out` with `pass` and running `PYTHONPATH=tests/hastub python3 tests/manual_plan.py` printed `1 of 129 manual plan checks FAILED`. The line was restored. The script's summary is 1.

`tests/features.py` also calls `configured_quiet_windows`, which calls `configured_specs`. `--pin-killed --scripts tests/features.py` was inconclusive: baseline `rc=1 failed=2`, the named check `R9-F2.1 P3: the shipped storage plan is no worse on its own objective than the half-price floor's plan refined under it`. No pin was written from that run.

`debugger.py`, `button.py` and `tests/debug_collect.py` are unchanged from the pin commit `6d5d796e955275cb76226bbae4d2cbc8150cabd0`. The pins recorded there still name those lines. `store.py` gains `evidence_since` on the accuracy domain from origin/main; that domain is not the debug store.

Replacing `60 sensors` with `59 sensors` in the mermaid and running `PYTHONPATH=tests/hastub python3 tools/audit/round4/D6/claims.py` prints `FALSE C5`. Restoring the line prints `claims_false=0`.

The earlier drive, `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --pin-killed --base origin/main --jobs 3 --scripts tests/debug_collect.py` on `6d5d796e955275cb76226bbae4d2cbc8150cabd0`, pinned 51 sites. `_repair`'s `if stamp is None` guard is `survivor_triage`, verdict equivalent: applying GUARD_OFF left `tests/debug_collect.py` at rc=0.

## Null control

Restoring `return out` and running `PYTHONPATH=tests/hastub python3 tests/manual_plan.py` printed `ALL 129 manual plan checks PASSED`.

The pin drive's comment-only edit, `quiet_windows.py:389 NULL_COMMENT`, survived `tests/manual_plan.py`. Baseline of that drive: `rc=0 failed=0`.

The same C5 run: the documented tuple is `(77, 59, 6, 5, 4, 1, 1)` and the measured tuple stays `(77, 60, 6, 5, 4, 1, 1)`.

`config_flow`'s capture matches the committed fixture (0 leaf diffs) and differs from origin/main's fixture by `_seed.debug_collect_enabled`, `_seeded.learning.debug_collect_enabled` and `learning.debug_collect_enabled`.

The earlier pin drive's null control, on `6d5d796e955275cb76226bbae4d2cbc8150cabd0`: `null control custom_components/heatpump_optimizer/store.py:73 NULL_COMMENT survived tests/debug_collect.py`.

## Figures

Taken at `b5cbc740e59ea0d16f4088399d6ba5e82cbbfb4a`, 2026-10-06T22:49:49Z, ratchet base `6001b09a557259f37319b400d219cf83e02c563f`.

- `python3 tests/structure.py` — `STRUCTURE RATCHET PASSED`. `RESULT max_class_loc=9048 count`. `RESULT seam_cut_total=766 count`.
- `python3 tests/mutation_table.py --pin-killed --base origin/main --jobs 1 --scripts tests/manual_plan.py` — `pinned custom_components/heatpump_optimizer/quiet_windows.py:370 RETURN_DEL -- killed by tests/manual_plan.py`. `PIN KILLED: 1 pinned, 0 left unpinned`. Exit 0.
- `PYTHONPATH=tests/hastub python3 tests/manual_plan.py` — `ALL 129 manual plan checks PASSED`.
- `/usr/bin/time -p python3 tests/mutation_table.py --scope changed --base origin/main` at `cf9de4e2a50332c608d854de900108afe890039a`, before this pin — exit 1, `real 4.52`. The refusal names one added site, `quiet_windows.py:370 RETURN_DEL`.
- `tests/mutation_table.py` `ratchet_base("changed", "origin/main")`, `unpinned_sites`, `added_unpinned` at this head: base `6001b09a557259f37319b400d219cf83e02c563f`, 4695 unpinned against 4695 there, 0 added.
- `node tools/policy/policy_lint_envmatrix.mjs` with this checkout, a fresh work directory, and `HEAD` — `16 declared outcome(s) held, 0 did not, across 6 environment shape(s)`. Exit 0.

Taken at `205943f950645b72866385d8c852e61a70cd3413`, 2026-10-06T20:20:03Z, origin/main `00da22db537a688efe6a7a9518a9fc91767c3a5a`. `PYTHONPATH=tests/hastub python3 tools/audit/round4/D6/claims.py` was run at that head. `git merge-tree --write-tree origin/main HEAD` at this head exits 0.

Merge of `00da22db` (`#1960`). The eight content conflicts are resolved. The claim table is the regenerated one, not a union of the two texts. Quiet-window composition lives in `quiet_windows.py`.

- `./tests/derive_closures.sh --single tests/debug_collect.py` — exit 0. `git diff` on `tests/closures.json` changes only the recorded `seconds` for that script.
- `PYTHONPATH=tests/hastub python3 tools/audit/round4/D6/claims.py` — `RESULT claims_true=123 claims`. `RESULT claims_false=0 claims`.
- `PYTHONPATH=tests/hastub python3 tests/debug_collect.py` — `ALL 30 DEBUG COLLECT CHECKS PASSED`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` — `MODE: FULL -- every test script runs, nothing is scoped out.` Reason: `tests/run.sh` changes the gate itself. `tests/run.sh` was not run unscoped.
- `git merge-tree --write-tree origin/main HEAD` — exit 0.
- `CLAIM_HEAD=$(git rev-parse HEAD) PYTHONPATH=tests/hastub python3 tests/env_drift.py --claims-only $(git merge-base origin/main HEAD)` — `claims hygiene: 1b1bbaad57bc4bb5fa710efe2c510b0b4bc64872 ok`.

## Red checks

`env-matrix`. Job 112529653069, run 37539776169, on `705c3be37fe94feb37be1600b57403e129c382f8`. The shallow row: `Error: Cannot find module '/home/runner/work/_temp/envmatrix/shallow/.claude/workflows/policy_lint.mjs'`. The same missing module is the `rc=1 pins=null` on `pr`, `push-main` and `no-remote`, and the absent `skip checkProvenance-pin` line. Cheaper detector: `node tools/policy/policy_lint_envmatrix.mjs` on the checkout. It is named in a comment in `tools/pr/prepr.sh` and is not one of that script's steps. A pass of it on this tree printed `16 declared outcome(s) held, 0 did not`. This head `b5cbc740e59ea0d16f4088399d6ba5e82cbbfb4a` starts `tools/policy/policy_lint.mjs`, and the env-matrix job keeps that file across the base restore.

`mutation`. Job 112484566102, run 37526452102, on `cf9de4e2a50332c608d854de900108afe890039a`: `ADDED UNPINNED custom_components/heatpump_optimizer/quiet_windows.py:370 RETURN_DEL: return out`. Cheaper detector: `python3 tests/mutation_table.py --scope changed --base origin/main`, which returns at that ratchet before any mutant is cloned. Standing cost on that head, while the site was unpinned: `/usr/bin/time -p` `real 4.52`. The command is not in `tools/pr/prepr.sh` or `.claude/hooks`. The kill is recorded at `19391406563cf785e723be51ceb7b9b34a850511` under `killed_by` for `tests/manual_plan.py`.

`mutation-autofix`. Job 112486109066 printed `AUTOFIX: skip-no-measurement` and the repair did not happen. The site was not started: it would have overrun `--budget-minutes`, so there was no kill to apply. Cheaper detector: the mutation job's ratchet, same command and standing cost as above. No bot commit was waited on.

`closures`. Job 112436237942, run 37512253135, on `50a36f792eb32913607bc003408c4b6661e41a73`: `selectable script(s) with NO recording this run: tests/debug_collect.py`. The committed closure already listed it. The full arm re-derives from the lanes in `tests/derive_closures.sh`, and those lanes did not record it. Cheaper detector: none. The roster check is `tests/closure.py check` on that full re-derive; nothing in the tree compares selectable scripts to the `rec` lines before CI.

`closures`. Under-scoped `tests/features.py` by `services.yaml` on an earlier head. The Linux recording's rc is 0 and that path is in the committed closure. Cheaper detector: the recording JSON's `rc` plus `tests/closure.py check`, both already produced by the job. No cheaper detector exists for a file a completed run newly opens.

`closures-autofix`. Job 112457301514 printed `allowed=True` and `AUTOFIX: skip-clean`. No bot commit. An earlier head printed `skip-failed-recording` on `tests/harness_headers.py`. Cheaper detector: `option_doc_coverage.py` and `claims.py`, seconds, for that earlier recording failure. `skip-clean` is the job's own summary line.

`fast (3.14)`. On `fca0bea0c9ab864d087a6ee8939500b833f7d32c`: `UNWIRED TEST: tests/debug_collect.py is not referenced by tests/run.sh`. Cheaper detector: the `UNWIRED TEST` grep at the start of `tests/run.sh`. This head has `run "$PYTHON" tests/debug_collect.py` in `lane_units`.

`delivery-status`. The row is `dev/programme/delivery/1987.md`. The earlier red was `DELIVERY STATUS UNCHECKED` over main's merge subjects. Cheaper detector: `python3 tests/delivery_status.py --check`, the check itself. Those subjects are main's.

`pr-contract` was red on an earlier head because `## Red checks` did not name `closures`, `closures-autofix`, `fast (3.14)`, `mutation` or `mutation-autofix`. This section names them. Cheaper detector: `tools/audit/prepr.sh`.

`nightly-status` graded main. This diff does not change `tests/nightly_status.py`, `tests.yml`, `governance.yml`, the plan or `docs/HANDOVER.md`.

## Forward-carry

none

## Friction

none
