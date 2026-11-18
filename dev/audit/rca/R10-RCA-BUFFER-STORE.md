# RCA: a buffer store absent from the single-zone step

Group R10-BUFFER-STORE (#2499, #2500), class **P2** — *one fact decided twice by
divergent predicates: a guard at one seam, missing at its sibling* (`P2` is
`barriered` in `dev/audit/config/bugclasses.json`). Measurements are at the merge
base `3b4180dcc` and at the fix's head; the fix is on
`handoff/r10-buffer-store`.

**Disclosure.** `dev/governance/roles/root-cause.md` requires the root cause *"in
parallel, and in a separate seat"*. This group's roster next step was `rca` and
the seat brief delivered it to the group's own fixer, so that independence is
**not** obtained. The fix reviewer should read this document adversarially, in the
spirit the separate-seat rule exists for.

## Result

- **Cause.** The single-zone step had no valve branch at all — recorded in the
  base's own docstring — and the terminal-cost store credit sat inside
  `if params.two_zone_enabled:`. A 750 L buffer behind a manual valve, the
  configuration the options page offers to every install, therefore planned
  exactly as if no tank existed.
- **Process state.** (c): the process existed and was followed; it did not
  produce the intended result.
- **Cost test.** Passes by roughly four orders of magnitude. Census built, not
  refused.
- **Countermeasure.** A census of the tank's three live store capabilities in
  **both** zonings, in `tests/features.py`, registered in `_P2_CENSUSES`
  (`tests/entities.py`). Shown red at the merge base, green at head, and firing
  per arm in the zoning whose path was planted.

## Root cause

### Cause, reproduced

Two predicates decide whether a buffer tank is a store, and they disagreed.

1. **The step.** At `3b4180dcc`,
   `custom_components/heatpump_optimizer/thermal_model.py:3171-3175` says of
   `simulate_step`'s `valve_target` argument:

   > *"The single-zone model has no valve branch, so it is accepted and ignored
   > there rather than being a two-zone-only signature."*

   That is the defect stated as a design. `_simulate_step_single` took no
   `valve_target`, never read the valve, never moved the tank, never booked
   `_step_buffer_refused`.

2. **The objective.** In `optimizer.py`, `_settlement_caps` (base :5010) computes
   `caps["buffer"]` for **every** zoning — it carries no zoning guard — while the
   consumer of that cap, `if params.buffer_is_store:` (base :2599), is nested
   inside `if params.two_zone_enabled:` (base :2593). The fact was measured in
   both zonings and spent in one.

Reproduced with `dev/audit/harnesses/r10_buffer_store.py plans` (750 L manual
valve, 24 h, 15-minute steps, spread day; the arm's own no-buffer twin beside it):

| tree | arm | plan sha1 | space kWh | cheap-quarter share | tank rise | cost | buffer identical to no-buffer |
|---|---|---|---|---|---|---|---|
| `3b4180dcc` | spread, 750 L | `21d0378f2f79` | 22.63 | 0.965 | +0.00 K | 22.184 | **True** |
| `3b4180dcc` | spread, 0 L | `21d0378f2f79` | 22.63 | 0.965 | +0.00 K | 22.184 | — |
| head | spread, 750 L | `6a546df76556` | 22.41 | 1.000 | **+40.00 K** | **21.947** | False |
| head | spread, 0 L | `21d0378f2f79` | 22.63 | 0.965 | +0.00 K | 22.184 | — |

The base's buffer plan is **byte-identical** to its no-buffer plan: the tank is
not merely under-used, it is absent. At head the tank charges 40 K, moves every
space kWh into the cheapest quarter, and cuts the day's cost by 0.237 (1.07 %).

Null control (flat price = the day's mean, so no window to store for): at head
the tank rises **+0.00 K** in both the 750 L and the 0 L arm. The flat arms do
differ byte-wise from one another — a valve lowers the flow temperature to the
load at flat prices, which is a COP effect, not storage — but neither charges the
tank, so the +40.00 K on the spread day is arbitrage and not an artefact of the
new branch.

### Class search

The shape is P2, whose barriered barrier is *one owner per fact*. Its census
registry already covers eight facts (`two_zone_enabled`, `wood_furnace_on`,
`dhw_enabled`, `state_age`, `on_threshold_kw`, `entity_write_domain`,
`fenced_cycle_step`, `plan_running_rule`) and two earlier censuses (the #1747 DHW
block, the #1526 routing). The fact here — *"is this buffer tank a store?"* — was
not among them, and the class's own instances recur through R10 (34 in the round,
100 in the ledger over ten rounds).

The nearest sibling is inside the same function: `_settlement_caps` priced the
buffer in every zoning while the credit refused it in one. That is the P2
mechanism exactly, and it is the reason the census drives the **cap** as well as
the step and the objective: a barrier over only the step would have passed while
the credit stayed gated.

### Process state: (c) followed and did not produce the intended result

Not (b): no step was skipped. The base docstring records the behaviour on
purpose, and the repository's parity grid ran and passed on every pull request.
The process that was followed is `_grad_parity` in `tests/features.py`
(base :6608-6611):

```
_grad_parity(False, label="single-zone")                     # no valve
_grad_parity(True,  label="two-zone")                        # no valve
_grad_parity(True,  valve="manual", label="two-zone with valve")
_grad_parity(True,  wood=True, valve="manual", label="two-tank")
```

Three of the four zoning × valve cells. The fourth — single-zone **with** a
valve — was never constructed. Every other valve-armed fixture in the base's
tests has the same bias: of 33 `ThermalParameters(...)` constructions that set
`mixing_valve_mode`, 32 also declare `two_zone_enabled=True`; the one that does
not (`tests/features.py:7787` at `3b4180dcc`) feeds `battery_view.build` and never
steps the thermal model. The grid's cells were chosen as "the valve belongs to
the two-zone path", which is the same assumption the defect encodes — so the
tests could not see it.

Not (d): the precondition never changed. `config_flow.py:1694` and `:2900` at the
base offer `CONF_BUFFER_TANK_VOLUME` and `CONF_BUFFER_MAX_TEMP` with **no `when=`
gate**, unlike the wood options at `:1697-1700`, which are gated on
`wood_furnace_on`. A single-zone install has always been able to configure a
buffer tank. Nothing moved underneath the process; the process never covered the
product's configuration surface.

### Cost test

`cost(countermeasure, recurring) < cost(defect) × P(recurrence)`, wall-clock per
release.

- **`cost(countermeasure, recurring)`.** The census runs inside
  `tests/features.py`: **0.001 s median** marginal over three runs, **0.031 s**
  worst, on a machine at load average 156. `tests/features.py` runs once per
  gated pull request; measured **2,338 merges over the 7 release intervals
  `v6.7.12..v7.0.4` = 334 per release**. Standing cost **0.33 s per release**
  (median), **10.4 s** at the worst sample.
- **`cost(defect)`.** The round-9 per-finding fix cost, **4.35 h = 15,660 s** per
  occurrence (`#1718`: 21.75 h over 5 findings).
- **`P(recurrence)`.** The class ledger carries **10 instances per round** (100
  over 10 rounds) and the tree carries **152 release tags over those 10 rounds =
  15.2 releases per round**, so **0.66 instances per release**.
- **Verdict.** 15,660 × 0.66 = **10,336 s per release** against **0.33 s** — the
  census pays for itself about **31,000×**; against the worst-case standing
  sample it still pays about **1,000×**.
- **The direct user cost is the reason the class matters, and it is not in the
  wall-clock test.** It is 0.237 per day (1.07 % of the day's cost) on the
  harness's synthetic 750 L install at 0 °C — every day of a heating season, for
  every install that configured a buffer without two zones.

### Countermeasure

A **census**, in the P2 barrier's own form (`_P2_CENSUSES`), addressing (c) by
comparing the fact across the product's configuration domain instead of trusting
that the grid's cells were the domain.

`tests/features.py:_zoned_store_capabilities(two_zone)` builds one zoning's
parameters and returns three numbers read off the production seams:

1. the tank's response to a configured valve — valved step minus identical
   unvalved step (K);
2. the heat the cap refuses while charging past `buffer_max_temp` (kW);
3. the terminal cost's credit for a tank left at 60 °C rather than 30 °C.

Each arm asserts the capability is **live in every zoning**. Three
`R.check`s, texts:

- `zoned store census: the valve moves the tank in every zoning (#2500)`
- `zoned store census: the cap books what it refuses in every zoning (#2500)`
- `zoned store census: the terminal cost credits the tank in every zoning (#2500)`

All three texts are listed in `tests/entities.py:_P2_CENSUSES` under
`zoned_store_valve_live`, `zoned_store_cap_live` and `zoned_store_credit_live`, so
a check text that vanishes is refused (`CENSUS-MISSING`) rather than silently
retiring the barrier.

**Demonstrated to detect** (the head's `tests/features.py` run against each
production tree):

| tree | valve arm | cap arm | credit arm |
|---|---|---|---|
| `3b4180dcc` (base) | **FAIL** single-zone +0.0000 K, two-zone +0.1973 K | **FAIL** single-zone 0.0000 kW, two-zone 1.5947 kW | **FAIL** single-zone 0.0000, two-zone −17.3299 |
| head (fixed) | ok +0.2744 / +0.1973 K | ok 3.4614 / 1.5947 kW | ok −17.3299 / −17.3299 |

**Per-arm, per-zoning controls** (plant one zoning's path, restore, re-run): each
arm must fire on the zoning that was broken and stay green on its sibling — a
census that only echoed the single-zone arm would pass the base/hand comparison
above while being blind to a regression in the two-zone path:

| plant | valve arm | cap arm | credit arm |
|---|---|---|---|
| C1 single-zone valve branch off | FAIL (SZ +0.0000 K) | FAIL (SZ 0.0000 kW) | ok |
| C2 two-zone step blind to the valve | FAIL (TZ +0.0000 K) | FAIL (TZ 0.0000 kW) | ok |
| C3 credit gated to two-zone only | ok | ok | FAIL (SZ 0.0000) |
| C4 credit gated to single-zone only | ok | ok | FAIL (TZ 0.0000) |

In every plant the untouched zoning's figure is exactly the head's live value, so
the arms are independent of one another and of zoning order.

**Bound.** The census costs 0.001 s median, adds no production code, and
`tests/structure.py` moves no metric (the scoped gate's `structure.py` arm is
attached to the handoff). Architecture: no production file grows; the
countermeasure is test-only.

### Recorded refusal

No exhaustive option-grid barrier. The obvious generalisation — step every
`ThermalParameters` option vector in every zoning — is combinatorially
infeasible in a gate script (the parameter set is dozens wide, and the
two-zone/valve/wood/tank product alone is four cells, which is what this census
covers). The class is `barriered`, so a barrier is owed; the form chosen is the
targeted census the P2 barrier already uses, and the refusal is of the
whole-option-space form, not of the barrier.
