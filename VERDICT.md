Fix review: blocked 9fe3c4cf81465123f5dc6b360a30df7631f75974 mutation-vacuous: the step tick's gate (MIN_OFF hold and blocked-mode OFF skip) is unchecked, a tick wired around _write_supply passes all 4617 checks

bus-nonce: 5f6e06db0a86b7121fa306fdf794c9f9

## Block

Review round 3 of PR #2968 (earlier blocks: `d26a00aa2` mutation-vacuous, `c4e9f6a3`/`ddf75aaf` ci-red). This review measured head `9fe3c4cf81465123f5dc6b360a30df7631f75974` from a detached worktree.

The PR says the tick goes through the same gate as the cycle. The design note says the gated write is `_write_supply`, "which both the cycle and the tick call". The `note_supply` docstring says "the tick passes the same cut-off hold and blocked-mode skip". The new `early_cutoff.py` module docstring says "a step the plan turns on passes :func:`allow_on` like the cycle's". No check holds that claim.

- Mutant R3 (mine): `coordinator.py`, in `_apply_action`'s `pump_arbiter.SupplyWiring(self.arbiter_inputs, boost.held_for(self), self._write_supply)`, replaces `self._write_supply` with `lambda on: pump_arbiter.switch_supply(self.hass, getattr(self, "_ctx", self)._config.heat_pump_switch_entity, on)`. The tick still writes at every boundary, but it no longer goes through `early_cutoff.allow_on` or `pump_arbiter.supply_write`.
  - The whole `PYTHONPATH=tests/hastub python3 tests/features.py` prints `ALL 4617 FEATURE CHECKS PASSED` (rc=0).
  - The mutation is one `str.replace`, asserted to match exactly once, in a fresh worktree (`ev/mutant_driver.py`, `ev/mutant_R3.res`, `ev/features_R3.log`).
- Why nothing fails: the only cut-off case, `an early cut-off holds across a step boundary the plan keeps on`, writes its cut with a direct `_sa_pa.switch_supply(hass, "switch.hp", False)` call. It never records an `early_cutoff` cut, so `allow_on` has nothing to hold. That check covers the tick's change-only rule (M3), not the gate.
  - No case drives the tick while the pump's signals block both channels or report cooling.
  - R1 (the gate removed inside `_write_supply`) is killed only by the cycle's check, `the coordinator's cycle inside MIN_OFF of a cut does not turn the switch on`.
- Consequence: the tick runs at every step boundary between cycles. If a later change wires it around the gate, the tick can turn the compressor back on inside `MIN_OFF` (10 min) of an early cut, or write OFF in a mode where the cycle skips OFF. No check would go red.
- What clears it: one `_sa_guarded`-style case per gate arm, driven through the real coordinator. Its null control is the same run with the gate inactive.
  - Arm 1: an `early_cutoff` cut recorded at 06:10, and a plan step turning ON at 06:15, inside `MIN_OFF`. Assert the tick writes no `turn_on`.
  - Arm 2: `_pump_signals` with both channels blocked (or cooling), and a step turning OFF. Assert the tick writes nothing.
  - Show R3 red on both.

## Findings

- The step tick's gate has no check of its own: mutant R3 (the tick wired around `_write_supply`) survives all of `tests/features.py`. This is the block above, owed by the fixer before the next handoff. Carry: R10-SAV-ACTUATION
- The duty ledger books the first reading of an OFF step after an ON step from the previous step's tail. Both phases book such a step `space-instead` at the head (`ev/harness_head.txt`). The control is phase independence, and it holds. A settle window on the ledger's run fold is still owed. The body routes it to #2492, which the PR leaves open (`Refs`). I confirmed the residue in the harness output. Carry: #2492

## Evidence

- RESULT head-measured 9fe3c4cf81465123f5dc6b360a30df7631f75974 (`ev/HEAD.txt`).
- RESULT merge: `git merge-tree --write-tree origin/main <head>` rc=0, tree `f3117c16`. origin/main `89ccf7326` is the merge base, so the head is 0 behind (`ev/merge_tree.txt`). Roles diff since the merge base is empty, so this contract is current.
- RESULT mutation proof. Each mutant is one exact-once `str.replace` in its own worktree, and the whole `tests/features.py` runs (`ev/mutant_*.res`).
  - The unmutated head prints `ALL 4617 FEATURE CHECKS PASSED`. The body says 4598; main's merge added checks.
  - Y1 (`i >=` -> `i >` in `step_supply`): `1 of 4617`, on `... under a step past the plan's power schedule`, as the body says.
  - Y2 (`note_supply`'s no-switch guard -> `if False:`): `1 of 4617`, on `an install with no supply switch arms no step tick ...`, as the body says.
  - M3 (`if on != last:` -> `if True:`): `3 of 4617`. It fails the two checks the body names plus the round-2 live-boost check, which was added after M3 was first measured.
  - M4 (the ledger reads `self._measured_power`): `1 of 4617`, on the phase-0/14 check, as the body says.
  - R1 (mine, `allow_on` dropped in `_write_supply`): `1 of 4617`, on the cycle's MIN_OFF check.
  - R2 (mine, `plan_step_runs` fallback ignores the hot-water draw): `1 of 4617`, on R9-F2.4 P2.
  - R3: survives (Block).
- RESULT harness. There is no finder harness: the roster states the control in words, and the body discloses `dev/audit/harnesses/r10_sav_actuation_phase.py` as the fixer's own build. Its sha1 is `d8871c1b...`, as the body says.
  - I ran it at the head: `AGREE: yes`.
  - I copied it into a detached worktree of the current merge base `89ccf7326`: `AGREE: no` (`ev/harness_*.txt`).
  - The body's base was `88c6ad5bb`; the outcome is the same at both bases.
- RESULT class census. `git grep -n 'switch_supply('` returns the definition plus the callers in `coordinator._write_supply` and `early_cutoff.on_room_event`. `git grep -n 'heat_pump_on_schedule\|plan_step_runs('` returns `optimizer.get_current_action`, `coordinator._apply_result_payload`, `pump_arbiter.step_supply`, the field in `optimizer.py` and `wood_fuel.py`. Both match the body's Figures (`ev/cheap_checks.txt`).
  - `coordinator.py:4904` (`ExternalHeatObservation`) still reads the cycle-sampled `_measured_power`. That is the per-cycle external-heat observer, not the duty ledger, so it is outside this seam.
- RESULT structure: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
  - Budgets move down only: `class_excess_loc` 17672->17659 and `max_class_loc` 8065->8063 at this merge base.
  - The movement is earned: the OFF-skip decision moved into the pure `pump_arbiter.supply_write`, and the inline plan-switch rule became `thermal_model.plan_step_runs`.
- RESULT archscore: `score.py --diff 89ccf7326 HEAD` prints `Architecture score: dS +0.0000 NULL`.
- RESULT version: `VERSION`, the manifest, `RELEASE_NOTES.md` and both claim files are untouched by the three-dot diff.
- RESULT CI at the head, as read at 12:41 UTC (`ev/check_runs.txt`): no check concluded red. Still running: `tests / fast (3.14)`, `tests / coverage`, `tests / closures`, `tests / mutation`, `codeql / Analyze (python)` and one `prelude`. Everything else that concluded is success, skipped or neutral. The R3 mutant is outside the mutation lane's operators (BOOLOP, GUARD_OFF, CMP_BOUND, RETURN_DEL), so a green lane would not cover it.
- Not re-derived: the body's `ci_predict.py` unpinned count (24), and the 484 s timing.
