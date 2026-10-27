R10-COP-PARTLOAD: price the compressor's power in COP, off by default

`ThermalModel.compute_cop` priced a heat pump's efficiency from outdoor
temperature, humidity and flow or tank temperature only. Electrical power entered
every heat conversion as a plain multiplier, `heat = cop * power`, so the model
called a compressor equally efficient at its modulation floor and at its maximum
— where the heat-exchanger approach the power sets has grown. A plan therefore
priced heat it could not deliver at the power it chose.

`ThermalParameters.cop_partload_derate` (options flow
`heat_pump_cop_partload_derate`, default 0) is the share of COP lost at maximum
power against the floor, linear across the band.
`thermal_model.delivered_heat_kw` applies it at the seven priced forward
conversions — the scalar and batch space-heat steps, the full hot-water
trajectory, `extend_dhw_temps`, and the optimizer's buffer charge ceiling — so
the plan's cost and its heat both see the fall. At the default 0 the helper
returns `cop * power` unchanged, so no existing install's plan moves.

The root-cause analysis is `dev/audit/rca/R10-RCA-COP-PARTLOAD.md`: the defect's
measured size, its process state with the evidence, the cost test, and the
forward-carried inverse conversions.

## Head

`775ae0340b1735db77bafe3d6a5d79e992706171`

The code under measurement is tree
`1ce05f7cc9f63f1afe7e5b11e76960b4da8775c5`; the seven commits after it touch the
golden fixture, the D6 claim counts, the mutation ledger, the closure record,
two audit header blocks and the RCA, and move no production code.

## Mutation proof

Run against the real `tests/features.py` — 4 466 checks — by a runner that
restores every file with `git checkout --` afterwards.

**R1, the factor itself deleted** (`partload_factor` returns 1.0, so every site
prices the flat law the defect shipped): `7 of 4466 FEATURE CHECKS FAILED` —
the factor, the pump heat, the scalar step, the buffer ceiling, the flat-price
plan and both hot-water checks, and only those. The configured-derate check
passes, as it must: it drives `from_config`, not the factor.

**R2, five site-level mutants in one run**, each owning a different check, so a
failing name is attributable to one mutant — the ceiling priced `max_power *
cop` again, the two-zone scalar step left plain (the second of the two
identical step blocks, so the single-zone twin stays wired), both hot-water
conversions left plain, and the range predicate forced true: `6 of 4466
FEATURE CHECKS FAILED`, one group per mutant:

- `batched simulation is bitwise-identical: two-zone part-load derate` and
  `batched jac == scipy 2-point FD bit-for-bit on free variables: two-zone
  part-load derate` — the two-zone twin, through the batch and its gradient
- `a configured derate inside [0, 0.5] is taken; a negative, oversized,
  non-numeric or NaN one refuses to the 0 default` — the range predicate
- `the buffer's charge ceiling prices the pump's max-power output with the
  derate: a derated pump stops charging at a cooler tank in deep cold` — the
  ceiling
- `a hot-water schedule carries the derate too: ...` and `the full
  trajectory's hot-water track prices the same conversion as the step twin:
  ...` — the two hot-water conversions

R1 says the fix's line is load-bearing; R2 says every site is pinned by its own
check rather than by a neighbour's.

## Unpinned sites

`ci_predict.py --base origin/main` lists ten sites the diff adds; every one is
in `custom_components/`, which is the lane `mutation-autofix` drives, so each is
pinned by that job from its own kill rather than by a claim here:

- `custom_components/heatpump_optimizer/optimizer.py:5073 RETURN_DEL`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/thermal_model.py:1738 CMP_BOUND*2`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/thermal_model.py:1738 GUARD_OFF`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/thermal_model.py:1740 RETURN_DEL`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/thermal_model.py:1751 CMP_BOUND`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/thermal_model.py:1751 GUARD_OFF`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/thermal_model.py:1755 CLAMP_DROP*3`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/thermal_model.py:1756 RETURN_DEL`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/thermal_model.py:1766 GUARD_OFF`: pinned by mutation-autofix
- `custom_components/heatpump_optimizer/thermal_model.py:1768 RETURN_DEL`: pinned by mutation-autofix

## Null control

With the derate at its default, the branch's plans are the merge base's, not
merely close: 32 of 32 plan hashes identical, over 16 synthetic installs of
R10-SETPOINT-BOOST at a spread and a flat price day and five pricing
configurations, each hash taken from `simulate_trajectory_with_dhw` and printed
by the same harness run against a worktree at the merge base (`term in tree
False`) and against this head (`failures 0`). Both arms print the same three
score summaries.

The feature's own checks carry the same control in miniature: at 1.5 kW — the
modulation floor, where the factor is 1 by construction — the derated and plain
arms agree exactly, so a check that would fire on any perturbation of the step
does not fire there.

## Figures

- `partload: grid 27 plants; ratio at p_max >= 0.808, at p_min >= 0.985` — the
  worst plant loses 19.2 % of its COP at maximum power.
  `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r10_cop_partload.py`
- `solves: central plant derate 0.112` — the central plant of that grid.
  Same command.
- `spread term vs none: cost per plant kWh change min -0.0598 max -0.0094 cells
  cheaper 16 dearer 0` — pricing the fall takes 0.94 % to 5.98 % off the cost
  per delivered kWh on price-spread days, on all 16 installs. Same command.
- `spread d=0.0: cells 16 heat short max 0.1093` and `spread d=0.112: cells 16
  heat short max 0.0822` — the plan delivers at most 8.2 % less heat than it
  promises instead of 10.9 %. Same command.
- `flat term vs none: cost per plant kWh change min -0.0754 max +0.0046 cells
  cheaper 10 dearer 4` — the flat-price day, where shaping buys no price: the
  term is not a one-way gain, which is why it ships off by default. Same
  command.
- `32 of 32 plan hashes identical` between the merge base and this head at
  `d=0` — the null control above. Same command, run in a worktree at
  `3b4180dcc`.
- The feature block costs 1.92 s CPU per `tests/features.py` run, median of
  three, measured by `$EXPORT/probe/pl_block_cost.py` (sha1 `fc6e9af30290`) —
  what the eight checks and two parity cells cost the suite every run.
- `60 sites in the package where a COP meets a power or a heat` — the class's
  seam rule, so the fix is not a search for the one instance: 7 priced forward
  conversions route through `delivered_heat_kw`, 2 are the helper's own lines,
  29 call the COP law itself, and the other 22 are dispositioned one group at a
  time in `dev/audit/rca/R10-RCA-COP-PARTLOAD.md` §5, with the four inverse
  conversions carried forward below.
  `$EXPORT/probe/cop_seams.py custom_components/heatpump_optimizer` (sha1
  `c628396caf3c`)

## Red checks

The scoped gate at the code head (`GATE_SCOPE=auto PREPR_SKIP_CLOSURES=1
./tests/run.sh`) printed `MODE: SCOPED -- 30 script(s) run, 3 scoped out` and
six scripts red. Classified by running the same script at the merge base
`3b4180dcc` in a scratch worktree, except the optimality one, which the file
itself records:

- `tests/golden.py`: 55 of 56 scenarios differ, and the unmodified merge base
  prints the same 55 names, compared as sets. The fixtures are the canonical
  environment's values; this host's solver reaches other optima. The one
  scenario this branch changes, `config_flow`, is `ok`. Not this branch's.
- `tests/stress.py`, `shoulder: cheaper than holding the setpoint [4.67 vs
  3.96]`: identical at the merge base. Not this branch's.
- `tests/optimality.py`, the `summer_negative|shoulder` claim: the file records
  that "the gate's platform is the one that counts, so this claim reads stale
  on arm64 only" (`tests/optimality.py`, the claim's note). Not this branch's.
- `node tests/card.mjs`: V8 heap OOM at ~2045 MB after ~166 s, reproduced at
  this head and at the merge base (1288 checks pass, then the abort). Not this
  branch's.
- `tests/harness_headers.py`: the three header counts this branch's option
  moves — 202 fields, 235 schema keys, 92 ranges — which `dc67636b2`
  re-measures in the two blocks the assertion reads. Re-run at this head:
  `ALL 112 HARNESS HEADER CHECKS PASSED`.
- `tests/stress.py`, the production-call channel: **this branch's**, and the one
  red that needs the owner. 13 scenarios grow 1.050x to 1.064x past the 1.05
  allowance on work their counts vouch at 1.000x, and the merge base does not
  fire it. The growth is `delivered_heat_kw`'s one call per heat conversion,
  which is the point of the change: the alternative is `cop * power` written at
  nine sites, the divergence the fix exists to remove. The CPU kernels stay
  inside their 3.0x factor, so this channel is the only one that sees a call.
  The channel's own rule is that a legitimate firing passes for one pull
  request, never by a raise, on the owner's approving review naming the merge
  and the measured growth.

- `budget-raise-gate`: red until the owner approves
  `tests/structure_budgets.json`'s `class_excess_loc` 18079 -> 18082 at this
  head (the raise, mandate scope all; the justification is below). Answer: no
  cheaper detector exists for this rise. A check that could tell an irreducible
  config surface from verbose growth would have to price each new line against a
  counterfactual shape, which no static read can do; the alternative — an
  allowlist of blessed lines — is the drift machine the RCA's §3 refused at a
  53-entry standing cost, and the per-PR owner judgement this gate already makes
  is the cheap end of that trade.
- `mutation`: red at this head, and this branch's own. The command is
  `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`;
  it exits 0 and prints ten `PREDICT tests / mutation ADDED UNPINNED` lines and
  `CI PREDICT: 10 unpinned site(s) the diff adds -- a warning; the body owes
  each a line under ## Unpinned sites`. `prepr.sh` step 6d feeds that list to
  step 7, which adds `mutation` to the reds (`body_line`'s seventh argument), so
  the reviewed head carries the red until `mutation-autofix` writes the ten
  dispositions after the push, which is what `ci-autofix.md` intends. The ten
  sites are the ones listed under `## Unpinned sites` above — nine in
  `thermal_model.py`'s derate helpers and one the optimizer's ceiling — and all
  are in `custom_components/`, the lane that job drives. Answer: no cheaper
  detector exists. A pin's claim is "some check in the suite fails when this
  operator is applied", which only running the suite against the mutant
  establishes; this tree's own measurement records 22 checks that executed the
  line they were named for and pinned nothing and 25 production guards
  deletable with no check failing (`tests/mutation_table.py`'s header), and a
  coverage delta prices both at zero and detects neither. The pins' standing
  cost is one disposition row per site, keyed on the line's content anchor
  rather than its number, each driven by the single script whose recorded
  closure reaches the file. R1 and R2 above already show each site is killed by
  a named check, so the pins record kills that exist rather than buy new work.
  The alternatives priced here are worse: the 53-entry census refused in
  `dev/audit/rca/R10-RCA-COP-PARTLOAD.md` §3 costs 53 re-justifications on every
  move, and the metered slope detector needs the heat meter whose absence is why
  the term defaults to 0.

## Forward-carry

- The inverse conversions still close the loop with `heat / cop`:
  `dhw_planner._plan_dhw_min_cost`, `_clamp_dhw_to_capacity`,
  `optimizer._compute_baseline_power` and `coordinator._dhw_setpoint_sweep`.
  With a derate the forward relation is quadratic in power, so the closed form
  understates the electrical power needed to deliver a given heat by up to the
  derate; the exact form is the positive root on the band, and at the default 0
  the current ones are exact. Every setpoint a plan holds is still met because
  the ceiling and the step share the helper, so this is a cost-accounting
  inaccuracy, not a control error.

  Carry: R10-COP-PARTLOAD
- D2's item 2 says which quantities the COP step sweeps, and power is not among
  them, so eight rounds of that step passed a law with no power term (the RCA's
  §2). The countermeasure is one sentence in the brief: derive the priced
  formula's inputs from the device's own control surface and mark each a
  modelled term, a documented constant or out of scope. It is policy
  (`dev/governance/dimensions/D2.md`) and the owner approves it; this seat did
  not edit it.

  Carry: R10-COP-PARTLOAD

## Friction

none

## Architecture score

Architecture score: dS +0.0000 NULL (`tools/audit/archscore/score.py --diff`,
merge base `3b4180dcc`; no archscore metric rose, and the one structure-budget
rise is explained below).

## Raise justification

`tests/structure_budgets.json` rises `class_excess_loc` 18079 -> 18082, and the
three lines are irreducible — the `cop_partload_derate` field on
`ThermalParameters`, its row in `_tabled_values`, and its validation call in
`from_config`. The parameter cannot exist without all three, and moving a
dataclass field out of its class trades the metric for a worse one.

Payments tried: measured on this head's tree (`f916a3279`, re-taken for this
body), written the naive way — the two helpers as class methods, the options row
at the three-line shape its neighbours use, the ceiling's single-use `p_max`
local kept — the tree reads 18111; as shipped it reads 18082. The shape pays 29
lines and the rise over `3b4180dcc` is 3, not 29.

Architecture score: dS +0.0000 NULL
