# The audit toolkit

Everything the eleven-dimension audit runs on, so that a finding can be
re-measured by someone who was not there: the briefs each auditor receives,
the schema every finding must satisfy, the harness contract, and the
harnesses themselves, one directory per round and dimension. The register
that records what came of it is `docs/audit-2026-09.md`; the orchestration
scripts are `.claude/workflows/audit-*.js`.

Nothing here is a test. `tools/` is in `tests/closure.py`'s `INERT` list:
no gate runs it, no test reads it, and the closures merge check proves that on
every re-derivation.

```
tools/audit/
  README.md                 this file: layout, contracts, the inventory of what to reuse
  finding.schema.json       what a finder must return; a finding without evidence cannot be returned
  briefs/COMMON.md          the contract every finder works under (read first)
  briefs/D0.md … D10.md     one dimension each: method, what to reuse, what has fooled people before
  briefs/verifier.md        the adversarial panel's contract
  briefs/judge.md           the judge's contract: re-measure, void, classify
  briefs/fixer.md           the fix protocol as a checklist
  briefs/fix-review.md      the adversarial fix reviewer's contract
  round<N>/D<k>/            harnesses and REPORT.md for that round and dimension
tools/release/stamp.py      the only way a version is assigned
```

## The harness contract

A harness is a standalone script under `tools/audit/round<N>/D<k>/`, Python or
Node, that produces the number a finding rests on. The judge re-runs it
without reading the finding, so it has to carry everything:

- A header comment stating what it measures (the metric definition, one
  line), the exact command to run it, the expected value ± tolerance, the
  baseline SHA it was measured against, and the machine.
- It runs from the repository root with `PYTHONPATH=tests/hastub` and never
  `cd`s elsewhere: `tests/harness.py` inserts relative paths, `tests/golden.py`
  opens `tests/golden/` relatively.
- Its first lines, before any numpy import, copy `tests/stress.py`'s thread
  pin — `os.environ.setdefault` for `OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS`,
  `MKL_NUM_THREADS`, `NUMEXPR_NUM_THREADS`, `VECLIB_MAXIMUM_THREADS`, all `"1"`.
  A threaded BLAS inflates `time.process_time()` by the thread factor
  (measured 3.33× on this box) and the ratio does not cancel unless both sides
  are pinned alike.
- It writes only under its own directory or a temp directory; it sets a
  private `HPO_PLANDATA` (under the temp root, `tests/plan_view.py` refuses
  anything else) before invoking any Node harness; if it uses `env_drift.py`
  it reads the shared warmed cache in `~/.cache/heatpump_optimizer/` and takes
  a private `DRIFT_CACHE_DIR` only when it modifies `env_drift.py` itself.
- It prints one `RESULT <name>=<value> <unit>` line per number, plus
  `RESULT thread_factor=<process_cpu/thread_cpu>`, `RESULT load1=<1-min load>`
  and `RESULT swapins=<count>` taken at the end of the measurement. The judge
  rejects a timing or memory RESULT whose `thread_factor` exceeds 1.05 or
  whose `load1` exceeds 1.5.
- It hooks a named production symbol (`instrumented_symbol` in the finding)
  and moves under a named `perturbation`: a config change or a one-line
  production edit under which the number must change in a stated direction.
  A RESULT computed from constants — `2·n+1` from the bounds shape, say,
  without ever hooking `simulate_step` — is voided by the judge.

## What to reuse, and what will trip you

Measured in this repository; verify a line before leaning on it, the tree
moves.

**Builders and fixtures**

| Need | Reuse | Note |
|---|---|---|
| A realistic coordinator payload | `tests/golden.py:_capture_coordinator(config)` and `coordinator_scenarios()` | 5 topologies (`coord_minimal`, `coord_dhw`, `coord_two_zone`, `coord_grid_fee`, `coord_all_features`); freezes the clock at `START`; injects 48 h of prices and forecasts; `_build_data_dict()` gives ~149 keys |
| A plan scenario | `tests/golden.py:make(...)` and `SCENARIOS` (55) | `capture(name, spec)` records everything; `assert_invariants` runs on record and check |
| Every entity through the real setup | `tests/entities.py:collect(module, data, coordinator)` | drives `async_setup_entry`; `_honest_coordinator(extra_config, states, dhw)` builds a coordinator with one input cycle done |
| A coordinator in feature tests | `tests/features.py:_t2_coord(states, **extra)` (131 uses), `_zone_coord`, `_write_coord` | `features.py` cannot be imported — copy the two-liner `HeatPumpOptimizerCoordinator(FakeHass(states), FakeEntry(data=cfg))` |
| The CPU-time ruler | `tests/stress.py:reference_solve()` and `Calibration` | fixed L-BFGS-B over a seeded vector; never "improve" it |
| The 48-combination sweep | `tests/stress.py:build_case(...)`, `SEASONS`, `BUILDINGS` | thread pin at lines 60–64 must precede numpy |
| Closed-loop days | `tests/rolling.py:run_rolling(...)` | `learn=True` drives the real coordinator's learner; `SLOW=1` only |
| Challengers and null control | `tests/optimality.py` (`setup`, `evaluate`, `mock.patch.object`), `tests/backtest.py:score`, `tests/profiles.py` | price profiles `winter_typical`, `winter_extreme`, `summer_typical`, `summer_negative`, `shoulder`, `winter_narrow`, `winter_moderate`, `flat`; weather `winter_cold`, `winter_mild`, `summer_warm`, `summer_cool`, `shoulder` |
| The card in Node | `tests/card_rig.mjs:buildCard`, `planStates`, `makeCardContext`, `qaTopologies` | the DOM stub returns a constant 900×400 rectangle: no geometry |
| The card's 26 states | `tests/card_drift.mjs:STATES` (`--list`) | drive both a working-tree card and a `git show` card |
| Real geometry | `tests/card_browser.mjs` | Playwright resolved from `NODE_PATH`; Chromium under `PLAYWRIGHT_BROWSERS_PATH` |
| Mutation-proof idioms | `tests/features.py:12382` (class-attribute swap, `try/finally`), `tests/features.py:7832` (input-mutation rail), `tests/optimality.py` (`mock.patch.object`) | the third is the only `unittest.mock` use in the suite |

**Traps**

- `tests/harness.py:FakeHass.async_add_executor_job` runs the function inline
  on the calling thread. An event-loop or GIL measurement built on `FakeHass`
  measures nothing about the executor boundary; use a real loop and a
  `ThreadPoolExecutor`.
- Only `golden.py`, `env_drift.py`, `closure.py`, `frontend.py` and
  `manual_plan.py` have `__main__` guards. `entities.py`, `features.py`,
  `stress.py`, `rolling.py`, `backtest.py` and `optimality.py` run every check
  at import and `sys.exit`.
- `tests/plan_view.py` writes `/tmp/plandata-<sha256(tests dir)[:12]>.json`;
  every Node harness reads it; `card.mjs` falls back to `/tmp/plandata.json`
  with a warning, the others fail. Set `HPO_PLANDATA` per harness.
- `tests/setup_qa_render.mjs` writes SVGs to `../setup-qa/`, outside the
  repository.
- `tests/env_drift.py` runs `git worktree add` in the repository it is run
  from and refuses a ref that resolves to `HEAD`.
- `tests/closure.py` globs `tests/*.py` and `tests/*.mjs` non-recursively;
  `tests/run.sh`'s wiring check does the same. A script in a subdirectory is
  invisible to both and to `no-copies`.
- The `SLOW_GATED` assertion that `tests/closure.py:96` says lives in
  `tests/entities.py` does not exist.
- `HeatpumpOptimizerSensorBase.__init_subclass__` wraps every subclass's
  `native_value` and `extra_state_attributes` in a non-finite scrub; deleting
  a per-sensor guard will not reproduce a non-finite publish.
- The GIL yields in `optimizer.py` are two `sleep(0.002)` calls: one between
  consecutive L-BFGS-B starts (`_multi_start_minimize`), one at the seam
  between the DHW stage and the space stage. Neither sits inside an iteration.

## Running the gate on the audit box

The committed golden fixtures were recorded on another machine and the
strict comparison does not reproduce here (`tests/README.md` says so; the
first local run of this program failed `golden.py` on last-decimal solver
differences in `winter_two_zone_dhw` while CI, in drift mode, was green).
Run the gate the way CI runs it, against the merge base:

```
BASE=$(git merge-base origin/main HEAD)
mkdir /tmp/hpo-gate.lock && GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$BASE \
  OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  ./tests/run.sh; rmdir /tmp/hpo-gate.lock
```

A full run takes about three minutes on the M1 (CI: 40–90 minutes), so a
full local gate is never the bottleneck; the shared box is.

## Resource rules on the audit box

8-core Apple M1, 8 GB, numpy on OpenBLAS. Timing is not measurable while
eleven agents share the box, so during a fan-out only contention-immune
evidence counts: call counts, bytes, and CPU-time ratios against the stress
reference solve. Every wall, CPU or RSS number is re-taken in the quiet
window before it enters the register. One local full gate at a time, through
`mkdir /tmp/hpo-gate.lock`; `stress.py` alone is not alone across worktrees.
