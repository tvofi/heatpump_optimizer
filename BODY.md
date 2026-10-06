Closes #1939

Merge `origin/main` `1b1bbaad57bc4bb5fa710efe2c510b0b4bc64872` into `058a5f8018e87cb7861477c8e7382ba9c7daada8`. `f07cd253c52f1012427d9869a808f1df39dafb93` is an ancestor of that tip; the commits above it add `docs/delivery/2000.md` only.

The mermaid and the D6 census keep both additions. Main adds the Model Restart Advisor (60 sensors). This branch adds the finalize button (5 buttons). The platforms construct 77 entities. The claim list kept is `config_flow`. `coord_all_features`, `coord_dhw`, `coord_grid_fee`, `coord_minimal` and `coord_two_zone` are origin/main's list; those fixture files match origin/main, and a `coord_minimal` capture differs from that file only in value leaves. `tests/structure.py` measures `max_class_loc` at the ledger sum, so the cap is not raised.

_Requested by **tvofi**_.

## Head

`50a36f792eb32913607bc003408c4b6661e41a73`

## Mutation proof

`debugger.py`, `button.py` and `tests/debug_collect.py` are unchanged from the pin commit `6d5d796e955275cb76226bbae4d2cbc8150cabd0`. The pins recorded there still name those lines. `store.py` gains `evidence_since` on the accuracy domain from origin/main; that domain is not the debug store.

Replacing `60 sensors` with `59 sensors` in the mermaid and running `PYTHONPATH=tests/hastub python3 tools/audit/round4/D6/claims.py` prints `FALSE C5`. Restoring the line prints `claims_false=0`.

The earlier drive, `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --pin-killed --base origin/main --jobs 3 --scripts tests/debug_collect.py` on `6d5d796e955275cb76226bbae4d2cbc8150cabd0`, pinned 51 sites. `_repair`'s `if stamp is None` guard is `survivor_triage`, verdict equivalent: applying GUARD_OFF left `tests/debug_collect.py` at rc=0.

## Null control

The same C5 run: the documented tuple is `(77, 59, 6, 5, 4, 1, 1)` and the measured tuple stays `(77, 60, 6, 5, 4, 1, 1)`.

`config_flow`'s capture matches the committed fixture (0 leaf diffs) and differs from origin/main's fixture by `_seed.debug_collect_enabled`, `_seeded.learning.debug_collect_enabled` and `learning.debug_collect_enabled`.

The pin drive's null control, on that same head: `null control custom_components/heatpump_optimizer/store.py:73 NULL_COMMENT survived tests/debug_collect.py`.

## Figures

Taken at `50a36f792eb32913607bc003408c4b6661e41a73`, 2026-10-06T18:20:18Z, origin/main `1b1bbaad57bc4bb5fa710efe2c510b0b4bc64872`.

- `python3 tests/structure.py` — `STRUCTURE RATCHET PASSED`. `RESULT max_class_loc=9048 count`. `RESULT seam_cut_total=765 count`.
- `PYTHONPATH=tests/hastub python3 tools/audit/round4/D6/claims.py` — `RESULT claims_true=123 claims`. `RESULT claims_false=0 claims`.
- `PYTHONPATH=tests/hastub python3 tests/debug_collect.py` — `ALL 30 DEBUG COLLECT CHECKS PASSED`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` — `MODE: FULL -- every test script runs, nothing is scoped out.` Reason: `tests/run.sh` changes the gate itself. `tests/run.sh` was not run unscoped.
- `git merge-tree --write-tree origin/main HEAD` — exit 0.
- `CLAIM_HEAD=$(git rev-parse HEAD) PYTHONPATH=tests/hastub python3 tests/env_drift.py --claims-only $(git merge-base origin/main HEAD)` — `claims hygiene: 1b1bbaad57bc4bb5fa710efe2c510b0b4bc64872 ok`.

## Red checks

`closures`. Under-scoped `tests/features.py` by `services.yaml` on an earlier head. The Linux recording's rc is 0 and that path is in the committed closure. Cheaper detector: the recording JSON's `rc` plus `tests/closure.py check`, both already produced by the job. No cheaper detector exists for a file a completed run newly opens.

`closures-autofix`. `skip-failed-recording` on `tests/harness_headers.py` at that earlier head. Cheaper detector: `option_doc_coverage.py` and `claims.py`, seconds.

`fast (3.14)`. On `fca0bea0c9ab864d087a6ee8939500b833f7d32c`: `UNWIRED TEST: tests/debug_collect.py is not referenced by tests/run.sh`. Cheaper detector: the `UNWIRED TEST` grep at the start of `tests/run.sh`. This head has `run "$PYTHON" tests/debug_collect.py` in `lane_units`.

`mutation`. On `9da596f2`, job 112303713384: `MUTATION TABLE REFUSED -- nothing was measured: 0 mutant(s) timed out, 52 not started for --budget-minutes`. Cheaper detector: none. The admission is `drive_pin_pool`, which does not start a mutant whose recorded driver sum exceeds 35 minutes. This head pins 51 under `killed_by` for `tests/debug_collect.py` and triages the stamp-is-None guard as equivalent.

`mutation-autofix`. Job 112305445205: `AUTOFIX: skip-no-measurement`. Cheaper detector: none beyond that summary line. The pins are in `6d5d796e`.

`delivery-status`. The diff adds `docs/delivery/1987.md`. The earlier red was `DELIVERY STATUS UNCHECKED` over main's merge subjects. Cheaper detector: `python3 tests/delivery_status.py --check`, the check itself. Those subjects are main's.

`pr-contract` was red on an earlier head because `## Red checks` did not name `closures`, `closures-autofix`, `fast (3.14)`, `mutation` or `mutation-autofix`. This section names them. Cheaper detector: `tools/audit/prepr.sh`.

`nightly-status` graded main. This diff does not change `tests/nightly_status.py`, `tests.yml`, `governance.yml`, the plan or `docs/HANDOVER.md`.

## Forward-carry

none

## Friction

none
