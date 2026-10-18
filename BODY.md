Part of #2247 (round-10 D7 findings ARCH2-s4 P1 and ARCH3-s6 P4; group R10-LEAF-IMPORTS, `fixes` is empty, so this closes nothing).

Two pure leaves reached the solver, and scipy with it, through one misplaced symbol each. The horizon clock `_utc_step_starts` lived in `optimizer.py`, so `silent_mode` and `quiet_windows` (and `setpoint_check`, `pump_arbiter`, `early_cutoff`, `repairs` through them) loaded the optimizer for a ten-line date walk; `legionella` loaded it for the string `"legionella"`.

- The clock moves verbatim into `drift.py`, the module already owning the UTC instant rules (`utc_elapsed_seconds`, `stored_instant`), as public `utc_step_starts`. The optimizer, coordinator, `silent_mode` and `quiet_windows` import it from there.
- The eighteen `REASON_*` codes move into `payload.py`, which owns the fields they are values of (`CurrentAction.space_reason` / `dhw_reason`, each plan row's `reason`). The optimizer imports the ones it writes; `legionella` imports `REASON_LEGIONELLA` from the payload. `_IDLE_REASONS`, the solver's grouping of those codes, stays in the optimizer.
- `coordinator.py`: import lines and moved-symbol references only (architect note 1). It also drops a `REASON_LEGIONELLA` import nothing in it read.
- Nothing is re-exported. Tests and the two live round-3 D2 harnesses import the moved names from their new owners. `utc_shift` stays in `accuracy.py`; see Forward-carry.
- No behaviour change. The function body and every code value are byte-identical moves. The gain is import time for tests and tools only, since Home Assistant loads the coordinator anyway, so no runtime gain is claimed and no timing figure is given.

Alternatives considered: the finder's P1 patch also moved `utc_shift` into drift and rewrote `utc_step_starts` on top of it, behind an `accuracy` re-export. That was rejected for three reasons: it needs a re-export (the architect note forbids one) or an edit to `boost.py` (outside this group's files), and it changes the body of the clock. A new `step_clock.py` module, archscore's planted control shape, was rejected because drift already owns the UTC-instant concept, and a second clock module would split that concept in two.

## Head

75e2a037d1f9d108605d7d5623492017c120ccbd (merge base 52f698905868c9140ed213ea542c44053fca7096). Main catch-ups by this seat: 3, all record-only. The third is this head's merge. The PR head under review, 8d76a9edf1ec3356ba7d8e55601e8e8c17553977, is an ancestor of this head. Since that review, this head adds the round-1 repairs listed below.

Production code is unchanged since the first figures: `git diff --quiet 00ef7abbd47e47968357dab4d320103fabf2d83e 75e2a037d1f9d108605d7d5623492017c120ccbd -- custom_components` exits 0. Every figure below was re-taken at this head and merge base.

## Mutation proof

The new checks are the `R10-LEAF-IMPORTS` block of `tests/features.py`. Each mutant is a single production edit on the committed tree, run through `python3 tools/audit/seat/features_block.py "# R10-LEAF-IMPORTS (ARCH2-s4 P1" "# A tank colder than the room it stands in"`. The tree is restored after each with `git checkout -- custom_components`.

- M1, in `silent_mode.py`: `from .drift import utc_step_starts` becomes `from .optimizer import utc_step_starts`. `1 of 5 FEATURES BLOCK FAILED`: `R10-LEAF-IMPORTS: silent_mode loads without the solver`.
- M2, in `legionella.py`: `REASON_LEGIONELLA` is imported from `.optimizer`. `1 of 5`: `legionella loads without the solver`.
- M3, in `optimizer.py`: `REASON_IDLE = "idle"` is assigned again. `1 of 5`: `the payload owns every reason code the optimizer writes`.
- M4, in `quiet_windows.py`: the same edit as M1. `1 of 5`: `quiet_windows loads without the solver`.
- M6, the review's survivor: `REASON_PUMP_MODE` is dropped from the payload import and `REASON_PUMP_MODE: str = "pump_mode"` is added. It is now killed, `1 of 5`, with the vocabulary check printing `optimizer binds ['REASON_PUMP_MODE'] outside its payload import`.
  - The check used to walk only module-level `ast.Assign`. It now refuses any Store-context name, def, class or import binding a `REASON_` name anywhere in optimizer.py, other than the one `from .payload import`.
- M7: a nested `REASON_IDLE = "idle"` inside a function. Killed, `1 of 5`.
- Revert arm: the merge base's `custom_components` under this head's checks gives `4 of 5 FEATURES BLOCK FAILED`. `store` passes at both ends, because its closure was already solver-free at the base.

## Null control

- The unmutated head prints `ALL 5 FEATURES BLOCK PASSED` from the same command.
- The census reads every module and prints `modules` and `import_failures`. An empty or failing census exits 1.
- The census at the merge base reads the leaves IN, so the instrument can see the edge it reports gone.

## Figures

- Runtime solver closure: `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_leaf_solver_closure.py <ref>` (sha1 4c1cd796815534bc57f29bf6c0c92bbbf359b263). The header carries the harness contract.
  - Base 52f698905: `modules=76 solver_in=17 scipy_in=18 import_failures=0`.
  - Head 75e2a037d: `modules=76 solver_in=10 scipy_in=11 import_failures=0`.
  - The seven that leave are early_cutoff, legionella, pump_arbiter, quiet_windows, repairs, setpoint_check and silent_mode. None enters.
- Class enumeration (fixer.md step 8): archscore `layering`'s `violations` whose target is the solver layer (`(… -> 1)`), from `tools/audit/archscore/metrics/layering.py` `measure()`.
  - Base: 3 (`quiet_windows`, `setpoint_check`, `silent_mode`). Head: 0. All three are closed in this diff.
  - The other 19 reach layer 2 (Home Assistant), not the solver. They are a distinct class (glue reach), outside this group.
- Ten modules still load the solver at the head: binary_sensor, button, climate, coordinator, datetime, diagnostics, optimizer, sensor, services and switch. Each is the optimizer itself or Home Assistant glue that orchestrates it, so each is a legitimate edge.
- Moved-symbol references at the old home: an `ast` walk of every tracked `.py` outside `dev/archive/`, looking for an `ImportFrom` of `*.optimizer` naming `REASON_*` or `_utc_step_starts`.
  - At 8d76a9edf it found 2: tests/features.py at line 25622 (8 codes) and line 60240 (6 codes). Both now import from `payload.py`; at this head the walk finds 0.
  - `tests/dst_checks.py` reads `utc_step_starts` through coordinator and optimizer on purpose: its identity check needs both bindings.
- Finder's harness: `PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round10/D7/arch2-s4/layering.py --ref <ref>` (export of b202335e2, sha1 314f35a49c474c1a21b6f4776aca7bb2af4efa1f). It counts static, module-level imports only.
  - Base 52f698905: closure_setpoint_check 23 (optimizer IN), closure_quiet_windows 21 (IN), closure_silent_mode 20 (IN), closure_store 18 (out), private_cross_module_names 16.
  - Head 75e2a037d: 14 (out), 11 (out), 8 (out), 18 (out), 13.
- Golden drift: `PYTHONPATH=tests/hastub python3 tests/env_drift.py 52f698905868c9140ed213ea542c44053fca7096` prints `NO UNCLAIMED DRIFT: 5 scenario(s) checked` and `NO STALE FIXTURE: 5 committed fixture(s)`. Both claim files are byte-identical to the merge base.
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- Gate scope: `python3 tests/closure.py select --diff 52f698905868c9140ed213ea542c44053fca7096 --workdir "$D"` prints `MODE: SCOPED -- 27 script(s) run, 6 scoped out.`
- CI prediction: `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` prints `no closures or fast red predicted`. The only lines it adds are the two drift.py sites, which `mutation-autofix` pinned in 3b76e0b08.
- Left to CI: the whole features.py and the heavy scripts.

## Architecture score

`python3 tools/audit/archscore/score.py --diff 52f698905868c9140ed213ea542c44053fca7096` prints `Architecture score: dS +0.4646 IMPROVES`. No metric rises.

- layer_violations 22 -> 19 (+0.2016) is the part this diff earns. Its mechanism is the two moved owners: putting the imports back (M1, M2, M4) returns the three solver-reach pairs.
- private_cross_module 17 -> 14 (+0.2630) is the private -> public rename `_utc_step_starts` -> `utc_step_starts`, not the move. A rename-only plant on the merge base reproduces it, leaving the clock in optimizer.py and moving nothing. The plant is the review's `armB.patch`, sha1 96df7cbfa45e21a7fb6e5638e80c0af00eac0f1c, committed on a scratch tree; `score.py --diff 52f698905868c9140ed213ea542c44053fca7096 <that commit>` prints `dS +0.2630 IMPROVES` with `private_cross_module 17 -> 14  +0.2630`. The rename is right for a public owner, but it is not an architectural gain, so it is not claimed as one. See Forward-carry.

## Unpinned sites

- `custom_components/heatpump_optimizer/drift.py:64 GUARD_OFF` (`if tz is None:`, in `utc_step_starts`): pinned by `mutation-autofix`. It is the same line, moved, that `optimizer.py:_utc_step_starts GUARD_OFF ca88efc3` pinned. That stale pin is deleted in this diff, because its site no longer exists, and `ci_predict.py` says a stale pin is deleted by hand.
- `custom_components/heatpump_optimizer/drift.py:67 RETURN_DEL` (the zoned `return`): pinned by `mutation-autofix`. Its old pin was `3be6dbf2`, deleted for the same reason.

## Red checks

- `mutation` at 29ccddab0 (the PR's first run) flagged the unpinned sites listed under `## Unpinned sites`. It is answered by naming it (`ci-autofix.md`): `mutation-autofix` pinned them in its bot commit 3b76e0b08. No cheaper detector is owed for a red the autofix chain repairs.
- prepr's `closures` refusals at earlier heads:
  - `failed while being recorded: tests/entities.py` at 00ef7abbd. The same script run alone at that head passed; the failure was the recording on a host at load average 131.
  - `INERT READS tests/harness_headers.py`, for the census harness in `dev/audit/harnesses/`. The cheaper detector is `tools/pr/ci_predict.py`'s `inert_siblings`, which fires in prepr before the push at no standing cost.
    - `harness_headers.py`'s `_scope_paths` reads that directory from a child process. A Darwin `--single` therefore records nothing for it: the recording at b5d774b48 listed 0 inert reads. Only CI's `strace -f` sees the read.
    - The entry is written the way that recording would write it, as 2f7aafdc8 did for `d6_page_anchors.py`: through `closure.write_closures`, sorted into `inert_reads[tests/harness_headers.py]`, one line, in its own `record(closures)` commit.
    - Review round 1 ruled that the earlier placement in `tools/audit/seat/` dodged this check, so the harness is back in its home.

## Forward-carry

- To the archscore stage: archscore's `private_cross_module` scores a pure private -> public rename as an improvement (+0.2630 here, reproduced by a rename-only plant). It counts crossings of names spelled with a leading underscore, so renaming a crossed private removes the crossing without changing the coupling. The orchestrator places it.
- To R10-LIVESTATE: a second UTC owner remains. `accuracy.utc_shift` is the same UTC walk as `drift.utc_step_starts`, and `boost.py` and `coordinator.py` import it from `accuracy`. Moving it into `drift` touches `boost.py`. R10-LIVESTATE is the live group whose files hold both `boost.py` and `accuracy.py`, and it is the structural (arch) move. R10-NIGHT-FOLDS and R10-TRUST-RELATIVE hold only `accuracy.py`, and each owns a learner body. The orchestrator append-carries it.
- The R10-TARIFF PeakBilling precondition holds: no `peak_cost` call is touched, and the only `tariff.py` hunk is one comment.

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)
