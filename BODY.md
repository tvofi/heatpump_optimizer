Closes #1939

Leaves #201 open.

The R9-DBG-1 debug collector (#1939): a week of what the install saw and did, behind the learning page's option, handed to Home Assistant's diagnostics download as an `hpo-debug/1` bundle. This body is a re-cut (`fixer.md`, past three rounds). Figures from earlier rounds are dropped. The only figures here were taken on this head.

This head merges `origin/main` `59b5ac6e4594b42cd5579cca182a743c25f4c48d` into the PR's head `95ad5034d4e41b5440b3c08350a2964c57867a84`. It goes through `a8d2e78ec189a5a8bb547df8ab7c23a426ec55ff`, an earlier merge of `421c77f950072f218d856dcf60f753e5f80ef10b`. After that come `3910026e` and `be0cb821`, which merged without conflict, and `59b5ac6e` (#2006, R9-SW-6). #2006 conflicted only in `tests/features.py`, where both sides appended before the SW-4 tail's shared closing `)`. `5b1ea517` keeps this branch's DBG-1 block, then #2006's #1955 block, and each one closes its own `R.check(`. `grep -c 'R\.check('` gives 3445 on this side, 3432 on main and 3423 at the merge base, and 3454 merged, which is 3445 plus #2006's 9. `R.section(` stays at 208. The file parses. #2006 also changed `coordinator.py`, but not `configured_quiet_windows`. There were content conflicts in `coordinator.py` and `tests/features.py`:

- `tests/features.py`. Both sides appended a block at the end of the file: this branch's DBG-1 checks and main's #1913 SW-4 checks. `a8d2e78e` keeps both and closes the DBG-1 `R.check(` call between them. Compared with the conflict file with its markers stripped, `diff` shows only that closing `)` and a blank line.
- `coordinator.py`, `configured_quiet_windows`. This branch had moved the body to `quiet_windows.configured_specs` to pay the structure ratchet. Main (#1913) changed that body's predicate from `silent_control_usable(entity)` to `silent_unenforceable(config, get_state)`, so a GCHV schedule can count as holdable. `a8d2e78e` took main's side whole, which re-inlined the body in the coordinator. That left `configured_specs` dead, still on the old predicate, and `tests/structure.py` failed (`max_class_loc 9070 > 9048`, `dead_top_level_symbols 2 > 1`). `c3d7f89f` keeps the move and applies main's change where the body now lives. `configured_specs(config, get_state=None)` calls `silent_unenforceable(config, get_state)`. The coordinator method passes `hass.states.get` with the same guard main used. It keeps the `out = ...` / `return out` shape both parents had, because main's ledger row `HeatPumpOptimizerCoordinator.configured_quiet_windows.RETURN_DEL.7edb83fa` pins that `return out`. When the call was returned directly, `tests/mutation_table.py` refused that row as naming no site (`347721aa`). Its docstring now says the predicate reads a GCHV schedule's numbers, so the old claim that the marker is decided "never from the state" is gone.
- `tests/closures.json`. `tests/debug_collect.py` was re-derived with `--single`, which adds `quiet_windows.py` and `modbus_prefill.py`. See `## Red checks`.

_Requested by **tvofi**_.

## Head

`93ddd53eab19d396ebb6960c97ea9684bf0a792c`

## Mutation proof

Each mutant was applied in place to a committed tree, run, and then reverted with `git checkout`. Mutants A and B ran at `1919f6312eacb7bfe77896abee323692069f3570`. Between that commit and this head, the only changes are `347721aa` (the call result bound to `out`, then `return out`) and main's `be0cb821` and `59b5ac6e`, which touch neither `configured_specs` nor `configured_quiet_windows`. `tests/features.py` takes over an hour on this seat at the current load, so it was not re-run at this head.

- Mutant A: `configured_quiet_windows` passes `None` instead of the state getter. `PYTHONPATH=tests/hastub python3 tests/features.py` printed `FAIL configured_quiet_windows does not mark a fully holdable GCHV daily window not-enforced` with the marker present, beside the seat's standing `R9-F2.1 P3` failure, and exited 1.
- Mutant B: `configured_specs` goes back to the pre-#1913 predicate, `out["quiet_silent_windows_spec"] and not silent_control_usable(config.get(CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY))`. `tests/features.py` printed the same `configured_quiet_windows does not mark a fully holdable GCHV daily window not-enforced` FAIL, beside `R9-F2.1 P3`, and exited 1.
- Mutant C: `if silent_unenforceable(config, get_state):` becomes `if False:`. `PYTHONPATH=tests/hastub python3 tests/manual_plan.py` printed `FAIL configured_specs returns the stored rows and the not-enforced marker  [got {'quiet_silent_windows_spec': '22:00-06:00', 'quiet_off_windows_spec': '09:00-09:30'}]` and exited 1. That mutant is the inventory's `quiet_windows.py:507 GUARD_OFF` site. `python3 tests/mutation_table.py --scope changed --base origin/main` lists it as this diff's one `ADDED UNPINNED` site, killed by `tests/manual_plan.py`. `mutation-autofix` printed `skip-no-measurement` for it at `4e3f09b6` (job 112772526098), so no bot pin came. Under `ci-autofix.md` ("When `mutation-autofix` goes red, run `--pin-killed` yourself") the fixer committed the pin in `93ddd53e`: `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --pin-killed --base origin/main --scripts tests/manual_plan.py` printed `pinned quiet_windows.py:507 GUARD_OFF -- killed by tests/manual_plan.py` and `PIN KILLED: 1 pinned, 0 left unpinned`. It wrote `tests/mutation_ledger/killed_by/quiet_windows.py/configured_specs.GUARD_OFF.b6ab8a95.json`.

## Null control

At `93ddd53eab19d396ebb6960c97ea9684bf0a792c`, `PYTHONPATH=tests/hastub python3 tests/manual_plan.py` printed `ALL 129 manual plan checks PASSED`.

At `1919f6312eacb7bfe77896abee323692069f3570`, unmodified, `PYTHONPATH=tests/hastub python3 tests/features.py` printed `1 of 3815 FEATURE CHECKS FAILED`. The one failure is `R9-F2.1 P3: the shipped storage plan is no worse on its own objective than the half-price floor's plan refined under it  [shipped 110.4366, seeded with the half-price plan 110.1297]`. That is a storage-solve objective comparison on this arm64 seat. Neither `configured_specs` nor `configured_quiet_windows` is on its path. The previous body reported the same check red on this seat at an earlier head. CI's `fast (3.14)` was green at `95ad5034`. A mutant counts as killed only by a FAIL line that is not this one.

## Figures

Taken at `93ddd53eab19d396ebb6960c97ea9684bf0a792c`, 2026-10-07T13:32:30Z, `origin/main` `59b5ac6e4594b42cd5579cca182a743c25f4c48d`, except where another SHA is named.

- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. At `a8d2e78e` the same command printed `FAIL dead_top_level_symbols 2 > 1 (+1)` and `FAIL max_class_loc 9070 > 9048 (+22)`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir <dir>`: at `1919f631`: `MODE: FULL -- every test script runs, nothing is scoped out.` The reason given was `tests/derive_closures.sh changes the gate itself`. The suite was not run unscoped locally. What did run is the set of scripts whose committed closure lists `quiet_windows.py`, minus `boost_drift_replay.py`, `harness_headers.py`, `entities.py`, `finite_boundary.py`, `golden.py`, `env_drift.py` and `arch_score_head.py`, which are left to CI. At `1919f631`, each script that ran printed its pass line and exited 0, except `features.py` (see `## Null control`): `manual_plan.py`, `guard_pins.py`, `debug_collect.py`, `plan_view.py`, `config_flow_steps.py`, `deployment_shape.py`, `doc_claims.py`, `solar_alignment.py`, `typing_ruler.py`, `wood_advisor.py`, `structure.py`, `card.mjs` and `card_drift.mjs`.
- At this head, `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`, and `PYTHONPATH=tests/hastub python3` on `tests/manual_plan.py`, `tests/debug_collect.py` and `tests/guard_pins.py` printed `ALL 129 manual plan checks PASSED`, `ALL 30 DEBUG COLLECT CHECKS PASSED` and `ALL 47 GUARD PIN CHECKS PASSED`.
- `./tests/derive_closures.sh --single tests/debug_collect.py` at `1919f631`: exit 0. It added `quiet_windows.py` and `modbus_prefill.py` to that script's closure and kept `silent_mode.py`, which this run did not read. The same command at `e23f8712` and again at this head changed only the recorded `seconds`, and each time that change was discarded. The file set is unchanged, so the closure needs no further edit.
- `uvx ruff check --select F` on `coordinator.py` and `quiet_windows.py`, compared with the same files at `95ad5034` after stripping line numbers: no new finding. One finding is gone: the unused `CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY` import, which main removed.
- `python3 tests/mutation_table.py --scope changed --base origin/main`: its first line is `4694 unpinned site(s) of 5743 candidate sites, 4694 at the ratchet base 59b5ac6e4594b42cd5579cca182a743c25f4c48d; the ledger agrees with the deterministic inventory`, and the output holds no `REFUSED`. At `4e3f09b6` it printed 4695 against 4694, refusing on `quiet_windows.py:507 GUARD_OFF`. The drive of the 8 changed-scope mutants that follows was stopped at this load (over 170), so its per-driver results are not claimed.
- `CLAIM_HEAD=$(git rev-parse HEAD) PYTHONPATH=tests/hastub python3 tests/env_drift.py --claims-only $(git merge-base origin/main HEAD)`: `claims hygiene: 59b5ac6e4594b42cd5579cca182a743c25f4c48d ok`.

## Red checks

The set below comes from `gh api repos/tvofi/heatpump_optimizer/commits/<sha>/check-runs` over the 32 commits in `git rev-list --first-parent e23f8712 ^origin/main` (origin/main then at `be0cb821`) and `git rev-list 95ad5034 ^618d014f`. Every call answered (0 API failures). It holds every check-run with conclusion `failure`. Each cause is read from that job's log, and from the `closure-recordings` artifact where a recording failed.

`closures`, 7 heads.
- `8f756547` (job 112237571054): `UNDER-SCOPED: tests/features.py` reads `custom_components/heatpump_optimizer/services.yaml`. It is in the committed closure from a later head on.
- `fca0bea0`, `058a5f80` and `50a36f79` (jobs 112362556983, 112408061804, 112436237942): `selectable script(s) with NO recording this run: tests/debug_collect.py`. The new script was in no derive lane. `fca0bea0`'s `fast` red, below, is the same gap.
- `cf9de4e2`, `705c3be3` and `95ad5034` (jobs 112484666778, 112529758058, 112609045485): `UNDER-SCOPED: tests/debug_collect.py` reads `custom_components/heatpump_optimizer/quiet_windows.py`. Main moved quiet-window composition into that module after the closure was recorded. Repaired in this head (`--single`, `## Figures`).
- Cheaper detector: `./tests/derive_closures.sh --single <script>` after each main merge, which takes seconds for these scripts. `tools/pr/prepr.sh` does not run it. Nothing before CI compares selectable scripts against the derive lanes.

`closures-autofix`, 4 heads, all `AUTOFIX: skip-failed-recording`, so no bot commit came.
- `8f756547` (job 112253526031): the run's artifact records `tests/harness_headers.py` with `rc=1`. Its `fast` red, below, is the same failure.
- `cf9de4e2`, `705c3be3` and `95ad5034` (jobs 112503452843, 112543035083, 112620088047): the artifacts record `tests/stress.py` with `rc=1`. At `95ad5034`, `stress.py.out` has `1 of 104 STRESS CHECKS FAILED` on its CPU-per-solve budget (329x against 268x) while being recorded under the audit hook. `fast (3.14)` and `mutation` were green in that run, and this diff touches neither `stress.py` nor the solver.
- Cheaper detector: none that runs before CI. The failure exists only under recording. It is `ci-autofix.md`'s third unclosed path, a script that fails only while recorded. Three heads with the same `stress.py` recording failure make a recurrence; see `## Friction`.

`fast (3.14)`, 2 heads.
- `8f756547` (job 112237478738): `tests/env_drift.py --all` failed with `STALE config_flow` and `1 UNCLAIMED DRIFT(S)`, because the learning page's new option moved the `config_flow` capture. `tests/harness_headers.py` printed `5 of 105 HARNESS HEADER CHECKS FAILED` on the `option_doc_coverage.py` and `claims.py` headers, each one count behind the new option and module. The fixture and headers were re-taken on later heads. `fast` was green at `95ad5034`.
- `fca0bea0` (job 112362400100): `UNWIRED TEST: tests/debug_collect.py is not referenced by tests/run.sh`. `tests/run.sh` now runs it in `lane_units`.
- Cheaper detector: `tests/env_drift.py --claims-only` and `tests/harness_headers.py` for the first. They are seconds to minutes, are in `tests/run.sh`, and are not in `prepr.sh`. For the second, the `UNWIRED TEST` grep at the start of `tests/run.sh`.

`mutation`, 3 heads.
- `8f756547` and `9da596f2` (jobs 112237478695, 112303713384): `ADDED UNPINNED` sites in `button.py` and `debugger.py`, the new collector code. They were pinned by a `--pin-killed` drive with `tests/debug_collect.py` on a later head.
- `cf9de4e2` (job 112484566102): `ADDED UNPINNED custom_components/heatpump_optimizer/quiet_windows.py:370 RETURN_DEL: return out`. It is pinned under `killed_by` for `tests/manual_plan.py` (`configured_specs.RETURN_DEL.a8227ccf`).
- `4e3f09b6` added one more site, `quiet_windows.py:507 GUARD_OFF`, which `93ddd53e` pins (`## Mutation proof`).
- Cheaper detector: `python3 tests/mutation_table.py --scope changed --base origin/main`, about 5 s. It is not in `prepr.sh`.

`mutation-autofix`, 3 heads. `8f756547` (job 112239901173) printed `AUTOFIX: skip-measure-failed`, and `9da596f2` and `cf9de4e2` (jobs 112305445205, 112486109066) printed `AUTOFIX: skip-no-measurement`. The repair did not happen, so the pins came from the drives named under `mutation`. Cheaper detector: the same ratchet command as for `mutation`.

`env-matrix`, `705c3be3` (job 112529653069): `Error: Cannot find module '/home/runner/work/_temp/envmatrix/shallow/.claude/workflows/policy_lint.mjs'`. The matrix still started the old path after `policy_lint.mjs` moved to `tools/policy/`, and `b5cbc740` points it at the new path. Cheaper detector: `node tools/policy/policy_lint_envmatrix.mjs`, seconds. It is named in a comment in `tools/pr/prepr.sh` and is not one of its steps.

`pr-contract`, 2 heads. `8f756547` (job 112253716391): `## Red checks` did not name `closures`, `closures-autofix`, `fast (3.14)`, `mutation` or `mutation-autofix`. `705c3be3` (job 112543221828): it did not name `env-matrix`. This section names all of them. Cheaper detector: `tools/pr/prepr.sh <body> 1939`, whose `ancestry reds` step reads the same check-runs.

`delivery-status`, 9 heads, each `DELIVERY STATUS UNCHECKED`. The pending rows and the merge-collection skip are over main's merge subjects (at `95ad5034`: main's `#1917`, `#2001`, `#2003`). This PR's row, `dev/programme/delivery/1987.md`, is on main. Cheaper detector: `python3 tests/delivery_status.py --check`, the check itself. The red belongs to main's record.

`nightly-status`, 9 heads, each `NIGHTLY FAILED: record-autofix failed last night.` (2 of them `1 night ago`). That grades main's nightly lane. This diff does not touch `tests/nightly_status.py`, the workflows or the record-autofix lane.

## Forward-carry

none

## Friction

ci-autofix.md: unenforced: on three heads of this PR (`cf9de4e2`, `705c3be3`, `95ad5034`), `closures-autofix` reported `skip-failed-recording` because `tests/stress.py` failed its CPU budget only under the recorder's audit hook. Each time, a real UNDER-SCOPED on an unrelated script (`tests/debug_collect.py`) waited on a human repair. This is a third instance, so it triggers `root-cause.md`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
