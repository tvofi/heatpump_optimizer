# R10-RCA-COP-PARTLOAD: the COP law priced no compressor power for six releases

The root-cause analysis for #2501. `dev/governance/roles/root-cause.md` wants it in
a separate seat beside the fix. The orchestrator directed this one instead: the
group's next step is `rca`, and the fixer seat wrote it, so the independence the
contract asks for is weaker than usual and the reviewer should weigh that when
reading §2.

**Defect.** `ThermalModel.compute_cop` / `_cop_law` priced COP from outdoor
temperature, humidity and flow or tank temperature only. Electrical power entered
the model as a plain multiplier, `heat = cop * power`, at every step site, so the
pump's efficiency was flat across its whole modulation band although the compressor
is the machine whose power sets the lift across the heat exchangers. The law
shipped in the initial release `ec45dc4d5` (2026-04-03, v1.0.0) and through v7.0.4.

**Measured size.** On a 27-plant synthetic grid
(`dev/audit/harnesses/r10_cop_partload.py`), COP at max power is 0.808 of the
no-term law's at worst — 19.2 % lower — and 0.985 at the floor; the central plant
loses 11.2 %. On the 16 synthetic installs of R10-SETPOINT-BOOST, a planner that
prices the fall plans 0.94 % to 5.98 % cheaper per delivered kWh on price-spread
days, 16 of 16, and its plan delivers up to 8.2 % more of the heat it promises
instead of 10.9 %.

## 1. Cause

The law was written from the refrigerant cycle — a Carnot fraction across the lift
— and the house's flow curve. Both are temperature quantities, and every
monotonicity check in the tree is a temperature sweep. Power is a *control*
quantity: the solver chooses it. Nothing in the law noticed that delivered heat at a
chosen power is not the same product at every power, and one accident hid it:
`min_electrical_power` and `max_electrical_power` were already parameters, used by
the floor guards and the capacity envelope, never by the COP law itself.

The tree has added one COP determinant it lacked before — `flow_lift_factor`,
#1067, `3b9e7b668`, 2026-09-17 — which shows the shape is not foreign here: a
missing term arrives as a fix, found by the feature that needed it, not by the audit
step that was supposed to look for it.

**Class search.** The mechanism is *a priced conversion that every sibling formula
makes without one of its inputs*. The siblings agree, so it is not P2 ("one fact
decided twice by divergent predicates"); there is no floor or divisor, so it is not
P3. No entry in `dev/audit/config/bugclasses.json` covers it. It is recorded here as
a first instance, not as a class; if it arrives twice more the register owns it.

The forward-conversion census (`$EXPORT/probe/cop_seams.py`, sha1 `c628396caf3c`)
found 60 sites in the package where a COP meets a power or a heat. Seven are the
priced forward conversions and route through one helper; the other 53 are
dispositioned in §5.

## 2. Process state: (c), followed and did not produce the intended result

D2's item 2 reads: "COP monotone in outdoor and flow temperature, Carnot fraction
within the stated band, every derate in [0, 1], defrost derate bounded and continuous
at the band edges, capacity envelope never below demand-at-derate without a reason
code." Every round from 3 to 10 has a D2 scope report, and round 10's scope 2 is the
COP step.

That step ran, and its report is honest: `dev/audit/rounds/round10/D2/s2/REPORT.md`
sweeps `compute_cop`, `_cop_law`, `flow_lift_factor`, `compute_cop_dhw`, `_batch_cop`
and the defrost derate over outdoor −35–40 °C, flow and tank 10–80 °C, three plant
modes and 40 learned derates, and its findings and non-findings are all monotonicity
in temperature and bounds on the derate *values*. Nothing in it varies compressor
power, because the item's text lists the quantities to sweep and power is not among
them. The item's second half — "capacity envelope never below demand-at-derate" — is
filed under **Unfinished** in that same report, and that is the half that needs
delivered heat at a power.

Nine rounds of the step therefore passed while the law had no power term. The defect
was found instead by D0's demand analysis, in another dimension, from a hypothesis
about price swings.

Not (a): the step exists. Not (b): it ran, and its harness is in the tree. Not (d):
no precondition moved — both power parameters were in the dataclass at v1.0.0, and
the item never named power. The state is (c): the step's unit, a sweep over the
quantities the item names, cannot detect a quantity the item omits.

## 3. Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, wall-clock per
release cycle.

- **cost(defect).** The lower bound is the round-9 per-finding fix cost, 4.35 h
  (#1718: 21.75 h over 5 findings), which excludes the finder, verify and judge
  seats: 15 660 s. The field cost is the mispriced plan above; it is money, not
  wall-clock, and is not counted here.
- **P(recurrence).** Two arrivals of "a COP determinant absent from the law" in the
  law's life — power (this one) and the flow-curve lift (#1067) — over 152 release
  intervals: 152 tags from `v2.3.0-beta.1` to `v7.0.4`, 151 intervals, plus the
  untagged `v1.0.0` interval. P = 2/152 = 0.013. On the single arrival the
  conservative figure is 0.0066.
- **Expected defect cost.** 15 660 x 0.013 = 206 s per release (103 s on one
  arrival).
- **The countermeasure.** One sentence in D2's item 2: derive the priced formula's
  inputs from the device's own control surface — outdoor temperature, humidity,
  flow or tank temperature, electrical power — and mark each a modelled term, a
  documented constant, or out of scope. One sentence in the brief and about a minute
  in each D2 scope that prices a formula; one such scope per round, so 60 s per
  release.
- **Verdict.** 60 s < 206 s, about 3.4x. Thin, and it rests on two arrivals, so it is
  recorded as a request to the owner, not as a settled change.

Two other countermeasures were priced and refused:

- **A census check in `tests/features.py`** that every COP-by-power product routes
  through `delivered_heat_kw` or a declared exception. Standing cost under a second,
  but the exception list is 53 entries a reviewer must re-justify on every move, and
  it pins a list rather than the property. Refused: it buys a list that drifts.
- **A metered slope detector**, comparing the model's COP fall with
  `flow_meter.cop_evidence`'s observed COP against measured power. It needs a heat
  meter, which is exactly why the term defaults to 0. Refused on that ground.

## 4. Countermeasures

**Built, in this pull request.**

1. The term, off by default, at the seven priced forward sites:
   `_simulate_step_single`, `_simulate_step_two_zone`, both branches of
   `simulate_trajectory_batch`, `simulate_trajectory_with_dhw`, `extend_dhw_temps`,
   and the optimizer's `_buffer_charge_ceiling`. The two public step entry points
   and `simulate_dhw_only` inherit through these.
2. Its null controls: a zero derate is exactly `cop * power`, asserted bit-for-bit;
   and the branch's plans at zero derate are byte-identical to the merge base's —
   32 of 32 plan hashes, spread and flat, 16 synthetic installs each.
3. Pins that a future removal fails: six checks in `tests/features.py` (factor,
   heat, step, config, ceiling, flat-price peak share), two more for the hot-water
   sites, and two gradient-parity cells; mutation-proven in §6.

**Proposed to the owner (policy, not edited by this seat).** The D2 item 2 sentence
in §3. It addresses state (c): the step's unit is a sweep, so the fix is a
derivation step before the sweep, not a firmer instruction. `dev/governance/` is
policy; the owner approves it before merge.

**Recorded refusal.** A class-wide census — "list every priced formula's actuators"
— refused on the numbers in §3. Whether the shape becomes a
`dev/audit/config/bugclasses.json` entry is the owner's call, not this seat's.

## 5. Seams not routed through the helper, and why

Of the 60 sites: 7 are the priced forward conversions (§4.1); 2 are the helper's
own lines; 29 are calls to the COP law itself, which get the term through the law
and need no site change — one of those, `sysid._valve_drive`, is also an inverse
conversion; and 22 are other conversions:

- **Inverse (power from heat), 4 sites** — `dhw_planner._plan_dhw_min_cost` and
  `_clamp_dhw_to_capacity`, `optimizer._compute_baseline_power`,
  `coordinator._dhw_setpoint_sweep`. With a derate the forward relation is quadratic
  in power, so the closed form `heat / cop` understates the electrical power needed
  by up to the derate. Making them exact is a separate change — the positive root of
  `c2 P^2 - c1 P + Q/cop = 0` on the band — and is carried forward rather than done
  here; at the default 0 they are exact.
- **Nameplate and design sizing, 6 sites** — `design_power = p_max *
  cop_nominal_floored` in `thermal_model.flow_target_for_indoor`,
  `_simulate_step_two_zone`, `_substeps_and_loss`, `simulate_trajectory_batch`,
  `optimizer._compute_baseline_power` and `sysid._held_state`. A plant constant that
  calibrates emitter UA, not a delivered-heat claim at a chosen power; folding a band
  share into it would double-count the derate against the UA it calibrates.
- **Measurements, 3 sites** — `flow_meter.cop_evidence` (two lines) and
  `coordinator._fold_capacity_envelope`. These read measured power; the derate is a
  model assumption.
- **Bounds and detectors, 2 sites** — `coordinator._max_pump_rise` uses
  `max(cop, 1.0) * p_max` deliberately as a loose upper bound for recognising an
  external heat source, and `sysid._size_step_power` bounds a step. Both are looser
  than the model on purpose; tightening a detector with an assumed plant term would
  raise its false-positive rate, not its accuracy.
- **Learning samples, 2 sites** — `sysid.SystemIdentification.step`. The fit reads
  the plan's power and the model's COP to infer UA; folding an assumed derate into
  the claimed heat would make the learned UA absorb the assumption.
- **Other converters or non-conversions, 5 sites** — `battery`, `pv`,
  `wood_fuel`, `topology`'s error estimate, and `dhw_planner`'s retained-fraction
  division. Not the heat pump's COP.

## 6. Mutation proof

Run against the real `tests/features.py` — 4 466 checks — by
`$EXPORT/probe/pl_mutants.py` (sha1 `8d3b2796f2ec`), which restores every file
with `git checkout --` afterwards.

**R1, the factor itself removed.** `partload_factor` returns 1.0, so every site
prices the flat law the defect shipped. Seven of 4 466 checks fail, and they are
exactly the seven that need the term: the factor, the pump heat, the scalar
step, the buffer ceiling, the flat-price plan, and the two hot-water checks. The
configured-derate check passes, as it must — it drives `from_config`, not the
factor — so the run fails its own checks and nothing else:

```
=== R1: 7 failing checks
  FAIL the part-load factor is 1 at and below the modulation floor, ...
  FAIL pump heat at max power carries the derate and at the floor does not; ...
  FAIL a step at max power warms the slab less with the derate on, ...
  FAIL the buffer's charge ceiling prices the pump's max-power output ...
  FAIL at a flat price the derate moves the plan off max power ...
  FAIL a hot-water schedule carries the derate too ...
  FAIL the full trajectory's hot-water track prices the same conversion ...
=== R1 summary: 7 of 4466 FEATURE CHECKS FAILED
```

R1 is the fix's line deleted. It cannot say *where* the term is missing, because
it removes the term everywhere at once.

**R2, five site-level mutants in one run**, each owning a different check, so a
failing name is attributable to one mutant: the optimizer's ceiling computes
`max_power * cop` again; the two-zone scalar step is left plain (the second of
the two identical step blocks, so the single-zone twin stays wired); both
hot-water conversions are left plain; and `_partload_derate`'s range predicate is
forced true. Six checks fail, one group per mutant — the two-zone twin through
the batch and its gradient, the predicate, the ceiling, and the two hot-water
conversions — so no site is pinned by a neighbour's check:

```
=== R2: 6 failing checks
  FAIL batched simulation is bitwise-identical: two-zone part-load derate
  FAIL batched jac == scipy 2-point FD bit-for-bit on free variables: ...
  FAIL a configured derate inside [0, 0.5] is taken; ...
  FAIL the buffer's charge ceiling prices the pump's max-power output ...
  FAIL a hot-water schedule carries the derate too ...
  FAIL the full trajectory's hot-water track prices the same conversion ...
=== R2 summary: 6 of 4466 FEATURE CHECKS FAILED
```

R1 says the fix's line is load-bearing; R2 says each site is load-bearing on its
own. Neither run is a search for the defect's instance: §1's census is the seam
rule, and §5 dispositions every seam it returns.


## Reproduce

- Harness: `PYTHONPATH=tests/hastub:custom_components:tests python3 -u dev/audit/harnesses/r10_cop_partload.py`
- Base arm: the same harness with `PYTHONPATH` on a worktree at `3b4180dcc`, where
  it prints `term in tree False`, the same 32 plan hashes and the same three score
  summaries for the d=0 arm.
- Census: `$EXPORT/probe/cop_seams.py custom_components/heatpump_optimizer`.
- Standing cost of the feature block: `$EXPORT/probe/pl_block_cost.py`
  (sha1 `fc6e9af30290`), 1.92 s CPU per run, median of three.
- Mutants: §6.
