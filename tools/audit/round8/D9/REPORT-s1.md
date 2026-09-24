# D9 round 8, seat s1: gradient cost, solves per cycle, GIL hold, DHW loops

Baseline cdf82daa, tree /home/claude/audit-r8/seats/D9-s1. The machine is a shared 4-vCPU x86 container with load1 between 13 and 24 throughout. Counts and ratios are final. Wall and CPU numbers are provisional.

## Method
- `s1_gradient.py` hooks ThermalModel.simulate_step, simulate_trajectory_batch and simulate_dhw_step. It also wraps the jac passed through optimizer._scoped_minimize and scipy's approx_derivative, and the DHW planner methods. It covers 5 shapes. Perturbations: `--scalar` and `--hours 48`.
- `s1_solves.py` counts _multi_start_minimize entries per optimize() by caller path over the 51 sweep scenarios, with co-opt adoption. Null control: `--flat`. Perturbation: `--no-coopt`.
- `s1_polish.py` counts njev by run kind (start or polish) and polish outcome (adopted or discarded) over the 51 sweep scenarios. Null control: `--flat`. Perturbation: `--maxls 5`, with `--skip-polish` as the upper bound.
- `s1_cycle.py` runs a real coordinator `_async_update_data` on a real asyncio loop with a real ThreadPoolExecutor and a 1 ms heartbeat. It has a process route (shipped), an inline route (the #511 fallback) and a null idle loop. Perturbation: `--no-gil-yield`. It also counts solves by path. Config `--config fuse_tiles` turns on the what-if paths.

## Findings
- **D9-s1-01 (low).** 149 of 206 polishes are discarded, costing 6.3% of all gradient evaluations (flat-price null: 7.8%). 24 polishes end ABNORMAL at nit 0 after about 21 gradients each. With maxls=5 the discarded share falls to 4.1%. Leave-one-out over 51 cells: min 0, max 0.416, mean 0.126 with the highest cell dropped.
- **D9-s1-02 (low, provisional).** On the inline fallback route, the loop spends 0.65 to 0.90 of executor-busy wall time in gaps over 5 ms, with a maximum gap of 30 to 46 ms. The process route gives 0.29 to 0.32 and the idle null gives 0.08 to 0.09. Removing _gil_yield raises it to 0.93 to 0.97. Cause: the batched gradient has no yield inside it.

## Non-findings
See report-s1.json. In short:
- Every shape costs 96 sse per gradient on the batched path, including the zero-range shapes. With `--scalar` it is 9,216.
- An optimize() makes 1.04 _multi_start_minimize entries.
- A default coordinator cycle submits 1 main solve and 2 _multi_start_minimize entries.
- With fuse+tiles enabled, the first cycle submits 1 main and 2 what-if solves.
- DHW planning is 0.2% of the two-zone solve's simulation steps and about 45% of a single-zone DHW solve's CPU. The cost is bounded and the min-run loop grows superlinearly with the horizon.

## Could not finish or harness gaps
- The GIL numbers need the quiet-window re-take.
- The task's `D9-s1-NN` ids fail finding.schema.json's id pattern. That is the only schema error.
- Raw outputs are in s1_out/.

exposure: none.
