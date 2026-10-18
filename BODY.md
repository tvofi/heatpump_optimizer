Part of #2247 (round-10 D7 findings ARCH2-s4 P1 and ARCH3-s6 P4; group R10-LEAF-IMPORTS, `fixes` is empty, so this closes nothing).

Two pure leaves reached the solver, and scipy with it, through one misplaced symbol each. The horizon clock `_utc_step_starts` lived in `optimizer.py`, so `silent_mode` and `quiet_windows` (and `setpoint_check`, `pump_arbiter`, `early_cutoff`, `repairs` through them) loaded the optimizer for a ten-line date walk; `legionella` loaded it for the string `"legionella"`.

- The clock moves verbatim into `drift.py`, the module already owning the UTC instant rules (`utc_elapsed_seconds`, `stored_instant`), as public `utc_step_starts`. The optimizer, coordinator, `silent_mode` and `quiet_windows` import it from there.
- The eighteen `REASON_*` codes move into `payload.py`, which owns the fields they are values of (`CurrentAction.space_reason` / `dhw_reason`, each plan row's `reason`). The optimizer imports the ones it writes; `legionella` imports `REASON_LEGIONELLA` from the payload. `_IDLE_REASONS`, the solver's grouping of those codes, stays in the optimizer.
- `coordinator.py`: import lines and moved-symbol references only (architect note 1). It also drops a `REASON_LEGIONELLA` import nothing in it read.
- Nothing is re-exported. Tests and the two live round-3 D2 harnesses import the moved names from their new owners. `utc_shift` stays in `accuracy.py`; see Forward-carry.
- No behaviour change. The function body and every code value are byte-identical moves. The gain is import time for tests and tools only, since Home Assistant loads the coordinator anyway, so no runtime gain is claimed and no timing figure is given.

Alternatives considered: the finder's P1 patch also moved `utc_shift` into drift and rewrote `utc_step_starts` on top of it, behind an `accuracy` re-export. That was rejected for three reasons: it needs a re-export (the architect note forbids one) or an edit to `boost.py` (outside this group's files), and it changes the body of the clock. A new `step_clock.py` module, archscore's planted control shape, was rejected because drift already owns the UTC-instant concept, and a second clock module would split that concept in two.

## Head

1aefeeba436dd14df7656d50f2dcb94e8c03fd87 (merge base 0310d10383530b536603ba0c6daa74c90251638c; one main catch-up so far, record-only). The figures below were taken at 00ef7abbd47e47968357dab4d320103fabf2d83e; the only commit after it deletes two ledger pins (see Unpinned sites), and `git diff --quiet 00ef7abbd47e47968357dab4d320103fabf2d83e 1aefeeba436dd14df7656d50f2dcb94e8c03fd87 -- custom_components dev tools` exits 0, so it touches no code those figures read.

## Mutation proof

The new checks are in `tests/features.py`, block `R10-LEAF-IMPORTS`. Each mutant is a single edit to production on the committed tree, run with `python3 dev/audit/harnesses/r10_leaf_imports_closure.py block`, which runs that block verbatim, and restored afterwards with `git checkout -- custom_components`:

- M1, in `silent_mode.py`: `from .drift import utc_step_starts` changed to `from .optimizer import utc_step_starts`. Fails `R10-LEAF-IMPORTS: silent_mode loads without the solver` (loaded `heatpump_optimizer.optimizer`, `scipy`).
- M2, in `legionella.py`: `REASON_LEGIONELLA` imported from `.optimizer`. Fails `R10-LEAF-IMPORTS: legionella loads without the solver`.
- M3, in `optimizer.py`: `REASON_IDLE = "idle"` assigned again. Fails `R10-LEAF-IMPORTS: the payload owns every reason code the optimizer writes` (optimizer assigns `['REASON_IDLE']`).
- M4, in `quiet_windows.py`: the same edit as M1. Fails `R10-LEAF-IMPORTS: quiet_windows loads without the solver`.
- Revert arm: the merge base's `custom_components` with the head's checks gives `4 FAILED`. The four failures are silent_mode, quiet_windows, legionella, and the vocabulary check (18 codes assigned in the optimizer, none in the payload). `store` passes at both ends, because its closure was already free of the solver at the base (already guarded, kept as a pin).

## Null control

- The unmutated head gives `0 FAILED` from the same `block` command.
- The census reads every module, and its last line counts the import failures. A census that imported nothing would print `import_failures`>0 or `modules=0` and exit 1.
- The census at the merge base reads the leaves IN, so the instrument can see the edge it reports gone.

## Figures

- Runtime solver closure, every package module except `__init__`, each imported in a fresh interpreter: `python3 dev/audit/harnesses/r10_leaf_imports_closure.py census <ref>` (harness sha1 e527ad86ca5574f0806b884c471722cb0481a176). Base 0310d1038: `modules=76 solver_in=17 import_failures=0`. Head 00ef7abbd: `modules=76 solver_in=10 import_failures=0`. The seven that leave are early_cutoff, legionella, pump_arbiter, quiet_windows, repairs, setpoint_check and silent_mode. None enters.
- Class enumeration (fixer.md step 8). The rule is archscore `layering`'s `violations` whose target layer is the solver's (`(… -> 1)`), from `tools/audit/archscore/metrics/layering.py` `measure()` on each tree. Base: 3 (`quiet_windows`, `setpoint_check`, `silent_mode`). Head: 0. Dispositions: all three are closed in this diff. The remaining 19 violations all reach layer 2 (Home Assistant) and none reaches the solver. They are a distinct class (glue reach), outside this group.
- Ten modules still load the solver at the head: binary_sensor, button, climate, coordinator, datetime, diagnostics, optimizer, sensor, services and switch. Every one is the optimizer itself or Home Assistant glue that orchestrates it. Each is a legitimate edge, not a leaf.
- Finder's harness, `PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round10/D7/arch2-s4/layering.py --ref <ref>` (export of b202335e2, sha1 314f35a49c474c1a21b6f4776aca7bb2af4efa1f). It counts static, module-level imports only.
  - Base 0310d1038: closure_setpoint_check 23 (optimizer IN), closure_quiet_windows 21 (IN), closure_silent_mode 20 (IN), closure_store 18 (out), private_cross_module_names 16.
  - Head 00ef7abbd: setpoint_check 14 (out), quiet_windows 11 (out), silent_mode 8 (out), store 18 (out), private names 13. store reads flat at both ends: its static closure was already solver-free at this base, and the finder's 28 -> 21 was measured at 9061fbd3d.
- Golden drift: `PYTHONPATH=tests/hastub python3 tests/env_drift.py 0310d10383530b536603ba0c6daa74c90251638c` prints `NO UNCLAIMED DRIFT: 5 scenario(s) checked` and `NO STALE FIXTURE: 5 committed fixture(s)`. Both claim files are byte-identical to the merge base. The full `--all` run is left to CI.
- `python3 tests/structure.py` at the head prints `STRUCTURE RATCHET PASSED`.
- Gate scope: `python3 tests/closure.py select --diff 0310d10383530b536603ba0c6daa74c90251638c --workdir "$D"` prints `MODE: SCOPED -- 27 script(s) run, 6 scoped out.`
- Run locally at the head, `PYTHONPATH=tests/hastub`:
  - green: manual_plan.py, plan_view.py, doc_claims.py, typing_ruler.py.
  - harness_headers.py: both edited round-3 D2 harnesses pass every header check. The script printed `12 of 109 HARNESS HEADER CHECKS FAILED`, all 12 from `dev/audit/rounds/round4/D7/sysid_estimator_frontier.py` hitting its 900 s wall cap (rc=124, cpu 71.1 s) on a seat host at load average 131. That file is not touched here, so the failure is the host's load, not this diff, and CI's run is the authority.
  - left to CI: features.py, which a session restart killed mid-run, and the heavy scripts.

## Architecture score

`python3 tools/audit/archscore/score.py --diff 0310d10383530b536603ba0c6daa74c90251638c` prints `Architecture score: dS +0.4646 IMPROVES`.

- layer_violations 22 -> 19 (+0.2016): the three solver-reach pairs above.
- private_cross_module 17 -> 14 (+0.2630): `coordinator`, `quiet_windows` and `silent_mode` no longer name `optimizer._utc_step_starts`.

No metric rises. The mechanism is the two moved owners, and putting either import back undoes it (M1, M4).

## Unpinned sites

- `custom_components/heatpump_optimizer/drift.py:64 GUARD_OFF` (`if tz is None:`, in `utc_step_starts`): pinned by `mutation-autofix`. It is the same line, moved, that `optimizer.py:_utc_step_starts GUARD_OFF ca88efc3` pinned. That stale pin is deleted in this diff, because its site no longer exists, and `ci_predict.py` says a stale pin is deleted by hand.
- `custom_components/heatpump_optimizer/drift.py:67 RETURN_DEL` (the zoned `return`): pinned by `mutation-autofix`. Its old pin was `3be6dbf2`, deleted for the same reason.

## Red checks

None so far. `tools/pr/prepr.sh` at 00ef7abbd refused `closures` with `failed while being recorded: tests/entities.py (exit 1)`. The same script run on its own at that head printed `ALL 2346 ENTITY CHECKS PASSED` (rc=0), and that run was taken on a host at load average 131. The failure is therefore the recording under load, not the script. CI's `closures` job re-records it, and its summary line is the authority. `INERT READS tests/harness_headers.py: dev/audit/harnesses/r10_leaf_imports_closure.py` is `closures-autofix`'s to merge (`ci-autofix.md`). That inert dimension is recorded on Linux only, so a Darwin seat cannot record it, and the second prepr run's only refusing `ci predict` line is that one.

## Forward-carry

- A second UTC owner remains. `accuracy.utc_shift` is the same UTC walk as `drift.utc_step_starts`, and it is imported from accuracy by `boost.py` and `coordinator.py`. Moving it into drift touches `boost.py`, which is outside this group's files, and it would need a re-export to stay inside them. This is reported to the orchestrator for the roster rather than filed.
- The forward-carried PeakBilling precondition from R10-TARIFF holds. This diff touches no `peak_cost` call: its only `tariff.py` hunk is one comment.

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)
