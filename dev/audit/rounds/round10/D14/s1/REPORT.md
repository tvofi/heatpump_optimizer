# D14-s1 — recurring bug classes, round 10 (baseline 17f1c55fad1b)

Cells: D14.M2, D14.M3, D14.M4, axis `open`, `prototype-only`, all files. Run from the export root
with `PYTHONPATH=tests/hastub` and the venv-ci python.

## Exposure
I read `dev/audit/config/bugclasses.json` in full: the classes, their instance ids, the `_rca` and
`_unclassified` blocks. I also read this worktree's git history for three of its open classes:
- **N-name-sort**: ea95fb88c, 9af8a477f, 87eeaeefd (F7.4), dc977f693 (F7.5) and their parents.
- **P10**: c4e1e0c07 (R9-F1.7) and its commit message.
- **N-step-grid**: the #1679 comment in `config_flow._number`.

I read `tests/replay.py` (the P10 kernel barrier) and `tests/entities.py` (the #1760 contiguity check)
as the barriers already in the tree. I did not run `gh`.

## M2 — pick
The ledger has five `open` production classes: P8, P10, N-name-sort, N-step-grid, N-reap-lock and
N-staleness. P10 and N-name-sort are tied on most rounds (6 each). N-step-grid was added because its
detector was cheap. P8 (also 6 rounds) is left unfinished.

## M3 — detectors (committed)
| harness | class | baseline | re-introduction | re-find at pre-fix |
|---|---|---|---|---|
| `p10_seams.py` | P10 | loop_kernels_all=0 (base, 48 cycles, 24 h); fallback: executor only, 0 loop; sysid: 0 loop | `--perturb` (solve inline on loop): 6967 | not run (see unfinished) |
| `p10_seams.py --away` | P10 | **183 loop calls / 6 cycles** | `--deficit 0`: 0 | n/a (new seam) |
| `namesort_seams.py` | N-name-sort | splits en/sv global = 0/0 over 81 instantiated entities, 16 families | `--perturb`: en 1 | `--names-at dc977f693^`: en 1 (away), sv 2 (away, compressor); `9af8a477f^`: en 3, sv 5 |
| `stepgrid_seams.py` | N-step-grid | off_grid=0 (42 stepped sliders, 42 box `any`) | `--perturb` (pre-#1679 box step): 8 | n/a |

## M4 — findings
### D14-s1-01 (P10): the away-recovery estimate runs a model kernel on the event loop, and the P10 barrier's replay never reaches it
**Property.** No model kernel (`ThermalModel.simulate_*`, a sysid fit, a scipy or numpy.linalg
solve) is called on the event loop.

**Rule.** `p10_seams.py`'s static list has 35 call sites. Each one is driven by a replay arm, and
the result is counted by the route it ran on.

**Evidence.** `HASTUB_TZ=Europe/Stockholm PYTHONPATH=tests/hastub python3
dev/audit/rounds/round10/D14/s1/p10_seams.py --away` gives
`RESULT loop_kernels_away_seam=183` (30.5 per cycle). The calls come from
`away.py:estimate_recovery_hours` → `ThermalModel.simulate_step`. That path is
`coordinator._resolve_away` → `away.resolve` → `_apply_return`, and the call sits inline in
`async_run_optimization`. The worst case is `MAX_RECOVERY_HOURS/0.25` = 96 steps per cycle.

**Control.** `--deficit 0` (the house is already at its recovery target) gives 0. The base arm gives
0, and so does the barrier's own count (`barrier_set_loop`). So `tests/replay.py:kernel_checks` is
green while the seam exists: its fixture never sets away.

**Seams.**
- Instance: `away.estimate_recovery_hours`.
- Listed, on the loop, not driven: `coordinator._replay_interval`, which runs 1 `simulate_step` per
  cycle from `_async_learn_house_heat_loss` and `_async_learn_lower_floor_loss`. The fixture is
  DHW-only, so the replay never reaches it.
- Guarded (counted in the worker): optimizer, dhw_planner (`linprog`, `minimize`), and sysid.
- Not applicable: `coordinator.async_simulate:simulate_wood_slots`, which only parses slots.

**Severity.** Low: bounded at ≤96 `simulate_step` calls per cycle, and a timing number is not
taken.

**Barrier.** Add an `away` arm (and a space-heating learner arm) to `KERNEL_ARMS` in
`tests/replay.py`. It costs about one extra 3 h replay (~13 s wall, provisional).

N-name-sort and N-step-grid: no finding (see non-findings).

## Non-findings
- **N-name-sort.** The global name sort of every instantiated entity (81 entities, 16 families) has
  0 en and 0 sv splits, with 0 untranslated entities and 0 missing names.
  - The detector re-finds the F7.5 instances at `dc977f693^`.
  - The device-page section view gives 9 splits per language. All of them come from HA sectioning by
    `entity_category` and none from the name sort, so they are not this class.
  - The class is effectively barriered by `tests/entities.py` (#1760), although the ledger says
    `open`.
- **N-step-grid.** 0 off-grid among 42 stepped slider fields. The 42 box fields carry `step: any`.
- **P10.** The base, fallback and sysid arms show 0 loop kernels across the widened set
  (`linprog`, `minimize` and `linalg` included).

## Unfinished
- **M3, P10.** The pre-fix re-find at `c4e1e0c07^` was not run, because `replay.kernel_routes`
  post-dates that fix. `_replay_interval` is not driven yet.
- **M2/M3, P8.** No detector built yet.
