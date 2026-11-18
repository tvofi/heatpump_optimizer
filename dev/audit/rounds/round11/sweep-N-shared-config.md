# Class sweep: N-shared-config (round 11, PLAN phase D)

Class status in `dev/audit/config/bugclasses.json`: `barriered` (R9-EG-B1, #1736:
`tests/arch_score_head.py` hub-write check over solve/cycle roots, `tests/features.py`
identity walk, `tests/entities.py` hub-argument check). Judged finding: D7-s2-03.

## Enumerator

`python3 dev/audit/rounds/round11/D14/sweep/enum_shared_config.py [--root DIR]` —
widens the finding's seam rule (`enum_m4.py | grep ctx_inplace`) from top-level
modules and one-level `<member>.<field> =` to: every `.py` under the package
recursively; any chain depth and subscripts under `_opt_config`, `_thermal_params`,
`_current_state`, `_config`; Assign, AugAssign, AnnAssign, `del`, `setattr(...)`;
mutating method calls (`.update()`, `.append()`, ...); one-step local aliases of a
member.

| control | result |
|---|---|
| positive (re-finds D7-s2-03's two writers) | 2/2: coordinator.py:4259, :10944 |
| null (clean fixture: publish via `replace`, read only) | 0 |
| perturbation (one line `ctx._thermal_params.heat_loss_coefficient = 0.2` after :4259) | 2 -> 3 |

## Seams

| seam | disposition |
|---|---|
| coordinator.py:4259 `async_set_target_temperature` `_opt_config.target_temp` | instance (judged site, D7-s2-03); probe `m4_order_context.py` -> `holder_torn_fields=2` |
| coordinator.py:10944 `_apply_comfort_weight` `_opt_config.comfort_weight` | instance (judged site, D7-s2-03); same probe |

Writes reached only through a parameter or local name (outside the enumerator's
member chain), checked by hand from a grep of `state.`/`config.`/`params.` writes:

| site | disposition |
|---|---|
| coordinator.py:6654-6763, 6853-6859 `_update_current_state` | guarded: writes a `replace(prior)` / `replace(_ctx_of(self)._current_state)` copy, published whole afterwards; R9-EG-B1 `arch_score_head.py` hub-write check |
| inputs.py:559-561 `read_start_hysteresis`, slab_seed.py:69 -> thermal_model.py:5043 | guarded: only caller passes that same `replace` copy (coordinator.py:6672, :6735) |
| thermal_model.py:4958-5044 `simulate_trajectory_with_dhw` | not applicable: solver-local `ThermalState`s, no hub member |
| away.py:511-543 `_apply_return` / `resolve` | not applicable: `AwayState` built locally in `resolve`, not a context member |

## Result

Instances beyond the finding: **0**. The class is barriered for solve-path writes;
D7-s2-03's two writers sit outside the solve roots, which is why the barrier does
not see them. Proposed barrier extension: run the `ctx_inplace` rule of
`enum_shared_config.py` as a zero-budget check in `tests/arch_score_head.py`
(AST walk, under 1 gate second), or freeze `OptimizationConfig` behind the `_hub`
facade as the finding's fix scope proposes.

Board lines: none raised by this sweep.
