R10-REGISTRY-LEAK: an unloaded entry's coordinator is freed; the cut-off record no longer pins it (D1-s1-01).

Closes #2231.

`early_cutoff._STATES` is a `WeakKeyDictionary` keyed by the coordinator, but its value, `CutoffState.wiring`, held `CutoffInputs.inputs`: the coordinator's bound `arbiter_inputs`. A weak-keyed entry whose value reaches its key is never collected, so after `async_unload_entry` every torn-down coordinator stayed alive (5 of 5 after 5 reload rounds). Unload released the room listener but never the wiring. Worse, the unload hook was registered only where a listener was (a room thermometer and a switch are configured), so an entry without them had no unload hook at all.

The fix is in `early_cutoff.py`. `arm` registers `detach` once per record, listener or not, and `detach` calls `release` and then drops the wiring. The `boost.py` (`_STATES`, `_PLAN_BASES`) and `pump_arbiter.py` (`_STATES`) registries were enumerated: their values hold no path back to the key (`_PLAN_BASES` holds plan dicts; the arbiter's `unsubs` are cleared by `release_listeners` at unload), and they read 5 -> 0 once the coordinator is freed, so no change there. `debugger._COLLECTORS` is popped at unload and reads 0 at both ends. No sibling seam to file.

## Head

`c777f855b9d87f8218ed3650aead1e92537f51e1` (origin/main `ef08fb420` merged in).

## Mutation proof

- The check "unloading the entry frees the coordinator the cut-off record was keyed by" (`tests/features.py`, after the listener-drop check) goes red on the base `early_cutoff.py`: `[False False]`.
- Mutant: register `detach` only inside the listener branch (the old shape of the hook). The check goes red on the no-switch arm alone: `[True False]`.
- Mutant: replace `if held.wiring is None:` in `arm` by `if True:`: the check "arming twice registers one unload hook, not one per cycle" goes red, `[2]`.
- Mutant: drop `held.wiring = None` from `detach`: the base behaviour, both arms `False`.

## Null control

- Control inside the same check group: an entry that is never unloaded still pins its coordinator (`not _ec_freed("switch.hp", False)`), so the freed-coordinator check can fail. It is green on base and fix.
- The carry's null: popping the registry at unload reads 5 -> 0 at the base (`--perturb`). At the fix the unperturbed run already reads 0, and `--perturb` reads 0 too, so the pop moves nothing. A live coordinator keeps its entry: the record's wiring is dropped only by `detach`, which only the entry's unload runs.

## Figures

- `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_registry_leak.py` (the finder's `m1_reload_leak.py` and its rig, one file, for a later seat): at the base `torn_alive=5`, `registry_early_cutoff_torn_keys=5`; at the head `torn_alive=0` and every registry 0. The finder's own `dev/audit/rounds/round10/D1/s1/m1_reload_leak.py` reads the same 5 -> 0.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: MODE: SCOPED, 21 scripts run. `tests/features.py`: ALL 4138 FEATURE CHECKS PASSED at the fix (three checks added).
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED, no budget touched. `python3 tools/audit/seat/tmp_paths.py --check`: 0 refused. `python3 tools/audit/archscore/score.py --diff origin/main`: dS +0.0000 NULL.

## Unpinned sites

custom_components/heatpump_optimizer/early_cutoff.py:160 GUARD_OFF (`if held.wiring is None:`): pinned by "arming twice registers one unload hook, not one per cycle", red on `if True:` (mutation proof above).

## Closures

`tests/closures.json`: `dev/audit/harnesses/r10_registry_leak.py` added by hand to `tests/harness_headers.py`'s `inert_reads`, one line (`--single` does not clear an inert read; precedents 387128bb, fbc9400a9, d7bfeb0dd).

## Red checks

`mutation` was red on head d19dd839: the diff added one unpinned site, `custom_components/heatpump_optimizer/early_cutoff.py:160` GUARD_OFF (`if held.wiring is None:`), which `prepr.sh` had also predicted. The cheaper detector is `prepr.sh`'s mutation prediction (standing cost: one prepr run, already paid); the body then owed the site a line under `## Unpinned sites`, and it names it. Answered by the `mutation-autofix` bot commit c723bd9d ("ci: pin killed mutants"), which recorded `tests/mutation_ledger/killed_by/early_cutoff.py/arm.GUARD_OFF.d460246f.json`: the `if False:` mutant takes `tests/features.py` from rc=0 to rc=1. The PR head c723bd9d carries that file (read back from the head). The pin is in addition to my `if True:` mutant, killed by "arming twice registers one unload hook, not one per cycle".

## Forward-carry

none

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)

