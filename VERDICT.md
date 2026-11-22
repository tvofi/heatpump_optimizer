Fix review: blocked d6a54399a63b76d43c4f3a84e1d2ac518da28ed0 mutation-vacuous: fault_hold.py:115 released, fault_hold.py:115 off, heat_curve.py:287 mode_off, fault_hold.py:150 since survive tests/features.py and tests/block_duty.py

bus-nonce: 1a661a73f02e6285b2187bf7240bde1a

Round 1 (first review; no `--reviewed-head`).

## Block

Four mutants on lines this PR adds survive the whole of `tests/features.py` (`ALL 6081 FEATURE CHECKS PASSED` under each, `ev/full_*.log`) and the fault-hold block with `tests/block_duty.py` (`ev/reviewer_mutants.log`). Three of them change behaviour the approved design `57d5d278` specifies, shown by a probe run at the head and under each mutant (`ev/probe.log`, `ev/probe_body.py`, `ev/probe_run.py`):

- `custom_components/heatpump_optimizer/fault_hold.py:115`, `consult`'s `released=inp.entry_released` dropped. At the head, a pass queued before the unload (`entry_released`) with a 30-minute fault raises 0 `pump_fault_hold` repairs. Under the mutant it raises 1. The design's carry **entry-released** names this exact path ("the consult sits before `apply`'s `entry_released` return"). The block's "an unloaded entry's displace raises no fault repair" drives only `heat_curve.publish`, and the "released guard" mutant dies through that path alone.
- `fault_hold.py:115`, `consult`'s `off=inp.mode == MODE_OFF` replaced by `off=False`. At the head, an Optimizer Off pass through `pump_arbiter.apply` after a held pass clears the latch and the repair: `(True, 1)` becomes `(False, 0)`. Under the mutant it stays `(True, 1)`. The design states that Off clears the latch and the repair. The check "and cleared on its falling edge, at Off and at unload" calls `holding(off=True)` directly, so the argument at the call site is never driven.
- `custom_components/heatpump_optimizer/heat_curve.py:287`, `off=mode_off` replaced by `off=False`. At the head, `publish(..., mode_off=True)` under a held latch sends the displace (`['mqtt']`), clears the latch and leaves no repair. Under the mutant it sends nothing, keeps holding and keeps `pump_fault_hold`.
- `fault_hold.py:150`, `diagnostics_view`'s `since` forced to `None`. This one is only in the diagnostics view. "the diagnostics download shows the fault latch under fault_hold" does not assert the value of `since`.

The fix this needs: one check per call site. A `pump_arbiter.apply` pass with `entry_released` and an old fault raises no repair. An `apply` pass at `MODE_OFF` after a held pass clears `held()` and the repair. `heat_curve.publish(mode_off=True)` under a held latch publishes and clears. The diagnostics row's `since` equals the latch start. Each check needs the null control its neighbours use.

The rest of my driver's survivors are dispositioned here, so this block lists every survivor it found:
- `duty_ledger.py:57`, a new row seeded with `"faulted": faulted`: an equivalent mutant, because the next line ORs `faulted` into the row anyway.
- `pump_arbiter.py:1911`, `space_before` dropped on every pass: a null-control mutant that the block misses and full `tests/features.py` kills (4 R10-ARBITER-OFF-RESTORE checks, `ev/full_spacebefore.txt`).

Neither of these is part of the block.

## Evidence

- Mutation proof (step 1): `python3 dev/audit/harnesses/r11_owner_fault_hold_mutants.py HEAD` at the head gives `BASELINE 0 failing`, `RESULT mutants=32`, `RESULT survived=0` (`ev/mutants.log`). The body's figure reproduces.
- My own mutants, driven by the fixer's runner (block plus `tests/block_duty.py`): `RESULT mutants=14`, `RESULT survived=6` (`ev/reviewer_mutants.log`, `ev/reviewer_mutants.py`). The 6 are dispositioned above.
- Full `tests/features.py` at this head: `ALL 6081 FEATURE CHECKS PASSED` (`ev/full_head.log`). The body quotes 6075, measured at `5eb7083aaa` before the main merge `32246a3fcc`. I did not re-derive that figure at `5eb7083aaa`.
- The block, re-run: `ALL 47 FEATURES BLOCK PASSED` (`ev/features_block.log`). `tests/block_duty.py` gives `ALL 154 BLOCK DUTY CHECKS PASSED` (`ev/block_duty.log`).
- Null control (step 3): `r11_owner_fault_latch.py synthetic` gives `latched_actuating=0`, `short_held=0`, `short_faults=6`, `repairs=1`. With `--opt-out` it gives `latched_actuating=260`, `short_held=0`, `repairs=0` (`ev/latch.log`, `ev/latch_optout.log`). Both match the body.
- Finder's harness (step 2): the packet names none. The latch replay and the mutant driver are the fixer's own instruments, committed under `dev/audit/harnesses/`.
- Class (step 6): I ran the design's sibling-site rule at the head (`ev/enum_head.txt`). Every site is either covered by the diff or dispositioned in the design: `_valve_write_problem`, `_async_set_pump`, the disinfection switch, `repairs.py` and the weather fetch. No class is open.
- Step 16: the release on a valid configuration is a legible off. "the cycle's OFF under the hold is left, and the step tick writes it once the alarm clears" drives it. The latch is in memory, so there is no persisted entry state. The design states, and the body repeats, that an unusable reading never ends a hold.
- Step 4/5: three-dot diff against `e3cb5c019b46`. It does not touch `VERSION`, the manifest, `RELEASE_NOTES.md` or either claim file.
- Step 13: `git merge-tree --write-tree origin/main d6a54399a63b` exits 0. origin/main is `e3cb5c019b46`, the merge base.
- Step 14: `tests/structure.py` prints `STRUCTURE RATCHET PASSED`. `module_excess_loc` goes 21779 → 21694, a lowering, and commit `6477e5f7df` gives the reason (the ledger moves out of `pump_arbiter.py`, the selector helpers fold into `_select`, and `_select` is identical to the three removed helpers). `tests/comment_ratchet.py` gives `long_units_head=2299`, `comment_ratchet: OK`.
- Step 10: all three body carries are on `origin/handoff/audit-r11-roster` `610138f1ac`, in `dev/programme/rosters/wave-r11-groups.json`: items 346bf281 (R11-OWNER-MODE-LEGS), 033699bc (R11-OWNER-FROST-HOLD) and 041d2bd4 (R11-OWNER-FAULT-TEXT).
- Step 7: the body's `## Head` names `d6a54399a63b76d43c4f3a84e1d2ac518da28ed0`, the head I measured.
- CI: I polled `merge_train.py classify d6a54399a63b --pr 3872` from 21:29 to 22:20 UTC. Every reading was `WAIT d6a54399a63b76d43c4f3a84e1d2ac518da28ed0 pending: gate red: none` (`ev/classify.log`). No red on this head, so no `## Red checks` is owed.
