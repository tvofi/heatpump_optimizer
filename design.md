# Design note: the pump's own start condition, one optional input per duty (R10-OUTSIDE-DHW-START-HYSTERESIS)

Designer seat, design round 2, a re-cut of accd88e772f45e322e6d947b791c58c5b43b58a3 after verdict
8062b84b3754515bcac430e6048f06f4974d1dff (`Design review: revise accd88e7 architecture-unsound`). Base and
`origin/main`: 0e28afd38b353ca8e66269d9ae4be8614fcf5cfb; it carries pull request 3398. Predecessor
R10-OUTSIDE-DISINFECTION-SETPOINT is unmerged; read at pull request 3452's head
0aed6ccbc99c5a3210dcb1caf013ea0d7c5ceed5. Outside pull request 3440 read at cbbd14e006, as data. Line
citations are at the base unless they name 0aed6ccbc9. No finder harness: the evidence is the feature-triage
probe, re-run at the base (Figures). Sections 1 to 6 replace the first note; what the verdict found sound
(seam, sibling sites, plan-around, the reader, the notice's place) is kept and not re-argued.

## 0. The verdict, point by point

1. **Accepted.** Run membership is dropped. The step that holds the cycle target is the step the plan books as
   the disinfection step: `classify_dhw_steps` books it on `i == legionella_step` alone (`optimizer.py:1811`),
   and the predecessor's hot-water write holds the cycle temperature only on that booking or while
   `inp.disinfecting` (`pump_arbiter.py:1105-1106` at 0aed6ccbc9). Section 3 names ONE predicate for it, read
   by the booking and by the planner's judgement. The 54/60/4 test is rewritten to that owner's answer: kept
   when the run begins ON the cycle step (54 below 60 less 4), banned when it begins on a step before it (the
   arbiter writes 55 there; 54 is at or above 51). Whether the write should also cover the run-up is the
   predecessor's seam: **decision: orchestrator**, with the measurement in section 3.
2. **Accepted, and dissolved with 3.** Nothing is capped any more, so the run-up floor, the availability floor
   and the ready level reach the four stages exactly as at the base. Test in section 5.
3. **Accepted.** The capped array had no published field. The cap is withdrawn on numbers (fork 2), so
   `DhwPlan.ready_temps` and the requirement stored on the optimizer are unchanged; its two readers
   (`optimizer.py:4287`, `:4645-4650`) are listed in section 4 with what they now see.
4. **Accepted.** At lift equal to hysteresis the first note wrote the border itself. The space rule now writes
   strictly above it, by a named margin of 0.2 K, and `_bounded` rounds the floor UP (section 3).
5. **Accepted.** Section 6 names `design/R10-DUTY-SWITCH-PLANNER-PRICE` at 439d17c930 and the shared door.
- Routed decision P1 (owner): unchanged from the first note and from the verdict's reading; section 1.
- Routed decision on the ready level (owner): the first note lowered it; this note keeps it as an obligation
  met by a charge begun below the start temperature, because the spike measures the cap as costing more and
  delivering less (fork 2). The owner may still pick the cap; its numbers are there.
- The verdict's five notes for the fixer are carried as items 5 to 9 below, item 6 with its number.

## 1. What was read, and one premise that does not hold

- Hot water is placed inside `_build_dhw_requirements` (`dhw_planner.py:951`) by the seed
  `_plan_dhw_min_cost`, the greedy `_plan_dhw_cheapest_first`, `_apply_dhw_min_run`, the greedy again and
  `_repair_dhw_floor`; three of them take the per-step door `forced_off` (`:1125`, `:1135`, `:1161`,
  `:1196`). External-heat suppression, the pin overlay and the Off-window zeroing run after (`:1219-1280`).
  The requirement is `np.maximum(np.maximum(floor_temps, ready_temps), runup_temps)` (`:1056`); the ready
  level is derived, not set by the user: the minimum plus the window's expected draw and standby, clipped
  to the set-point (`:926-940`).
- **Premise P1 (decision: owner).** The brief has the plan's modulation floor read the effective lift. The
  plan has no reader of a lift: `git grep -n "configured_flow_min_lift_k\|FLOW_MIN_LIFT_K\|modulation_floor_flow_c" 0e28afd38b -- custom_components`
  prints `thermal_model.py`, `pump_arbiter.py`, `const.py` and `config_flow.py`. The plan's floor is the
  power `min_electrical_power`; no lift-to-power model exists and no finding measures one. Fork 3 is decided
  on what exists; a plan-side cost of the larger lift is a new finding.

## 2. Owning seam

One concern, the pump's start condition; its two rules are pure functions in `thermal_model.py`. Callers:
`dhw_planner.py` (placement), `pump_arbiter.py` (space write, ledger), `setpoint_check.py` (notice),
`coordinator.py` (the one read). `inputs.py` owns the reader. The cycle-step predicate is owned by
`dhw_planner.py`, which owns `legionella_step`. `tests/seam_map.json` maps coordinator methods only.

## 3. Shape, and the four forks decided

**Inputs (fork 4), unchanged.** Two optional entity options, one per duty (the author's keys). `inputs.py`
gains ONE pure reader of a temperature difference: K and degrees Celsius as they stand, Fahrenheit times
5/9, non-finite or outside 0 to 20 K is no reading; never `normalize_temperature_c`. The coordinator reads
both once per cycle; the hot-water value travels on the thermal state to the planner, both on the arbiter's
inputs; the arbiter reads no entity for it. A reading of 0 or less is no reading at both owners. The option
always holds a DIFFERENCE: an install with only the absolute border (Luxtronik input 10107) points it at a
template sensor of return target minus border, given in `docs/configuration.md`. Part 3 of
R10-WATER-SETPOINT-FEEDBACK builds inputs 10104 and 10103 only.

**The cycle-step predicate (verdict point 1).** One module function in `dhw_planner.py`: given the plan's
`legionella_step` and a step, whether that step holds the cycle target. Today its body is the equality
`classify_dhw_steps` writes inline. Two readers: `classify_dhw_steps` calls it where it books
`REASON_LEGIONELLA` (`optimizer.py:1811`, one line; `optimizer.py` already imports from `dhw_planner.py`),
and that booking is what the predecessor's write reads; the planner's judge calls it to build the per-step
target, cycle temperature where it holds and the everyday set-point elsewhere. The planner thereby reads the
arbiter's own input and derives nothing. `optimizer.py` is not in the roster's file list: **decision:
orchestrator** (add it, one line, or accept the equality twice under a test that the two sets are equal on
every solve of the harness). Two limits, stated: the arbiter quantises and clamps its write to the entity's
range (`_bounded`), which the pure planner cannot read, so on an entity whose maximum is below the cycle
temperature the planner's start temperature is the higher one and the ledger, which uses the written value,
says so; and `inp.disinfecting` is a live state that only bears on step 0, which is never judged.
*Run-up, the predecessor's seam.* The planner raises the ceiling above the everyday limit on run-up steps
(`dhw_planner.py:673-674`) while the arbiter writes the everyday set-point there. On the cycle arm of the 18
solves 6 plans carry one run-up step powered above the everyday set-point, the tank entering the cycle step
at 55.3 to 55.4 against a write of 55; all 18 cycle runs begin at step 0 and reach 60.0 with and without a
hysteresis, and judging the run-up against the cycle temperature instead changes no number there. So this
group needs no widening; if the orchestrator widens the write, it changes the predicate's body and both
readers follow.

**Hot water: plan around, not actuate (fork 1).** Rule owner in `thermal_model.py`: start temperature is
target less hysteresis, none without a positive hysteresis. Judge, a pure module function in
`dhw_planner.py`: one forward sweep over a schedule and its simulated tank; every run that begins after step
0 on a tank at or above its step's start temperature (equal does not start) is banned from its first step to
the last step before the idle tank falls below the start temperature of the step it is on, and the sweep
continues on the schedule without those steps. `_build_dhw_requirements` wraps seed to external-heat
suppression in a loop: place, judge, OR the bans into a copy of `forced_off`, place again, until the judge
returns nothing. The judge reads the schedule after suppression and the capacity clamps, so a run they
split is seen. Pins and the Off-window zeroing stay after the loop. Step 0 is never judged.
*Why not the author's post-pass, or a gate inside the greedy only:* as the first note, uncontested.
*Three loop bodies were measured at 4 K* (Figures): the sweep above, 95 rounds, 22 at worst in one build,
cost plus 1.08 percent; the same with the seed retained after round 1, 91 rounds, 20 at worst, plus 1.71
percent, so the first note's refusal line is withdrawn; a wider ban (every idle step at or above its start
temperature), 33 rounds, 2 at worst, plus 2.19 percent. Decided: the sweep, because plan cost outranks
build time here (D0); **refusal line:** more than 6 rounds in a build switches that build to the wider ban,
which from a fresh build ends within 2 on these solves (the switch itself is unmeasured), and the fixer reports rounds and build time against the base (D9).
*Actuation, decided against:* the first note's numbers stand (writes of 55.2 to 58.9 against a charge limit
of 55, a disinfection run not actuable at all, `_bounded` restoring the unstartable run silently).

**Feasibility (fork 2), re-cut: no cap.** At 4 K, capping the ready level at the start temperature against
keeping it: cost 121.53 against 121.43; ready steps more than 0.5 K under the base's level 28 against 23
(base 13); worst such gap 4.00 against 2.34 K (base 1.04); rounds 50 against 95. At 2 K and 6 K the order is
the same except cost at 2 K (120.69 against 120.93). The cap buys rounds and nothing else, and lowers a level
the tank often still reaches by a charge begun below the start temperature. What holds in every arm: no step
of the 18 solves falls more than 0.05 K under the availability floor. So the plan keeps its requirement,
the published ready level and trajectory stay truthful (the trajectory shows the lower tank), and the floor
is held by charges inside the window, which start because the tank is then below the start temperature.
The notice is unchanged from the first note: `setpoint_check.py`, one more check called from `_evaluate`
through `ConfigNotices`, raised when `dhw_min_temp` sits above the everyday set-point less the hysteresis,
naming both numbers and the three remedies. `docs/configuration.md` states that a ready level above the
start temperature is met only when a charge is already running.

**Space heating (fork 3).** One pure owner beside `configured_flow_min_lift_k`: the effective lift is the
configured lift, or the hysteresis plus a start margin where that is larger; with no positive hysteresis it
is the configured lift, bit for bit. The margin is a named constant of 0.2 K, the size
`FEEDBACK_STOP_MARGIN_K` already uses to clear a controller border in the same loop (`pump_arbiter.py:278`).
`_flow_target` passes the effective lift to `modulation_floor_flow_c`; it already hands `_bounded` the
floor as `lo`, which rounds UP onto the entity's step (`pump_arbiter.py:547-574`, `:855-865` at
0aed6ccbc9), so the write is at least inlet plus hysteresis plus 0.2 K and never the border. No report shows
whether equality starts on the author's controller; the margin makes the answer not matter. Per P1 the plan
has no second reader. The over-command of a larger lift is bounded by `FEEDBACK_START_HOLD` only where
`_feedback_on` holds (power-feedback option on, a meter, duty space); elsewhere it is a limitation recorded
in `docs/configuration.md`. `_full_draw_c` is out of scope.

**Ledger (kept).** `_observe` records on the row the start temperature of what the hot-water write returned
for that step, less the hysteresis; `_verdict` returns a distinct not-startable verdict for a planned
hot-water step left idle on a tank at or above it.

```
entity -> inputs (difference reader) -> coordinator --hot water--> thermal state -> dhw_planner loop + judge
                                                   \--both------> arbiter inputs -> _flow_target, _observe
dhw_planner: cycle-step predicate  <- classify_dhw_steps (books the reason the arbiter's write reads), judge
thermal_model: start temperature(target, h); effective lift(config, h)  <- planner, arbiter, setpoint_check
```
Invariants: unset or 0 changes no plan, write or verdict; the schedule the loop hands to the pin overlay has
no run after step 0 beginning at or above its start temperature; the requirement, the ready level and the
run-up are byte-identical to the base's with any hysteresis; the caller's `forced_off` is never mutated.

## 4. Sibling sites

`git grep -n "forced_off" -- custom_components/heatpump_optimizer/dhw_planner.py` (every stage that obeys
the ban). `git grep -n "_build_dhw_requirements(" -- custom_components/heatpump_optimizer/` (three callers,
`optimizer.py:1454`, `:3316`, `:5144`; the loop is inside). `git grep -n "_dhw_requirement" --
custom_components/heatpump_optimizer/optimizer.py`: two readers of the unchanged requirement. `:4287` is the
blocked-mode shortfall figure, untouched. `:4645-4654` releases a force-off pin before any step more than
0.5 K short; such steps rise from 13 to 23 at 4 K, so a ban-caused shortfall can release a user's pin. It
stays as it is (the freed step is offered to the stages, and the pin could be the cause); the fixer pins the
behaviour with a test. `git grep -n "legionella_step" -- custom_components/heatpump_optimizer/optimizer.py`
(the booking, the predicate's other reader). The lift grep of section 1.

## 5. Evidence plan, by file

- Failing first, `dev/audit/harnesses/` (new file, the probe as `--count`): runs after step 0 beginning at
  or above their start temperature, for h of 2, 4, 6, on the 18 solves; and on the cycle arm.
- Null control, same harness `--null`: option unset, and h of 0, against a detached worktree of the merge
  base on the same machine: schedules and tank trajectory of the 18 solves and of the cycle arm, the
  `desired` commands over the step rows of `tests/block_duty.py`, each ledger `_verdict`, byte for byte.
- `tests/block_duty.py`: the reader; the floor write at lift equal to hysteresis (inlet 30.0, both 2 K,
  step 0.5: 32.5, never 32.0) and at configured lift 5 with hysteresis 2 (unchanged); the feedback base
  equals the floor write; the not-startable verdict; equality does not start.
- `tests/features.py`: the rewritten 54/60/4 pair of point 1; the predicate's two readers agree on every
  solve; with a hysteresis and a cycle due the requirement returned equals the base's byte for byte and the
  tank reaches the cycle temperature at the cycle step wherever the base's does (point 2); no step more than
  0.05 K under the availability floor; a force-off pin fixture for `:4645`; rounds per build recorded.
- `setpoint_check.py` notice: raised at minimum 52, set-point 55, h 4; clear at minimum 51.
- Goldens: `tests/golden/config_flow.json` gains the two keys and is CLAIMED in
  `tests/golden/claimed_drift.txt`. Three translations, `strings.json`, the card's two labels, and the
  derived counts in `dev/audit/rounds/round3/D5/option_doc_coverage.py`.
- Mutants to kill: M1 the judge's comparison weakened or removed; M2 step 0 judged; M3 the predicate
  returning false (the cycle step judged against the everyday set-point); M4 the effective lift returning
  the configured lift, or the smaller; M5 the 5/9 dropped, or the affine conversion used; M6 the
  not-startable branch removed; M7 the notice comparison inverted; M8 the start margin dropped; M9 a reading
  of 0 treated as a reading; M10 the judge reading the schedule before suppression. **Null mutant that must
  survive:** each of M1 to M4, M6, M8 and M10 applied while `--null` runs.

## 6. Hot files, serial position, carries

After R10-OUTSIDE-DISINFECTION-SETPOINT (`pump_arbiter.py`, `thermal_model.py`, `setpoint_check.py`,
`tests/block_duty.py`); revalidate at its merge against section 3's reading of its write. Serial with
`design/R10-DUTY-SWITCH-PLANNER-PRICE` (439d17c930, its paragraph "The ban's channel") on `dhw_planner.py`:
that design adds a placement-ban keyword OR'd into the local `forced_off` after `dhw_planner.py:1089`. One
door, two callers: its ban is in `forced_off` before this loop starts, the loop ORs its own bans into a copy
on top, inside each candidate build, and neither removes the other's. Either order works and the second
rebases; **decision: orchestrator**. Beside part 3 of R10-WATER-SETPOINT-FEEDBACK (`config_flow.py`,
`const.py`, translations: the second reuses the first's option plumbing).

## Figures

Enumerator: the spike of the Appendix, `PYTHONPATH=tests/hastub python3 spike2.py` at the base, 18 solves
(price winter_typical and flat; weather winter_cold, winter_mild, summer_warm; tank 45, 50, 53; set-point 55).
Base: 114 runs after step 0, 53, 64 and 65 unstartable at 2, 4 and 6 K (the triage probe prints 54 at 2 K; it
rounds the tank to 0.1 K before comparing, this spike does not), 97.28 kWh, cost 120.13. Per arm (h; body): cost, ready steps over 0.5 K under
the base level, worst such gap, rounds total and worst per build; unstartable runs are 0 in every arm.
2 sweep 120.93, 10, 0.59, 51, 3. 2 cap 120.69, 25, 2.00, 15, 1. 4 sweep 121.43, 23, 2.34, 95, 22. 4 cap
121.53, 28, 4.00, 50, 19. 4 retained seed 122.19, 23, 2.34, 91, 20. 4 wide ban 122.76, 25, 2.34, 33, 2.
6 sweep 126.96, 21, 2.34, 112, 23. 6 cap 127.22, 26, 6.00, 52, 21. 6 wide ban 128.87, 27, 2.34, 34, 2.
Steps over 0.05 K under the floor: 0 everywhere. Final-plan shortfall steps lying on a banned step that the
final trajectory finds startable: 0 everywhere (item 6). Cycle arm (disinfection on, 30 days since the last):
base cost 119.06, 18 unstartable; at 4 K 119.71, 0, 43 rounds, 3 at worst, the same figures with the run-up judged against
the cycle temperature; cycle step at step 0, 1 or 2, every cycle run beginning at step 0 and ending at 60.0.
These are estimates of the design from a monkey-patched planner, not of the fix.

## Notes for the fixer

- `Carry: R10-OUTSIDE-DHW-START-HYSTERESIS (item 1)` - the structure ratchet is paid by the loop reusing
  `forced_off`, never by rewrapping comments; ask before the push if a budget cannot be met.
- `Carry: R10-OUTSIDE-DHW-START-HYSTERESIS (item 2)` - `_dhw_shortfall` tolerates 0.05 K and the base shows
  up to 1.04 K against the requirement on these solves; compare against the base, not zero.
- `Carry: R10-OUTSIDE-DHW-START-HYSTERESIS (item 3)` - OR the ban into `forced_off` after
  `dhw_planner.py:1089`, never into `off_steps`, which `_legionella_off_mask` reads for its meaning.
- `Carry: R10-OUTSIDE-DHW-START-HYSTERESIS (item 4)` - keep the author's commit as the base of the option
  plumbing, tests and translations, with authorship.
- `Carry: R10-OUTSIDE-DHW-START-HYSTERESIS (item 5)` - assert the no-unstartable-run invariant on the
  schedule `_build_dhw_requirements` returns, pins excepted (the judge already reads past suppression).
- `Carry: R10-OUTSIDE-DHW-START-HYSTERESIS (item 6)` - bans only grow: test that no floor shortfall of the
  final plan lies on a banned step the final trajectory finds startable; the spike counts 0 in every arm.
- `Carry: R10-OUTSIDE-DHW-START-HYSTERESIS (item 7)` - word the over-command limitation by `_feedback_on`'s
  condition (option on, a meter, duty space), not "a metered install".
- `Carry: R10-OUTSIDE-DHW-START-HYSTERESIS (item 8)` - a new field on the thermal state and two card labels
  can move `tests/golden/coord_*.json` and the card goldens; claim them and show the null control on them.
- `Carry: R10-OUTSIDE-DHW-START-HYSTERESIS (item 9)` - re-anchor every line citation at the merge base.
- `Carry: R10-WATER-SETPOINT-FEEDBACK (item 7)` - input 10107 is served by this group's space option through
  a template difference; part 3 adds no start option and no reader for an absolute border.
- `Carry: R10-OUTSIDE-DISINFECTION-SETPOINT (item 10)` - the plan charges run-up steps above the everyday
  set-point (55.3 to 55.4 on 6 of 18 cycle solves) while the write there is the everyday set-point; whether
  the write covers the run-up is that group's and the orchestrator's decision, and this design follows it.

## Appendix: the spike (scratch, never merges)

The probe's solve with `DhwPlanner` monkey-patched: the three `forced_off` stages OR in a per-build ban;
`_build_dhw_requirements` loops, judging the returned schedule by the sweep of section 3 (per-step target
from `legionella_step`), cap 60 rounds; variants cap `ready_temps` in `_dhw_window_floors`' return, return
the previous schedule less its bans as the seed, or widen the ban. It judges the returned schedule, pins and
suppression absent on these solves. h of 0 runs 0 rounds with totals identical to the base.
