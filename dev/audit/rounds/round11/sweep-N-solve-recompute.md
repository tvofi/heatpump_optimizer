# Class sweep: N-solve-recompute (round 11, D14 steps 3-4)

Class status in `dev/audit/config/bugclasses.json`: `barriered` (the
production-call channel in `tests/stress.py`). That barrier counts calls inside
one solve on an unchanged plan. It cannot see a second whole solve that an
action triggers, which is how D9-s1-01 works.

Finding swept: D9-s1-01. A diagnose press ends in `async_request_refresh()`,
so the press runs a full cycle and re-solves. The analysis it publishes needs no solve.

## Enumerator

`python3 dev/audit/rounds/round11/D14/sweep-N-solve-recompute/enumerate.py`

This is a static AST walk of `custom_components/heatpump_optimizer/`. It lists
every reference to `async_request_refresh` or `async_refresh`, whether called or
passed as a callback, together with the function that encloses it. The listing
is the finding's `seam_rule` widened to the whole package.

`--controls` runs three checks and exits 0 only if all three pass:

- **Positive:** the enumerator re-finds `coordinator.py:async_diagnose_interval` (D9-s1-01).
- **Null:** a clean fixture that publishes through `_build_data_dict` and `async_update_listeners` gives 0 seams.
- **Perturbation:** adding one line, `await self.async_request_refresh()`, to that fixture gives 1 seam.

Result: `seams=20 positive_D9-s1-01=True null=0 perturbed=1`, exit 0.

## Dispositions (20 seams)

| seam | disposition | reason / probe |
|---|---|---|
| coordinator.py:10686 `async_diagnose_interval` | **instance** (judged site, D9-s1-01) | `h_diagnose_refresh.py`: 2-4 `_multi_start_minimize` per press, 0 when it only publishes |
| button.py:110 `RunOptimizationButton.async_press` | **instance** (beyond finding) | `probe_run_button.py`: the press awaits `async_run_optimization()`, then schedules a refresh whose `_async_update_data` solves again at the same instant on the same inputs. `msm_run_alone=2`, `msm_press=4`, exit 1. The `run_optimization` service runs the solve once. The button's extra refresh is there for fetch-and-actuate, and that step only needs the plan the press already computed. |
| button.py:175 reset comfort weight | not applicable | it changes the comfort weight, which is a solve input |
| button.py:192, services.py:1194 reset heat loss | not applicable | they reset the heat-loss learners, which are solve inputs |
| coordinator.py:1449 `async_adopt_heat_loss_refit` | not applicable | it changes the heat-loss scale |
| coordinator.py:6541 `async_set_mode` | not applicable | the mode bounds the solve |
| coordinator.py:6592 `async_update_thermal_params` | not applicable | thermal params are solve inputs |
| coordinator.py:8583 / 8609 apply/clear manual plan | not applicable | they change the plan source |
| coordinator.py:9760 `async_restore_learned_snapshot` | not applicable | it restores the learned inputs |
| coordinator.py:9921 `async_set_away` | not applicable | the away state changes setpoints and bands |
| coordinator.py:11049 `async_arm_system_identification` | not applicable | the experiment advances and overrides power inside the cycle, after the solve, so that cycle is the action's own output |
| coordinator.py:3590 `__init__` (away-input watch) | not applicable | it fires on a changed away input |
| coordinator.py:3592 `__init__` (InputReturnWatch) | guarded | it fires only when an input returns, and is rate-limited to the optimisation interval |
| coordinator.py:7203 `_fetch_solar_forecast` | not applicable | this is `OpenMeteoSolar.async_refresh`, an irradiance fetch, not a coordinator refresh |
| \_\_init\_\_.py:355 `async_setup_entry` | not applicable | the first solve, with no earlier plan |
| boost.py:681 / 696 `set_channel` / `set_block` | not applicable | boost holds and blocks bound the solve |
| entity.py:339 `publish_then_refresh._refresh` | not applicable | its callers in switch.py, climate.py and datetime.py write config that is a solve input |

**Instances beyond the finding: 1** (button.py `RunOptimizationButton.async_press`).

## Barrier note

The `tests/stress.py` channel counts work inside one solve. It does not see a
second whole solve started by an action. Proposed barrier: a lint in `tests/`
built on this enumerator. Each `async_request_refresh` site would have to be on
an allow-list naming the solve input that its action changes. Any new site, or a
site whose action changes no input, would fail. The check reads the AST only,
so its gate cost is under 1 s.
