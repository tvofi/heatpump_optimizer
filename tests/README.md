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

## The scoped gate

A full run is about forty minutes. A change to the dashboard card genuinely
needs `card.mjs`, `plan_view.py` and `frontend.py` — about five seconds of
those forty minutes. On **pull requests only**, the gate runs just the scripts
the change can actually reach:

```bash
GATE_SCOPE=full ./tests/run.sh                       # the default, everywhere
GATE_SCOPE=auto ./tests/run.sh                       # scope to the diff vs origin/main
GATE_SCOPE=auto GATE_SCOPE_BASE=v5.1.0 ./tests/run.sh   # ...vs something else
```

`GATE_SCOPE=full` is the default in every context, including this repository's
own scripts when nobody has said otherwise. Scoping has to be asked for by
name.

### How a closure is derived

Never by hand. A hand-maintained table of "what does this test depend on"
would rot on the first refactor and nobody would notice.

`tests/derive_closures.sh` runs the whole suite once under instrumentation and
rewrites `tests/closures.json`. For each script, `tests/closure.py` runs it for
real in a subprocess with a `sys.addaudithook` hook installed and then records
the union of

* every `open` the run performed — this is how the fixture and catalogue files
  get in: `tests/golden/*.json`, `strings.json`, `services.yaml`,
  `manifest.json`, `VERSION`, `translations/*.json`, `tests/harness.py`,
  `tests/profiles.py`, the recorded Open-Meteo payloads;
* every repo path that appeared on a subprocess command line — this is how
  `features.py` reaches `tests/dst_checks.py`;
* every entry in `sys.modules` whose `__file__` is inside the repo — the
  integration modules and the `tests/hastub` stub.

`card.mjs` has no audit hook, so it is recorded under `strace` instead; the
result is the same list of repo files it really opened.

Three closures are then widened by rule, because a trace of *this* process
cannot see what they depend on:

* **`env_drift.py` and `golden.py`** compare *behaviour* between two
  checkouts, in subprocesses, inside a worktree outside this repo. Their
  closure is the entire integration plus every file in `tests/golden/`. On top
  of that, `env_drift.py` **always runs whenever anything under
  `custom_components/` changed**, whatever the closure says — file-name
  reasoning cannot justify skipping a behavioural comparison.
* **`card.mjs`** inherits `plan_view.py`'s whole closure, because
  `plan_view.py` writes the payload the card is rendered against; anything
  that changes the payload changes what the card is tested with. Selecting
  `card.mjs` also selects `plan_view.py` to *run*, which is a different kind
  of dependency — not "what can change this script's answer" but "what has to
  run first for it to run at all". A scope that took the card without its
  producer would leave it with no payload, or, on a developer's box, with a
  stale one from an earlier run.

### What it actually saves

Measured against a real CI run of the fast job (2435 s: `stress.py` 1254 s,
`features.py` 415 s, `edge.py` 307 s, `validate.py` 207 s, `backtest.py`
199 s, everything else inside 53 s between them):

| change | scripts run | CI seconds | saved |
|---|---|---|---|
| a change to `RELEASE_NOTES.md` | 1 of 16 — `entities.py` | 5 | 100% |
| a change to `tests/card.mjs` | 3 — `plan_view.py`, `card.mjs`, `card_drift.mjs` | 15 | 100% |
| a change to the card's JavaScript | 5 — `plan_view.py`, `card.mjs`, `card_drift.mjs`, `features.py`, `entities.py` | 430 | 82% |
| a config-flow change (`config_flow.py`, `strings.json`, both translations) | 4 — `features.py`, `entities.py`, `golden.py`, `env_drift.py` | 431 | 82% |
| a change to `optimizer.py` | 14 — everything but `frontend.py` and `open_meteo.py` | 2424 | 0% |

The last row is the point, not an embarrassment. A change to the solver can
reach almost every script in the suite, the closures say so, and the gate
runs almost the whole suite. A scoped gate that found a way to skip work
there would be lying.

The card row is worth reading twice, because it is not what anyone would have
guessed. A card-only change does **not** cost five seconds: `features.py` and
`entities.py` both open the card's JavaScript, and `features.py` alone is
415 s. Meanwhile `frontend.py` — which sounds like the most card-adjacent
script in the suite — is *not* run, because it checks how the card reaches the
browser and never opens the card's code at all. Both of those are the
measurement disagreeing with the intuition, and the measurement is what the
gate uses.

### When it refuses to scope

Scoping turns itself off and runs everything whenever it cannot be sure:

* `tests/closures.json` is missing, or has no closure for some script in
  `tests/`, or names a script that no longer exists;
* a changed file is not mentioned by *any* recorded closure and is not on the
  short, checked list of files no test can read (`docs/`, `tools/`, this
  file, the licence files, `DISCLAIMER.md`, the quality-scale register). The
  repository's top-level `README.md` and `RELEASE_NOTES.md` are not on this
  list — `entities.py` reads both — and neither are the brand images, which
  `env_drift.py` reads; a change to any of the three is closure-mapped, not
  assumed safe. "No test reads it" is not something to assume about a file
  nobody measured;
* the change touches the gate itself — `run.sh`, `closure.py`,
  `closures.json`, `requirements-ci.txt` or `.github/workflows/`;
* `closure.py` fails for any reason at all;
* the diff cannot be determined.

### Adding a test script

A new runnable script in `tests/` has no closure until one is recorded, and an
unclosed script makes the gate above refuse to scope — silently, on every PR,
with only a line in the run log. The `closures` job on main therefore **fails**
when a selectable script went unrecorded: the omission costs one red main run
instead of weeks of quiet full gates.

Recording one script is deliberately cheap (a full re-derivation runs the
whole suite and takes as long):

```
./tests/derive_closures.sh --single tests/<the-new-script>.py
```

which records just that script and merges the result into
`tests/closures.json`. Commit both together. (`golden.py` and `env_drift.py`
get their cheap recorded arguments automatically; `card.mjs` and
`card_drift.mjs` are recorded through strace.) If the script belongs in a
lane permanently, add it to `tests/derive_closures.sh` as well, so full
re-derivations keep it fresh.

### What you see when something is skipped

Both before and after the run, every scoped-out script is printed by name with
its reason and the size of the closure it was checked against:

```
      SKIP  tests/stress.py  (closure: 61 files, no changed file is in its measured closure)
...
########## NOT RUN: scoped out of this gate ##########
  tests/stress.py          did NOT run -- no changed file is in its measured closure (closure: 61 files)
```

This suite already has six known instances of a test that looked like it ran
and asserted nothing. A script that quietly did not run at all would be worse,
because it would look like a pass, so it is said twice and never in passing.

### What the post-merge gate guarantees

Scoping applies to pull requests. `.github/workflows/tests.yml` forces
`GATE_SCOPE=full` on **every push to `main`**, on the nightly, and on any
manual dispatch, so the whole suite runs, unscoped, against every merged
change regardless of what it touched. If a closure is ever wrong, the scoped
PR gate may miss it — but the next gate, the unscoped one on `main`, does not.
`main` goes red within one merge instead of never.

A second job, `closures`, runs beside it on `main` and on the nightly: it
re-derives every closure from real instrumented runs and fails if
`tests/closures.json` misses anything a run actually touched
(`closure.py check`). A closure that lists *more* than a run touched only
costs time and is reported rather than failed. So the closures cannot silently
drift out of date behind a refactor; the run that would have caught the drift
is the same run that reports it.

If you have changed what a test reaches — new fixture, new import, a script
that starts reading a file it did not before — regenerate and commit:

```bash
./tests/derive_closures.sh                # ~one full suite; rewrites tests/closures.json
./tests/derive_closures.sh --record-only  # record without rewriting it — what main does
```

A pull request that touches `tests/closures.json` is itself in the "changes
the gate" case above, so it runs the whole suite unscoped. The change that
redefines what may be skipped is never validated by the definition it is
introducing.

Closures that have fallen behind the tree degrade towards *more* work, not
less. A file that has appeared since they were recorded is in no closure, so
it is unmapped and forces a full run; a test script that has appeared has no
closure, so it forces a full run too. Stale closures make the gate slow before
they make it wrong, and the `closures` job on `main` says so out loud.

Or individually:

```bash
export PYTHONPATH=tests/hastub

python tests/features.py     # the feature modules, driven directly
python tests/entities.py     # entities, platforms, options pages, translations
python tests/manual_plan.py  # manual plan pinning: parsing, solver interaction, safety release
python tests/open_meteo.py   # the irradiance client
python tests/solar_alignment.py  # irradiance lands on the right optimizer steps
python tests/golden.py       # exact behaviour, pinned (--record to re-record)
python tests/validate.py     # 22 seasonal scenarios, asserts invariants
python tests/edge.py         # degenerate inputs and boundary conditions
python tests/backtest.py     # replay against alternative strategies
python tests/stress.py       # 48 combinations, 17 edge cases, economics
python tests/rolling.py      # days of re-planning against a mismatched house
python tests/optimality.py   # solution-quality floor against cheap challengers
python tests/env_drift.py    # sensitive fixtures vs origin/main, same machine
python tests/plan_view.py    # plan sensor payloads, writes HPO_PLANDATA (default /tmp/plandata-<hash>.json)
node   tests/card.mjs        # renders the dashboard card against that payload
node   tests/setup_qa_render.mjs  # setup-page SVGs off the same payload, for designer review
node   tests/card_drift.mjs       # the card's markup gate: this tree vs GOLDEN_REF, byte for byte
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

## A test must never re-implement what it is testing

A test may build inputs and expected *values*. It must never contain its own
copy of a production formula, constant or guard, and then assert against the
copy.

This is a distinct failure from a test that cannot fail, and it survives the
review that catches those. The assertion *can* fail — it just fails when the
test file's arithmetic changes rather than when production's does, so it looks
convincing under a mutation proof while pinning nothing. It has been found
twice, the second time in the round that was explicitly told to fix the first:

* a test defined its own `phi()` reproducing the coordinator's confidence
  curve, and the check named "the weight is exactly 0 at no samples and
  exactly 1 at convergence" asserted against that copy;
* a test defined its own `material()` reproducing the coordinator's
  materiality guard, and every epsilon assertion ran against it. Deleting the
  constant from the coordinator's *real* guard left the whole suite green.

The rule: **every assertion about a computed quantity imports and calls the
production symbol.** If production is awkward to call from a test — the value
is buried in a method, or needs a coordinator to exist — that is a finding
about production's shape, not permission to copy the formula. Extract it and
test the extraction.

The corollary for reviewers: "name a single-line production mutation that
kills this assertion" is necessary but not sufficient. Also ask *which file*
the mutation has to be made in. If the answer is the test file, the assertion
is measuring itself.

## The two guards

Most of these scripts ask "is the answer good?". Two ask something different,
and between them they cover the failures that are otherwise invisible.

**`golden.py` asks "has the answer changed?"** It records the complete output of
55 fixtures (49 plan scenarios, 5 coordinator captures and the config-flow
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
have been checked to agree across all 55 scenarios including the five sensitive
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

  Every budget here is checked from **both** sides. "Is the run slower than its
  budget" is only half the question; the other half is "could this budget ever
  notice", and for two releases the answer was no — the two global ratios were
  sized when the dearest scenario cost 655× the reference, the batched jacobian
  then made every combination 10–20× cheaper, and nobody brought the budgets
  back down. An injected exact 2× regression tripped neither of them (#287). So
  a run now also fails when no budget is within `STRESS_DETECTION_TARGET`
  (default 2) of the cost it was **recorded** against, so widening a budget to
  make a red run pass turns the run red somewhere else.

  Recorded, not observed, and that was executed rather than reasoned: the first
  version compared budgets to the run's own figures and false-failed on CI,
  because the ratio does not travel. The same scenario costs 1.08× more on a
  GitHub runner than on the M1 while the tiny reference solve costs 1.85× more,
  so every ratio compresses by up to 1.7× there. A budget is a property of the
  recording; an observation is a property of the machine. Both headrooms are
  printed every run.

  The **sweep** budget is what carries that 2× requirement, and the
  per-scenario factor deliberately does not. CI ran `shoulder/tariff+cycle` at
  352.7× its reference against a recorded 154.4× — 2.28× the *work*, on a
  runner whose own reference solve was steady to a millisecond — so the
  multi-start solver had landed in another basin. Some scenarios' cost is
  bimodal across platforms, no per-scenario budget under about 2.3× is portable,
  and totals average that away where a single scenario cannot.

  The sweep also samples the **zero-range-bound** path (#286): three scenarios
  pass a `power_caps_extra` fuse cap or a forced-off `space_pins` step, which is
  what a fuse guard and a manual plan pass in production. Before those three,
  nothing in `stress.py` or `optimality.py` had ever passed either argument, so
  a whole class of regression was not under-budgeted but unsampled — measured
  across #317, which fixed it, the same three scenarios cost 68.0×/34.5×/54.1×
  their reference before and 7.4×/5.5×/4.3× after. They are what would notice
  if that fix were ever reverted. `optimality.py` carries the quality half: a
  plan built with a fixed variable in it must still meet the comfort floor,
  honour its pin, and not be routed by a trivial challenger — a gradient that
  returns NaN at a fixed variable makes the solver give up at iteration zero,
  which is *faster*, so cost alone would never see it.
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
  provenance. It writes the result to `HPO_PLANDATA`, which defaults to
  `/tmp/plandata-<sha256(tests dir)[:12]>.json` (a per-checkout path, so two
  worktrees never collide); `card.mjs` alone falls back to an unhashed
  default under `/tmp` with a warning if the variable is unset, but every
  other Node harness requires it.
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
- **card_drift.mjs** is the card's markup gate, the `env_drift.py` idea
  applied to the dashboard card. It runs the working tree's card and the
  comparison ref's card (`git show`, the card is one file) through the same
  twenty-odd states -- inline, expanded, zoomed, a dirty slot draft with its
  menu open, an edited what-if draft, an override in force, the tooltip,
  the three QA topologies' setup pages, a layout drag, a filtered entity
  picker, the config editor's schema -- in one process, against the same
  payload and the same frozen clock, and requires every rendered tree to be
  byte-identical. A state that moves must be claimed, with a reason, in
  `tests/golden/card_claimed_drift.txt`, whose `claims-for:` stamp must equal
  `VERSION` (checked by `card.mjs` too, so a strict local run without a ref
  still sees a stale stamp). Differential rather than golden-based because a
  committed rendering would move with Node's ICU, the time zone and every
  optimizer change; two cards in one process share all of those. `run.sh`
  skips it when `GOLDEN_REF` is unreachable or is this commit, exactly as it
  does for `env_drift.py`.

Seven files in `tests/` are not tests at all and are excluded from the
"every script must be wired into `run.sh`" accounting:

- **dom_stub.mjs** is the DOM the Node card harnesses run against (#101),
  and **card_rig.mjs** the rest of what they share: the vm context around
  that stub, the plan-sensor states built from `plan_view.py`'s payload,
  the three setup-page topologies, the frozen clock, and the claim-file
  parser `card.mjs` and `card_drift.mjs` both use. One copy, three
  importers, for the reason #101 records.
- **harness.py** and **profiles.py** are shared fixtures the unit-style and
  end-to-end scripts import — fakes and price/weather profiles, not scripts
  with assertions of their own; see "What each script is for" below for what
  each holds.
- **setup_qa_render.mjs** is a manual QA render: it writes SVGs to
  `../setup-qa/`, outside the repository, for a designer to eyeball, and
  nothing in the gate reads its output.
- **card_browser.mjs** is a real test — the only one that exercises the card
  in an actual browser rather than a DOM stub — but it runs in its own
  `browser` CI job, not this gate's scoped selection; see "Note on browser
  checks" below.
- **closure.py** is the scoping instrument. It runs the tests in order to
  measure what they touch, derives each one's dependency closure, folds the
  records into `tests/closures.json`, decides what a given diff needs, and
  (`closure.py check`) fails when the committed closures miss something a real
  run touched. Wiring it into the suite would make the suite run itself.
- **derive_closures.sh** drives it across every script, in three lanes, and
  rewrites `tests/closures.json`. See "The scoped gate" above.

## Note on browser checks

`card.mjs` renders against a DOM stub that returns a constant rectangle for
every measurement, so it cannot catch a visual overflow, a font that failed to
load, or anything else that depends on real layout. `tests/card_browser.mjs`
covers that gap: it drives the card in an actual Chromium (via Playwright,
resolved from `NODE_PATH`, under `PLAYWRIGHT_BROWSERS_PATH`) and is run by its
own `browser` job in `.github/workflows/tests.yml` on every push and pull
request — never scoped, and not one of the sixteen scripts `run.sh` lanes
above. For changes to the chart's geometry, that job is what actually verifies
them; running `card_browser.mjs` locally needs the same Playwright/Chromium
setup CI uses.
