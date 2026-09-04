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
| A realistic coordinator payload | `tests/golden.py:_capture_coordinator(config)` and `coordinator_scenarios()` | 5 topologies (`coord_minimal`, `coord_dhw`, `coord_two_zone`, `coord_grid_fee`, `coord_all_features`); freezes the clock at `START`; injects 48 h of prices and forecasts; `_build_data_dict()` gives ~156 keys |
| A plan scenario | `tests/golden.py:make(...)` and `SCENARIOS` (49) | `capture(name, spec)` records everything; `assert_invariants` runs on record and check |
| Every entity through the real setup | `tests/entities.py:collect(module, data, coordinator)` | drives `async_setup_entry`; `_honest_coordinator(extra_config, states, dhw)` builds a coordinator with one input cycle done |
| A coordinator in feature tests | `tests/features.py:_t2_coord(states, **extra)` (133 call sites), `_zone_coord`, `_write_coord` | `features.py` cannot be imported — copy the two-liner `HeatPumpOptimizerCoordinator(FakeHass(states), FakeEntry(data=cfg))` |
| The CPU-time ruler | `tests/stress.py:reference_solve()` and `Calibration` | fixed L-BFGS-B over a seeded vector; never "improve" it |
| The 51-combination sweep (`sweep_combinations()`; was 48 before #286/#287's 3 zero-range-bounds scenarios) | `tests/stress.py:build_case(...)`, `SEASONS`, `BUILDINGS` | thread pin (the `os.environ.setdefault` loop) must precede the `numpy` import; it does, a few lines above it |
| Closed-loop days | `tests/rolling.py:run_rolling(...)` | `learn=True` drives the real coordinator's learner; `SLOW=1` only |
| Challengers and null control | `tests/optimality.py` (`setup`, `evaluate`, `mock.patch.object`), `tests/backtest.py:score`, `tests/profiles.py` | price profiles `winter_typical`, `winter_extreme`, `summer_typical`, `summer_negative`, `shoulder`, `winter_narrow`, `winter_moderate`, `flat`; weather `winter_cold`, `winter_mild`, `summer_warm`, `summer_cool`, `shoulder` |
| The card in Node | `tests/card_rig.mjs:buildCard`, `planStates`, `makeCardContext`, `qaTopologies` | the DOM stub returns a constant 900×400 rectangle: no geometry |
| The card's 27 states | `tests/card_drift.mjs:STATES` (`--list`) | drive both a working-tree card and a `git show` card |
| Real geometry | `tests/card_browser.mjs` | Playwright resolved from `NODE_PATH`; Chromium under `PLAYWRIGHT_BROWSERS_PATH` |
| Mutation-proof idioms | `tests/features.py` (search `_fl_orig = _FlOpt`: class-attribute swap, `try/finally`), `tests/features.py` (search `rail: {name}`: input-mutation rail over a `_SAFE` baseline dict), `tests/optimality.py` (`mock.patch.object`) | the third is the only `unittest.mock` use in the suite; the first two are cited by search text, not line number -- `features.py` is ~19,600 lines and grows every wave |

**Traps**

- `tests/harness.py:FakeHass.async_add_executor_job` runs the function inline
  on the calling thread. An event-loop or GIL measurement built on `FakeHass`
  measures nothing about the executor boundary; use a real loop and a
  `ThreadPoolExecutor`.
- `golden.py`, `env_drift.py`, `closure.py`, `frontend.py`, `manual_plan.py`,
  `stress.py` (`:1597`) and `structure.py` (`:1275`, there since it was
  added, in `b38e079` -- #193 PR-0, #331) have `__main__` guards.
  `entities.py`, `features.py`, `rolling.py`, `backtest.py` and
  `optimality.py` run every check at import and `sys.exit`.
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
- The `SLOW_GATED` assertion that `tests/closure.py:100-101` says lives in
  `tests/entities.py` (checking every name in the `SLOW_GATED` set at
  `:102` is in fact `SLOW`-gated in `run.sh`) does not exist.
- `HeatPumpOptimizerSensorBase.__init_subclass__` wraps every subclass's
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
  ./tests/run.sh; rm -rf /tmp/hpo-gate.lock
```

`rm -rf`, not `rmdir`, and this is not a stylistic preference: **once you write
the owner file the section below asks for, `rmdir` cannot remove the lock** --
it only removes empty directories, so it fails with `Directory not empty` and
the lock survives your run. Take-with-owner and release-with-`rmdir` are
individually reasonable and jointly unsatisfiable, which is how a session that
followed both left a lock standing behind a green gate and blocked two others.


A full run takes about three minutes on the M1 (CI: 40–90 minutes), so a
full local gate is never the bottleneck; the shared box is.

## Running the fix wave

One group at a time is `/audit-fix with args {group, issues, repo, baseline, fixerModel, reviewerModel, effort}`; many groups at once, honoring `after`-dependencies between them, is `/audit-wave with args {groups, repo, baseline}`; either way, a reviewed PR is merged with its own `/audit-merge with args {pr, bump, title, repo}` — merges are never batched. `fixerModel` and `reviewerModel` each default to `opus`, `effort` to `high`, and a reviewer whose tier ranks below its fixer's is refused before either agent runs. A session that has no Workflow tool available runs the same fixer and reviewer prompts (see `.claude/workflows/audit-fix.js`) through the Agent tool instead, passing the model explicitly per call.

## Resource rules on the audit box

8-core Apple M1, 8 GB, numpy on OpenBLAS. Timing is not measurable while
eleven agents share the box, so during a fan-out only contention-immune
evidence counts: call counts, bytes, and CPU-time ratios against the stress
reference solve. Every wall, CPU or RSS number is re-taken in the quiet
window before it enters the register. One local full gate at a time, through
`mkdir /tmp/hpo-gate.lock`; `stress.py` alone is not alone across worktrees.

## Two things the judge's round-2 run proved wrong about this file

**`load1 <= 1.5` is unattainable on this box, and demanding it produced nothing.**
The ambient desktop floor with zero audit workload is **1.86**; over ten 60-second
retries the judge's best reading was **1.55**. A quiet window that never comes is
not a safeguard, it is a stall. What actually protects a timing number here is a
*ratio* metric and a null control taken under the same load in the same session --
which is how the D9 numbers were taken, and why they are trustworthy despite a
`load1` of 2.2-3.7. Quote the real `load1` and the control; do not wait for 1.5.

**The gate lock needs an owner, or it cannot be reclaimed.** A `mkdir` lock records
that someone holds it, never who. Round 2 lost 113 minutes to a lock created at
22:33 with no process behind it: the judge could not remove it (rightly -- the rule
is never remove a lock you did not create) and neither could any fixer, so every
full gate queued behind a directory that was protecting nothing.

Take the lock with an owner file, and it becomes decidable:

    mkdir /tmp/hpo-gate.lock && printf '%s pid=%s at=%s\n' \
      "$AGENT_NAME" "$$" "$(date -u +%FT%TZ)" > /tmp/hpo-gate.lock/owner
    # ... run the gate ...
    rm -rf /tmp/hpo-gate.lock          # NOT rmdir: the owner file makes it non-empty

Releasing your own lock is `rm -rf` for that reason, and it is the same command
as reclaiming someone else's -- the difference is entirely in what you must
prove first, not in what you type.

**`$$` is the SHELL's pid, and that is not always the work's.** A run started
with `nohup ... &` outlives the shell that launched it, so the owner file then
names a dead process while the measurement it protects is still going. That
happened within hours of this section being written: a coverage run held the
lock correctly for forty minutes with its recorded `pid=98736` already gone.
Record the work's pid where you can (`nohup cmd & echo $!`).

Before reclaiming one you did not create, prove it is dead -- the owner pid is
gone AND no test process is running out of the repository at all. The first
version of this check grepped only for three names, and would have called that
live coverage lock stale on both counts:

    cat /tmp/hpo-gate.lock/owner
    ps aux | grep -E "[t]ests/run\.sh|[s]tress\.py|[e]nv_drift\.py|[c]overage|[t]ests/[a-z_]+\.py"

Only then `rm -rf /tmp/hpo-gate.lock`, and say in your report that you did and why.
A lock with a live process behind it is never yours to take, however old it looks.

## `stress.py` always takes the lock, even run on its own

The advice everywhere else in this file — run the scripts your diff selects
directly, and take `/tmp/hpo-gate.lock` only for a full `tests/run.sh` — is
wrong for exactly one script, and following it cost a whole measurement.

`tests/run.sh` runs `stress.py` **alone, after every other lane**, because its
solve-time guard cannot tolerate a shared box. Running it "directly, without
the lock" therefore defeats the one arrangement that makes its numbers mean
anything. On 2026-09-03 three `stress.py` processes ran concurrently at
load 6.5 — one of them recording the budget table that is the gate's entire
reference — because three agents had each been told to run their selected
scripts directly and all three selections included `stress.py`. The lock
holder had the lock and still did not have the box.

So:

- **Taking the lock is required for `stress.py`**, whether you run it through
  `run.sh` or on its own.
- **The lock records intent; it enforces nothing.** It cannot stop a script
  someone runs directly. Before any timing run, confirm exclusivity by
  process, not by ownership:

      ps aux | grep -E "[s]tress\.py|[t]ests/run\.sh"

  Proceed only when yours is the sole entry, and print the concurrent-process
  count beside every timing RESULT so a reader can see the conditions rather
  than infer them.
- **Separate ratios from absolutes when contention is possible.** The stress
  gate's ratio metric cancels load by design — the reference solve is lifted
  with the scenario, and an injected 2x was measured landing at 1.9967 on a
  loaded box. Absolute wall and CPU numbers do not cancel and must be re-taken.
  Say which kind each number is; do not discard sound ratios along with
  contaminated absolutes.

## A harness at the evidence tag may measure the tag, not your tree

The harnesses under `audit-round2-evidence` do not agree on how they find the
repository root. `D6/claims.py` uses `ROOT = Path(".")`, so it measures the
working directory. `D7/sysid_plant.py` resolves from `__file__`, so it measures
the checkout the *file* lives in. Run the second kind from the tag's own
worktree and it silently measures the tag's production code instead of the tree
under review -- with plausible numbers and no error.

**Copy a harness into the tree under test before running it**, and say in your
report which root rule it used. Three reviewers have been caught by this.

The tag has moved once already, and by name only. The round-2 numbers were
**recorded** at `c398fc84` (which contains no `tools/audit/round2/` at all --
that absence is why the two-tree recipe in `HARNESSES.md` exists),
**archived** at `de668be`, and are **runnable** at `757e164`, which is where
`audit-round2-evidence` points today; `de668be` stays reachable. Cite the SHA
you actually ran, not just the tag name -- a name-only citation stops meaning
anything the next time the tag moves.

The tag has been swept, and which harnesses run, which don't, and by which of
three rot classes, is recorded in `tools/audit/round2/HARNESSES.md` -- read
that file, not this paragraph, for the current state, including per-harness
results at whatever `main` head last checked it. In short: `D6/claims.py` is
repaired (the B5 sweep landed at `757e164`); `D9/d9lib.py`'s marker-cut
fragility is unrepaired and, run in the tag's own checkout, still gives the
`IndentationError` `HARNESSES.md` records -- but do not assume that against a
current `main` tree without checking, since the same cut has already stopped
and started reproducing there once, coincidentally, as an unrelated file
changed shape around it.
