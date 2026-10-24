# D2 seat s1: thermal-model identities, COP and derates (method steps 1 and 2)

Baseline `cdf82daabcfe3777d98b31489f36df5555ec9d82`. Tree: `/home/claude/audit-r8/seats/D2-s1` (a copy tree).
Machine: a shared 4-vCPU cloud container. No finding depends on a timing. Every RESULT is a temperature,
a ratio, a count or a kWh from a deterministic computation. load1 during the runs was 13.9–22.0,
and thread_factor was 1.000–1.002. Exposure: none.

## Method
- **Step 1.** Four checks, each a random sweep:
  - Per-step energy balance: sum of C·ΔT against dt·(sources − losses − booked refusals). This runs on the two-zone step (4 topologies), the single-zone step and the DHW step.
  - Bitwise batch/scalar parity across 8 input kinds.
  - dt convergence order against a 1/32 h reference.
  - Trajectory monotonicity under a +1e-3 kW bump, and cap behaviour (rate, not state).
  - The golden fixtures' store bounds were also scanned.
- **Step 2.** A grid over compute_cop and compute_cop_dhw for monotonicity; DefrostDerate range and continuity; DHW-vs-buffer law consistency at equal water temperature; and planner-vs-physics COP inputs across the optimizer's DHW seams.

## Findings
### D2-s1-01 (medium, bug): the DHW planner prices COP at the current humidity, not the forecast
- **Where.** `ThermalModel.extend_dhw_temps` and `simulate_dhw_only`, and the DHW planning calls to `compute_cop_dhw`/`marginal_cop('dhw')` in `optimizer.py`, pass no humidity. `_cop_law` therefore falls back to `params.ambient_humidity`, which holds the current reading (`coordinator.py:5398`). `simulate_trajectory_with_dhw`, which produces the published trajectory, passes the per-step forecast instead.
- **Result.** With a learned humid-bucket derate, the humid forecast (85/95 %) and the current reading (55 %) disagree. The optimizer's own DHW schedule then gives trajectories that differ by up to **4.97 K**:
  - over 6 cells the gap ranges from 3.27 to 4.97 K;
  - dropping the most favourable cell still leaves 4.89 K.
- **Energy.** The planner buys 4.85 kWh of DHW electricity, against 5.62 kWh when the current humidity matches the forecast.
- **Null controls.** Forecast equal to ambient gives 0.0000 K. No learned derate gives 0.0000 K.
- **Perturbation.** `--ambient-matches` (ambient set to the forecast) gives 0.0000 K in all six cells.
- **Command.** `PYTHONPATH=tests/hastub python3 tools/audit/round8/D2/s1_dhw_humidity.py`
- **Seam rule.** The rule is the grep given in `report-s1.json`. `coordinator._capacity_caps` shares the pattern but was not separately measured.

### D2-s1-02 (low, bug): two COP laws for one lift
- **The two laws.**
  - `compute_cop_dhw` uses a linear, outdoor-independent penalty that is two-sided about 35 °C.
  - The buffer and the direct-plant curve use `flow_lift_factor`, a Carnot ratio that is one-sided and depends on outdoor temperature.
- **Result.** With `cop_flow_carnot` on, the DHW/buffer COP ratio at equal water temperature exceeds 1.01 in 102 of 105 cells, with a maximum of **1.4548** (70 °C tank, 7 °C outdoor).
- **Below 35 °C.** The DHW law grants a 1.12× boost that the space law refuses by design.
- **Warm vs cold at 55 °C.** The DHW law puts the warm/cold COP ratio at 1.4286; the Carnot law puts it at 1.2500.
- **Null control.** At 35 °C both laws agree exactly, with deviation 0.000000.
- **Perturbation.** The one-line edit `dhw_penalty = self.flow_lift_factor(...)` gives a ratio of 1.0000.
- **Command.** `PYTHONPATH=tests/hastub python3 tools/audit/round8/D2/s1_cop_laws.py [--perturb]`

## Non-findings (`tools/audit/round8/D2/s1_identities.py`)
| Check | Result |
|---|---|
| Energy conservation | Residuals are 3.3e-14 kWh (two-zone), 3.3e-14 kWh (single-zone) and 2.4e-15 kWh (DHW). With `--drop-refused` the two-zone residual becomes 10.55 kWh, so the balance does see the booked refusals. |
| Batch/scalar parity | 0 bitwise mismatches over 600 cases × 5 rows. |
| dt order | 2.35 / 2.34 / 2.45 / 2.35, i.e. first order. Valved buffers substep, so 1 h, 30 min and 15 min steps give identical results. |
| Monotonicity | 0 violations, including a 35 L Carnot buffer at 12 kW. |
| Caps | A buffer read 5 K above its cap cools 2.23 K in one idle step instead of snapping to the cap. The DHW tank behaves the same way (0.135 K). |
| COP monotonicity | 0 violations on the grid. |
| Defrost derate | Stays in [0.85, 1] for the learned values used, inside the [0.55, 1] bounds. The largest step is 4.3e-4 per 0.01 K or 0.01 %RH, so it is continuous at the bucket and band edges. |
| Derate outside the band (observation, not a finding) | The derate is up to 0.18 below 1 just outside the 0–5 °C learning band. The interpolation support reaches the neighbouring bucket centres at −2.5 °C and 6.5 °C. |
| DHW inlet floor injection | Booked, and on the conservative side. It fires in 45 of 288 configs, all heavy draws within a 1 h window. It reaches 0.05 kW at most for tanks of 150 L or more. |
| Golden store bounds | Buffer 16.56–62.11 °C, never below min(upper, slab) at the same step. DHW 30–60 °C. Wood ≤ 55 °C. |

## Not finished
- **Capacity envelope.** I did not check the envelope against demand-at-derate or its reason codes.
- **Schema conflict.** The task mandates ids of the form `D2-s1-NN`, but `finding.schema.json` pins `^D\d{1,2}-\d{2}$`. That id pattern is the only validation error in `report-s1.json`.
