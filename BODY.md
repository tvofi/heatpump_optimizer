R10-OUTSIDE-DISINFECTION-SETPOINT, built on outside pull request #3439 (Bankaifan, fork head f9a7bcb4ee; adopted as feeb0b6b39 with the author kept and the tool trailers dropped by the ref_privacy.py guard's attribution classes). With Pump duty control writing the hot-water set-point, a disinfection cycle wrote the everyday set-point (stock pair 55/60: 55.0 on a booked and on a held step), so the pump's own thermostat ended the cycle below its target; and the set-point repair stood permanently against the arbiter's own 55, its Fix (60) rewritten to 55 at the next step.

The rule for a cycle's temperature now has one owner on `ThermalParameters`: `dhw_disinfection_temp` (the disinfection temperature where #3398's `legionella_cycle_active` holds, else `None`: the one cycle predicate) and `dhw_cycle_temp` (the higher of the everyday set-point and that). `dhw_hard_max_temp` and the repair's `_dhw_floor` read them instead of each restating the predicate and the max. The arbiter decides when (`_dhw_write`: the step's action books `dhw_reason` legionella, or `disinfecting` holds) and every row of `desired` that writes hot water takes that one answer; the cycle's target is rounded up onto the entity's step and bounded by its range (above the range is left to the guard's unreachable notice). `dhw_gated` is generalised from "the arbiter's gate, below the everyday set-point" to "the arbiter's own write, still as written": a record exists only while the arbiter controls the pump (`_forget` clears it when Control is left), so an install where the arbiter writes nothing keeps the repair unchanged.

Alternatives not taken: the contributor's private helper computing the max inside the arbiter (a third copy of the expression the ceiling and the floor already held); a special case in the repair for the cycle (the brief asks the existing exemption to generalise, and a special case would restate the arbiter's when-rule in a second module); folding the repair's floor onto `dhw_cycle_temp` (changes the repair on an install whose everyday set-point is above the disinfection temperature with the pump reading between them, which the null controls forbid).

The mutation table's one surviving site (`_dhw_write` CMP_BOUND, `cycle <= everyday` to `cycle < everyday`) was a defect, not an equivalent mutant: `dhw_cycle_temp` is already the max with the everyday set-point, so the comparison only routed a cycle whose temperature equals the everyday set-point to the nearest-step write, and with everyday 60.4, disinfection 60.2, entity step 1 the cycle wrote 60.0, below its own target (the guard's credit test the docstring names). `8da43a2f` drops the comparison: every cycle write rounds up. Alternatives not taken: a check pinning the old routing (it pins the defect); a `survivor_triage` verdict (the site was killable, `fixer.md` step 17); comparing the quantised values (a second rounding rule for one branch).

`dhw_target_temperature` (`optimizer.py` predictive_info, copied onto every step's action) is left the everyday set-point: it is published beside `dhw_min_temperature` as the configured target, no production code reads it to act (`git grep -n dhw_target_temperature -- custom_components`: the optimizer's two writes, the sensor attribute, the payload type), and a cycle step already says so through its `dhw_reason` legionella; moving it would move every golden fixture that records it for a label change.

The space-only gate row (`DHW_GATE_C`) stays a gate on a step the plan booked for a cycle only when a block removed hot water from it; a held cycle turns a space step into Heating + DHW, whose write is the cycle's temperature (pinned).

## Head

cb7f294a9499b2bd4668f1ccf006943feb11d26a, on the PR head d2ab2743 (two commits: `8da43a2f` the fix above, `cb7f294a` the ledger pins); merge base cbd23f1c8b; origin/main's tip ee64358be7 at 2026-11-11T11:28:55Z (`date -u`), `git merge-tree --write-tree origin/main HEAD` clean. `python3 tools/audit/seat/review_carry.py 49a45dd8a8aad27f63b797bc747e79d9246e439a cb7f294a` answers FRESH-REVIEW: `8da43a2f` changes production code, so the merge verdict at 49a45dd8 does not carry.

## Merge resolution (delta from 1713468b)

`git merge origin/main` at 1713468b conflicted in three files against #3398 (R10-COMBI-TANK-PR-B), which replaced the readers' `dhw_legionella_enabled` with `ThermalParameters.legionella_cycle_active` (enabled, and not an active combi store at or under `COMBI_LEGIONELLA_POTABLE_LIMIT_L` unless forced). Each hunk keeps both behaviours:

- `thermal_model.py` `dhw_hard_max_temp`: this group's form (`min(70.0, dhw_setpoint if dhw_cycle_temp is None else dhw_cycle_temp)`), and `dhw_disinfection_temp` now reads `legionella_cycle_active` where it read `dhw_legionella_enabled`. Main's `if self.legionella_cycle_active: top = max(top, dhw_legionella_temp)` is that expression through the owner, so main's ceiling is unchanged and #3398's gating now reaches the arbiter's write and the repair too.
- `setpoint_check.py` `_dhw_floor`: this group's form (`max(floor, dhw_disinfection_temp)` where not `None`), equal to main's `legionella_cycle_active` branch through the same owner.
- `tests/features.py`, three fakes (`_p8_setpoint`, `_pa_mbs._thermal_params`, the `_df_sc.evaluate` space-slot check): this group's real `ThermalParameters` (`_r9f12_tp`), from which `legionella_cycle_active` derives (combi off by default, so equal to the flag); main's namespace fakes carried `legionella_cycle_active` by hand and no `dhw_disinfection_temp`.

Commits after the merge: `b8736ad3` adds a `tests/block_duty.py` check on an active combi store holding 2 L (forced and unforced, over the three cycle bookings), retargets M7's anchor to the merged line and adds M10; `1aa850c2` records `class_excess_loc` down (main's own reduction under this branch's recorded budget); `49a45dd8` deletes #3398's two `killed_by` pins on the rewritten lines (`_dhw_floor` GUARD_OFF ea9e613f, `dhw_hard_max_temp` GUARD_OFF f3c560aa), which `ci_predict.py` named STALE PIN.

## Mutation proof

`python3 tools/audit/seat/r10_disinfection_setpoint_mutants.py` (this PR): each mutant applied to a detached worktree of HEAD, `tests/block_duty.py` run there, worktree removed; exit 0 only when NULL survives and every other mutant is killed. Exit 0 at cb7f294a; killed:

- `NULL` (no change): survives, 63 of 63 checks pass.
- `M1-no-cycle-write` (`_dhw_write`: `cycle = None`): killed by "a commanded or held disinfection cycle writes its temperature, not the configured set-point" and five more.
- `M2-round-nearest` (`_dhw_write`: drop `rounding="up"`): killed by "an off-step disinfection temperature is written on the step above it, never below".
- `M3-booking-ignored` (`_dhw_write`: `if inp.disinfecting`): killed by "a commanded or held disinfection cycle writes its temperature, not the configured set-point", "every row a cycle step can take writes the cycle's temperature, the idle and baseline rows too".
- `M4-hold-ignored` (`_dhw_write`: `if booked`): killed by "a commanded or held disinfection cycle writes its temperature, not the configured set-point" and four more.
- `M5-gate-only-excuse` (`dhw_gated`: restore `and written[0] < configured - SETPOINT_TOLERANCE`): killed by "the arbiter's own everyday write raises no disinfection-floor repair: it writes the cycle itself".
- `M6-excuse-any-reading` (`dhw_gated`: drop the `_differs` term): killed by "a person's value beside the arbiter's write still raises the repair, its Fix on the floor".
- `M11-everyday-cycle-nearest` (`_dhw_write`: restore `or cycle <= float(inp.params.dhw_setpoint)`, the surviving CMP_BOUND site's predicate): killed by "a cycle whose temperature is an off-step everyday set-point is rounded up too, never below the disinfection temperature; the same install's everyday step keeps the nearest step"; that check failed at d2ab2743 (1 of 63) and passes at cb7f294a.
- `M7-flag-ignored` (`dhw_disinfection_temp`: ignore `legionella_cycle_active`): killed by "null control: a disabled cycle writes the everyday set-point on every row and booking".
- `M10-enabled-not-active` (`dhw_disinfection_temp`: the merge's resolution reverted to `dhw_legionella_enabled`): killed by "a combi store at or under the potable limit runs no cycle: a booked or held step writes the everyday set-point, unless the cycle is forced (#3398's predicate, read through the cycle's owner)".
- `M8-cycle-not-max` (`dhw_cycle_temp`: `return target`): killed by "a cycle never lowers the tank: an everyday set-point above the disinfection temperature is the cycle's and the ceiling's" (it survived the first cut: the arbiter's own everyday branch masked it; that check was added for it).
- `M9-floor-no-disinfection` (`_dhw_floor`: `return floor`): killed by "a person's value beside the arbiter's write still raises the repair, its Fix on the floor", "null control: with no arbiter write the pump's own set-point must still permit the cycle".

Failing first at main: `tests/block_duty.py` at the head copied over an origin/main cbd23f1c worktree fails 9 of 62 checks (at 49a45dd8's copy), both faces among them: "a commanded or held disinfection cycle writes its temperature, not the configured set-point" (the write) and "the arbiter's own everyday write raises no disinfection-floor repair: it writes the cycle itself" (the standing repair); every null-control check passes there.

## Null control

`dev/audit/harnesses/r10_disinfection_setpoint.py` (this PR) drives the production `desired` and `setpoint_check._dhw` over 5 rows x 4 bookings for six installs and prints one line each; run at origin/main ee64358be (the file copied over a main worktree; sha1 276cb8cf1d68e145cb169db474825d317319d5e0) and at cb7f294a, then `diff <(grep '^null_' base) <(grep '^null_' head) && echo IDENTICAL` printed IDENTICAL over the 80 `null_*` lines: the cycle disabled, an everyday set-point at (60) and above (62) the disinfection temperature, and no hot-water set-point entity. Had the fix leaked into them the diff would print those lines. The 40 `stock`/`offstep` lines differ (36 lines changed): the defect's install, which is the fix. Each null control is also a check in `tests/block_duty.py` (four `null control:` checks), passing at main and at the head.

The `repair_none` column is the repair on an install whose arbiter has written nothing: unchanged on every non-cycle line (`stock none * repair_none=60` at both ends).

Precondition of the generalised exemption, stated rather than assumed: an arbiter writing an everyday set-point below `dhw_min_temp` would now be excused where main raised the repair; the options form refuses that pair (`config_flow.py` `_dhw_min_too_close`, minimum within 5 °C of the set-point), and the null-control installs carry `dhw_min_temp` 40.

## Figures

Taken at cb7f294a against merge base cbd23f1c (origin/main ee64358be at 2026-11-11T11:28:55Z).

- Scoped gate: `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: SCOPED -- 28 script(s) run, 5 scoped out`; `GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh` ran them: `1 TEST SCRIPT(S) FAILED`, `tests/features.py` alone, 1 of 5237, the combi_type_branch census inherited from origin/main (`## Red checks`); every other script green, `tests/golden.py` with no fixture failed or claimed. `tests/block_duty.py` 63 of 63. `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: `Architecture score: dS +0.0023 IMPROVES` (`coord_footprint 2496 -> 2492`).
- Mutants: `python3 tools/audit/seat/r10_disinfection_setpoint_mutants.py` exit 0, 11 named mutants killed, NULL survived (`## Mutation proof`). Pins: `## Unpinned sites`.
- Harness: `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_disinfection_setpoint.py` (sha1 276cb8cf1d68e145cb169db474825d317319d5e0) at origin/main ee64358be and at cb7f294a: `diff <(grep '^null_' base) <(grep '^null_' head) && echo IDENTICAL` printed IDENTICAL over 80 `null_*` lines (`grep -c '^null_'`); 36 of the 40 `stock`/`offstep` lines changed (`diff ... | grep -c '^>'`). The harness's installs are on-step everyday set-points, so `8da43a2f` moves none of its lines; its own off-step case is the block_duty check under M11.
- Class seams (`fixer.md` step 8). Rule: `git grep -nE "\.dhw_legionella_enabled|\.legionella_cycle_active|\.dhw_legionella_temp" -- custom_components` (every reader of the cycle's predicate or temperature) and `git grep -n '"dhw_setpoint"' -- custom_components/heatpump_optimizer/pump_arbiter.py` (every hot-water write of the arbiter). Dispositions:
  - `thermal_model.py` `legionella_cycle_active` (#3398's predicate) and `dhw_disinfection_temp`: the owner; this diff routes the predicate through it.
  - `pump_arbiter.py` `_dhw_write` (two `_bounded` calls): this diff; the gate row `DHW_GATE_C`: a gate by design, pinned on a cycle step; `dhw_gated`: this diff.
  - `dhw_planner.py` (legionella step placement on `legionella_cycle_active`, `ready_temps` max with the disinfection temperature): the plan's per-step requirement the cycle must meet, a floor below `dhw_cycle_temp` by construction; not the hold temperature. Already consistent.
  - `legionella.py` (the guard's credit target and watch flags, on `legionella_cycle_active`): the threshold a cycle must reach, at or below `dhw_cycle_temp` by construction; the arbiter rounds up so its write passes that test. Already consistent.
  - `coordinator.py` elastic-legionella deadline and the diagnostics echo (`dhw_legionella_cycle_active`): when a cycle is due and what is configured, not its temperature. Already consistent.


## Unpinned sites

None left: `python3 tests/mutation_table.py --pin-killed --base origin/main --scripts tests/block_duty.py,tests/guard_pins.py,tests/env_drift.py` at 8da43a2f printed `PIN KILLED: 10 pinned, 0 left unpinned` and `cb7f294a` commits the ten `killed_by` records. The 11th site (`_dhw_write` CMP_BOUND) no longer exists: its comparison was the defect above. The default driver set printed `MUTATION TABLE INCONCLUSIVE` locally and on CI's `mutation-pins (3)` at d2ab2743 (null control and baselines run first; `tests/features.py`'s baseline is red, origin/main's census below), so the drivers named are the three whose baselines pass (rc=0, failed=0) and whose closures reach the sites; the null control `pump_arbiter.py:194 NULL_COMMENT` survived each. Kills by `tests/guard_pins.py` (5) and `tests/block_duty.py` (5) per the run's `pinned` lines.

- pump_arbiter.py `_dhw_write` GUARD_OFF, RETURN_DEL; `dhw_gated` RETURN_DEL: pinned in this PR
- setpoint_check.py `_dhw_floor` CLAMP_DROP, RETURN_DEL: pinned in this PR
- thermal_model.py `dhw_hard_max_temp` CLAMP_DROP, RETURN_DEL; `dhw_disinfection_temp` RETURN_DEL; `dhw_cycle_temp` CLAMP_DROP, RETURN_DEL: pinned in this PR

## Red checks

At d2ab2743, each in `python3 tools/audit/seat/merge_train.py owed-reds`' set:

- `tests / mutation`: red, `MUTATION TABLE REFUSED -- 2633 unpinned site(s) against 2626 at the ratchet base cbd23f1c`, 11 added by this diff. Ten were killed and unpinned, one (`_dhw_write` CMP_BOUND) a true survivor, fixed above. The cheaper detector exists: `tools/pr/ci_predict.py` (prepr.sh step 6d) listed all 11 locally before the handoff at no standing cost beyond the prepr run every seat makes; the body then deferred them to `mutation-autofix`, which could not pin them (its baseline is INCONCLUSIVE on origin/main's red `tests/features.py`) and cannot triage a survivor. The miss was the seat's (the process existed; state (b)), not a missing detector: no further countermeasure. Repaired in `8da43a2f` and `cb7f294a`.
- `tests / fast (3.14)`: red on `tests/features.py`, 1 of 5237: "combi_type_branch census ... no product or vendor name in the package's Python" (vendor hits `const.py:812`, `const.py:1595`, `heat_curve.py:72`, `pump_arbiter.py:256`, `pump_arbiter.py:1015`, `thermal_model.py:1867`), inherited from origin/main since #3398, hotfix in flight; each hit is a `Luxtronik` comment present at main, none in this diff's hunks. No commit of this branch turned it red: no root-cause answer is this branch's.
- `gate`: red, `FAIL run(s) [43004573627] at this head are still being judged; their gate decides` — the edit-run deferral (that CI run queued at d2ab2743), not a failed test; no root-cause answer owed.

`tests / nightly-status` is red at d2ab2743 but outside the owed set: it grades `main` (`defect-root-cause.md`), not this branch.

## Forward-carry

none

## Friction

none
