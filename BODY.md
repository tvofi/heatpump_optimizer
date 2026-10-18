Part of #2247 (round-10 D7 findings ARCH2-s4 P1 and ARCH3-s6 P4; group R10-LEAF-IMPORTS, `fixes` is empty, so this closes nothing).

Two pure leaves reached the solver, and scipy with it, through one misplaced symbol each. The horizon clock `_utc_step_starts` lived in `optimizer.py`, so `silent_mode` and `quiet_windows` (and `setpoint_check`, `pump_arbiter`, `early_cutoff`, `repairs` through them) loaded the optimizer for a ten-line date walk; `legionella` loaded it for the string `"legionella"`.

- The clock moves verbatim into `drift.py`, the module already owning the UTC instant rules (`utc_elapsed_seconds`, `stored_instant`), as public `utc_step_starts`. The optimizer, coordinator, `silent_mode` and `quiet_windows` import it from there.
- The eighteen `REASON_*` codes move into `payload.py`, which owns the fields they are values of (`CurrentAction.space_reason` / `dhw_reason`, each plan row's `reason`). The optimizer imports the ones it writes; `legionella` imports `REASON_LEGIONELLA` from the payload. `_IDLE_REASONS`, the solver's grouping of those codes, stays in the optimizer.
- `coordinator.py`: import lines and moved-symbol references only (architect note 1). It also drops a `REASON_LEGIONELLA` import nothing in it read.
- Nothing is re-exported. Tests and the two live round-3 D2 harnesses import the moved names from their new owners. `utc_shift` stays in `accuracy.py`; see Forward-carry.
- No behaviour change. The function body and every code value are byte-identical moves. The gain is import time for tests and tools only, since Home Assistant loads the coordinator anyway, so no runtime gain is claimed and no timing figure is given.

Alternatives considered: the finder's P1 patch also moved `utc_shift` into drift and rewrote `utc_step_starts` on top of it, behind an `accuracy` re-export. That was rejected for three reasons: it needs a re-export (the architect note forbids one) or an edit to `boost.py` (outside this group's files), and it changes the body of the clock. A new `step_clock.py` module, archscore's planted control shape, was rejected because drift already owns the UTC-instant concept, and a second clock module would split that concept in two.

## Head

29ccddab0130e462fbb825a0f6cc48426dd9fbcd (merge base e5f7e169d64b93d4ae117eb07c68ecef6d47aea6). Main catch-ups so far: 2, both record-only. Production is unchanged since the first figures: `git diff --quiet 00ef7abbd47e47968357dab4d320103fabf2d83e 29ccddab0130e462fbb825a0f6cc48426dd9fbcd -- custom_components` exits 0. Every figure below was re-taken at this head and merge base.

## Mutation proof

The new checks are in `tests/features.py`, in the block `R10-LEAF-IMPORTS`. Each mutant is a single edit to production on the committed tree. Each is run through the existing block runner, `python3 tools/audit/seat/features_block.py "# R10-LEAF-IMPORTS (ARCH2-s4 P1" "# A tank colder than the room it stands in"`, and restored afterwards with `git checkout -- custom_components`:

- M1, in `silent_mode.py`: `from .drift import utc_step_starts` changed to `from .optimizer import utc_step_starts`. `1 of 5 FEATURES BLOCK FAILED`: `R10-LEAF-IMPORTS: silent_mode loads without the solver` (loaded `heatpump_optimizer.optimizer`, `scipy`).
- M2, in `legionella.py`: `REASON_LEGIONELLA` imported from `.optimizer`. `1 of 5` failed: `R10-LEAF-IMPORTS: legionella loads without the solver`.
- M3, in `optimizer.py`: `REASON_IDLE = "idle"` assigned again. `1 of 5` failed: `R10-LEAF-IMPORTS: the payload owns every reason code the optimizer writes` (optimizer assigns `['REASON_IDLE']`).
- M4, in `quiet_windows.py`: the same edit as M1. `1 of 5` failed: `R10-LEAF-IMPORTS: quiet_windows loads without the solver`.
- Revert arm: the merge base's `custom_components` with this head's checks gives `4 of 5 FEATURES BLOCK FAILED`. The four are silent_mode, quiet_windows, legionella, and the vocabulary check (18 codes assigned in the optimizer). `store` passes at both ends: its closure was already free of the solver at the base, so that check is already guarded and is kept as a pin.

## Null control

- The unmutated head prints `ALL 5 FEATURES BLOCK PASSED` from the same command.
- The census reads every module, and its last line counts the import failures. A census that imported nothing would print `modules=0` or a non-zero `import_failures`, and would exit 1.
- The census at the merge base reads the leaves IN, so the instrument can see the edge it reports gone.

## Figures

- Runtime solver closure: every package module except `__init__`, each imported in a fresh interpreter, measured by `python3 tools/audit/seat/solver_closure_census.py <ref>` (sha1 875a003a852d310be0d0293d852bf873989f3305).
  - Base e5f7e169d: `modules=76 solver_in=17 import_failures=0`.
  - Head 29ccddab0: `modules=76 solver_in=10 import_failures=0`.
  - The seven that leave are early_cutoff, legionella, pump_arbiter, quiet_windows, repairs, setpoint_check and silent_mode. None enters.
- Class enumeration (fixer.md step 8). The rule: archscore `layering`'s `violations` whose target layer is the solver's (`(… -> 1)`), from `tools/audit/archscore/metrics/layering.py` `measure()` on each tree.
  - Base: 3 (`quiet_windows`, `setpoint_check`, `silent_mode`). Head: 0. Disposition: all three are closed in this diff.
  - The other 19 violations all reach layer 2 (Home Assistant), and none of them reaches the solver. They are a distinct class (glue reach), outside this group.
- Ten modules still load the solver at the head: binary_sensor, button, climate, coordinator, datetime, diagnostics, optimizer, sensor, services and switch. Each is either the optimizer itself or Home Assistant glue that orchestrates it, so each is a legitimate edge rather than a leaf.
- Finder's harness: `PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round10/D7/arch2-s4/layering.py --ref <ref>`, from the export of b202335e2 (sha1 314f35a49c474c1a21b6f4776aca7bb2af4efa1f). It counts static, module-level imports only.
  - Base e5f7e169d: closure_setpoint_check 23 (optimizer IN), closure_quiet_windows 21 (IN), closure_silent_mode 20 (IN), closure_store 18 (out), private_cross_module_names 16.
  - Head 29ccddab0: 14 (out), 11 (out), 8 (out), 18 (out), 13.
  - store reads flat at both ends: its static closure was already solver-free at this base. The finder's 28 -> 21 was measured at 9061fbd3d.
- Golden drift: `PYTHONPATH=tests/hastub python3 tests/env_drift.py e5f7e169d64b93d4ae117eb07c68ecef6d47aea6` prints `NO UNCLAIMED DRIFT: 5 scenario(s) checked` and `NO STALE FIXTURE: 5 committed fixture(s)`. Both claim files are byte-identical to the merge base. The full `--all` run is left to CI.
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- Gate scope: `python3 tests/closure.py select --diff e5f7e169d64b93d4ae117eb07c68ecef6d47aea6 --workdir "$D"` prints `MODE: SCOPED -- 27 script(s) run, 6 scoped out.`
- CI prediction: `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` prints `no closures or fast red predicted`. The only lines it adds are the two unpinned sites below, which are warnings.
- Scripts run locally with `PYTHONPATH=tests/hastub`:
  - Green at 00ef7abbd, whose production code is identical to this head's: manual_plan.py, plan_view.py, doc_claims.py and typing_ruler.py. `tests/entities.py` printed `ALL 2346 ENTITY CHECKS PASSED`.
  - harness_headers.py, run in its recording at b5d774b48, refused one thing: a depth-counted root in the census harness, which was then under `dev/audit/harnesses/`. That harness now uses the canonical `repo_root` walk, and has moved to `tools/audit/seat/`. The two round-3 D2 harnesses this diff edits passed every header check.
  - Left to CI: the whole features.py and the heavy scripts.

## Architecture score

`python3 tools/audit/archscore/score.py --diff e5f7e169d64b93d4ae117eb07c68ecef6d47aea6` prints `Architecture score: dS +0.4646 IMPROVES`.

- layer_violations 22 -> 19 (+0.2016): the three solver-reach pairs above.
- private_cross_module 17 -> 14 (+0.2630): `coordinator`, `quiet_windows` and `silent_mode` no longer name `optimizer._utc_step_starts`.

No metric rises. The mechanism is the two moved owners, and putting either import back undoes it (M1, M4).

## Unpinned sites

- `custom_components/heatpump_optimizer/drift.py:64 GUARD_OFF` (`if tz is None:`, in `utc_step_starts`): pinned by `mutation-autofix`. It is the same line, moved, that `optimizer.py:_utc_step_starts GUARD_OFF ca88efc3` pinned. That stale pin is deleted in this diff, because its site no longer exists, and `ci_predict.py` says a stale pin is deleted by hand.
- `custom_components/heatpump_optimizer/drift.py:67 RETURN_DEL` (the zoned `return`): pinned by `mutation-autofix`. Its old pin was `3be6dbf2`, deleted for the same reason.

## Red checks

None so far. Two of prepr's `closures` refusals at earlier heads are answered here.

- `failed while being recorded: tests/entities.py` at 00ef7abbd: the same script run alone at that head passed. The failure was the recording on a host at load average 131.
- `INERT READS tests/harness_headers.py` on the census harness: the cheaper detector is `tools/pr/ci_predict.py`'s `inert_siblings`, which fired in prepr before any push, at no standing cost.
  - harness_headers.py reads `dev/audit/harnesses/` from a child process. That read is visible only to CI's Linux strace, so a Darwin `--single` records nothing for it: the recording at b5d774b48 listed 0 inert reads.
  - The harness therefore moved to `tools/audit/seat/`, which is INERT and globbed by no gate script. Its duplicate block runner was dropped for `features_block.py`, the instrument already there.

## Forward-carry

- A second UTC owner remains. `accuracy.utc_shift` is the same UTC walk as `drift.utc_step_starts`, and it is imported from accuracy by `boost.py` and `coordinator.py`. Moving it into drift touches `boost.py`, which is outside this group's files, and it would need a re-export to stay inside them. This is reported to the orchestrator for the roster rather than filed.
- The forward-carried PeakBilling precondition from R10-TARIFF holds. This diff touches no `peak_cost` call: its only `tariff.py` hunk is one comment.

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)
