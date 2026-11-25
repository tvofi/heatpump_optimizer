Fix review: blocked 91cfc89fdade5cb556ad5e7fd3353ac4c3eae07b unload-row-written: the real unload restores twice and the second pass, after pump_arbiter.release drops the latch, writes the baseline row into the faulted pump

bus-nonce: 51095a75eff3f4685902e138ac1369ce

Round 2. This is a delta re-review over the reviewed head d6a54399a63b76d43c4f3a84e1d2ac518da28ed0. Scope is the packet's `delta`, widened as fix-review.md step 12 allows to one production seam: the merge with #3812 moved the unload row guard into `pump_arbiter._release_row` (`custom_components/heatpump_optimizer/pump_arbiter.py:2195`). That puts the design's **unload-row** carry at a non-obvious risk, and CI cannot see it, because the test helper does not model the production unload sequence.

## Block

- The production unload restores the row twice, at `custom_components/heatpump_optimizer/__init__.py:452` and again at `:457`. The comment at `:455` reads "Once more behind the released latch". Between the two passes, `coordinator.async_shutdown()` (`:454`) calls `pump_arbiter.release` (`coordinator.py:6572`), and that calls `fault_hold.release`, which pops the latch (`pump_arbiter.py:2168`).
- The first pass under the hold gets `False` from `_release_row`'s new guard `(reason == "unload" and fault_hold.held(coord.entry))`, so the row stays owed. On the second pass `fault_hold.held` is already `False`, so the row is written into the pump while its fault alarm still holds. The approved design's **unload-row** carry, and the body ("An unload writes no baseline row ... so the row stays owed"), say the opposite.
- The tests miss this because `tests/features.py:64892` `_pa_unload` models only one restore followed by `release`. The docstring says "as `async_unload_entry` runs them", but `async_unload_entry` runs a restore, then `release`, then a second restore. So "unload under the hold writes no baseline row, and drops the latch" passes against a sequence that production never runs.
- Probe: at this head I added the second restore to `_pa_unload`, exactly as `__init__.py:457` runs it (`ev/probe_two_pass_unload.diff`). The fault-hold block then gives `1 of 59 FEATURES BLOCK FAILED`. The failure is `FAIL unload under the hold writes no baseline row, and drops the latch [([('select', 'select.pump_mode', 'Heating + DHW')], False)]` (`ev/probe_two_pass_unload.log`). The unmodified block passes: the harness baseline is `BASELINE 0 failing` (`ev/mutants.log`), and the body reports `ALL 59`.
- The fix this needs: keep the row owed across the second pass. Either let `release` keep a "held at unload" mark that `_release_row` reads, or drop the latch only after the second restore. Then make `_pa_unload` run the restore, `release` and restore sequence that `async_unload_entry` runs, so the existing check and its null control drive the real order. Before the merge, at d6a54399a63b, the guard sat inside `release()` itself, so it was not exposed to this sequence. The #3812 merge resolution introduced the defect.

## Findings

- Residual: `tests/closures.json` re-records timing fields well above main's: `tests/cycle_lane.py` seconds 61.7 → 189.2, `tests/typing_ruler.py` 0.6 → 44.2, `tests/guard_pins.py` 18.2 → 23.4. These are host timings from the fixer's `--single` and ledger-driver runs, not closure membership. Carry: dismissed: timing fields are not closure membership and gate no selection read in this review

## Evidence

- Previous block (four survivors) resolved. `python3 dev/audit/harnesses/r11_owner_fault_hold_mutants.py HEAD` gives `BASELINE 0 failing`, `RESULT mutants=38`, `RESULT survived=0` (`ev/mutants.log`). Each mutant is killed: `consult released` (1 failing), `consult Off` (2), `publish mode_off` (1) and `diagnostics since` (1). The two new merge mutants are killed too: `Off row held too` and `stale hand-back held`. The new checks in `ce9619a4f4` each carry a null control.
- `python3 tests/env_drift.py --all`: `NO UNCLAIMED DRIFT: 56 scenario(s)`, `NO STALE FIXTURE`, EXIT 0 (`ev/env_drift.log`). The `config_flow` claim line is the only change to either claim file (three-dot against `bb6377b4da`).
- `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched (three-dot diff empty).
- `git merge-tree --write-tree origin/main 91cfc89fdade` exits 0 with origin/main `bb6377b4da` (`ev/merge_tree.txt`).
- `tests/structure.py`: `STRUCTURE RATCHET PASSED` (`ev/structure.log`). `module_excess_loc` goes 21774 → 21739, a lowering. `tests/comment_ratchet.py`: `comment_ratchet: OK`.
- Full `tests/features.py` at this head ran into my 900 s local timeout with 0 `FAIL` lines (`ev/full_head.log`, EXIT 124). So I did not re-derive the body's `ALL 6206`; CI's run is the authority.
- I read the merge resolutions against both sides. `duty_ledger.py` is main's `step_verdict` plus this group's `observe`, `RUN_SETTLE` (one minute, equal to main's `_TICK`) and the fault-first branch. `coordinator.py` takes the union for the frequency guard and the stale half gated by `fault_hold.held`. Off's row being written at the mode change (`_release_row` with reason `mode_off`, before any `apply` pass clears the latch) is the body's stated new behaviour. Only the unload seam above is defective.
- CI: `merge_train.py classify 91cfc89fdade --pr 3872` read `WAIT ... pending: gate red: none` on every poll from 12:32 to 12:58 UTC (`ev/classify.log`). No red on this head, so no `## Red checks` is owed. The block stands on code regardless of CI.
