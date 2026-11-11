R10-ARBITER-OFF-RESTORE: turning the optimizer off, and every unload, restores the pump arbiter's space set-point to the person's baseline, under the owner's ruling (tvofi, #201 comment 6708225978, 2026-11-07, "Arbiter too"), which retracts the 2026-09-26 "off writes nothing" ruling for that slot. No finding, no issue to close, no finder harness: the build is the owner's ruling.

**What changed** (only `pump_arbiter.py` in production; the off_restore hook is consumed as built, unedited).
- The space set-point is an off_restore consumer, key `pump_arbiter_space`: `Restorer(space_setpoint_entity, write_setpoint_c, baseline_of=read_setpoint, restored=_space_restored)`, the writer registered for rule R. Off and unload restore it through the hook's existing `async_mode_change` and `async_unload_entry` call sites: no second owner of either path.
- `_write` arms before every space write (`_held_back`, which also takes `_write`'s retry and read-only-mode guards, unchanged), so the baseline is on disk before the write is sent. `_arm_space` refuses a first capture whose reading equals the arbiter's own last write (`ArbiterState.written`, the existing persisted record; no second record), latched once per entity, and holds the write until the controller reads anything else.
- A person's edit between writes becomes the baseline (`_adopt` / `_edited`, read before `hold` rewrites it), bounded to the entity's own range and step (`_bounded`, the arbiter's existing clamp), so off writes back a value the entity takes. It is adopted only when the reading differs from the arbiter's write once `ECHO_GRACE_S` has passed, on the first miss, and differs from the reading when that write was sent (`ArbiterState.space_before`). `space_before` is unknown after a restart and reset while the power switch reads off, so the pump's own reset on power-up is never adopted. While active, the edit is still written over.
- A value set while the optimizer is off is captured at the next arm, because a successful restore disarms the key (hook behaviour).
- `release` (unload) writes the fallback row without the space set-point and saves the record; `_space_restored` drops the slot from the arbiter's record; the Off pass saves that drop.
- Docs: `docs/configuration.md` (Pump duty control) and the module docstring.

**Repair round 1** (dispatch at PR head `a57d1fe92223f8e53c908613eef5a494b9404d63`, continued, not re-cut). Built: the range bound at adoption (Carry 11), a check observing the write-ahead order (Carry 10), and checks killing the two sites `tests / mutation` refused (`_edited`'s `>= ECHO_GRACE_S`, `_restorer`'s no-entity guard). Mutants M17 to M20 added to the harness; M07 re-anchored on the rewritten `_adopt` line.

**The roster's carries, `Carry N` being roster index N-1 ( `origin/handoff/audit-r10-roster`, group R10-ARBITER-OFF-RESTORE, field `carry`).**
- Carry 1 (73eb63bd): met. The space set-point is a `register_consumer` consumer that arms before every space write; `off_restore.py` and `__init__.py` are unedited.
- Carry 2 (a94cb8b6) and Carry 3 (0a8663d2), entity keying: met. The baseline entry records its entity, so rule R restores a changed entity to its own value; `_space_restored` is the `restored` callback and drops the arbiter's own record on any restore of its key (M09 to M11).
- Carry 4 (8755bcb3) and Carry 14 (its repeat): met. Consumed as built through `register_consumer`, `Restorer(..., baseline_of=, restored=)`, `async_arm`, `async_armed_entry` and `async_rebaseline`; no class attribute named `state`.
- Carry 5 (76ae476a), Carry 6 (2bcac34a), Carry 15 and Carry 16 (their repeats): not this group's. The reserve rule binds a consumer that budgets writes; the arbiter has no per-day write cap (`_write` keeps no counter; `hold` retries every `RETRY_MINUTES`), so no restore write is reserved (`## Forward-carry`).
- Carry 7 (the 2026-11-10 stacking ruling): met. R10-GENERIC-HEAT-CURVE-PERSISTENT's pull request #3402 is merged to main (this branch's merge base), and origin/main was merged in at `a57d1fe92`, so this pull request carries only this group's diff. R10-WATER-SETPOINT-FEEDBACK has not landed (`git grep -c "_note_sent" origin/main -- custom_components/heatpump_optimizer/pump_arbiter.py` exits 1), so `ArbiterState.written` is the one write record and the own-write refusal reads it.
- Carry 8 (a070f930) and Carry 9 (its repeat), WSF's dropped space record: not met here, and not yet applicable: `_note_sent` and `ArbiterState.feedback` do not exist at this head (same `git grep`, exit 1 at `HEAD`). The precondition binds when this branch meets WSF's: `_arm_space` reads an absent space record as "no own write to refuse", which WSF's sub-`SETPOINT_TOLERANCE` drop would make wrong between `_note_sent` and `_write`. Restated to WSF as its precondition (`## Forward-carry`).
- Carry 10 (648c3c80) and Carry 12 (its repeat), write-ahead: built. The arm (which saves the baseline) precedes the send; the new check reads the off_restore store at the moment the space write's service call is made and finds the baseline `53.0` there, the store having held nothing before that pass. M18 (send, then arm) is killed by it and survived every other check. The arbiter's own write record (`held.written`) stays after the send, deliberately: a record lost to a crash between send and save leaves `space_before` unknown after the restart, so `_edited` adopts nothing, and the armed baseline already makes the own-write refusal moot.
- Carry 11 (5b825bae) and Carry 13 (its repeat), range bound at adoption: built. `_adopt` rebaselines to `_bounded(inp, "space_setpoint", edit)`. Control: `number.water_set` declares min 25, max 63; an edit reading 70 is restored as 63, and at the PR head it was restored as 70 (failing first, below); 40 is restored as read.

**Departure from the brief, for the reviewer.** The brief restores "on unload while Home Assistant is not stopping"; the hook as built restores on every unload, a stop included (`off_restore.py` module docstring, "Home Assistant stopping changes nothing"). A per-consumer stop rule would need an edit of the hook, which Carry 1 forbids ("never a second owner of the unload"), so this consumer follows the hook, and the docs say so.

## Head

`561edf4c8f9b99420013b48ce1d225645ef70b95` merges the authored code head `656cd9310c06a62e3862d277dc06edb72aecf7b8`.

`656cd9310c06a62e3862d277dc06edb72aecf7b8`, on merge base `45adb0c3b425dc44e72fd9ce4ef51f480b5a3af6` with origin/main at `d08ed31049cd3636cde4d2fdeb3bd7cd4b3c842a` (`2026-11-11T01:45Z`); `git merge-tree --write-tree origin/main HEAD` exits 0 there, so origin/main is not merged. Figures are this head's unless named.

## Mutation proof

Failing test first: the round's new checks, run with `pump_arbiter.py` from `a57d1fe92` over a `git archive` copy of the head, give `1 of 54 FEATURES BLOCK FAILED`, "R10-ARBITER-OFF-RESTORE: an edit outside the entity's own range is adopted bounded to it ..." with `_pa_between('70')=(1, [70])`; at the head, `ALL 54 FEATURES BLOCK PASSED`. The other three new checks pin behaviour the PR head already had (the write-ahead order, the grace's bound, the unconfigured restorer): they are the killers of M18, M19 and M20.

Twenty named mutants of the lines this group adds, each applied alone to a `git archive` copy and driven by the pump-duty arbiter block of `tests/features.py` (`dev/audit/harnesses/r10_arbiter_off_restore_mutants.py`, which holds the spec). NULL survives; every mutant is KILLED:
- M01 `register_consumer` deleted; M02 `_held_back` never arms; M03 the own-write refusal off; M04 the before-write comparison dropped; M05 the first-miss condition dropped; M06 power-off does not forget `space_before`; M07 no `async_rebaseline`; M08 release writes the space set-point; M09 `_space_restored` keeps the record; M10 release does not save; M11 the Off pass does not save on `space_before`; M12 no echo grace; M13 `_forget` keeps `space_before`; M14 the factory answers None; M15 `_adopt` skipped; M16 the written-value comparison dropped.
- This round: M17 the adoption unbounded (`baseline = edit`); M18 the space write sent before the arm; M19 the grace strict (`>` for `>=`); M20 `_restorer` without its no-entity guard.

## Null control

- With the arbiter not controlling (`pump_duty_mode` observe), off writes nothing and the hook sends 0 (`_pa_ro_null_sent == 0`, `writes() == []`).
- Range bound: 40, inside the range, is restored as read. Grace: a reading one second inside `ECHO_GRACE_S` is not adopted, and off restores 53. Write-ahead: the store holds no baseline before the pass (`_pa_wa_before is None`). Restorer: an install with the space set-point has one.
- Every pre-existing arbiter check passes unchanged, the "off writes nothing" ones included (they set `_mode` directly and never call the hook).

## Figures

At `656cd9310c06a62e3862d277dc06edb72aecf7b8` unless named.
- Arbiter block: `env PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py "R.section(\"pump-duty arbiter — mode and set-points per plan step" "_pa_subs = _PaCoord("`: `ALL 54 FEATURES BLOCK PASSED`; with `pump_arbiter.py` from `a57d1fe92`: `1 of 54 FEATURES BLOCK FAILED`.
- Mutants: `python3 dev/audit/harnesses/r10_arbiter_off_restore_mutants.py`: `SURVIVED NULL`, then `KILLED` for M01 to M20, exit 0 (taken at `ec5ee8d2b5`; later commits add ledger pins, a docstring and a docs sentence, no line a mutant names).
- Mutation table: `python3 tests/mutation_table.py --pin-killed --base origin/main`: `PIN KILLED: 4 pinned, 0 left unpinned` (`_edited` CMP_BOUND, `_adopt` GUARD_OFF twice, `_restorer` GUARD_OFF), after deleting the `_adopt` GUARD_OFF `010585c0` pin whose line this round rewrote (the table refused it: "disposition names no site the inventory generates").
- Scoped gate: `python3 tests/closure.py select --diff 45adb0c3b4 --workdir $D`: `MODE: SCOPED`; every script `scope.run` names, and `run.sh`'s `run_always` pair (`env_drift.py --claims-only`, `closure.py selftest`), run with `PYTHONPATH=tests/hastub GOLDEN_MODE=drift GOLDEN_REF=45adb0c3b4`: every one exits 0 (`tests/features.py`: `ALL 5199 FEATURE CHECKS PASSED`).
- Ratchet: `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`; no budget re-recorded.
- Score: `python3 tools/audit/archscore/score.py --diff 45adb0c3b4`: `IMPROVES` (`coord_footprint` down one); against `a57d1fe92`, this round alone: `NULL`.
- CI prediction: `python3 tools/pr/ci_predict.py --base origin/main`: `no closures, fast, governance or instrument red predicted against 45adb0c3b425`, and no unpinned site listed.
- Class seams (fixer.md step 8), one rule per carry built:
  - Range bound: every baseline move, `git grep -n "async_rebaseline(" -- custom_components/`: two sites. `pump_arbiter._adopt`: bounded in this diff. `heat_curve.write_persistent`: already bounded (`_within_range`, #3402). Capture is not a move: `baseline_of=` (`git grep -n "baseline_of=" -- custom_components/`) returns `heat_curve`'s and this group's `read_setpoint`, each the value the entity held before the first write.
  - Write-ahead: every arm, `git grep -n "off_restore.async_arm(" -- custom_components/`: three sites. `pump_arbiter._arm_space`: ordered ahead of the send and now observed (M18). `heat_curve.py` (the offset arm and `_write_persistent_target`): arm ahead of send in the code; their order's unobserved mutant is #3402's fix review R21, recorded there and carried here for the arbiter only, a distinct seam of a landed group.
  - The degC writes (the original rule): `git grep -n "write_setpoint_c(" custom_components/heatpump_optimizer/`: `pump_arbiter._write`, armed; `coordinator._valve_write_problem`, the valve, not this ruling's entity.

## Red checks

`merge_train.py owed-reds` lists `tests / mutation` among the required contexts; it is this PR's one red on a required check.
- `tests / mutation` (job 130227732011): "MUTATION TABLE REFUSED -- 2628 unpinned site(s) against 2627 at the ratchet base 45adb0c3b4, 2 of them added by this diff": `_edited`'s `>= ECHO_GRACE_S` CMP_BOUND and `_restorer`'s `if not entity` GUARD_OFF, both survivors of the `ci: pin killed mutants` run (`3aab9d804c`), so no autofix could pin them. Repaired here by checks that kill both (M19, M20), and pinned. Cheaper detector: prepr's mutation step (step 6d, `ci_predict.py`), which listed both sites before the first handoff; that body answered them as `mutation-autofix`'s to pin, wrongly for a survivor. The detector existed and fired; the answer misread a survivor as an unpinned kill. Standing cost of reading the difference before the handoff: one local `--pin-killed` run of this diff's sites (not timed in this round), against a CI round trip and a repair dispatch.

## Forward-carry

- R10-WATER-SETPOINT-FEEDBACK goes before this group on `pump_arbiter.py`. The arbiter's space write record is `ArbiterState.written["space_setpoint"]` plus `ArbiterState.space_before`, read by `_arm_space` (the own-write refusal) and `_edited` (edit adoption). Precondition for WSF: a record WSF adds for the space write extends these two fields rather than adding a second, and `_arm_space` must not read the space record's absence after `_note_sent`'s sub-tolerance drop as "no own write" without checking `ArbiterState.feedback`. Control: M03 and M04/M16 here go red if the record they read stops being written. Carry: R10-WATER-SETPOINT-FEEDBACK
- The reserve-rule carries (76ae476a, 2bcac34a) bind a consumer that budgets writes. The arbiter has no per-day write cap, so nothing here owes the restore a reserved write. Carry: dismissed: the arbiter budgets no writes
- Entity keying (a94cb8b6, 0a8663d2) is met by the hook's rule R plus `_space_restored`. Carry: dismissed: built here

## Friction

- brief-stop-restore: contradiction: the brief restores "on unload while Home Assistant is not stopping", while the hook it must reuse restores on every unload, a stop included. Built to the hook. Carry: dismissed: the departure is raised in the body for the reviewer; a stop-exempt restore would be a change to the hook, R10-GENERIC-HEAT-CURVE's seam
- wip-ref-diverged: cost: `handoff-wip/r10-arbiter-off-restore` held an earlier repair attempt (tip `f97f6cefd9`, 2026-11-10) that was never handed off and is not an ancestor of the PR head, so a fast-forward push of this round was refused. Each step went up as a commit with this round's tree whose parents are that tip and the step; the PR branch carries none of it, and its unit check of the grace bound is replaced by this round's end-to-end one. Carry: dismissed: the step ref is deleted at handoff

