# Sweep: N-shared-config (round 11, D14 steps 3-4)

Class mechanism: solve-scoped state is mutated on, or read from, live shared objects
while the solve runs off the loop, so a concurrent reader publishes it or a concurrent
writer is reverted. This round's finding is D7-s2-03: `CoordinatorContext` is frozen
and published whole, but two writers edit a member in place
(`ctx._opt_config.target_temp`, coordinator.py:4259; `_opt_config.comfort_weight`,
coordinator.py:10944). `dataclasses.replace` copies member references, so every
superseded context sees the edit. Ledger status: `barriered` (R9-EG-B1, #1736). That
barrier prices solve-path hub writes and the solve record's identity walk, not a
holder of a superseded context, so the judged writes pass it.
Baseline: origin/handoff/audit-r11-register (28b864af6d). The finding reproduces here:
`m4_order_context.py` gives holder_torn_fields=2, and `--perturb-ctx` gives 0.

## Enumerator (two arms)

Static: `python3 dev/audit/rounds/round11/D14/N-shared-config/ctx_inplace_seams.py [--null] [--plant]`.
An AST walk over every package module (subpackages included) for an assignment,
aug-assignment, `setattr`/`object.__setattr__`/`vars(..).update`, or container mutator
rooted at a context member (`_opt_config`, `_thermal_params`, `_current_state`,
`_config`). It also follows a member through a local alias (`cfg = ctx._opt_config;
cfg.f = ..`) and `getattr(x, "<member>")`. This widens the finder's seam rule
(`enum_m4.py | grep ctx_inplace`: direct `X.<member>.f =` in top-level modules only).

Dynamic: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/N-shared-config/ctx_write_trace.py [--perturb] [--plant]`.
A hub object also travels untyped, as a `params`/`state` parameter or through
`ThermalModel.params`, so this arm wraps `__setattr__` of `OptimizationConfig`,
`ThermalParameters` and `ThermalState`. It records every write into an instance that a
published context holds as a member, attributed to the first package frame. The drive is
the D1-s2 rig (real loop, spawned store loads, real cycle with the memoised solve):
construction, 4 full cycles 15 min apart, then `async_update_thermal_params`,
`async_set_target_temperature`, `_apply_comfort_weight`, `async_set_mode` (comfort,
auto) and a fifth cycle.

| run | static seams | dynamic write sites |
|---|---|---|
| baseline (positive control) | 2 (4259, 10944) | 3 (4259, 10944, thermal_model.py:420) |
| null: `--null` clean fixture (publish by replace, reads only) / dynamic `--perturb` (4259 publishes `replace(ctx, _opt_config=replace(..))`) | 0 | 2 (4259 leaves) |
| perturbation: `--plant` (static: one aliased `cfg.min_temp = 1.0`; dynamic: one in-place write into the published `_thermal_params`) | 1 | 4 |

Both arms re-find both judged sites. The dynamic arm also shows that
`_apply_comfort_weight` edits the published `_opt_config` on every cycle (writes on
cycle0-4), not only when the learner moves. No container member of a hub was mutated
in place in the drive; `__setattr__` does not see a list mutation, and the static
`mutate` arm found none.

## Seams (3) and dispositions

| seam | disposition |
|---|---|
| coordinator.py:4259 `async_set_target_temperature` (`_opt_config.target_temp`) | **instance**, judged site (D7-s2-03). Probe: `m4_order_context.py` holder_torn_fields=2 (0 under `--perturb-ctx`). Dynamic arm: write on a published member, gone under `--perturb` |
| coordinator.py:10944 `_apply_comfort_weight` (`_opt_config.comfort_weight`) | **instance**, judged site (D7-s2-03). Same probe. Dynamic arm: written into the published member on every cycle |
| thermal_model.py:420 `ThermalParameters.topology_layout` (`_layout_cache`) | guarded: a keyed memo. `_layout_cache` is `field(init=False, repr=False, compare=False)` and its key holds all four inputs `topology_layout` reads (`topology_layout_override`, `mixing_valve_mode`, `two_zone_enabled`, `wood_tank_configured`). A holder of a superseded context therefore reads exactly the layout its own fields imply, `replace()` drops the cache, and no compared or published field changes |

Instances beyond the finding: **0**.

## Barrier implication

R9-EG-B1's `arch_score_head.py` refuses hub writes reachable from a solve outside
`CYCLE_HUB_WRITERS`, and the identity walk refuses a solve record sharing a mutable hub
object. Neither states the context's own property, "a superseded context never changes".
Proposed: the static arm as a tests/ check, today 2 seams and 0 once D7-s2-03's fix
publishes a replaced `_opt_config`. Either it refuses any in-place edit of a context
member outside a reasoned list (memo fields declared `compare=False, init=False` with a
complete key), or `OptimizationConfig` becomes `frozen=True`, which makes the class
impossible at runtime for that hub. Static and AST only, well under a gate second. Not
built here.
