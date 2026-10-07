Closes #1939

Leaves #201 open.

The R9-DBG-1 debug collector (#1939): a week of what the install saw and did, behind the learning page's option, handed to Home Assistant's diagnostics download as an `hpo-debug/1` bundle. This body is a re-cut (`fixer.md`, past three rounds). Figures from earlier rounds are dropped. The only figures here were taken on this head.

This head merges `origin/main` `be0cb82134bd3a008e59127da6f2b67fb1c77e98` into the PR's head `95ad5034d4e41b5440b3c08350a2964c57867a84`. It goes through `a8d2e78ec189a5a8bb547df8ab7c23a426ec55ff`, an earlier merge of `421c77f950072f218d856dcf60f753e5f80ef10b`. After that come `3910026e` and `be0cb821`, which merged without conflict. There were content conflicts in `coordinator.py` and `tests/features.py`:

- `tests/features.py`. Both sides appended a block at the end of the file: this branch's DBG-1 checks and main's #1913 SW-4 checks. `a8d2e78e` keeps both and closes the DBG-1 `R.check(` call between them. Compared with the conflict file with its markers stripped, `diff` shows only that closing `)` and a blank line.
- `coordinator.py`, `configured_quiet_windows`. This branch had moved the body to `quiet_windows.configured_specs` to pay the structure ratchet. Main (#1913) changed that body's predicate from `silent_control_usable(entity)` to `silent_unenforceable(config, get_state)`, so a GCHV schedule can count as holdable. `a8d2e78e` took main's side whole, which re-inlined the body in the coordinator. That left `configured_specs` dead, still on the old predicate, and `tests/structure.py` failed (`max_class_loc 9070 > 9048`, `dead_top_level_symbols 2 > 1`). `c3d7f89f` keeps the move and applies main's change where the body now lives. `configured_specs(config, get_state=None)` calls `silent_unenforceable(config, get_state)`. The coordinator method passes `hass.states.get` with the same guard main used. It keeps the `out = ...` / `return out` shape both parents had, because main's ledger row `HeatPumpOptimizerCoordinator.configured_quiet_windows.RETURN_DEL.7edb83fa` pins that `return out`. When the call was returned directly, `tests/mutation_table.py` refused that row as naming no site (`347721aa`). Its docstring now says the predicate reads a GCHV schedule's numbers, so the old claim that the marker is decided "never from the state" is gone.
- `tests/closures.json`. `tests/debug_collect.py` was re-derived with `--single`, which adds `quiet_windows.py` and `modbus_prefill.py`. See `## Red checks`.

_Requested by **tvofi**_.

## Head

`e23f87122f177d532a515cc17ff6a35d53190f22`

## Mutation proof

Each mutant was applied in place to a committed tree, run, and then reverted with `git checkout`. Mutants A and B ran at `1919f6312eacb7bfe77896abee323692069f3570`. Between that commit and this head, the only changes are `347721aa` (the call result bound to `out`, then `return out`) and main's `be0cb821`, which touches neither `configured_specs` nor `configured_quiet_windows`. `tests/features.py` takes over an hour on this seat at the current load, so it was not re-run at this head.

- Mutant A: `configured_quiet_windows` passes `None` instead of the state getter. `PYTHONPATH=tests/hastub python3 tests/features.py` printed `FAIL configured_quiet_windows does not mark a fully holdable GCHV daily window not-enforced` with the marker present, beside the seat's standing `R9-F2.1 P3` failure, and exited 1.
- Mutant B: `configured_specs` goes back to the pre-#1913 predicate, `out["quiet_silent_windows_spec"] and not silent_control_usable(config.get(CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY))`. `tests/features.py` printed the same `configured_quiet_windows does not mark a fully holdable GCHV daily window not-enforced` FAIL, beside `R9-F2.1 P3`, and exited 1.
- Mutant C: `if silent_unenforceable(config, get_state):` becomes `if False:`. `PYTHONPATH=tests/hastub python3 tests/manual_plan.py` printed `FAIL configured_specs returns the stored rows and the not-enforced marker  [got {'quiet_silent_windows_spec': '22:00-06:00', 'quiet_off_windows_spec': '09:00-09:30'}]` and exited 1. That mutant is the inventory's `quiet_windows.py:507 GUARD_OFF` site. `python3 tests/mutation_table.py --scope changed --base origin/main` lists it as this diff's one `ADDED UNPINNED` site, killed by `tests/manual_plan.py`. Pinning it is `mutation-autofix`'s job (`ci-autofix.md`). No local `--pin-killed` was run.

## Null control

At `e23f87122f177d532a515cc17ff6a35d53190f22`, `PYTHONPATH=tests/hastub python3 tests/manual_plan.py` printed `ALL 129 manual plan checks PASSED`.

At `1919f6312eacb7bfe77896abee323692069f3570`, unmodified, `PYTHONPATH=tests/hastub python3 tests/features.py` printed `1 of 3815 FEATURE CHECKS FAILED`. The one failure is `R9-F2.1 P3: the shipped storage plan is no worse on its own objective than the half-price floor's plan refined under it  [shipped 110.4366, seeded with the half-price plan 110.1297]`. That is a storage-solve objective comparison on this arm64 seat. Neither `configured_specs` nor `configured_quiet_windows` is on its path. The previous body reported the same check red on this seat at an earlier head. CI's `fast (3.14)` was green at `95ad5034`. A mutant counts as killed only by a FAIL line that is not this one.

## Figures

Taken at `e23f87122f177d532a515cc17ff6a35d53190f22`, 2026-10-07T09:11:40Z, `origin/main` `be0cb82134bd3a008e59127da6f2b67fb1c77e98`, except where another SHA is named.

- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. At `a8d2e78e` the same command printed `FAIL dead_top_level_symbols 2 > 1 (+1)` and `FAIL max_class_loc 9070 > 9048 (+22)`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir <dir>`: at `1919f631`: `MODE: FULL -- every test script runs, nothing is scoped out.` The reason given was `tests/derive_closures.sh changes the gate itself`. The suite was not run unscoped locally. What did run is the set of scripts whose committed closure lists `quiet_windows.py`, minus `boost_drift_replay.py`, `harness_headers.py`, `entities.py`, `finite_boundary.py`, `golden.py`, `env_drift.py` and `arch_score_head.py`, which are left to CI. At `1919f631`, each script that ran printed its pass line and exited 0, except `features.py` (see `## Null control`): `manual_plan.py`, `guard_pins.py`, `debug_collect.py`, `plan_view.py`, `config_flow_steps.py`, `deployment_shape.py`, `doc_claims.py`, `solar_alignment.py`, `typing_ruler.py`, `wood_advisor.py`, `structure.py`, `card.mjs` and `card_drift.mjs`.
- At this head, `PYTHONPATH=tests/hastub python3` on `tests/manual_plan.py`, `tests/debug_collect.py` and `tests/guard_pins.py` printed `ALL 129 manual plan checks PASSED`, `ALL 30 DEBUG COLLECT CHECKS PASSED` and `ALL 47 GUARD PIN CHECKS PASSED`.
- `./tests/derive_closures.sh --single tests/debug_collect.py` at `1919f631`: exit 0. It added `quiet_windows.py` and `modbus_prefill.py` to that script's closure and kept `silent_mode.py`, which this run did not read. The same command at this head changed only the recorded `seconds`, and that change was discarded. The file set is unchanged, so the closure needs no further edit.
- `uvx ruff check --select F` on `coordinator.py` and `quiet_windows.py`, compared with the same files at `95ad5034` after stripping line numbers: no new finding. One finding is gone: the unused `CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY` import, which main removed.
- `python3 tests/mutation_table.py --scope changed --base origin/main`: exit 1, `4696 unpinned site(s) against 4695 at the ratchet base be0cb82134bd3a008e59127da6f2b67fb1c77e98, 1 of them added by this diff`, which is `quiet_windows.py:507 GUARD_OFF` (see `## Mutation proof`).
- `CLAIM_HEAD=$(git rev-parse HEAD) PYTHONPATH=tests/hastub python3 tests/env_drift.py --claims-only $(git merge-base origin/main HEAD)`: `claims hygiene: be0cb82134bd3a008e59127da6f2b67fb1c77e98 ok`.

## Red checks

At `95ad5034`, run 37564484318:

`closures`. Job 112609045485: `UNDER-SCOPED: tests/debug_collect.py really reads 1 file(s) the committed closure does not list: custom_components/heatpump_optimizer/quiet_windows.py`. Main moved quiet-window composition into a module that the coordinator imports, after this script's closure had been recorded. Cheaper detector: `./tests/derive_closures.sh --single tests/debug_collect.py` after each main merge. It takes seconds for this script. `tools/pr/prepr.sh` does not run it. Repaired in this head (see `## Figures`).

`mutation` (expected on this head, not yet run): the one added unpinned site above. Cheaper detector: `python3 tests/mutation_table.py --scope changed --base origin/main`, about 5 s. It ran here, and its site is killed by `tests/manual_plan.py`.

`closures-autofix`. Job 112620088047: `AUTOFIX: skip-failed-recording`, `THE REPAIR DID NOT HAPPEN`. By `ci-autofix.md` no bot commit was coming, so the repair above was made here. The failed recording was `tests/stress.py`: the downloaded `closure-recordings` artifact has `rc=1` in `stress.py.json`, and `stress.py.out` has `1 of 104 STRESS CHECKS FAILED` on `FAIL every scenario's solve costs what it should, in CPU, for this machine  [shoulder/tariff+pv+cycle used 18728 ms of CPU = 329x the 56.9 ms reference measured beside it (budget 268x)]`. That is a CPU budget measured while the recorder's audit hook was attached. `fast (3.14)` and `mutation` were green in that run, and this diff does not touch `stress.py` or the solver. Cheaper detector: none that runs before CI. The failure exists only while a script is being recorded. The class it belongs to is the third unclosed path in `ci-autofix.md`, a script that fails only under recording. This instance is a timing budget, not a truncation, which that rule does not yet name. See `## Friction`.

`delivery-status`. Job 112608980070: `DELIVERY STATUS UNCHECKED`. Its pending rows are main's `#1917`, `#2001` and `#2003`, and the merge-collection skip lists main's merge subjects. This branch's row, `dev/programme/delivery/1987.md`, is on main. Cheaper detector: `python3 tests/delivery_status.py --check`, the check itself. The red belongs to main's record.

`nightly-status`. Job 112608980459: `NIGHTLY FAILED: record-autofix failed last night.` That grades main's nightly. This diff does not touch `tests/nightly_status.py`, the workflows, or the record-autofix lane.

## Forward-carry

none

## Friction

ci-autofix.md: unenforced: `closures-autofix` reports `skip-failed-recording` for a `tests/stress.py` recording whose only failure is its CPU budget under the audit hook (run 37564484318), so a single real UNDER-SCOPED on an unrelated script waited on a human repair.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
