# Design note: the pump's own start condition, one optional input per duty (R10-OUTSIDE-DHW-START-HYSTERESIS)

Designer seat, first design. Base and `origin/main`: a7628041dc02e298c5399003d4c0576391dd5c4e. Predecessor
R10-OUTSIDE-DISINFECTION-SETPOINT is unmerged; read at its work-in-progress head
bc7dc3b31647caba17af262dbcd49f4079332ada (branch handoff-wip/r10-outside-disinfection-setpoint). Outside pull
request 3440 read at cbbd14e006004a60cd74998098691d01ba567057 (one commit by Bankaifan), as data. Pull request
3398 (head 141f8af1b1a59840ec18522dd4e44ad321d4c397) is NOT in the base; its whole edit to `dhw_planner.py` is
one condition in `_dhw_legionella_due`, which nothing below relies on. No finder harness: the evidence is the
feature-triage probe, re-run here (Figures).

## 1. What was read, and one premise that does not hold

- Hot water is placed by four stages inside `_build_dhw_requirements` (`dhw_planner.py`): the linear seed
  `_plan_dhw_min_cost`, the greedy `_plan_dhw_cheapest_first`, `_apply_dhw_min_run`, then `_repair_dhw_floor`.
  All four already honour one per-step door, `forced_off` (merged by `_forced_off_with`), through which a quiet
  Off window's energy is re-bought elsewhere. No stage knows a start condition.
- The arbiter writes a mode and a hot-water set-point in `desired` (`pump_arbiter.py`); the predecessor routes
  every hot-water write through one new function there (its head names it the hot-water write) and puts the
  cycle's temperature on the thermal parameters (its head names it the cycle temperature property).
- **Premise P1, for the design reviewer.** The brief says the plan's modulation floor and the arbiter's write
  must both read the effective lift. At the base the plan has no reader of the lift:
  `git grep -n "configured_flow_min_lift_k\|FLOW_MIN_LIFT_K" -- custom_components/heatpump_optimizer/*.py`
  prints `thermal_model.py` (definitions) and `pump_arbiter.py` only. The plan's floor is the power
  `min_electrical_power`; the lift exists only where `_flow_target` maps the plan's lowest level to a
  set-point through `modulation_floor_flow_c` and `flow_setpoint_for_level`. No lift-to-power model exists in
  the tree and no finding measures one, so this note does not invent one. Fork 3 below is decided on what
  exists; if the owner meant a plan-side cost term, that is a new finding and a `revise`.

## 2. Owning seam

One concern, the pump's start condition, with its two rules owned in `thermal_model.py` (pure, no Home
Assistant import) and four callers: `dhw_planner.py` (placement), `pump_arbiter.py` (write and ledger),
`setpoint_check.py` (notice), `coordinator.py` (the one read, glue only). `inputs.py` owns the reader.
`tests/seam_map.json` maps coordinator methods only and has no entry to move.

## 3. Shape, and the four forks decided

**Inputs (fork 4).** Two optional entity options on the pump entity page, one per duty, named in prose here:
the hot-water start hysteresis entity and the space start hysteresis entity (the author's two keys are kept).
`inputs.py` gains ONE pure reader of a temperature difference beside `temperature_c`: kelvin and degrees
Celsius as they stand, Fahrenheit times 5/9, anything non-finite or outside 0 to 20 K reads as no reading. It
must not call `normalize_temperature_c`, which is affine and reads 2 K as minus 271. The coordinator reads both
once per cycle; the hot-water value travels on the thermal state to the planner (the author's field), both
travel on the arbiter's inputs. The arbiter does not read the entity itself (the author's second read path in
`pump_arbiter.py` is dropped: one read, values passed in). **A reading of 0 or less is no reading at the two
owners**, so 0 equals unset by rule, not by coincidence of the arithmetic.
*Border and setting, one option.* The option always holds a DIFFERENCE. An install with the hysteresis setting
points it at that number. An install with only the absolute border (Luxtronik input 10107, return target less
hysteresis) points it at a Home Assistant template sensor of return target minus border; `docs/configuration.md`
gives the template. Rejected: telling the two apart by magnitude (a border of 18 degrees while the target sits
at the gate would read as an 18 K hysteresis and write an 18 K lift), and a kind selector (a second option and a
second branch in the one reader, for a subtraction Home Assistant already does). Part 3 of
R10-WATER-SETPOINT-FEEDBACK therefore builds inputs 10104 and 10103 only.

**Hot water: plan around, not actuate (fork 1).** Rule owner, a pure function in `thermal_model.py`: the start
temperature is the target less the hysteresis, none without a positive hysteresis. The target is passed in by
the caller: the planner passes the cycle temperature on the steps of the run that carries the disinfection
step and the everyday set-point elsewhere; the arbiter passes what its hot-water write holds on that step. A
disinfection run is thereby judged against its own target, with no exemption.
Placement, in `dhw_planner.py`: a pure module function returns, for a plan and its simulated tank trajectory,
the steps of the FIRST run that begins after step 0 on a tank at or above its start temperature (the author's
edge: equal does not start), extended to the last step before the idle tank reaches the start temperature.
`_build_dhw_requirements` wraps stages seed-to-repair in a loop: place, ask that function, OR the steps into
`forced_off`, place again, until it returns nothing. Bans only grow, so it ends within the horizon's step
count. A run at step 0 is never judged (a charge that may be under way). The manual-pin overlay
(`_apply_dhw_pins`) stays after the loop: a user's force-on is the user's.
*Why not the author's post-pass:* it zeroes the run after `_repair_dhw_floor`, so nothing re-buys the energy.
*Why not a gate only inside the candidate tests of the greedy and the repair:* heat placed at step j raises
every later tank temperature, so a later run that was startable stops being so; a closing validation is needed
anyway, and the seed is a linear program that cannot carry the condition. The loop is that validation and uses
the door all four stages already obey.
*Actuation, decided against, with numbers.* The arbiter could write tank plus hysteresis so the pump starts.
By definition every unstartable run needs a write ABOVE the user's target; the 64 measured runs start at 51.2
to 54.9, so at 4 K the writes are 55.2 to 58.9 against a set-point and charge limit of 55 and a physical
ceiling (`dhw_hard_max_temp`) of 60; a disinfection run at 60 would need 64 and is not actuable at all. What
would bound the tank is only the arbiter's own next write: if it stops mid-run the pump charges to the written
value, up to the hysteresis above the target (4 K is 1.39 kWh of heat in the profile's 0.348 kWh/K tank), and
`_bounded` clamps a write to the entity's range, silently restoring the unstartable run on a pump whose
set-point tops out near 55. It also forces the 64 mostly single-step top-ups, 3.6 extra compressor starts a
day, that the pump's hysteresis exists to refuse. Plan-around costs, on the same 18 solves by the spike
(Appendix): unstartable runs 64 to 0, runs after step 0 from 114 to 85, planned hot-water energy 97.28 to 97.04
kWh, hot-water cost 120.13 to 121.43 (plus 1.1 percent), and the largest shortfall against the requirement
grows in 13 solves, at worst 1.04 to 2.34 K. That last number is fork 2.

**Feasibility (fork 2).** The spike's shortfall is a ready-level requirement above the start temperature: this
pump cannot top a tank up from 52.7 to a ready level near 55. So, with a hysteresis read: (a) the requirement
handed to the four stages is capped per step at that step's start temperature, which is the level this pump
can be made to hold; the plan (`DhwPlan`, and the card through it) then shows the capped level, not a promise it
breaks. Uncapped, the spike needed 264 re-plans over 18 solves, 26 at worst, most of them chasing those
unholdable levels. (b) `setpoint_check.py` gains one notice in `_evaluate`, through the existing
`ConfigNotices`: raised when `dhw_min_temp` sits above the everyday set-point less the hysteresis, naming both
numbers and the three remedies (lower the minimum, raise the set-point, lower the pump's hysteresis); not
fixable by a repair flow, cleared when the condition goes. The ready-level cap is not a notice (it holds for
every such install and nothing is wrong); the option's description in `docs/configuration.md` states it.

**Space heating (fork 3).** One pure owner in `thermal_model.py` beside `configured_flow_min_lift_k`: the
effective lift, the larger of the configured lift and a positive hysteresis. `_flow_target` passes it to
`modulation_floor_flow_c` in place of the configured lift, so the floor set-point, every level
`flow_setpoint_for_level` slides from it, and the feedback loop's open-loop base all come from one value. Per
P1 there is no second, plan-side reader to convert; the owner exists so that the first one built reads it.
What the plan books at the floor stays `min_electrical_power`; the over-command of a larger lift is bounded by
`FEEDBACK_START_HOLD` on a metered install, because `_feedback_bounds` does not read the lift and still admits
the planned power afterwards. Without a meter it is a recorded limitation in `docs/configuration.md`.
`_full_draw_c` reads the constant for the ceiling probe's headroom, not the floor: out of scope.

**Ledger (kept from the author).** `_observe` records the step's start temperature (the owner's value for what
the hot-water write holds) on the row; `_verdict` returns a distinct not-startable verdict for a planned
hot-water step left idle on a tank at or above it. After plan-around it fires only when the real tank is
warmer than the plan's.

```
entity -> inputs (difference reader) -> coordinator --hot water--> thermal state -> dhw_planner loop
                                                   \--both------> arbiter inputs -> _flow_target, _observe
thermal_model: start temperature(target, h); effective lift(config, h)   <- planner, arbiter, setpoint_check
```
Invariants: unset or 0 changes no plan, write or verdict; no run after step 0 begins at or above its start
temperature; the loop removes no energy it does not offer back to the stages; the arbiter remains the only
writer of the hot-water set-point and writes nothing new.

## 4. Sibling sites

`git grep -n "forced_off" -- custom_components/heatpump_optimizer/dhw_planner.py` (every stage that must obey
the ban; `_apply_dhw_pins` deliberately does not). `git grep -n '"dhw_setpoint"' --
custom_components/heatpump_optimizer/pump_arbiter.py` (every hot-water write; after the predecessor, one). The
lift grep in section 1. `git grep -n "_build_dhw_requirements(" -- custom_components/heatpump_optimizer/`
(every caller, all in `optimizer.py`; the loop is inside, so each is covered).

## 5. Evidence plan, by file

- Failing first, `dev/audit/harnesses/` (new file, the probe below as `--count`): on the 18 solves, runs after
  step 0 beginning at or above set-point less h, for h in 2, 4, 6; before the fix 54, 64, 65, after it 0.
- Null control, same harness `--null`: option unset, and h of 0, against a detached worktree of the merge
  base on the same machine (never stored floats: solver floats do not reproduce across BLAS builds): the
  hot-water and space power schedules and tank trajectory of the 18 solves, the `desired` commands over the
  step rows of `tests/block_duty.py`, and the `_verdict` of each ledger row, compared byte for byte.
- `tests/block_duty.py`: the reader (K, Fahrenheit, minus 271 refused, out of range); the floor write equals
  inlet plus the effective lift and the feedback base equals it (the brief's plan-prices-the-written-lift test,
  in the form P1 allows); the not-startable verdict; a disinfection run on a 54 degree tank with cycle 60 and
  h 4 kept, the same run judged against 55 would be banned; step 0 kept; equality does not start.
- `tests/features.py` or the planner's own script: after the loop no shortfall exceeds the capped requirement
  by more than the base's worst on the same solve; loop rounds per solve recorded. **Refusal line:** more than
  3 rounds of the full chain on any of the 18 solves with the cap in place means the fixer re-runs only the
  greedy-to-repair stages on the retained seed, and reports build time against the base (D9).
- `setpoint_check.py` notice: raised at minimum 52, set-point 55, h 4; clear at minimum 51.
- Goldens: `tests/golden/config_flow.json` gains the two keys and is CLAIMED in
  `tests/golden/claimed_drift.txt`, not re-recorded as the author did. Three translations, `strings.json`, the
  card's two labels, and the derived counts in `dev/audit/rounds/round3/D5/option_doc_coverage.py`.
- Mutants to kill: M1 the ban comparison weakened or removed; M2 step 0 judged; M3 the cycle run judged
  against the everyday set-point; M4 the effective lift returning the configured lift, or the smaller; M5 the
  reader's 5/9 dropped, or the affine conversion used; M6 the not-startable branch removed; M7 the notice
  comparison inverted; M8 the requirement cap removed; M9 a reading of 0 treated as a reading. **Null mutant
  that must survive:** each of M1 to M4, M6 and M8 applied while `--null` runs: the unset arm stays
  byte-identical, which shows the null control cannot be passed by the new code misbehaving quietly.

## 6. Hot files, serial position, carries

After R10-OUTSIDE-DISINFECTION-SETPOINT (`pump_arbiter.py`, `thermal_model.py`, `setpoint_check.py`,
`tests/block_duty.py`); beside pull request 3398 (`dhw_planner.py`, `const.py`, budgets) and part 3 of
R10-WATER-SETPOINT-FEEDBACK (`config_flow.py`, `const.py`, translations: whichever lands second reuses the
first's option plumbing). Assumed of the predecessor: one function in the arbiter answers what the hot-water
set-point holds on a step, and the thermal parameters own the cycle temperature. Revalidate at its merge.

## Figures

Enumerator: the PROBE of the dispatch brief (commit 321db848c9, `PROMPT.md`) restricted to price profiles
winter_typical and flat, run as `PYTHONPATH=tests/hastub python3 probe3440.py` at the base. Printed here:
114 runs not at step 0 carrying 86.34 kWh; 54 at or above set-point less 2 K (9.29 kWh), 64 less 4 K (12.60),
65 less 6 K (13.30); lowest tank over the 18 solves 41.99. The triage figures reproduce. The spike's numbers
(section 3) come from the Appendix loop and are estimates of the design, not of the fix: it re-runs the whole
solve per round and bans by an estimated sag.

## Notes for the fixer

- `Carry: R10-OUTSIDE-DHW-START-HYSTERESIS (item 1)` - the structure ratchet is paid by the loop reusing
  `forced_off`, never by rewrapping comments; ask before the push if a budget cannot be met.
- `Carry: R10-OUTSIDE-DHW-START-HYSTERESIS (item 2)` - `_dhw_shortfall` already tolerates 0.05 K and the base
  already shows up to 1.04 K against the requirement on these solves; compare against the base, not zero.
- `Carry: R10-OUTSIDE-DHW-START-HYSTERESIS (item 3)` - a not-None `off_steps` changes the disinfection
  placement's reading of the Off window (`_legionella_off_mask`); OR the ban into `forced_off` after that
  point, never into `off_steps`.
- `Carry: R10-WATER-SETPOINT-FEEDBACK (item 7)` - input 10107 is served by this group's space option through a
  template difference; part 3 adds no start option and no reader for an absolute border.
- `Carry: R10-OUTSIDE-DHW-START-HYSTERESIS (item 4)` - keep the author's commit as the base of the option
  plumbing, tests and translations, with authorship.

## Appendix: the spike (scratch, never merges)

The probe's solve, with `DhwPlanner._build_dhw_requirements` wrapped to OR a global mask into `off_steps`, and
per solve: find the first run start i after step 0 with tank above set-point less h; ban from i for the
larger of the run's length and (tank minus threshold) over the largest idle one-step sag; solve again; stop
when none is left (cap 40). Reported per h: runs, unstartable runs, summed hot-water kWh and price-weighted
cost, the largest positive (requirement minus tank), rounds. h of 0 gave 0 rounds and identical totals.
