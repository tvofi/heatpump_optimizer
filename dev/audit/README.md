# The audit toolkit

Everything the per-dimension audit runs on, so that a finding can be
re-measured by someone who was not there: the briefs each auditor receives,
the schema every finding must satisfy, the harness contract, and the three
harnesses a judge still re-runs (the instruments section below). The register
that records what came of it is `docs/audit-2026-09.md`; the orchestration
scripts are `.claude/workflows/audit-*.js`.

Almost nothing here is read by the gate. `tests/closure.py`'s `INERT` tuple and
its `INERT_EXCEPT` record which paths under `tools/` that covers and which it
does not, including the one file here a test executes. Do not restate them.

`CLAUDE.md` tables every brief under `briefs/` and says which one binds which
seat; this file does not repeat that list. The rest of the layout:

```
dev/audit/README.md           this file: the harness contract, and the instruments kept live
tools/audit/
  finding.schema.json       what a finder must return; a finding without evidence cannot be returned
  briefs/                   every contract and dimension brief, tabled in CLAUDE.md; COMMON.md first
  preflight.sh              executed by tests/entities.py, so it is not INERT
  seat/                     the stateless seat instruments; each carries --self-test
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
  A threaded BLAS inflates `time.process_time()` by the thread factor and the
  ratio does not cancel unless both sides are pinned alike. Print the factor.
- It writes only under its own directory or a temp root derived from
  `$TMPDIR` (`mktemp -d`, `tempfile.mkdtemp`), a `pip download -d` or
  `--target` included: a literal seat path breaks the judge's re-run in
  another sandbox, and the cwd is the repository (round 8 judge notes 2, 9).
  It sets a private `HPO_PLANDATA` under that root before any Node harness;
  if it uses `env_drift.py` it reads the shared warmed cache in
  `~/.cache/heatpump_optimizer/` and takes a private `DRIFT_CACHE_DIR` only
  when it modifies `env_drift.py` itself.
- It prints one `RESULT <name>=<value> <unit>` line per number, plus
  `RESULT thread_factor=<process_cpu/thread_cpu>`, `RESULT load1=<1-min load>`
  and `RESULT swapins=<count>` at the end of the measurement, the
  `thread_factor` beside every timing and memory RESULT — a block that
  carries none is defective however quiet the box (#950, round 4 D9-INST).
  A RESULT whose `thread_factor` exceeds 1.05 is
  rejected and re-taken; the factor is a BLAS signal, not a tax on real
  threads. A harness that deliberately runs work on a second thread (the
  real `ThreadPoolExecutor` the FakeHass trap below mandates) can never
  satisfy the bare ratio — that thread's honest CPU lands in
  `process_time` and not in `thread_time` (`h2_cycle.py`: 1.27–1.30 over
  four re-takes, structural) — so it subtracts that thread's CPU, prints
  the residual `(process_cpu - deliberate_thread_cpu)/thread_cpu` as the
  `thread_factor` with the subtracted CPU as its own RESULT.
  **`load1` is quoted, not gated**: the round-2 judge measured this box's
  ambient floor at 1.86 (best of ten retries: 1.55), so a
  `load1 <= 1.5` bar is a stall, not a safeguard. What protects a timing
  number is a *ratio* metric and a null control under the same load in
  the same session. Quote the real `load1`; do not wait for 1.5.
- It hooks a named production symbol (`instrumented_symbol` in the finding)
  and moves under a named `perturbation`: a config change or a one-line
  production edit under which the number must change in a stated direction.
  Perturb in memory (`mock.patch.object`, an attribute swap); an on-disk edit
  goes in a worktree of its own, never a tree another run imports from — the
  gate lease serialises `stress.py` alone, not an import (round 8 judge note 3).
  A RESULT computed from constants — `2·n+1` from the bounds shape,
  without hooking `simulate_step` — is voided by the judge.

## What to reuse, and what will trip you

Measured in this repository; verify a line before leaning on it, the tree
moves.

**Builders and fixtures**

| Need | Reuse | Note |
|---|---|---|
| A realistic coordinator payload | `tests/golden.py:_capture_coordinator(config)` and `coordinator_scenarios()` | 5 topologies (`coord_minimal`, `coord_dhw`, `coord_two_zone`, `coord_grid_fee`, `coord_all_features`); freezes the clock at `START`; injects 48 h of prices and forecasts; `_build_data_dict()` gives ~156 keys |
| A plan scenario | `tests/golden.py:make(...)` and `SCENARIOS` (49) | `capture(name, spec)` records everything; `assert_invariants` runs on record and check |
| Every entity through the real setup | `tests/entities.py:collect(module, data, coordinator)` | drives `async_setup_entry`; `_honest_coordinator(extra_config, states, dhw)` builds a coordinator with one input cycle done |
| A coordinator in feature tests | `tests/features.py:_t2_coord(states, **extra)`, `_zone_coord`, `_write_coord` | `features.py` cannot be imported — copy the two-liner `HeatPumpOptimizerCoordinator(FakeHass(states), FakeEntry(data=cfg))` |
| The CPU-time ruler | `tests/stress.py:reference_solve()` and `Calibration` | fixed L-BFGS-B over a seeded vector; never "improve" it |
| The 51-combination sweep (`sweep_combinations()`) | `tests/stress.py:build_case(...)`, `SEASONS`, `BUILDINGS` | thread pin (the `os.environ.setdefault` loop) must precede the `numpy` import; it does, a few lines above it |
| Closed-loop days | `tests/rolling.py:run_rolling(...)` | `learn=True` drives the real coordinator's learner; `SLOW=1` only |
| Challengers and null control | `tests/optimality.py` (`setup`, `evaluate`, `mock.patch.object`), `tests/backtest.py:score`, `tests/profiles.py` | price profiles `winter_typical`, `winter_extreme`, `summer_typical`, `summer_negative`, `shoulder`, `winter_narrow`, `winter_moderate`, `flat`; weather `winter_cold`, `winter_mild`, `summer_warm`, `summer_cool`, `shoulder` |
| The card in Node | `tests/card_rig.mjs:buildCard`, `planStates`, `makeCardContext`, `qaTopologies` | the DOM stub returns a constant 900×400 rectangle: no geometry |
| The card's drift states | `tests/card_drift.mjs:STATES` — run it with `--list` rather than carrying a count | drive both a working-tree card and a `git show` card |
| Real geometry | `tests/card_browser.mjs` | Playwright resolved from `NODE_PATH`; Chromium under `PLAYWRIGHT_BROWSERS_PATH` |
| Mutation-proof idioms | `tests/features.py` (search `_fl_orig = _FlOpt`: class-attribute swap, `try/finally`), `tests/features.py` (search `rail: {name}`: input-mutation rail over a `_SAFE` baseline dict), `tests/optimality.py` (`mock.patch.object`) | the third is the only `unittest.mock` use in the suite; the first two are cited by search text, not line number -- `features.py` grows every wave |

**Traps**

- `tests/harness.py:FakeHass.async_add_executor_job` runs the function inline
  on the calling thread. An event-loop or GIL measurement built on `FakeHass`
  measures nothing about the executor boundary; use a real loop and a
  `ThreadPoolExecutor`.
- `golden.py`, `env_drift.py`, `closure.py`, `frontend.py`, `manual_plan.py`,
  `stress.py` (`:1597`) and `structure.py` (`:1275`) have `__main__` guards.
  `entities.py`, `features.py`, `rolling.py`, `backtest.py` and
  `optimality.py` run every check at import and `sys.exit`.
- `tests/plan_view.py` writes a per-checkout plan payload under `/tmp` and
  every Node harness reads it; `card.mjs` alone falls back to an unhashed
  legacy path with a warning, the others fail. Set `HPO_PLANDATA` per harness.
- `tests/setup_qa_render.mjs` writes SVGs to `../setup-qa/`, outside the
  repository.
- `tests/env_drift.py` runs `git worktree add` in the repository it is run
  from and refuses a ref that resolves to `HEAD`.
- `tests/closure.py` globs `tests/*.py` and `tests/*.mjs` non-recursively;
  `tests/run.sh`'s wiring check does the same. A script in a subdirectory is
  invisible to both and to `no-copies`.
- The `SLOW_GATED` assertion that `tests/closure.py:100-101` says lives in
  `tests/entities.py` (checking every name in the `SLOW_GATED` set at
  `:102` is in fact `SLOW`-gated in `run.sh`) does not exist.
- `HeatPumpOptimizerSensorBase.__init_subclass__` wraps every subclass's
  `native_value` and `extra_state_attributes` in a non-finite scrub; deleting
  a per-sensor guard will not reproduce a non-finite publish.
- The GIL yields in `optimizer.py` are two `sleep(0.002)` calls: one between
  consecutive L-BFGS-B starts (`_multi_start_minimize`), one at the seam
  between the DHW stage and the space stage. Neither sits inside an iteration.

`check_scopes.py` proves `scopes.json`'s seats disjoint and complete.

## Running the gate on the audit box

Drift mode against the merge base, and the lease `run.sh` takes around
`stress.py`, are `.claude/rules/gate-scoping.md`. A direct `stress.py` run
takes no lease. A ratio cancels load; an absolute number does not.

## A defect in an instrument is a finding

The audit measures the integration with instruments that are themselves code:
`tests/hastub`, the gate's checks and budgets, the harness contract, the lint
lanes, this toolkit. A defect your dimension's method meets in one of those is a
finding **of your dimension**, under the same bar as any other — executed number,
instrumented symbol, perturbation, metric definition, control — and not a
paragraph of prose in your report.

It travels the ordinary route: panel, judge, then an issue. **Filing waits for
the judge**, as a product finding does, and the reason is not symmetry: the seat
that finds an instrument defect is using the instrument it accuses, and the judge
re-measures with that same instrument. A verifier who cannot make the accused
check fire has not refuted the finding; say which of the two you could not
separate.

`CLAUDE.md`'s order still governs — fix it, verify it independently if you
cannot, file it only then — so a one-line instrument repair is made in place and
needs no issue. What this refuses is the third outcome: recorded in a report,
carried by nobody, met again next round.

## Running the fix wave

`/web-fix-wave` fixes, reviews and merges groups, honoring `after`-dependencies,
one merge at a time; a reviewer whose tier ranks below its fixer's is refused
before either agent runs. `/web-stamp` stamps only where the deploy key is. A
session with no Workflow tool runs the same prompts through the Agent tool,
passing the model explicitly per call.

The seat record instruments sit beside the seat scripts, each with `--self-test`.

## Resource rules on the audit box

Fan-out limits are `COMMON.md`'s. One local full gate at a time.

## A harness at the evidence tag may measure the tag, not your tree

The harnesses under `audit-round2-evidence` do not agree on how they find the
repository root. `D6/claims.py` uses `ROOT = Path(".")`, so it measures the
working directory. `D7/sysid_plant.py` resolves from `__file__`, so it measures
the checkout the *file* lives in. Run the second kind from the tag's own
worktree and it silently measures the tag's production code instead of the tree
under review -- with plausible numbers and no error.

**Copy a harness into the tree under test before running it**, and say in your
report which root rule it used.

**Cite the SHA you actually ran, not the tag name.** The tag has moved once
already, by name only: the round-2 numbers were recorded at `c398fc84`;
`audit-round2-evidence` points at `757e164` today. A name-only citation
stops meaning anything the next time it moves.

Which harnesses at that commit still run, and by which of three rot classes, is
recorded in `round2/HARNESSES.md` at `d5d8c4a`; its verdicts are final at that
commit and not against a current `main` tree.

## Rounds 1-3 are at a tag

`tools/audit/round1/`, `round2/` and `round3/` held 212 files and 5.5 MB of
write-once evidence for three closed rounds: reports, panel and judge verdicts,
mutant patches, quiet-window logs, `.out` files. Nothing in the gate reads them
(`tools/audit/` is `INERT` in `tests/closure.py`), and every number they carry
that anything still acts on is in `docs/audit-2026-09.md`, which stays.

They are reachable in full at **`d5d8c4a72fa7be7aebecc9e58d55002be17cac08`**
— `origin/main` at v6.3.18, the commit this archival was cut from, and
on `main`'s first-parent history:

    git show d5d8c4a:tools/audit/round2/JUDGE.md
    git checkout d5d8c4a -- tools/audit/round2/D5/REPORT.md

Every citation names that SHA rather than a tag (this file
carries why).

Round 2's executable harnesses were archived earlier, at
`audit-round2-evidence` (`757e164`); this file carries the rule
for running one, and the root-resolution trap that has caught three reviewers.

The done wave rosters — `wave-1b-groups.json`, `wave-2-groups.json`,
`wave-3-groups.json` — were archived at that same commit, along with
`web-phase0.js` and `triage-quiet-judges.json`. Their briefs record what a
judge established and refuted, so read them before re-deriving anything a group
in them already settled.

## The four that stayed

Each was added by a fix pull request *after* its round closed, and each is an
instrument someone re-runs rather than a report someone reads. That is the whole
of the rule: evidence is archived, instruments are kept.

| file | metric | added by | who re-runs it |
|---|---|---|---|
| `j5_gil.py` | starvation share = sum(heartbeat gaps > 5 ms) / solve wall, on a real asyncio loop with a 1 ms heartbeat and `HeatPumpOptimizer.optimize` submitted the way production submits it | `8542e51` (W3-G3, #290 #199) | the #290 judge built it; `briefs/fix-review.md` §9 sends a fix reviewer to it |
| `h8_single_scenario.py` | whether the stress gate detects a 2x regression confined to one scenario, and stays quiet on a multi-start basin flip (#346) | `291ae76` (#378) | anyone changing `tests/stress.py`'s per-scenario or solver-work rules |
| `h9_basin_coverage.py` | how many of the 51 sweep scenarios the solver-work rule judges rather than exempts, against the tree's own floor (#387) | `32f309f` (#388) | the same |
| `k1725_blas_kernel_gap.py` | the ftol check's arms and the R9-F2.1 P3 margins, per OpenBLAS kernel via `OPENBLAS_CORETYPE` | `613bff1b` (#1726, #1725) | anyone adding a knife-edge optimizer comparison (`tests/README.md`'s kernel rule) |
| `eg_b7_seam_hubs.py` | loads of `_opt_config`, `_thermal_params` and `_current_state` through a state root, per coordinator seam, and each seam's owned attributes, at this tree and at main before #1887 (`31567b71`), with `seam_metrics`' own attribute walk (R9-EG-B7, #1744) | R9-EG-B7 (`301abb21`, landed under #1744) | anyone proposing to detach a coordinator seam: the cut falls only where the hub loads and owned attributes moved |

Each drives production code and prints under the harness contract in this file. `j5_gil.py` must never be run on
`FakeHass`, whose executor runs inline and would measure nothing.
