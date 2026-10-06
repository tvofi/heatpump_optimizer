Closes #1939

The debug collector, its learning-page option, the `debug_collect` action, the finalize button and the `hpo-debug/1` bundle. The ring is the `debug` store. The collector listens to the coordinator, so `coordinator.py` names no debugger.

This head records the 52 mutation sites the diff added. CI run 37473761833 on `9da596f2e578e846a1fdff8619bf4acced647e46` killed none of them: job 112303713384 printed `MUTATION TABLE REFUSED -- nothing was measured: 0 mutant(s) timed out, 52 not started for --budget-minutes`, and job 112305445205 printed `AUTOFIX: skip-no-measurement`. The admission compares one mutant's whole driver sum with the 35-minute budget, and that sum exceeds it for `button.py`, `debugger.py` and `store.py`, so the drive never started. A full local `--pin-killed` is `MUTATION TABLE INCONCLUSIVE` on this host because `tests/features.py`'s baseline is the R9-F2.1 P3 pair; that run wrote no pins and was not used.

`tests/debug_collect.py` is the driver that kills 51 of the sites. `_repair`'s `if stamp is None` guard is equivalent: `admitted` already refuses every stamp `stored_instant` refuses, and applying that GUARD_OFF left `tests/debug_collect.py` at rc=0. That site is `survivor_triage`, verdict equivalent.

This head merges `origin/main` `6b1ccb685e51903e7e524995a84d831d3904da9f` (delivery rows only) onto the pin commit `6d5d796e955275cb76226bbae4d2cbc8150cabd0`. The merge does not touch the pinned files.

## Head

`fca0bea0c9ab864d087a6ee8939500b833f7d32c`

## Mutation proof

`PYTHONPATH=tests/hastub python3 tests/mutation_table.py --pin-killed --base origin/main --jobs 3 --scripts tests/debug_collect.py` on `6d5d796e955275cb76226bbae4d2cbc8150cabd0`, against base `fc76a05577985c92574e4d42433f61192efe47f4`. Each of the 51 killed sites took `tests/debug_collect.py` from rc=0 failed=0 to rc=1. One ledger row: `tests/mutation_ledger/killed_by/debugger.py/_repair.GUARD_OFF.a7fab6b5.json` records GUARD_OFF `if False:` failed=1. The equivalent site was not in that pool.

## Null control

The same drive: `null control custom_components/heatpump_optimizer/store.py:73 NULL_COMMENT survived tests/debug_collect.py`. A comment-only edit, every driver in play must let it survive, and this one did.

Applying GUARD_OFF to `debugger.py`'s `if stamp is None` and running `PYTHONPATH=tests/hastub python3 tests/debug_collect.py` stayed rc=0, which is why that site is triaged rather than pinned.

## Figures

`PYTHONPATH=tests/hastub python3 tests/debug_collect.py` at `6d5d796e955275cb76226bbae4d2cbc8150cabd0`, 2026-10-06T14:58:47Z, origin/main `6b1ccb685e51903e7e524995a84d831d3904da9f` — `ALL 30 DEBUG COLLECT CHECKS PASSED`.

`PYTHONPATH=tests/hastub python3 tests/mutation_table.py --pin-killed --base origin/main --jobs 3 --scripts tests/debug_collect.py` — `PIN KILLED: 51 pinned, 0 left unpinned`. Inventory line before the drive: 4750 unpinned, 4699 at the ratchet base.

`python3 tests/structure.py` — `STRUCTURE RATCHET PASSED`. `RESULT coordinator_private_reach=0 count`, `RESULT max_class_loc=9067 count`, `RESULT seam_cut_total=772 count`.

`PYTHONPATH=tests/hastub python3 tests/entities.py` — `ALL 2187 ENTITY CHECKS PASSED`.

`python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` before the delivery-row merge — `MODE: SCOPED -- 30 script(s) run, 2 scoped out.` `tests/stress.py` is in `scope.run` and was not run.

`./tests/derive_closures.sh --single tests/debug_collect.py` — recorder exit 0, `closure: updated 1 closure(s)`, `tests/debug_collect.py` 81 files, recorded rc 0.

## Red checks

`closures`. Under-scoped `tests/features.py` by `services.yaml` on an earlier head. The Linux recording's rc is 0 and that path is in the committed closure. Cheaper detector: the recording JSON's `rc` plus `tests/closure.py check`, both already produced by the job. No cheaper detector exists for a file a completed run newly opens.

`closures-autofix`. `skip-failed-recording` on `tests/harness_headers.py` at that earlier head (header counts behind the tree). Cheaper detector: `option_doc_coverage.py` and `claims.py`, seconds. The headers name the printed counts.

`fast (3.14)`. `env_drift.py --all` and `harness_headers.py` on that earlier head. Cheaper detector: those two scripts. Both were green on `9da596f2` against the claim ref that head named.

`mutation`. On `9da596f2`, job 112303713384: `MUTATION TABLE REFUSED -- nothing was measured: 0 mutant(s) timed out, 52 not started for --budget-minutes`. Cheaper detector: none. The refusal is `drive_pin_pool`'s admission, which does not start a mutant whose recorded driver sum exceeds 35 minutes; the inventory that lists the 52 sites is the same process, not an earlier one. This head pins 51 under `killed_by` for `tests/debug_collect.py` and triages the stamp-is-None guard as equivalent, so the added-unpinned set is empty.

`mutation-autofix`. Job 112305445205: `AUTOFIX: skip-no-measurement`. The pin process exited 1 under `pipefail` before `measurement()` wrote a status, so no bot commit was coming. Cheaper detector: none beyond reading that summary line. The pins are in this commit.

`delivery-status`. The diff adds `docs/delivery/1987.md`. The job on the earlier head was `DELIVERY STATUS UNCHECKED` over main's merge subjects, which `subject_number` does not recognise. Cheaper detector: `python3 tests/delivery_status.py --check`, the check itself. Those subjects are main's, not this row.

`pr-contract` was red on an earlier head because `## Red checks` did not name `closures`, `closures-autofix`, `fast (3.14)`, `mutation` or `mutation-autofix`. This section names them. Cheaper detector: `tools/audit/prepr.sh`, the same contract. Not run here: another `prepr.sh` was already in flight.

`nightly-status` graded main. This diff does not change `tests/nightly_status.py`, `tests.yml`, `governance.yml`, the plan or `docs/HANDOVER.md`.

## Forward-carry

none

## Friction

none

_Requested by **tvofi**_.
