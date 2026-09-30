<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

Three findings, one owner, and a price.

**D12-s2-01 (P2, medium).** Four copies of `max(0.1, min_electrical_power * 0.5)`
answered two different questions: whether a PLAN step must run, and whether a
METER sample proves the pump ran. On a fixed-speed pump — min == max, a
configuration `config_flow._power_errors` accepts — the plan-side copies put the
switch at half the rating, so the switch path switched off steps whose heat the
same plan's trajectory, cost and published savings booked as delivered. At this
merge base, on the finder's own harness: 3 of 9 golden cells withhold more than
a tenth of their booked energy, the shoulder cell 0.671 of it, 30 end-to-end
`switch.turn_off` calls land on steps carrying planned heat, and the actuated
house ends 17.23 K*h below the trajectory the plan was priced on (19.89 °C
against a planned 20.64 °C). The finder read 4 failing cells at baseline
`1936d5ca` against a stated ±1; this box reads 3.

The plan side now reads the plan's own running rule, which the tree already had
and nobody owned: a step below the modulation floor is duty cycling WITHIN the
step — the solve's bounds start at 0, and `_compute_baseline_power` records why
flooring them burned `min_electrical_power` around the clock — the objective
prices the chatter, and `count_compressor_starts` already counted such a step as
a run at the same 0.1 kW floor. `thermal_model` owns it now:
`MIN_RUNNING_DRAW_KW`, `planned_draws_run`, and a scalar twin that calls it, so
the comparison is written once. The meter's threshold keeps its formula behind
`on_threshold_kw`, a name that says what it reads, because the two questions
genuinely differ: a running pump draws at least its modulation floor, so half of
it separates a run from a standby draw, and a plan step the solver priced as
duty cycling must not be switched off for it. `pump_arbiter.step_duty` loses its
caller-supplied threshold parameter — a threshold handed in by a caller is the
shape that let the plan and the meter diverge — and `_on_kw` is `_ran_kw`.

One design choice is stated rather than smuggled, because a check encodes it:
the step's draw is the SUM of its two circuits, not the max the old comparison
took. The plan prices `space + dhw` (`_build_result`'s `total_power`) and counts
a compressor start on that sum, so a per-circuit max would leave a step both
circuits trickle through switched off while the plan books its heat — the same
defect one floor down. The 0.05 + 0.06 row of the block's first check is that
case.

The obvious objection — that switching a trickle step on short-cycles the
compressor — is answered by the plan's own arithmetic and then measured. The
solve already prices chatter: `cycling_penalty_batch` charges `cycling_cost ×
Σ|Δp| / (2 p_max)` on the plan the objective picks, the wear autotune raises that
cost to the measured replacement price when the user has not priced it higher,
and `count_compressor_starts` publishes the count so the question stays
answerable after the fact. What the integration owes the plan is to deliver what
the plan booked; the pump's own minimum-run protection is what physically limits
cycling. Measured on three golden fixtures (`basin_carry.py`, below): the
published `compressor_starts` is **unchanged** at base and head — 5, 4 and 6 —
while the on schedule's True count rises 67 → 68, 62 → 63 and 49 → 55. The steps
this fix switches on sit inside stretches the plan already ran, so the fix
delivers booked heat without adding a single start.

**D8-s1-03 (P2, low) does not reproduce at this merge base, and is fixed
anyway.** `minpower.py` reads 0 steps publishing power while Heat Pump Action
reads "off" in all 5 topologies × 4 min-power arms, `worst_published_kw_while_off`
0.00 kW, against the finder's 4 steps and 0.41 kW at `1936d5ca`. The mechanism
is unchanged and still live — `entity.commanded_power_kw` never read
`heat_pump_on` — and this PR's own D12 fix moves the reachable band rather than
closing it: a step booking 0.08 kW is correctly off under the new floor, and
without this gate would still publish 0.08 kW beside a state of "off", above the
finder's own 0.05 kW bar. So the gate lands in the owner every publisher
already reads (sensor.py three times, climate.py once), which is the P2 point:
one change, four surfaces. Because the finder's harness reads flat at both ends,
fixer.md step 3's companion is a pin on the owner itself, in the ledger that
already holds #1499's publisher census, plus the owner's own behaviour change
disclosed below. That change is wider than the finding and is stated rather than
left to be found: the empty plan's `_idle_action` carries the pump's minimum
electrical power as a `power` placeholder while declaring `heat_pump_on` False,
so Recommended Power on an idle pump read 1.0 kW and now reads 0.0. An idle pump
asks for nothing; the placeholder is a stand-in for the frequency command, not an
ask, and no other reader of `action["power"]` is gated.

**D0-s2-02 (P4, low) is a recorded refusal, priced in money and CPU.** No seed
is added and no tolerance tightened; #1664 is closed on the price. The finding
reproduces at this merge base (shoulder 16 cells: gap max 1.1941 % against the
finder's 1.2012 %, mean 0.3164 %, 7 of 16 over 0.1 %; flat-price null 16 cells:
0.4735 % max, 0.1162 % mean), so the excess over the null is 0.72 pp at max and
0.20 pp at mean. `seed_price.py` then prices the cheapest option the finding
leaves open — ONE extra bang-bang seed, never the 13-rung ladder #1294 refused —
at five rungs of Emax over the same 16 cells. The best single rung buys 0.3087
SEK/day summed (mean 0.0193, max 0.2414, 11 of 16 cells exactly zero, none
worse) and costs a solve-CPU ratio of 1.2277 mean, 1.6245 worst; the five rungs
span 1.17–1.28 with no dependence on the rung, which is the cost of a refinement
and not of a value. The whole ladder buys 0.6709 SEK/day summed and its arm
costs 24.7 s/cell against the plain arm's 10.25 s/cell. tvofi refused +24 %
solver CPU on #1294 as over the Raspberry-Pi-class budget, and the gain there
did not reproduce across BLAS builds; the cheaper option lands in the same cost
class for 0.0193 SEK/day per cell, so the refusal stands and is recorded on
#1664.

Part of #1644 (P2). Fixes #1664 (P4). Part of #201.

## Head

`720a5de1` — the code head. The scoped gate and the typing lane ran at exactly
this commit, and the mutation pin lane ran at its parent `d4372dde`, whose tree
differs from it only by the two ledger pins that lane wrote and its own log. The
one commit above it is the hand-off commit: it carries this body, that run's
logs and the seat's resume note, and `git diff --stat 720a5de1..<branch tip>`
touches `tools/audit/handoff/r9-f2-solver-4.md`,
`tools/audit/handoff/r9-f2-solver-4/ev/` and `handoff/round9/fix/resume/F2.4.md`
and nothing else, all outside every closure by the INERT prefix and none read by
a lane.

Environment: the `hpo-ci` container (Linux amd64, CPython 3.14.7, numpy 2.4.6,
scipy 1.17.1, scipy-openblas 0.3.31 DYNAMIC_ARCH, `OPENBLAS_CORETYPE=Sandybridge`,
OMP/OPENBLAS/MKL at 1 thread, `PYTHONPATH=tests/hastub`), each lane behind a
host-side `tests/gate_lock.py auto-lease` and never a lease nested inside the
container around `run.sh`. The host arm (CPython 3.11, numpy 2.4.6 on Accelerate)
is named wherever a figure rests on it, because it is a different basin — see the
P4 carry below.

Cut from `f88e6af8`, with `bd79bc9e` absorbed and then `a15e3e33` (at merge
commit `bfee5fd0`). `bd79bc9e`'s whole diff against the cut point is one line of
`docs/delivery/1767.md`; `a15e3e33`'s against `bd79bc9e` is the v6.7.11 stamp
(`VERSION`, the manifest and card version strings, `RELEASE_NOTES.md`, the two
claim files' `claims-for:` header and the D6 register's manifest row) and
record-only files under `docs/` and `tools/audit/round9/`. No production Python
line moved, so the base arms below, measured at `f88e6af8`/`bd79bc9e`, describe
the same production solver as the merge base `a15e3e33`; the gate, the pin lane
and the typing lane were re-run against `a15e3e33` itself. The claimnotes driver
carried the nine claims under main's `claims-for: 6.7.11`.

## Mutation proof

**The checks fail at the merge base, measured.** This PR's block, inserted into
the base tree's own `tests/features.py` before its `# -- R9-F2.5:` marker and run
through the same slice runner, reads **7 of 8 FAILED** at `bd79bc9e`
(`ev/features_block_base.log`) and 8 of 8 PASSED at the head
(`ev/features_block_head_host.log`, `ev/features_head_container.log`), with the
base's own values in each detail line: `on=[False, False, False, False, False,
True, True]` for a fixed-speed pump's `[0.0, 0.05, 0.12, 1.0, 2.9, 3.0, 6.0]`,
`step_duty takes 3 parameters`, `_ran_kw=None on_threshold_kw=None
plan_floor=None`, and the census `optimizer=2 pump_arbiter=1 thermal_model=0`.
The one check that passes at base is the null arm — a step the plan books no
heat for stays off — which is what a null control is for. The twin-parity check
fails at base on its first clause, both forms being absent, and its detail line
reads `0 of 27 pairs on`, so it does not pass vacuously there either. The base tree's own
legacy three-argument `step_duty` call sites are outside the slice, so the run
records failing checks rather than aborting on the signature this PR retires.
The D8 arm has no slice runner (its fixtures are spread through
`tests/entities.py`), so its base behaviour is measured directly on the owner:
`commanded_power_kw` at base returns 0.41 for an action declaring the pump off
and 1.0 for the idle action's power placeholder, where the two pins assert 0.0,
and returns 0.41 and 2.0 for the two null arms, where the pins assert the same
(`ev/entity_owner_base.log`).

`tools/audit/handoff/r9-f2-solver-4/mutation_proof.py`, seven mutants, each one
seam of the fix restored to its base form, driven through
`tools/audit/handoff/r9-f2-solver-4/run_block.py` — which execs
`tests/features.py`'s own prologue plus the source between the block's two
markers, so the checks that go red are the suite's own bytes and nothing here
restates an assertion. M4's checks live in `tests/entities.py`, so its runner is
that script in full. Each mutant is applied in place on a committed tree and
restored with `git checkout --`; the script refuses to start on a dirty
production file and refuses a mutant that restores clean but adds no failing
check. A mutant is judged on the checks it ADDS to the healthy arm's failing
set, so a red this box already has is not read as a kill.

| mutant | what it restores | added failing checks |
|---|---|---|
| M0 | nothing (healthy arm) | 0 |
| M1 | `_power_to_heat_pump_schedule` decides at half the modulation floor | 3 |
| M2 | the action's fallback reads the meter's threshold | 2 |
| M2b | the action's space band reads the meter's threshold | 1 |
| M3 | the arbiter's space duty reads the meter's threshold | 1 |
| M4 | `commanded_power_kw` stops reading the action's own declaration | 2 |
| M5 | `on_threshold_kw` loses its half-floor (the retired `_on_kw` CLAMP_DROP pin, on the owner now) | 2 |
| M6 | `planned_draw_runs` (the scalar form) returns nothing — the RETURN_DEL site the allocation-free rewrite re-anchored | 3 |
| M7 | `planned_draws_run` (the batch form) returns nothing — the RETURN_DEL site the typing repair's annotated local re-anchored | 2, and the runner stops on a `TypeError` |

M1 through M5 ran in the container (`ev/mutation_proof_container.log`, whose
healthy arms read `ALL 8 R9-F2.4 BLOCK CHECKS PASSED` and `ALL 1990 ENTITY
CHECKS PASSED`, so both counts are the runner's own summary and not a grep); the
same five on the host read identically (`ev/features_block_head_host.log` for the
block arm). M6 and M7 were added when the two owner returns were re-anchored —
M6 by the allocation-free scalar rewrite, M7 by the typing repair (`3bc0980b`,
Red checks) — so they ran after that container log and are recorded on the host
through the same slice runner (`ev/mutant_m6_host.log`, `ev/mutant_m6_m7_host.log`).
M7 stops the block runner with `TypeError: 'NoneType' object is not iterable`
before it prints its own verdict, having already named two failing checks; the
proof's verdict was judging the summary line alone and read that as
`added_fails=0`, so it now reads the pair — the named checks of this block that
went red, or the suite's count moving — and prints a missing summary as what it
is, with the runner's last lines beside it. Both sites are also **pinned**: the
container's pin lane drove them through the whole `tests/features.py` and
recorded `killed_by` for each (Figures, the mutation lane), so no site this diff
adds is left without a disposition.

M1's three: "on a fixed-speed pump every step the plan books heat for is
switched on, not off at half the rating", "one result cannot publish a
compressor start on a step its own on schedule calls off", and "no seam this PR
owns re-derives the meter's threshold". M5's two are the meter's null arm and
the same census check, which pins the formula's presence in the owner as well as
its absence everywhere this PR owns.

The mutation ledger moves with the fact: five pins keyed on lines this diff
deleted or rewrote are retired (`pump_arbiter.py/_on_kw.CLAMP_DROP.159d5a81`,
`step_duty.BOOLOP.b6dd3d98` on `s_on = ... >= on_kw`,
`step_duty.BOOLOP.17ca3f91` on `d_on = ... > 0.1`, and
`thermal_model.py/planned_draw_runs.RETURN_DEL.5198b86a` when the scalar form
stopped delegating, and `planned_draws_run.RETURN_DEL.d544f1b9` when the batch
form's one-line return became an annotated local) — `completeness_problems` refuses a disposition that names no
site, and it reads 0 after each retirement. The eleven sites the first pass added
and the two the rewrites re-anchored were all pinned by `mutation_table.py
--pin-killed` in the container; the drivers, the lane's own null control and the
re-derivation are in Figures.

## Null control

- **The modulating arm of the finder's own harness.** A pump with a real
  modulation band (min 1.0, max 6.0 kW) reads 0 failing cells and a mean
  withheld fraction of 0.001 at base and 0.000 at head, and its end-to-end
  `turn_off` count is 58 at both ends: the fix moves the fixed-speed arm, where
  the threshold was half the rating, and leaves the arm where it was already
  near the floor.
- **The harness's own perturbation arm is this fix.** `onoff_switch.py
  --perturb` patches a 0.1 kW on-threshold in memory at base and reads
  `onoff_failing_cells` 3 → 0, `e2e_turn_off_with_planned_heat` 30 → 0,
  `withheld_frac_mean` 0.133 → 0.000, and the actuated shoulder minimum 19.89 →
  20.64 °C against a planned 20.64. The head's plain arm reads the same five
  numbers (0, 0, 0.000, 20.64, 62 `turn_off` calls), so the fix and the
  finder's demonstrated remedy agree at the digit.
- **The flat-price twin is D0-s2-02's own null.** A basin gap exists at flat
  prices too (0.4735 % max against shoulder's 1.1941 %); the price-optimality
  part is the excess, 0.72 pp at max.
- **`seed_price.py`'s `none` arm** is the same 16 cells solved through the same
  wrapper with no seed appended, in the same process, so the CPU ratio is a
  ratio of two arms of one run and not of two boxes. Its `f0` column reproduces
  `race.py`'s `f=` per cell, which is the control that the wrapper measures the
  quantity the finder measured.
- **Two null arms in the block**: a step the plan books no heat for stays off on
  a fixed-speed and a modulating pump alike, and the meter's threshold is
  unchanged at 0.2 kW on a 0.4 kW plant while the plan's floor stays at 0.1 —
  the two thresholds disagreeing on purpose is the point of the split.
- **The class instruments at base and head.** The P2 sweep enumerator's
  `--selftest` reads clean 0 and reintroduced 1 at both ends, so its zeros are a
  measurement and not an empty set; every instrument ran INSIDE the tree being
  measured, at its canonical path, because an enumerator that resolves its own
  location reads nothing from an export.
- **The golden fixtures are the fix's null arm in the other direction.** Of the
  scenarios `env_drift.py --all` compares against the merge base in the pinned
  container, 28 are byte-identical here — among them all five coordinator
  captures, which are the fixtures carrying a published power — 16 are on the
  gate's own may-drift list, and 9 move and are claimed. Every leaf the report
  prints, for the claimed and the may-drift alike, is
  `heat_pump_on_schedule[i]` going `False -> True` (100 printed leaves, one
  field, one direction), and the complete census of the 9 claimed fixtures and
  the 5 coordinators is in Figures: 46 leaves, all in that field, all in that
  direction, coordinators at zero. A fix that had moved the plan rather than the
  switch would have moved costs, trajectories and reason codes with it.

## Figures

Every command ran from the repository root of the tree it measures. `$EX` is
the export of the evidence commit `79aa98ec`; the harnesses insert `tests` and
`custom_components` relative to the cwd, so they measure the cwd's tree and not
the export's — the rule `onoff_switch.py`'s own header states. Instrument sha1s:
`onoff_switch.py` 1693786192e920778d708de2754dadac331795f4, `minpower.py`
9e6103c375f37a5e3857fa77e7a971e485acfaad, `matrix.py`
e8c0f86e786fd5574852d1bbbadc165cc01b0987, `race.py`
75739b2688b3ea4c3e838258fe0f2e0f0c172ff1, P2 `enumerator.py`
d266a4052de977686cd306ae51ae77d4a710ed51 (sweep S1 `c44e7bcd60`), P4
`enumerate.sh` b39c66ed00fa1d1e781a57f39c3c9ec1bb356195 (sweep S6 `6b65c9c4a8`),
`owners_lint.py` 3aad65da7e9a2656e1d5ff32bb14bc82f777f772 (RCA prototype
`3938c8ea`). `$SW1`, `$SW6` and `$RCA` are the exports of those three instrument
commits, and each class instrument was planted from its export at the same
canonical path inside the tree being measured before it was run, because an
enumerator that resolves its own location reads nothing from an export and
prints the same zeros a fixed tree does; the commands below are written as
`$NAME/<canonical path>`, which is byte-identical to the planted copy at the
sha1 above. Logs: `tools/audit/handoff/r9-f2-solver-4/ev/`, one per figure, named
`<instrument>_<base|head>.log`.

**D12-s2-01 — `python $EX/tools/audit/round9/D12/s2/onoff_switch.py`** (container,
both arms; `ev/onoff_switch_{base,head}.log`, `..._perturb_base.log`):

| figure | base | head |
|---|---|---|
| `onoff_failing_cells` (of 9; LOO) | 3 (2) | 0 (0) |
| `onoff_withheld_frac_mean`, range | 0.133, 0.000..0.671 | 0.000, 0.000..0.001 |
| `onoff_e2e_turn_off_with_planned_heat` / `..._calls` | 30 / 92 | 0 / 62 |
| `onoff_shoulder_min_room_planned` / `..._actuated` | 20.64 / 19.89 °C | 20.64 / 20.64 °C |
| `onoff_shoulder_Kh_below_plan_actuated` | 17.23 | 0.00 |
| `modulating_failing_cells`, mean withheld, e2e | 0, 0.001, 0 of 58 | 0, 0.000, 0 of 58 |

**D8-s1-03 — `python $EX/tools/audit/round9/D8/s1/minpower.py`** (container;
`ev/minpower_{base,head}.log`): `power_while_off_min0_2` / `min0_6` / `min1_0` /
`min1_5` all 0 steps of 96 in 5 cells, `worst_published_kw_while_off` 0.00 kW —
at base and at head, and under `--perturb` at both. The finder's 4 steps and
0.41 kW were measured at `1936d5ca`; the instance is not reachable in this grid
at this merge base, so the fix is demonstrated by the companion pins in
`tests/entities.py`'s #1499 publisher census: an action declaring the pump off
publishes 0.0 on all four surfaces (Heat Pump Action's `power_kw`, Recommended
Power, the climate's `recommended_power_kw`, Measured Power's
`recommended_power`), one declaring it on still publishes its whole ask, and one
carrying no declaration at all is not gated.

**D0-s2-02 — `python $EX/tools/audit/round9/D0/s2/race.py --horizon 24 --cells
shoulder,flat --weather winter_cold,winter_mild,summer_cool,shoulder
--first-only`** (container; `ev/race_base.log`, 32 cells): `gap_max` 1.1941 %,
`gap_mean` 0.2163 %, `cells_over_0p1pct` 13, `gap_mean_drop_worst` 0.1848 %.
Split on the cell name's price field: shoulder 16 cells 1.1941 % max / 0.3164 %
mean / 7 over 0.1 % / 0.2579 % drop-worst; flat 16 cells 0.4735 % / 0.1162 % /
6 / 0.0923 %. The headline cell `one|nodhw|shoulder|shoulder` reads 1.1941 %
against the finder's 1.2012 % (its stated tolerance ±0.05 pp).
`... --cells shoulder --perturb add_emax_ladder` (16 cells;
`ev/race_ladder_base.log`): `gap_max` 0.0472 %, `gap_mean` 0.0031 %,
`cells_over_0p1pct` 0. The objective the two arms ship, differenced per cell
(the `f=` column of each log): sum 0.6709, mean 0.0419, max 0.3649, 4 of 16
cells 0.0000, none worse.

**The price of one seed — `python
tools/audit/handoff/r9-f2-solver-4/seed_price.py --export $EX`** (container, base
tree; `ev/seed_price_base.log`). One bang-bang seed appended to the candidates
production hands its own seam, built as `race.py`'s ladder builds it, at five
rungs of the bounds' max energy, over the same 16 shoulder cells:

| rung | obj gain sum | mean | max | cells at zero | worse | CPU ratio mean | max |
|---|---|---|---|---|---|---|---|
| 0.2×Emax | 0.0796 | 0.0050 | 0.0763 | 14 | 0 | 1.1989 | 1.4917 |
| 0.4 | 0.0161 | 0.0010 | 0.0159 | 14 | 0 | 1.1720 | 1.4978 |
| 0.6 | 0.0278 | 0.0017 | 0.0278 | 15 | 0 | 1.2392 | 1.6813 |
| 0.8 | 0.1664 | 0.0104 | 0.0684 | 13 | 0 | 1.2805 | 1.6921 |
| 1.0 | 0.3087 | 0.0193 | 0.2414 | 11 | 0 | 1.2277 | 1.6245 |

SEK/day per cell, on the objective the harness races. `cpu_s` is
`time.process_time()` around the whole `optimize()`, ratioed against the `none`
arm of the same cell in the same process; the `none` arm ran first in each cell,
so any warm-up bias understates the cost. The 0.8 rung closes the headline cell
entirely (0.0684, the whole 1.1941 %), which is the basin the finding named.

**The P4 carry — `python tools/audit/handoff/r9-f2-solver-4/basin_carry.py`**
(container and host, base and head; `ev/basin_carry_{base,head}.log`). F2.1
disclosed a P4 basin effect in `everything_on` as summed degree-steps below
`config.min_temp` over the zone trajectories, 0.276 → 0.896 on its box, and
ruled it not a regression: the sub-17.0 steps fall in the night-setback window
where the solver's own floor is `min_temp − 0.5`. Re-measured here with #1694's
rule and its caveat (it counts `config.min_temp` at every step, setback window
included), in the pinned container:

| scenario | figure | base | head |
|---|---|---|---|
| `everything_on` | deg_steps | 0.578119 | 0.578119 |
| | predicted_cost / compressor_starts | 59.254608 / 5 | 59.254608 / 5 |
| | `heat_pump_on_schedule` True | 67 of 96 | 68 of 96 |
| | `plan_sha1` | `2e023086a7bbff0f6a1bb0517506c3dfb6b7f4ef` | identical |
| `winter_two_zone_no_dhw` | deg_steps / cost / starts | 0.855744 / 58.851802 / 4 | identical |
| | `heat_pump_on_schedule` True | 62 of 96 | 63 of 96 |
| | `plan_sha1` | `cdb56eb16a69c43cb82bb07ecc97175ece31e1fd` | identical |
| `shoulder` | deg_steps / cost / starts | 0.000000 / 3.782815 / 6 | identical |
| | `heat_pump_on_schedule` True | 49 of 96 | 55 of 96 |
| | `plan_sha1` | `8baabfecb541f141915435fec0594ed81d64165d` | identical |

`plan_sha1` is the sha1 of the captured space and DHW schedules, so "the solve
did not move" is a comparison and not an adjective: this PR touches only what
happens after the solve, and the plan, its cost, its start count and its
trajectories are byte-identical at both ends. What moves is the on schedule —
one more step actuated on in `everything_on` and `winter_two_zone_no_dhw`, six
more in `shoulder` — which is the fix, on fixtures nobody chose. The number this
body reports is the one measured here, not F2.1's, and it is a runner property:
the same tree on this Mac's Accelerate reads `everything_on` at 0.851747
degree-steps, `predicted_cost` 59.743849 and `plan_sha1`
`d8aa13d97728959ea4fd3f5be385a6b6bdfdfd32` — a different basin, identical at
base and head there too (`ev/` carries both arms in the container; the host arms
are in this body's Friction line and reproducible by the same command). That
kernel sensitivity is #1294's second ground for refusing a seed, and it is why
the refusal below does not rest on one box.

**The golden drift, and its complete census.** `python tests/env_drift.py --all
bd79bc9e` in the container (`ev/env_drift_all_head.log`) reports 9 unclaimed
scenarios and 16 MAY-DRIFT ones; a name cannot be both, so the 9 are claimed in
`tests/golden/claimed_drift.txt` and the may-drift entries and `claims-for:` are
untouched. `env_drift` prints at most five leaves per scenario, so the claim's
reason is not read off a truncated log: `python
tools/audit/handoff/r9-f2-solver-4/drift_leaves.py --out <dump>` in each tree and
`--diff base.json head.json` gives the whole census
(`ev/drift_leaves.log`) — `scenarios_moved=9`, `leaves_moved=46`,
`leaves_by_field[heat_pump_on_schedule]=46`, `leaves_by_direction[False ->
True]=46`. One field, one direction, and the per-scenario counts agree with
`env_drift`'s (1, 16, 2, 1, 1, 2, 14, 7, 2). The five coordinator captures in
the same census — `coord_minimal`, `coord_dhw`, `coord_two_zone`,
`coord_grid_fee`, `coord_all_features`, the fixtures that carry a published
power — moved 0 leaves, which is the D8 gate changing no published number
anywhere a fixture records one. The direction is one-way by construction: 0.1 kW
is at or below `max(0.1, min_electrical_power * 0.5)` on every plant, so a step
can only gain the pump.

**Class sweeps (fixer.md step 8), run inside each tree at its canonical path.**

- **P2's owner registry** — `python3 $RCA/tools/audit/round9/rca/p2/owners_lint.py`
  (the RCA prototype at `3938c8ea`, whose `on_threshold_kw` entry is the owner
  this PR creates and F1.11 registers). Base: `p2_owner[on_threshold_kw] FAIL
  hits=4 stray=4 owner_missing=1`, the four strays being
  `optimizer.py:7098` `_power_to_heat_pump_schedule`, `optimizer.py:7163`
  `get_current_action`, `pump_arbiter.py:432` `_on_kw` and `coordinator.py:10010`
  `_observe_compressor_start`. Head: `FAIL hits=2 stray=1 owner_missing=0` — the
  owner exists and the one remaining stray is `coordinator.py:10010`, F1's file
  and F1.10's route, exactly as this group's brief carries it. The lint's other
  five entries read identically at both ends, including
  `p2_owner[dhw_enabled] FAIL stray=2` (`config_flow.py:2175`
  `_omit_unstored_defaults`, `:2914` `async_step_dhw`), which is D14-s2-01's and
  not this PR's: dispositioned as a distinct finding by id, unchanged by this
  diff. `p2_owner_entries_failing` 2 at both ends.
- **P2's sweep enumerator** — `PYTHONPATH=tests/hastub python3
  $SW1/tools/audit/round9/D14/sweep/P2/enumerator.py --seams`: `dhw_enabled` 13,
  `two_zone_enabled` 0, `wood_furnace_on` 10 at base and at head, and the SEAM
  lines are byte-identical between the two arms, so this diff adds no
  configuration-fact seam. The dynamic probe reads `cells=40`,
  `derive_preset_disagree=0`, `prefill_refused_or_missed=0`,
  `null_control_disagree=0` at both ends — D14-s2-01's instances are closed —
  and its perturbation arm REFUSES at this base with
  `AssertionError: ('_derive_preset', 'two_zone=bool(current.get(CONF_UPPER_FLOOR_THERMAL_MASS)),')`:
  the instrument patches a source line that #1724 already replaced, so the arm
  cannot run here and its absence is reported rather than read as a zero.
  `--selftest` reads clean 0, reintroduced 1 at both ends, which is the control
  that the enumerator is live.
- **P4's sweep enumerator** — `bash
  $SW6/tools/audit/round9/D14/sweep/P4/enumerate.sh`: two `_multi_start_minimize`
  call sites at base (`optimizer.py:3557`, `:4123`) and two at head (`:3567`,
  `:4133`) — the same two seams S6 dispositioned as instances of D0-s2-02, moved
  by line only. Both are refused with the price above; neither seed set is
  widened by this diff, which is what the register's carry requires.
- **The findings' own seam rules.** D12-s2-01's, verbatim (`grep -rn
  "min_electrical_power.*\* 0\.5\|_on_kw(" custom_components/heatpump_optimizer/`):
  6 hits at base (`pump_arbiter.py:421,431,432,568`; `optimizer.py:7098,7163`),
  1 at head — the owner's own line, `thermal_model.py:1161`. A widened rule that
  cannot be fooled by operand order (a line reading both `min_electrical_power`
  and `0.5`), which is what catches the copy the finding's grep misses: 4 at
  base, 2 at head (the owner and `coordinator.py:10010`). The block pins the
  widened rule over the two files this PR owns or borrows — 0 copies — and
  deliberately does not pin `coordinator.py`, because an allow-list entry
  silences everything its key matches. D8-s1-03's (`grep -rn
  'commanded_power_kw(' custom_components/heatpump_optimizer/`): 5 hits at both
  ends, one definition and four publishers, all four reading the owner the fix
  is in.

**The D6 claim register — `PYTHONPATH=tests/hastub python3
tools/audit/round4/D6/claims.py`** in the container: `claims_extracted=125`,
`claims_checked=125`, `claims_true=123`, `claims_false=0`, `claims_stale=0`,
`claims_unverifiable=2` — the counts the committed header states, unchanged, with
C77 restated to the rule this PR lands and its evidence reading
`thermal_model`'s owner instead of a deleted optimizer line. Its two committed
artifacts move by exactly the one C77 row each (`git diff --stat`: 1 insertion
and 1 deletion in `claims.json`, the same in `claims.md`).

**The suites.** In the container at `720a5de1`, inside the scoped gate:
`tests/features.py` **ALL 3588 FEATURE CHECKS PASSED** (569 s), 8 of them this
PR's; `tests/entities.py` **ALL 1990 ENTITY CHECKS PASSED** (292 s), 2 of them
this PR's; `tests/harness_headers.py` **ALL 91 HARNESS HEADER CHECKS PASSED**,
the lane the D6 claim repair was owed to (`ev/gate_head.log`).
On the host (CPython 3.11, Accelerate) the same `features.py` reads 1 of 3588
FAILED at the pre-block head, and the one failure is `R9-F2.1 P3: the shipped
storage plan is no worse on its own objective than the half-price floor's plan
refined under it [shipped 110.4366, seeded with the half-price plan 110.1297]` —
the kernel-dependent arm #1711 documented, green in the pinned container
environment and on CI, and not this PR's: `ev/features_head_host.log`.

**The scoped gate.** `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git
merge-base origin/main HEAD) ./tests/run.sh` in the container at `720a5de1`,
merge base `a15e3e33` (`ev/gate_head.log`). The mode line reads `MODE: SCOPED --
24 script(s) run, 3 scoped out.` over 87 changed files — the mode line is the
signal, not the count — and the three not run are `tests/frontend.py`,
`tests/ha_contract.py` and `tests/open_meteo.py`, each because no changed file
is in its measured closure, a claim main's own unscoped run re-checks.
`tests/golden.py` is replaced by drift mode's `env_drift.py --all`. The summary
is `1 TEST SCRIPT(S) FAILED`: 24 lanes `ok` and **`tests/stress.py` FAILED on one
of 87 checks**, the memory arm on `winter/cycle` — answered in Red checks with a
base-against-head measurement. Lane results, with the seconds `run.sh` printed:

| lane | s | lane | s |
|---|---|---|---|
| `features.py` (ALL 3588) | 569 | `env_drift.py --all a15e3e33` | 255 |
| `entities.py` (ALL 1990) | 292 | `env_drift.py --claims-only` | 3 |
| `harness_headers.py` (ALL 91) | 221 | `optimality.py` (ALL 84) | 281 |
| `stress.py` — **FAILED, 1 of 87** | 434 | `backtest.py` (ALL 25) | 126 |
| `finite_boundary.py` | 36 | `edge.py` | 44 |
| `validate.py` | 46 | `card.mjs` | 20 |
| `config_flow_steps.py` | 18 | `card_drift.mjs` | 9 |
| `doc_claims.py` | 5 | `deployment_shape.py` | 4 |
| `plan_view.py` | 2 | `structure.py` | 4 |
| `closure.py selftest` | 2 | `guard_pins.py` | 1 |
| `solar_alignment.py` | 2 | `manual_plan.py` | 7 |
| `md_tables.mjs` | 2 | `wood_advisor.py` | 1 |
| `typing_ruler.py` (census arm) | 1 | `golden.py` | replaced by drift mode |

`env_drift --all` printed `NO UNCLAIMED DRIFT: 56 scenario(s) checked against
a15e3e33507bde9e566858ce32b2ded840edfa02`, which is the nine claims matching the
nine moved fixtures and no claim left stale after the merge driver carried them
under `claims-for: 6.7.11`. The stress lane's CPU arm read `shoulder/tariff+cycle
used 13314 ms of CPU = 254.3x its 52.4 ms reference; budget is 268x`, ok.

A second runner, run by the orchestrator at exactly `720a5de1` on a cloud Linux
box with CI's hash-pinned environment (OpenBLAS Haswell, 1 thread), reported:
`MODE: SCOPED -- 24 script(s) run, 3 scoped out`, `stress.py` **ALL 87 passed**
there along with features 3588, entities 1990, backtest 25, optimality 84 and
structure; in drift mode against `a15e3e33` `NO UNCLAIMED DRIFT: 56 scenario(s)`
and `NO STALE FIXTURE: 56`; strict-mode `golden.py` reads `34 of 56 GOLDEN
SCENARIOS CHANGED`, which is that box's BLAS against fixtures recorded on
another, the reason drift mode exists. Those lines are the orchestrator's
report, not a log this branch carries.

**The typing lane.** `python tests/typing_ruler.py --mypy` in the container at
`720a5de1` (mypy 2.3.1, homeassistant-stubs 2026.9.3): **ALL 9 typing-ruler
checks PASSED**, `errors did not grow` and `type_ignores did not grow`
(`ev/typing_head.log`); the orchestrator's cloud runner read the same line at
the same head. The red it answers is in Red checks.

**The mutation lane.** `python tests/mutation_table.py --pin-killed --base
bd79bc9e` in the container drove the 11 candidate sites this diff first added and
recorded **11 pinned, 0 left unpinned** (`ev/mutation_pin.log`). The two owner
returns the later rewrites re-anchored were driven by a second run at `d4372dde`,
`python tests/mutation_table.py --pin-killed --base origin/main --scripts
tests/features.py` against `a15e3e33` (`ev/mutation_pin_r4.log`): **2 pinned, 0
left unpinned** — `thermal_model.py` `planned_draw_runs` RETURN_DEL (features
failed 0 → 50) and `planned_draws_run` RETURN_DEL (0 → 4), the lane's baseline
`rc=0 failed=0 665s` and its null control, a comment-only edit at
`thermal_model.py:124`, surviving. The driver set is narrowed to the one script
the mutation proof already measured killing both sites; `--scripts` is the lane's
own option for it, and it spares 18 baselines a two-site run would otherwise
pay (Friction). Which driver
killed which: `tests/features.py` the on schedule's return, both of
`step_duty`'s circuit reads, the plan-floor constant, both owner returns and
both `on_threshold_kw` mutants; `tests/entities.py` the `heat_pump_on` gate in
`commanded_power_kw`; `tests/structure.py` `_ran_kw`'s return; `tests/stress.py`
`get_current_action`'s DHW-length guard. The lane's own null control — a
comment-only edit at `entity.py:118` — survived every driver including stress,
so the kills are the mutants' and not the environment's. With the five retired
pins gone and the thirteen recorded, the exact-count ratchet reads **3580 unpinned
of 4078 candidate sites against 3583 at the ratchet base** — down, not up — and
`completeness_problems` reads 0, so no disposition outlives its line; both
re-derived at the head through `mutation_table.py`'s own `inventory`,
`unpinned_sites`, `base_unpinned`, `ratchet_refusal` and `completeness_problems`,
which are pure AST and drive nothing, re-run at `720a5de1`:
`ledger_form_problems` 0, `completeness_problems` 0, `unpinned_sites` 3580 of
4078, `base_unpinned(origin/main)` 3583. No site this diff adds is left
unpinned. The retired
pins are the ones whose `old` line this diff deleted or rewrote —
`completeness_problems` refuses a disposition that names no site, and it reads 3
before the first retirement and 0 after each, which is the check that the
retirement was owed rather than convenient. The retired `_on_kw CLAMP_DROP` pin
is not lost: `on_threshold_kw.CLAMP_DROP` is the same mutant on the owner the
formula moved to, killed by the same driver, and M5 of the mutation proof above
is the same mutant again with the check named.

**One pre-existing check re-anchored, not weakened.** The pump-duty arbiter
section's "a space draw at half the pump's minimum or more is a space duty"
pinned the retired boundary: `_on_kw(coord) == 0.2` and a 0.2 kW step reading
`space`. Its boundary is now 0.1 kW and its threshold is no longer a caller's to
supply, so the check is restated on the rule that replaced it — a 0.15 kW step
the plan books is a space duty on a 0.4 kW plant — which fails at base and
passes at head, and the meter's 0.2 kW is pinned by this PR's own null arm.

**One in-tree evidence harness updated, disclosed.** `tools/audit/round9/D12/s2/mode_domain.py:173`
called the three-argument `step_duty` with `pump_arbiter._on_kw`, so retiring
both broke it. Round-9's harnesses landed in main at #1769, which made them
in-tree instruments a later production fix can break with no lane to tell it
(`tools/audit/` is INERT by prefix; `tests/harness_headers.py` reads headers
only). An instrument that cannot run is the defect this repository already
recorded, so the call is updated rather than left: `pa.step_duty(result, now)`.
Its metric — a mode-slot service call whose domain differs from its target's —
never read the threshold, so the harness measures what it measured, and its
`Baseline SHA` expectations are unchanged in kind. Re-running it at its own
baseline needs the three-argument form, which git history carries. No other
in-tree harness calls a seam this PR changes: `onoff_switch.py` reads
`_power_to_heat_pump_schedule` and `get_current_action`, whose signatures are
unchanged, and `matrix.py` / `l2_d8_leads.py` read `commanded_power_kw`, whose
signature is unchanged.

**Structure.** `python3 tests/structure.py` at head: STRUCTURE RATCHET PASSED,
every metric at its recorded cap in `structure_budgets.json`
(`recorded_at 5395394da9d8`), none moved — `internal_call_edges` and
`cross_seam_edges` are measured on the coordinator's own method calls, which
this diff does not touch, and the three new module-level symbols in
`thermal_model.py` each have a caller in the package, so
`dead_top_level_symbols` stays at its budgeted 1 (`const.py:1545
ENTITY_FAMILY_OVERRIDES`, pre-existing). No budget raise is asked for.

## Red checks

Six lanes went red on a commit in this branch, each named below with the answer
`defect-root-cause.md`'s second trigger asks for. Four were this branch's own
doing and are answered inside the diff — the unclaimed drift the claims were
written from, the documentation claim the fix falsified, a real 0.5 MiB the
owner's first draft allocated, and a return mypy could not type; two are this
box's, and neither is left as an adjective where a measurement was available.

- **`tests/typing_ruler.py --mypy` (the pinned typing lane, in the container),
  at `b9f86fb5` — `2 of 10 typing-ruler checks FAILED`: `errors did not grow
  [recorded 0, measured 1 (+1)]` and `by_code[no-any-return] did not grow
  [recorded 0, measured 1 (+1)]`, both `thermal_model.py`** (`ev/typing_b9f86fb5.log`).
  numpy's stubs type `ndarray.tolist()` as `Any`, and the owner's batch form
  returned it directly from a function annotated `-> list[bool]`. Fixed in
  `3bc0980b` with an annotated local, the shape the optimizer's own copy of this
  comparison had before the owner existed; `type_ignores` stays 0, because a
  suppression would have moved the count the ruler's other arm watches. The
  rewrite re-anchored the batch return's RETURN_DEL site, which M7 and the second
  pin run then covered. Cheaper detector: none cheaper than the lane that found
  it — the scoped gate runs only the ruler's census arm, and the mypy arm is the
  pinned toolchain that cannot install on this host (`fixer.md` routes it to the
  container); the process state is **(c)**, the lane existed and was run, and it
  ran after the round-3 gate instead of beside it because the container lease was
  held. Green at the code head (Figures, the typing lane).

- **`tests/env_drift.py --all bd79bc9e`, at `fb705496` — `9 UNCLAIMED DRIFT(S)`.**
  This is the measurement the claim file is written from, in the order
  `fixer.md` step 4 prescribes: a golden that moves is claimed by whoever
  measured the drift, and the only honest way to know which fixtures move and
  in which direction is to run the lane unclaimed first. Cheaper detector:
  none, and the standing cost is the one run — predicting the moved fixtures
  from the diff would be a claim about a solver this branch does not touch, and
  the census that replaced the prediction (`drift_leaves.py`) is itself derived
  from captures, not from the diff. Green at the head that carries the nine
  claims: `baseline tests/env_drift.py: rc=0 failed=0 459s`.
- **`tests/features.py` on the host (CPython 3.11, numpy on Accelerate) — `1 of
  3588 FEATURE CHECKS FAILED`, `R9-F2.1 P3: the shipped storage plan is no worse
  on its own objective than the half-price floor's plan refined under it
  [shipped 110.4366, seeded with the half-price plan 110.1297]`.** Not this
  branch's, and the attribution is a measurement rather than an assertion: the
  check compares two solves of the 750 L storage house, and `basin_carry.py`
  shows this diff leaves every plan byte-identical (`plan_sha1` equal at base
  and head, in the container and on this host, for all three scenarios it
  carries), because it touches only what happens after the solve. Both of the
  check's numbers are therefore the same at base and head on one box, so its
  verdict cannot be this diff's. It is the kernel-dependent arm #1711 documented
  — green on an AVX-512 box, red on Haswell-class and on this host's Accelerate
  — and the same tree in the pinned container reads 3587 of 3587. No new check
  is owed: the detector that exists (`tests/backtest.py`'s storage margin and
  the F2.1 block's own basin arm, which pins the basin by objective rather than
  by margin) is the one #1711 built for exactly this, and it is green here.

- **`tests/harness_headers.py` — 3 of 91, and `tests/entities.py` — 1 of 1990,
  both at `8a7a16c2`.** The three header checks are `claims_true matches header
  [header='123' printed='122']`, `claims_false matches header [header='0'
  printed='1']` and `the executed harnesses leave their committed output
  byte-identical [uncommitted: M tools/audit/round4/D6/claims.json; M
  tools/audit/round4/D6/claims.md]`; the entity check is the acceptance's own
  null control — `node .claude/workflows/policy_lint.mjs` over the live tree
  returning 1 where it must return 0. Two causes, both this branch's, both
  answered in the diff rather than owed.
  - *The doc claim this fix falsified.* `docs/ecl110.md` said a step is ON when
    either circuit "clears the pump's activation threshold (half its modulation
    floor, at least 0.1 kW)", and `tools/audit/round4/D6/claims.py`'s C77
    verified that sentence against the exact optimizer source line this fix
    deleted, so the D6 verifier read `documented=True measured=False` and its
    committed output moved. Cheaper detector: none cheaper than the gate that
    found it — the D6 claims lane *is* the documentation-claim detector, it runs
    in 8 s, and it is what turned red; the process failure was that the fix
    grepped the package for the rule it was changing and not the docs and the
    claim verifier that restate it (state **(c)**: the process existed, was
    followed, and its scope was too narrow). Countermeasure, in `f79b0d50`: the
    page, the claim's sentence and the claim's evidence move together, the
    evidence now reading `thermal_model`'s owner instead of a deleted line, and
    the artifacts regenerated in the container to `claims_true=123`,
    `claims_false=0` — unchanged — with each artifact moving by exactly the one
    C77 row.
  - *A named document with no corpus cap.* A new `README.md` under
    `tools/audit/handoff/` is named by `tools/audit/README.md`, and `named-docs`
    refuses it because prose moved into a file no `POLICY_GLOBS` pattern matches
    leaves the corpus and buys headroom in every cap at once.
    `.claude/workflows/corpus_excluded.json` gains the entry, on the precedent of
    the `r9-f2-solver-5` entry beside it, and it is data rather than a block
    inside `policy_lint.mjs` for the reason that file states: the `policy-docs`
    job restores the check source from the base before grading, so an exclusion
    shipped in the same branch as the evidence it excludes has to arrive outside
    the restored pathspec. `node .claude/workflows/policy_lint.mjs` then reads
    `TOTAL: 0 error(s) across 40 policy file(s)`.
- **`tests/entities.py` — 1 of 1990 a second time, at `f79b0d50`, the same
  template arm.** Both causes named above were already fixed in that head, and
  the same command in the same container at the same head returns 0 afterwards:
  in the mutation proof's healthy arm (`ALL 1990 ENTITY CHECKS PASSED`,
  `ev/mutation_proof_container.log`), run directly (`TOTAL: 0 error(s) across 40
  policy file(s)`), and in the round-3 gate (`ok python3 tests/entities.py
  (270s)`, `ev/gate_round3_head.log`), and again in the code head's gate (292 s). The failing detail line names no policy error, only the acceptance's
  exit status, so what it saw is not reproducible from the tree; the window
  (04:23–04:30Z) had two peer seats driving git-heavy `prepr.sh` and
  `derive_closures.sh --single` lanes against the same repository, and
  `policy_lint.mjs` shells out to git for its corpus and required-context arms —
  a mechanism this body does not claim to have established, only a window it
  cannot exclude. Attribution: transient, of the environment and not of this
  diff, and the round-3 gate is the measurement that settles it. Cheaper
  detector: none; the arm *is* the detector, a two-second node run.
- **`tests/stress.py` — `the probed scenarios' memory peaks stay within their
  recorded budgets [winter/cycle attributable RSS 14.1 MiB vs recorded 9.4 MiB
  (x1.5 headroom; probe 128.4 MiB over a 114.3 MiB baseline)]`, at `8a7a16c2`,
  again at `f79b0d50`, and — the same line to the byte — at the code head
  `720a5de1`; and `every scenario's solve costs what it should, in CPU,
  for this machine [shoulder/tariff+cycle used 15876 ms of CPU = 291x the 54.5 ms
  reference measured beside it (budget 268x)]`, at `f79b0d50` only.** The memory
  arm was this branch's, the CPU arm was not, and both are answered by
  measurement rather than by calling the lane noisy.
  - *Memory, rounds 1–3: an allocation found and removed.* The first draft of the owner's scalar form
    delegated to the batch form, so every call built two one-element numpy
    arrays — and its callers are per-call paths, an action per cycle and a duty
    per arbiter tick. `winter/cycle`'s attributable RSS read **14.1 MiB at both
    heads that allocated** (`ev/gate_round1_head.log`, and the round-2 run)
    against **13.9 at the merge base** (`ev/stress_base.log`, same container,
    same pin) and a 1.5× allowance of 14.1 — on the boundary, over it. Rewriting
    the scalar form in plain floats, which is the sounder shape for a scalar
    predicate whatever the lane said, reads **13.6 MiB** at `d28d6901`
    (`ev/gate_round3_head.log`) and the lane passes. The other five probed scenarios
    move ±0.6 MiB between runs of one tree and the instrument reports all six
    "at this platform's import floor", so 0.2 MiB is inside this box's noise —
    which is why the fix is argued on the shape and evidenced by the direction,
    not claimed as a precise saving. Cheaper detector: none; the attributable-RSS
    arm *is* the detector and the lane that found it. How much of the 0.2 MiB
    was the allocation and how much the draw is what the next point bounds.
  - *Memory at the code head: measured base against head, not re-recorded.*
    `720a5de1` changes no allocation over `d28d6901` (its only production edit
    is `3bc0980b`'s annotated local), yet its gate draw read 14.1 again where
    `d28d6901`'s read 13.6 — one draw of a statistic whose own docstring gives a
    clean spread up to 2.1x. So a single draw is not the measurement:
    `tools/audit/handoff/r9-f2-solver-4/rss_ab.py` runs the lane's own
    `--memory-baseline` and `--memory-probe` entry points for `winter/cycle`, six
    draws per tree, alternating base (`bd79bc9e`, production-identical to
    `a15e3e33`) and head so drift in the box lands on both
    (`ev/rss_ab_winter_cycle.log`, container, one lane at a time):
    **base attributable 12.8 / 13.5 / 13.9 MiB (min / median / max), head 13.4 /
    13.9 / 14.4**, traced peak **3.46 MiB in all twelve draws**. The head sits
    about 0.4 MiB above the base at the median with overlapping ranges, and the
    traced arm — the precise detector for Python-side growth, clean spread ~1 % —
    does not move at all. That is what this body can say: a sub-MiB RSS shift of
    uncertain origin at the container's import floor, invisible to tracemalloc,
    far below the 1.5x the arm is sized to detect, on a record (9.4 MiB) that
    `tests/stress.py`'s own docstring calls thin for exactly this scenario (a
    clean gate draw of 14.4 against it on 2026-09-13, with the instruction to
    re-record with the gate draw folded in). The orchestrator's cloud runner, on
    CI's pinned environment, read `stress.py` ALL 87 at this same head. **Not
    re-recorded here**: folding a 14.4 draw into `winter/cycle` raises a value in
    `tests/stress_budgets.json`, and a raise in any `*_budgets.json` is posted on
    #201 before the push and merges only on tvofi's approving review
    (`budget-raise-gate`); a seat that cannot post there hands the decision up
    rather than making it. CI's `stress.py` at the PR head is the authority; if
    it reds on this arm, the honest route is the docstring's re-record under
    that gate, not a code change, because what this diff allocates per result
    is a few step-length float arrays and one list of 96 booleans in the batch
    owner — kilobytes, against a 0.4 MiB median shift. Cheaper detector: none — the arm is
    the detector; process state **(c)** for the record, which was taken as the
    recorder prescribes and still under-samples this scenario.
  - *CPU: contention, and it did not reproduce.* `shoulder/tariff+cycle` read
    291x against a 268x budget in the round-2 run, which started at 04:12Z while
    two peer seats on this Mac were driving `prepr.sh` and
    `derive_closures.sh --single` against the same repository (their processes
    are in this seat's `ps` output at 04:29Z, and the shared repo's background
    `git gc` is in its log). The same lane at the same head read `rc=0 failed=0`
    in the pin lane at 02:3x, and reads **ok in 482 s** in the round-3 gate with
    the box to itself (`ev/gate_round3_head.log`), and ok at the code head —
    `254.3x its 52.4 ms reference; budget is 268x` (`ev/gate_head.log`). The ratio is a CPU-time measurement against a reference
    measured beside it, so it is the reference — 54.5 ms, a single short solve —
    that a contended box distorts. Nothing is re-recorded: a budget this box
    cannot measure honestly under load is not this box's to move, and CI records
    and grades these on its own platform.

## Forward-carry

`.claude/workflows/carry-1644.json`, created in this diff, is the destination:
`brief_lint.mjs` reads it at 0 errors and 0 warnings, and its `stage` names the
seats that route `coordinator.py`'s copy of the threshold through the owner
(round-9 F1.10) and that register the owner in the P2 registry (F1.11). Round-9's
roster already carries the route itself; what the roster does not carry, and what
this carry adds, is that **the route is not only a call edit** — the docstring
above `_observe_compressor_start` (`coordinator.py:9997`) says "The threshold is
the optimizer's own on/off convention (half the pump's minimum electrical power),
so the counter and the plan agree about what 'running' means", and the second
clause is false once the owner exists: the counter's convention is
`on_threshold_kw`, half the modulation floor, and the plan's is
`MIN_RUNNING_DRAW_KW`, 0.1 kW, and they differ on purpose, which is the fix. A
route that moves the call and leaves the sentence publishes a claim the code
contradicts, in the file class I5 audits and in the shape the D6 claim register
verifies for docs — the register caught exactly this falsification in
`docs/ecl110.md` inside this PR, and no static lint reads prose, so the carry is
what tells the routing seat.

The control the next stage needs is in the carry and measured here: on a plant
whose `min_electrical_power` is 0.4, `on_threshold_kw` returns 0.2 while
`MIN_RUNNING_DRAW_KW` is 0.1, so a 0.15 kW step is a run to the plan and is not
one to the meter — the disagreement the block's null arm pins. F1.11's registry
entry needs no change: the RCA prototype at `3938c8ea` already names
`thermal_model.py::on_threshold_kw`, which is the module and name this PR
creates, and its `owners_lint` reads `owner_missing=0` at this head.

## Friction

- `fixer.md#3`: stale: the P2 class enumerator's dynamic perturbation arm (`tools/audit/round9/D14/sweep/P2/enumerator.py`, S1 @ `c44e7bcd60`) refuses at this merge base with `AssertionError: ('_derive_preset', 'two_zone=bool(current.get(CONF_UPPER_FLOOR_THERMAL_MASS)),')` — it recompiles a production function with one source line replaced, and #1724 replaced that line. Its `--seams` and `--selftest` arms run and its probe arms read 0, so the class is still measurable, but step 8's "run the enumerator at base and head" has one arm fewer than the sweep had, and every class enumerator whose perturbation is keyed to one commit's source decays the same way as the tree moves. Not repaired here: the enumerator is the sweep's record, and this PR is not its owner.
- `fixer.md#3`: unclear: step 3's companion rule is written for a harness that "measures what the fix rightly leaves alone" and so reads flat at both ends. D8-s1-03 is the opposite shape — the fix changes the owner the harness's own route reads, and the harness's grid no longer reaches the band it was written for (0 steps in 20 arms at this merge base against the finder's 4). What discharged it was a pin on the owner, inside the census that already covers every publisher (#1499's), rather than a second harness; the rule does not say which of those a seat owes when the mechanism is live and the instance is not.
- `fixer.md#2`: cost: `mutation_table.py --pin-killed` runs a baseline for every driver in play before it drives any mutant — 19 drivers, 3657 s of baseline (61 min, `tests/features.py` alone 966 s and `tests/stress.py` 616 s) in a lane whose 11 sites each need at most one kill, and the whole lane ran 115 min. Cheap-first ordering is per mutant, not per lane, so a diff that adds one site pays the same fixed cost as one that adds eleven. The lane's own `--scripts` option narrows the net to named drivers, and this branch's second run used it for the two re-anchored sites (one baseline, 665 s, `ev/mutation_pin_r4.log`); `fixer.md` does not say when a net narrowed to the driver a mutation proof already measured killing the site is enough, so the first run paid for all 19.
- `fixer.md#9`: unclear: step 9 tells a seat to correct a claim it finds to be wrong and step 8 tells it to enumerate the class's seams, but neither names the tree's own claim verifier — `tools/audit/round4/D6/claims.py`, 125 claims whose evidence is often a source-text assertion — as a place where changing a production line falsifies a documented claim. Grepping the package for the rule this PR changed found every code seam and no document; the D6 lane found `docs/ecl110.md` in 8 s, at the cost of a red `harness_headers` and a re-run. A step-8 line naming the D6 register as a seam rule for any change to a documented behaviour would have put it in the first pass.
- `fixer.md#3`: unenforced: round-9's evidence harnesses became in-tree instruments at #1769, and nothing runs them — `tools/audit/` is INERT by prefix and `tests/harness_headers.py` reads headers only — so a production fix can break one silently. This PR found and updated the one its own diff broke (`mode_domain.py:173`, above) by grepping for every symbol it renamed or re-signatured; a fix that does not grep leaves the breakage for whoever re-runs the harness next, and a cheap compile-or-import lane over `tools/audit/round*/**/*.py` would have named it instead.
