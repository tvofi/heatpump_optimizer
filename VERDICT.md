Fix review: blocked dec7b91ea734b7b3ebcdfebe402f9aee553b1faf product-tradeoff-regression: the six sites this PR routes through log_held only ever pass active=True, so the latch never clears and a condition that recovers then recurs logs nothing above DEBUG for the owner's lifetime (hass for _age_gate and _space_target, so it survives an entry reload); measured recur=0 at the head against 2-4 at the base, and a planted one-line clear moves it to 1

bus-nonce: 141ac3cd62d36b4c99a1ea89e941a76d
Round: 4 or later (body re-cut minimal). Judged at head dec7b91ea734b7b3ebcdfebe402f9aee553b1faf only.
Head delta: dec7b91ea is the fixer's 72a6844ae plus main 082984f69. `git merge-tree --write-tree 72a6844ae 082984f69` returns tree f2f537771, which is the head's own tree. So the merge resolved nothing, and the head's work is exactly the fixer's code. merge-tree against current origin/main 017045fef: rc=0, no conflict.

## The blocking finding (attack 3: the user-visible signal)

`log_latch.log_held` is a transition latch. Its docstring promises WARNING when a condition starts, DEBUG while it holds and INFO when it clears. The PR's own test in tests/features.py pins "warns again on recurrence". None of the six sites this PR routes through the latch ever calls it with `active=False`: `_note_solve_failure`, the three `_command_valve_target` sites, `pump_arbiter._space_target` and `inputs._age_gate` (grep: every call passes a literal True). Each key is therefore set once and kept until its owner dies. For `_age_gate` and `_space_target` the owner is `hass`, which outlives a config-entry reload. The result is a once-per-process filter, not a transition latch. The base's `_FENCED_CAUSES` precedent says so in its own message ("first occurrence; repeats log at DEBUG"). These sites say nothing.

My harness, built by me and not the finder (dev/audit/rounds/round10/D14/log_flood/recurrence_review.py, a copy is in evidence/recurrence.py). Each arm has three phases, two passes each: hold the condition, clear it (a real successful `_async_update_data` cycle for the solve failure, a fresh stamp, a fixed entity minimum), then recur.
RESULT base future_stamp.hold=4 clear=0 recur=4
RESULT head future_stamp.hold=2 clear=0 recur=0
RESULT base solve_failure.hold=2 clear=0 recur=2
RESULT head solve_failure.hold=1 clear=0 recur=0
RESULT base space_target.hold=2 clear=0 recur=2
RESULT head space_target.hold=1 clear=0 recur=0
RESULT base future_stamp_after_reload.warnings=2   (a new coordinator on the same hass)
RESULT head future_stamp_after_reload.warnings=0
Null control: the clear phase reads 0 at both ends.
Perturbation: at the head I added one line, `log_held(self, "solve_failure", False)` beside the success path's `self._solve_failures = 0` (coordinator.py:5804). solve_failure recur went 0 -> 1, and the other arms were unchanged. So the harness moves, and the correct latch is a one-line call per site.
Compounding: `_note_solve_failure` also went from ERROR with `exc_info=True` to a WARNING with no traceback. The stale-plan hold was demoted to DEBUG on the grounds that the solve failure (plus EVENT_PLAN_STALE, which reaches nobody without an automation) carries the signal. So a second stale-plan episode with the same exception text puts no line at WARNING or above in the log.
Repair, which belongs to the fixer: give each site its clearing call where the condition ends. That is the shape the latch's pre-existing callers in this module already use, e.g. `log_held(self, "no_prices", not self._prices, ...)`. Sites: the success path for solve_failure, a successful valve command, a non-future reading per input, a non-misdeclared set-point. Restoring exc_info for the solve failure (at DEBUG on repeats if need be) is also owed, or the body must state the downgrade.

## The four attacks

1. Public `log_held` (step 14 and step 17). It is earned, not gamed. evidence/step14_plant.txt, measured with archscore layering and public_surface on package copies:
RESULT base private_cross_module=17 public_surface=625
RESULT head private_cross_module=17 public_surface=625
RESULT renamed-back(_log_held at head) private_cross_module=20 public_surface=625
Removing the mechanism restores the +3 (three importing modules), so the movement is the rename's. It is the sound shape. The leaf module has one owner and one function, that function is the module's whole API, and the leaf is what breaks the coordinator<-arbiter/reader import cycle. A private name imported by three modules is exactly the smell the metric names. The planted shape (rename any private to public) would move the metric with nothing improved, but only where it is applied to a real internal. Here it is not. That is an instrument property, not this diff's gaming. Not blocked on this.
2. Five re-keyed ledger rows. I re-killed every pin at the head with my own targeted mutants (evidence/mutants.txt; the tree was restored clean):
RESULT mutant_70f837e7 GUARD_OFF "if not active:" killed by tests/solar_alignment.py rc=1
RESULT mutant_80a0007e RETURN_DEL "return True" killed by tests/solar_alignment.py rc=1
RESULT mutant_96c9f042 RETURN_DEL "return False" killed by tests/solar_alignment.py rc=1
RESULT mutant_83745963 GUARD_OFF "if held.pop(...)" killed by tests/features.py rc=1 (#2226 latch check)
RESULT mutant_da0bf41e GUARD_OFF "if held.get(key) == text:" killed by tests/features.py rc=1 (#2226 checks)
Each killed_by holds at the new anchor. One row is stale: its `reason` still names the old pin SHA 0570b86e9. That is cosmetic.
3. Demotions. `optimize`'s manual-release WARNING is covered by EVENT_MANUAL_PLAN_RELEASED and the override's released_* fields: fine. `_optimize_space_only`'s ERROR returns "failed (...)", which the coordinator turns into a RuntimeError and then `_note_solve_failure`: fine, apart from the finding above. `_solve_space`: the first call's failure reaches the status. A failure in `_co_optimize`'s candidate pass does not, because its score equals best_score, so the first status stands. That makes the body's "surfaces once through _note_solve_failure" untrue for that path. It is a non-fatal improvement pass whose sibling except already logs at DEBUG, so I note it rather than block on it. Stale-plan hold: see the compounding above.
4. Class-open. The census enumeration rule (enumerate.py, the finder's): RESULT base sites=80 latched=6 seams=74; RESULT head sites=70 latched=6 seams=64. The set difference is exactly the ten OWED sites, plus coordinator._log_held -> log_latch.log_held. The 64 head seams equal `_R10_LOG_ALLOWED_BY_REASON` key for key and count for count: RESULT seams_not_on_list=0 list_not_in_census=0 (evidence/barrier_vs_census.txt). The rule is closed. It counts `_LOGGER.warning/error` calls only, so it cannot see a `log_held` call that never clears. The finding above sits in that blind spot of the instrument.

## Finder's harness, both ends (step 2, step 9)
The finder's probe (the base version of probe.py) has no arm for any of the ten sites. It is flat by design at both ends: RESULT base and head: all 8 arms floods=0, rc=0. The five DIRECT arms in the head's probe.py are the fixer's own: RESULT probe_head at base: solve_failure=1 stale_plan=2 valve_mistyped=1 space_target_misdeclared=1 future_stamp=2 floods, rc=1; at head: all 13 arms floods=0, rc=0. None of those arms has a clear-then-recur phase, so neither harness can see the finding. The optimizer's three sites have no runtime arm in either probe.

## Other steps
Step 5: VERSION, manifest, the RELEASE_NOTES heading and both claim files are untouched (empty three-dot diff). Step 7: the body's ## Head names dec7b91ea734b7b3ebcdfebe402f9aee553b1faf, which is what I measured. Step 10: forward-carry is none, and I found nothing in this review that needs carrying. Step 11, latest run per name at dec7b91ea734b7b3ebcdfebe402f9aee553b1faf (evidence/check-runs.head.tsv): 27 success, 15 skipped, 0 red. That covers fast (3.14), mutation, arch-score, closures, pr-contract, typing, coverage, budget-raise-gate and delivery-status. I read the mutation lane's log: scope changed, 5 production files, "MUTATION TABLE PASSED", null control log_latch.py:24 survived every driver. The body names the earlier-head reds (fast, delivery-status, pr-contract, arch-score, mutation) with their detectors. Not re-run: the gate and the mutation table.
Evidence: /Users/timmalmstrom/hpo-seats/r10s3/review-n-log-flood/evidence
