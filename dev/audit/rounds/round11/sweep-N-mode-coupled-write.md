# Class sweep: N-mode-coupled-write (round 11, PLAN phase D)

Class mechanism: one actuator serves two heat targets; on a pump with no mode
separating them, the write for the served target leaves the other target's
gate floored above the case, so the off-duty thermostat starts. Source finding:
D16-s1-02 (weakened, low). The class has no entry in
`dev/audit/config/bugclasses.json` at `handoff/audit-r11-register` (new class).

## Enumerator (D14 method step 3)

`python3 dev/audit/rounds/round11/D14/n_mode_coupled_write.py` -- AST pass over
every `custom_components/**/*.py`, starting from the finding's seam_rule
(`DHW_GATE_C|FLOW_GATE_C` in `pump_arbiter.py`) and widened to every
`_bounded(inp, <slot>, <fixed floor>)` in any function. A seam is `instance`
when the written value is a named `*_GATE_C` constant with no lower entity
bound; otherwise `guarded`.

| control | command | result |
|---|---|---|
| positive | enumerator on the tree | re-finds D16-s1-02 at `pump_arbiter.py:1310` (instances=1, seams=2) |
| null | `--null` (clean fixture: gate at the entity minimum) | instances=0 |
| perturbation | `--perturb` (one line: floor re-set to `DHW_GATE_C`) | instances 0 -> 1 |

## Disposition (method step 4)

| seam | disposition | reason / probe |
|---|---|---|
| `pump_arbiter.desired` line 1310: space row under Heating + DHW writes tank `DHW_GATE_C` (30 C) | **instance** (the finding's own site) | probe: `cells.py --no-gates`, min-cold-tank rows of gchv-flow and gchv-indoor FAIL (tank 20 C < 30 - 5 K); `--perturb dhw_gate` -> 0 |
| `pump_arbiter.desired` line 1312: hot-water row on an indoor unit under Heating + DHW writes the room set-point 5.0 C, rounded down | guarded | the floor is 5 C rounded down to the entity's minimum; no occupied room reads below 5 C less a thermostat hysteresis, so the space thermostat never starts on it |
| `pump_arbiter._gate_c` (flow unit, hot-water row under Heating + DHW; not listed: floor passed as the lower bound) | guarded | `_bounded(..., gate, gate)` writes the entity minimum, floored at `FLOW_GATE_C` 25 C, the GCHV water set-point minimum; loop water in a heated house sits at or above room temperature (about 20 C = 25 C - 5 K), so the water thermostat does not start. Residual: an entity accepting below 25 C in a house below 20 C; no rig reproduces it |
| `_disinfecting` (space step under a held cycle -> both) | not applicable | coupling is the plan's intent: the cycle books hot water |

Instances beyond the finding: **0**. Proposed barrier: the D16-s1-02 fix
(gate the tank at the entity minimum / below the reading less hysteresis) plus
this enumerator as a `tests/` check, cost under 1 s of gate time.
