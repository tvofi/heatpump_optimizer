# D2-s2 report (round 10, D2.M2 COP and derates), baseline 17f1c55fad1b

Harness: `dev/audit/rounds/round10/D2/s2/cop_laws.py` (run from root, PYTHONPATH=tests/hastub; `--perturb` arm).

## Method
Swept `ThermalModel.compute_cop` / `_cop_law` / `flow_lift_factor` / `compute_cop_dhw` / `_batch_cop`
and `defrost.DefrostDerate.factor` / `derate_from_duty` over outdoor -35..40 C (0.05 K), flow and
tank 10..80 C, three plant modes (default, cop_flow_carnot, flow_curve_cop), and 40 randomly
trained derate learners.

## Findings
**D2-s2-01 (low, bug)** compute_cop_dhw has two DHW laws selected by the space-circuit valve flag
`cop_flow_carnot`: the non-valve branch uses a linear 0.008/K penalty with no upper bound, so the same
tank at the same outdoor is priced up to 1.435x the valve branch's COP (o=+7, T=65 C); over 41 outdoor
cells the deviation ranges 0.20..0.43 (drop-max 0.43). Below 35 C the linear branch also hands a
COP boost up to 1.20x (T=10 C), which the Carnot branch and `_batch_cop`'s comment explicitly refuse.
Perturbation: route the non-valve branch through `_cop_law(o, h, dhw_temp)` -> ratio 1.0000, boost 1.0000.

## Non-findings (all from the same harness)
- COP non-decreasing in outdoor in every mode/flow: 0 violations.
- COP non-increasing in flow/tank temperature (space Carnot path, both DHW branches): 0 violations.
- Defrost derate in [0.55, 1.0] under random learning; derate_from_duty in [0.55,1.0] for duty in [-1,2].
- Derate continuous: max jump over a 1e-9 K step 1.6e-10 (slope-bounded), including bucket and humidity edges.
- `_batch_cop` vs scalar `compute_cop` bit parity with a learned derate: 0 of 63570 mismatches.

## Unfinished
Capacity envelope vs demand-at-derate reason codes (coordinator `_capacity_caps`) not measured; Carnot
fraction band: no stated band found in tree, so not checked against one.

## Exposure
none.
