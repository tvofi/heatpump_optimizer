Fix review: blocked de9a409ecb00c7ed7b63ea9fa24399b1958de255 actuator-release: a smart_write valve on a climate that reads no target is never written, released only by a person, with no owner acceptance and no release check
bus-nonce: 20805fc827df1aee8a4f2af42e4cfc12

Round 1 (first review, full scope), from a detached worktree at de9a409ecb00c7ed7b63ea9fa24399b1958de255 (ci: merge main over 51181432cf, the body's 039d0bf832 plus a pin commit). Base: merge base e83a2c919f. I ran the finder's harnesses from git archive 0a7ea717c6, the same sha1s as the body: m6_restore d4618082, m5_holds 4ac4d570, cells 407d2f87, off_restore_race bb009fa9.

Blocking item (step 16, a new refusal on an actuator write with no release that ends it unattended):
The registry now refuses a smart_write valve write when it cannot capture the entity's baseline. That includes a climate valve whose state is "off" and which has no temperature attribute, a state tests/features.py itself treats as a valid install ("a degF climate that reports no target yet ... None while it is off"). I wrote a probe for this (it is not the finder's harness): ev/probe_valve_off_climate.py. It runs coord._command_valve_target() over five cycles with the climate off, then once more with a target readable.
RESULT valve_writes_while_climate_off_no_target=1 calls at base, 0 at head (5 cycles)
RESULT valve_writes_after_target_readable=0 at base (deduped), 1 at head
The write is skipped for as long as the climate reports no target. The optimizer never writes the climate's hvac mode, so only a person or another automation at the valve controller ends the refusal. The body lists this as a departure "pending owner confirmation". No owner acceptance is on the pull request (no comment, no review). No check drives the refusal's entry state to its release: the one changed check ("climate on degF, no target": ([], None)) pins the refusal only. The same holds for the frequency entity with no readable state: its release, the entity reading a number again, is natural, but no check drives it. Repair: either keep writing an entity whose baseline is unreadable (with a stated restore, e.g. none or a neutral) or get the owner's in-person acceptance on the PR. Either way, add a check that drives "no baseline" to the first write that lands.

Everything else I measured holds. These lines are also the re-take for the next round:
RESULT m6_restore base/head: unrestored_off 5/0, unload 4/0, remove 4/0, off_modbus 4/0, off_disinfecting 6/0, unload_disinfecting 5/0, remove_disinfecting 5/0, duty_change 7/7, duty_change_disinfecting 8/7; every restored_more_than_once_* 0/0; every null_unrestored_* 0/0
RESULT m5_holds base/head: writes_again_off_restore_failed_while_off 0/1, space_setpoint_final_while_off 25/45, heat_curve_offset_final_while_off 3/0, person_toggle_restores 1/0, null_restore_without_failure_later_writes 0/0, null_space_final 45/45
RESULT cells --no-gates base/head: baseline_switch_off 5/0, clause_switch 5/0, failing_rows 55/50, fail_cells 418/380, cells 532/532, unattributed_calls 0/0; NULL baseline-on FAIL [stale] rows 0/5 (number.hp_freq restore to 40, as the body discloses)
RESULT off_restore_race base/head: consequences 2/0; --serial 0/0
RESULT section (features_block, R11-SEAM-actuation-release up to the R10-HOTFIX-FLOW-SETPOINT-STUCK marker) at head: ALL 65 FEATURES BLOCK PASSED
RESULT d16-writes at head: the 8 write sites the body dispositions; none undispositioned (step 6, class closed)
RESULT VERSION/manifest/RELEASE_NOTES/tests/golden diff lines: 0
RESULT git merge-tree origin/main 51181432cf: exit 0 (LEDGER-MERGE resolved tests/structure_budgets.json and tests/closures.json); the live head is the bot's clean merge of main

Note: mutation-survivor: two reviewer mutants survive the section; CI's whole-file mutation lane may kill them elsewhere. (a) pump_arbiter._supply_restored without "held.supply, held.supply_held = None, False". (b) off_restore._restore_key "return done and release is not None" -> "return done", which counts an unwritten disarm as a landed restore in held.restores and last_restore. Evidence: ev/mutant_*.out.
Note: owner-decision: the stale-plan release of frequency, valve and space pump is decision: owner in the design note. cells' baseline-on null arm reads FAIL [stale] on the frequency restore at the head. That turns on the owner's ruling, not on this review.
Note: carry-missing: the two R11-SEAM-actuation-writes items (design invariant 2; the GCHV night registers armed under ROW and never written back) and the R11-SEAM-kernel-step re-run are routed in the body only, not landed on those groups' briefs. Carry: dismissed: evidence, not a finding (the routing is the orchestrator's, named in the body)
Note: ci: at this head classify read WAIT (gate pending; 66 runs queued repo-wide), and dispatch waited for instrument-self-tests. No red was read at this head. A blocked verdict is not refused at WAIT (C8 binds merge only).
