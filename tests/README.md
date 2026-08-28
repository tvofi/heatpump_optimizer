# Tests

These are plain scripts, not a pytest suite, so they can be run against a real
Home Assistant environment without extra tooling. They need `numpy`, `scipy`,
`voluptuous`, `aiohttp` and `pyyaml`; `tests/requirements-ci.txt` pins the
exact versions CI uses.

```bash
./tests/run.sh          # everything except the slow closed-loop simulation
SLOW=1 ./tests/run.sh   # including it (adds about fifteen minutes)
GATE_JOBS=1 ./tests/run.sh   # one script at a time, streaming, for watching a failure
```

`run.sh` runs the suite in lanes rather than in one long line: the unit-style
scripts, the characterization gate and the end-to-end scripts go in parallel,
then `stress.py` runs **alone** on an otherwise idle box, because its
solve-time guard measures this machine while it solves and the rest of the
suite must not be part of what it measures. `plan_view.py` writes the payload
`card.mjs` reads, so those two stay in one lane in that order. Every script
still runs with the same arguments, and every failure still counts — and a
script that is wired into `run.sh` but that no lane actually executes now
fails the run, which the older "is it mentioned?" grep could not see. Output
is captured per script and replayed whole, one script at a time, once the
lanes finish — four scripts interleaving their output is not something anyone
can read — with live start/finish lines while they run and a wall-clock table
at the end. `GATE_JOBS=1` puts it back to one script at a time with streaming
output, which is what to reach for when a failure needs watching as it happens.

CI runs the same `run.sh` on every push and pull request
(`.github/workflows/tests.yml`), with one difference: `GOLDEN_MODE=drift`
replaces the exact golden-fixture comparison with a same-environment
comparison against the PR's merge-base (see `env_drift.py` below), because
solver floats recorded on one machine do not reproduce bit-exactly on
another. The `SLOW=1` closed-loop simulation runs nightly and on manual
dispatch.

Or individually:

```bash
export PYTHONPATH=tests/hastub

python tests/features.py     # the feature modules, driven directly
python tests/entities.py     # entities, platforms, options pages, translations
python tests/open_meteo.py   # the irradiance client
python tests/solar_alignment.py  # irradiance lands on the right optimizer steps
python tests/golden.py       # exact behaviour, pinned (--record to re-record)
python tests/validate.py     # 18 seasonal scenarios, asserts invariants
python tests/edge.py         # degenerate inputs and boundary conditions
python tests/backtest.py     # replay against alternative strategies
python tests/stress.py       # 48 combinations, 17 edge cases, economics
python tests/rolling.py      # days of re-planning against a mismatched house
python tests/optimality.py   # solution-quality floor against cheap challengers
python tests/env_drift.py    # sensitive fixtures vs origin/main, same machine
python tests/plan_view.py    # plan sensor payloads, writes /tmp/plandata.json
node   tests/card.mjs        # renders the dashboard card against that payload
```

`profiles.py` holds Nord Pool SE3 price curves and Swedish weather profiles for
winter, summer and shoulder season, used by the end-to-end scripts.
`harness.py` holds the fakes the unit-style scripts share.

## The Home Assistant stub

`tests/hastub/` is a minimal stand-in for the parts of `homeassistant` the
integration imports, so the suite runs without a Home Assistant install. It is
version-controlled: it used to live in `/tmp` and disappear on every reboot,
which made the suite unreproducible.

It is deliberately small. A fuller stub would drift from the real thing without
anyone noticing, and the job here is to let the integration *import* and its
entities be *constructed*, not to reimplement Home Assistant.

## The two guards

Most of these scripts ask "is the answer good?". Two ask something different,
and between them they cover the failures that are otherwise invisible.

**`golden.py` asks "has the answer changed?"** It records the complete output of
53 fixtures (47 plan scenarios, 5 coordinator captures and the config-flow
schema) — every schedule, trajectory, setpoint, cost, reason code and
option-page field — and diffs byte for byte. The optimizer is deterministic, so
any difference is real. This is what makes a refactor safe: the outcome-based
scripts would happily pass a change that shifts a plan by one interval or drops
a constraint in a rare branch, and this will not. Every capture also passes a
physical-invariant layer (finite values, power within the compressor maximum,
trajectories inside -40..120 °C, savings ≤ 100 %) on both record and check, so
`--record` cannot bake an impossible plan into a fixture.

Five fixtures (`valve_storage_smart_write`, `wood_two_tank`,
`wood_two_tank_smart_write`, `wood_coil`, `valve_upper_direct_slab`) are the
non-convex valve/wood solves and do not reproduce across BLAS builds. On such
machines their exact comparison is meaningless, so **`env_drift.py`** captures
them twice in the *same* environment — working tree vs a worktree of
`origin/main` (or any ref) — and requires byte-identity; solver noise cancels
and only the branch's own footprint remains. With `--all` it does this for
every fixture, which is how CI checks goldens. A branch that deliberately
moves fixtures lists them in `tests/golden/claimed_drift.txt` with a reason;
claimed scenarios print their diffs without failing, and a claim that matched
nothing fails as a *stale claim* — counted and reported separately from drift,
since nothing regressed.

That file is committed, so two rules stop a claim from outliving the diff it
describes. It carries a `# claims-for: <version>` line that must equal the
repo-root `VERSION` — checked by both `env_drift.py` (before any capture, in
either mode) and `entities.py` — so a release that moves no goldens still
bumps the line and empties the list. And under `--all`, the claim list must
differ from the baseline's: identical names with identical reasons mean the
list was written for the baseline's diff and carried forward, which the stamp
alone cannot catch, because it only expires claims when `VERSION` *changes*
and consecutive commits often share one. An empty list is always fine.

The comparison ref must not resolve to `HEAD`. A tree compared against itself
is identical by construction, so nothing can ever drift and every claim is
stale; `env_drift.py` refuses that instead of passing, and CI resolves the ref
with no fallback to `HEAD`. So a run from a checkout that *is* `main` needs a
real baseline — `GOLDEN_REF=HEAD^1 ./tests/run.sh` — rather than the default
`origin/main`, which there is this same commit.

Without `--all` only the five sensitive fixtures are captured, so claims
naming any other scenario are reported there as *not evaluated* rather than
stale; judging those is `--all`'s job, which is what CI runs.

The baseline half of the comparison is the slowest step in the whole suite,
and it is byte-identical for every branch forked from the same commit, so it
is cached between runs in `~/.cache/heatpump_optimizer/drift-baseline`
(outside the repository, so it is never committed; `DRIFT_CACHE_DIR` moves it,
`DRIFT_NO_CACHE=1` turns it off, `DRIFT_CACHE_KEEP` bounds how many entries
are kept). The key covers the baseline commit *and* its tree, the SHA-256 of
`env_drift.py` itself — which is what decides which scenarios are captured and
how — the capture mode, the interpreter, the full installed distribution
inventory, numpy's build configuration, the environment variables the capture
path reads, and a `numeric_probe`: a fixed seeded numpy/scipy workload hashed
to the last bit, so a swapped BLAS or a rebuilt scipy invalidates the entry by
measurement rather than by guesswork. A hit prints a banner naming the key and
the entry it came from, so gate output always says when a baseline was reused.
`python tests/env_drift.py --cache-key <ref> --all` prints the key a run would
look up; CI keys `actions/cache` with it on pull requests, where the
merge-base is stable across pushes.

Reading a cache hit in gate output: the banner is the gate telling you it did
*not* recompute the baseline. Everything after it — every `ok`, `DRIFT`,
`CLAIMED` and `may-drift` line — was judged against bytes captured by an
earlier run on this machine, not against a worktree built just now. The banner
names the key, the entry file, the commit and tree it stands for, how long ago
it was captured, and a digest per key component, so you can see what the reuse
was conditional on. If a result looks wrong and you want the baseline rebuilt
from scratch to be certain, re-run with `DRIFT_NO_CACHE=1`; the verdict must
come out identical, and a cold and a warm run of `--all` against the same ref
have been checked to agree across all 53 scenarios including the five sensitive
ones. A cache hit never changes how a scenario is judged — it only changes
where one side of the comparison came from. The branch half is always recaptured, so
even if the environment moved without moving the key, a mismatched baseline
shows up as drift — a loud, over-strict failure — rather than as a silent pass.

`--record` re-records from current behaviour. **Read the diff before doing
that.** A change here is either a bug or a deliberate decision that belongs in
a commit message; the whole value of the file is that re-recording is a choice
rather than a reflex.

**`rolling.py` asks "does it hold up in the loop?"** Everything else solves
once. The integration re-plans every half hour against a house that never quite
matches its model, and feeds the outcome into learners that then change the
model. Drift, oscillation and learner divergence only appear there.

## What each script is for

- **features.py** drives the v2.8.0 feature modules directly: the staleness
  watchdog, external heat detection, the learned price shape, the capacity
  tariff, PV surplus pricing, away mode, closed-loop accuracy, the defrost
  derate, building presets, system identification, comfort learning and the
  virtual battery. These need mechanism-level tests because their failure mode
  is a *plausible* plan: a detector that never fires, or a watchdog that lets a
  flatline through, produces output that looks entirely normal.
- **entities.py** constructs every entity through the real `async_setup_entry`,
  so an entity that is written but never registered shows up as missing. It
  also checks that `PLATFORMS` and `PLATFORM_LIST` agree, that every options
  menu row has a handler behind it, that `strings.json` and both translations
  have identical keys, and that the accumulating sensors are
  `TOTAL_INCREASING` — a `MEASUREMENT` there silently keeps them out of the
  Energy dashboard with no error anywhere.
- **validate.py** runs single-zone and two-zone houses through winter, summer
  and shoulder conditions, with and without hot water, and checks solver
  status, power bounds, per-step comfort bounds, savings range, hot water
  availability during demand windows, how much energy lands in the most
  expensive quarter of the day, that no heating step lacks a reason code, and
  that plans do not chatter. It prints `NO ISSUES` when everything holds, and
  reports compressor starts and projected peak per scenario.
- **edge.py** covers single-step and 48 hour horizons, flat/zero/negative
  prices, -25 °C and storm conditions, starting outside the comfort band, an
  overdue legionella cycle, a 1500 L tank, and a collapsed comfort range.
- **golden.py** pins exact behaviour; see above.
- **stress.py** sweeps 48 combinations of season, building archetype, zoning
  and feature flags, plus 17 edge conditions, and checks three families of
  invariant: physical (power in bounds, tank not boiled, energy conserved),
  economic (cheaper than a thermostat where there is spread to exploit, costs
  reconcile with the schedule, the README's comfort-weight table still holds)
  and comfort (the floor respected to within what the soft penalty allows, and
  never worse than running flat out would achieve — an undersized pump in a
  leaky house cannot hold the floor, and blaming the optimizer for that would
  be blaming it for physics). This sweep found three real defects: a capacity
  tariff that raised the peak it was meant to lower, a tariff term that dwarfed
  the energy cost on a fresh install, and DHW planners that could push the tank
  past its rating. Its solve-time guard is denominated in **CPU time**, not
  wall clock, and normalised against a reference solve. An absolute wall-clock
  budget cannot tell a slower solver from a busier machine, and on a shared box
  it answers the second question — it produced five false failures in one day,
  once on pristine `main` with worse timings than the branch under test, and a
  clean run of this file recorded its dearest scenario at 87,977 ms against the
  90,000 ms the release gate allows: two seconds of headroom on code that had
  changed nothing. Measured here by adding three CPU hogs mid-run, a scenario's
  wall time moved 3.08× while its CPU time moved 0.99×; only one of those is
  about the code. A fixed reference solve (defined in `stress.py`, so no change
  to the integration can move it) is timed beside every scenario and the ratio
  of CPU times is budgeted: `STRESS_SOLVE_RATIO` per scenario, and
  `STRESS_SWEEP_RATIO` for the sweep as a whole on a much tighter margin, which
  is what catches a change that made everything moderately slower.

  Two things the run states out loud rather than assuming. `time.process_time()`
  sums CPU over every thread, so a threaded BLAS inflates it; the ratio only
  cancels that if the reference and the scenarios are parallelised alike, so the
  run measures both thread factors and **fails** if they diverge, telling you to
  pin `OMP_NUM_THREADS=1`/`OPENBLAS_NUM_THREADS=1` or recalibrate. And
  `STRESS_SOLVE_CEILING_MS` stays on the *wall* clock and is not redundant: a
  CPU budget is blind to a regression that makes the solver block rather than
  compute — a lock, an I/O stall, a retry loop, a solve that never returns.
  `STRESS_SOLVE_BUDGET_MS` is retired; a run that sets it says so.
- **rolling.py** drives the real re-planning cycle for several simulated days
  against a plant deliberately mismatched from the optimizer's model, and is
  the only test that exercises the self-learning heat-loss correction against a
  house that genuinely differs from its model. It drives the coordinator's own
  estimator rather than a copy of its arithmetic, because a test that
  reimplements a learner only proves the reimplementation works.
- **backtest.py** replays the same house, prices and weather through the
  optimizer, an always-on thermostat, a hand-written night-tariff schedule and
  a price-only greedy schedule, and scores each on cost *and* on degree-hours
  below the comfort floor. It also reconciles the savings the integration
  reports with the savings the replay measures, so the dashboard figure is the
  same quantity a user would compute themselves. A cheaper strategy only counts
  as a competitor if it is also comfortable.
- **optimality.py** is a solution-quality floor. It compares the optimizer
  against a greedy cheapest-hours schedule with the same total energy and
  against 300 comfort-preserving random perturbations, and fails if either
  finds a materially cheaper comfortable plan — the margin says "the solver
  missed its basin", with headroom over the measured gap so solver noise
  cannot trip it. The challengers price energy only, not the full objective
  (comfort pull, cycling), so a small measured gap on the two-zone house is
  expected and documented in the file.
- **plan_view.py** runs a winter scenario and builds the payloads the two plan
  sensors publish, checking that the slot summaries reconcile with the raw step
  schedule and that every heating step carries a reason code and price
  provenance. It writes the result to `/tmp/plandata.json`.
- **frontend.py** checks how the card reaches the browser: that a missing
  resource is created, a stale cache-busting query is refreshed rather than
  left to serve a cached card, a duplicate copy installed elsewhere is
  reported, and YAML mode is left alone.
- **card.mjs** loads the Lovelace card in Node against a DOM stub and the
  payload written by `plan_view.py`. The stub *parses* `innerHTML` rather than
  merely storing it: the card queries its own output for the controls it then
  wires up, so a stub that keeps the markup as an opaque string skips every one
  of those paths and reports a pass. It checks the seven series, entity
  discovery by `plan_kind`, the expanded dialog, legend scaling in the popup,
  reason codes in the tooltip, the shading of estimated prices, and the what-if
  simulator's debounce and error handling.

## Note on browser checks

`card.mjs` does not lay anything out, so it cannot catch a visual overflow. For
changes to the chart's geometry, verify in a real browser as well.
