Carry 1 (#2365, arbiter step width) is closed by the first check pair and the `_share`/`log_steps` edit; Carry 2 (#2351, shutdown call site) by the second pair, a test only; Carry 3 (coordinator lane) is honoured: `coordinator.py` is not edited (`git diff --name-only` against it is empty).

Two production residuals from the s9 sweep: #2365 (the arbiter spells the plan step width as literals) and #2351 (nothing pins that `async_shutdown` calls `forget_held`). No `coordinator.py` edit; arm 2 is a test only. No golden fixture moved.

## Head

`9a2b6ba8fe6b0040b87680ef5f79388f45686884` adds one commit to the previous head, containing only this PR's own row, `dev/programme/delivery/3199.md`. The authored code head is `316f0a2ee5e80f5354fc1fef18186cd7a6b92b12`.

316f0a2ee5e80f5354fc1fef18186cd7a6b92b12

## Mutation proof

Each mutant is a copy of this head, full `tests/features.py` run.
- #2365: `pump_arbiter.py` restored to origin/main (literal `15.0`, `LOG_STEPS = 96`): 1 of 4781 FEATURE CHECKS FAILED, `R10-PROD-RESIDUE-PINS #2365: a 40 % hot-water share splits at minute 12 ...  [('space', 'space', 96)]`.
- #2351: the `forget_held(self.hass)` line deleted from `async_shutdown`: 1 of 4781 FAILED, `R10-PROD-RESIDUE-PINS #2351: async_shutdown re-arms a hass-owned latch ...  [[30, 10]]` (second call stays at DEBUG).
- Strict-`<` bound of `_share`'s short-remainder guard (a `<=` mutant survived the first pin drive): added check `a remainder of exactly SPLIT_MIN_MINUTES is still a heating share`; the `<=` mutant fails 1 of 4782 (`[('dhw', 'dhw')]`), this head passes ALL 4782 FEATURE CHECKS.
- The earlier counts above (4781) were taken before that one check was added.

## Null control

At the real 15-minute width the split is minute 6 and the log holds 96 steps (check `#2365 null control`, green at this head and on the #2365 mutant). Without the shutdown between the two `log_held` calls the second stays DEBUG (check `#2351 null control`, green on all three trees).

## Figures

- Full features run per tree: `PYTHONPATH=tests/hastub python3 tests/features.py` (this head, the #2365 mutant, the #2351 mutant).
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` printed MODE: SCOPED; every python script in `scope.run` run with `GOLDEN_MODE=drift` and passed, including `tests/golden.py`, `tests/env_drift.py` and `tests/finite_boundary.py`; `tests/card.mjs` and `tests/card_drift.mjs` were not run locally (no JS or card surface touched).
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED, no budget touched.
- Toolchain: the venv started at numpy 2.4.6 / scipy 1.17.1; after `tools/audit/seat/cloud-setup.sh` it reads 2.5.4 / 1.18.1, matching `tests/requirements-ci.txt`, and every run above was after that. CI remains the authority for goldens (none moved here).
- origin/main moved twice while the gate ran (c3a279e32 -> a9c2f90fc -> 8e90d8144); both merged cleanly. The second delta touched thermal_model.py, the card, audit harnesses and ledger records, none of the files this diff or its closure edits (`git diff --name-only` against pump_arbiter, coordinator, plan_step, log_latch, features, golden returns nothing); the scoped scripts and a full `tests/features.py` were rerun at this head. `tools/pr/prepr.sh` rerun at this head.

## Red checks

`mutation` (predicted by `prepr.sh` step 6d, never red on the remote): the diff removed two pinned arbiter sites (`LOG_STEPS = 96`, the `15.0 -` guard) and added three unpinned ones, and one of them (the `<` bound) survived the pin drive. Cheaper detector: `tools/pr/prepr.sh` step 6d / `ci_predict`, already standing, which named all of it before the handoff; the survivor got a killing check rather than a triage.

## Unpinned sites

- `pump_arbiter.py:220 RETURN_DEL` (`log_steps`): pinned, killed by `tests/typing_ruler.py` (`mutation_table.py --pin-killed`; `log_steps.RETURN_DEL.abf5020b.json`).
- `pump_arbiter.py:1165 GUARD_OFF` (`_share`): pinned, killed by `tests/features.py` (`_share.GUARD_OFF.4f254e46.json`).
- `pump_arbiter.py:1165 CMP_BOUND` (`_share`): survived the first drive; killed by the new boundary check, then pinned by a second `--pin-killed` (`_share.CMP_BOUND.4f254e46.json`).
- The two old pins on the removed sites (`@module.CONST.4fed562a`, `_share.GUARD_OFF.5c3377cc`) are deleted: their sites no longer exist.

## Forward-carry

none

## Friction

none

