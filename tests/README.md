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
`card.mjs` reads, so those two stay in one lane in that order. A script that is
wired into `run.sh` but that no lane actually executes fails the run, which the
older "is it mentioned?" grep could not see. Output is captured per script and
replayed whole, one script at a time, once the lanes finish; `GATE_JOBS=1` puts
it back to one script at a time with streaming output, which is what to reach
for when a failure needs watching as it happens.

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

### The gate lock on a shared box

`tests/stress.py` measures this machine while it solves, so only one agent on
a box may run it (or a full gate that includes it) at a time. Use
`tests/gate_lock.py` — not `mkdir /tmp/hpo-gate.lock` and a shell pid:

```bash
python3 tests/gate_lock.py take --label <your-label>
HPO_GATE_LOCK_LABEL=<your-label> GATE_SCOPE=auto GOLDEN_MODE=drift \
  GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh
python3 tests/gate_lock.py renew --label <your-label>   # between commands
python3 tests/gate_lock.py release --label <your-label>
python3 tests/gate_lock.py status
```

The owner file at `/tmp/hpo-gate.lock/owner` carries your label and an
`expires_at` lease (30 minutes — above the longest observed full gate and
stress lane). Every script `run.sh` runs under lock renews it. An expired
lease, or an abandoned hold (`holding` marker, no live flock), may be taken
without forensics — the script decides that, you do not. `run.sh` holds `flock`
on `/tmp/hpo-gate.lock/flock` for the gate run so a crash drops flock and a
waiter can take immediately; the lease covers the window between commands when
nothing holds flock (#404). Take the lock only when `tests/closure.py select`
reports `MODE: FULL` or names `tests/stress.py`.

### How a closure is derived

Never by hand. `tests/closure.py`'s module docstring states how a record is
taken, which two instruments it unions, and why a hand-maintained table cannot
be trusted. Three things it does not say, because they are rules about *using*
a recording rather than about taking one:

* A single stale closure does not need a whole re-derivation:
  `./tests/derive_closures.sh --single tests/<script>.py` re-records one script
  and merges it in — the same flag "Adding a test script" below uses for a
  brand-new script, and the cheap path for an existing one.
* A Darwin node recording is a **subset** of `strace -f`. `merge --partial`
  unions a `how: node-fs-trace` record into the committed list so `--single`
  can grow a node closure without dropping files only Linux `strace` saw. Do
  **not** use Darwin `--single` to repair a CI `UNDER-SCOPED` — that job already
  recorded under `strace`, and Linux `closures` on `main` stays the
  completeness check.
* Three closures are widened by rule, because a trace of *this* process cannot
  see what they depend on. **`env_drift.py` and `golden.py`** compare
  *behaviour* between two checkouts, in subprocesses, inside a worktree outside
  this repo, so their closure is the entire integration plus every file in
  `tests/golden/` — and on top of that, `env_drift.py` **always runs whenever
  anything under `custom_components/` changed**, whatever the closure says,
  because file-name reasoning cannot justify skipping a behavioural comparison.
  **`card.mjs`** inherits `plan_view.py`'s whole closure, because
  `plan_view.py` writes the payload the card is rendered against; selecting
  `card.mjs` also selects `plan_view.py` to *run*, which is a different kind of
  dependency — not "what can change this script's answer" but "what has to run
  first for it to run at all". A scope that took the card without its producer
  would leave it with no payload, or, on a developer's box, with a stale one
  from an earlier run.

### What it actually saves

Measured against a real CI run of the fast job (2435 s: `stress.py` 1254 s,
`features.py` 415 s, `edge.py` 307 s, `validate.py` 207 s, `backtest.py`
199 s, everything else inside 53 s between them):

| change | scripts run | CI seconds | saved |
|---|---|---|---|
| a change to `RELEASE_NOTES.md` | 1 — `entities.py` | 5 | 100% |
| a change to `tests/card.mjs` | 3 — `plan_view.py`, `card.mjs`, `card_drift.mjs` | 15 | 100% |
| a change to the card's JavaScript | 5 — `plan_view.py`, `card.mjs`, `card_drift.mjs`, `features.py`, `entities.py` | 430 | 82% |
| a config-flow change (`config_flow.py`, `strings.json`, both translations) | 4 — `features.py`, `entities.py`, `golden.py`, `env_drift.py` | 431 | 82% |
| a change to `optimizer.py` | 14 — everything but `frontend.py` and `open_meteo.py` | 2424 | 0% |

Those are one CI run's numbers against the suite as it stood, kept as measured.
Script counts move as lanes are added; the shape of each result is the point,
and `tests/closure.py select` prints the live selection for your own diff.

The last row is the point, not an embarrassment: a change to the solver can
reach almost every script, the closures say so, and a scoped gate that found a
way to skip work there would be lying. The card row is the measurement
disagreeing with the intuition — a card-only change costs 430 s and not five,
because `features.py` and `entities.py` both open the card's JavaScript, while
`frontend.py` is *not* run, because it checks how the card reaches the browser
and never opens the card's code at all.

### When it refuses to scope

Scoping turns itself off and runs everything whenever it cannot be sure: a
missing `tests/closures.json`, a script in `tests/` with no closure or a
closure naming a script that no longer exists, a changed file that no recorded
closure mentions and no list classifies, a change to the gate itself, a
`closure.py` failure of any kind, or a diff it cannot determine.

The classifications are `closure.py`'s own `INERT`, `GATE_FILES` and
`SLOW_GATED` tuples, each with its reason beside it — read them there, never
from prose, because prose goes stale against a tuple that gets narrowed. The
rule they encode: **"no test reads it" is not something to assume about a file
nobody measured.** The repository's top-level `README.md`, `RELEASE_NOTES.md`
and brand images all look unreadable by any test and are all closure-mapped
rather than listed, because `entities.py` and `env_drift.py` do read them.

### Adding a test script

A new runnable script in `tests/` has no closure until one is recorded, and an
unclosed script makes the gate above refuse to scope — silently, on every PR,
with only a line in the run log. The `closures` job on main therefore **fails**
when a selectable script went unrecorded: the omission costs one red main run
instead of weeks of quiet full gates. Record it with the `--single` form above
and commit the script and `tests/closures.json` together; if it belongs in a
lane permanently, add it to `tests/derive_closures.sh` too, so full
re-derivations keep it fresh. (`golden.py` and `env_drift.py` get their cheap
recorded arguments automatically; `card.mjs` and `card_drift.mjs` record
through `strace` on Linux or `--import` on Darwin.)

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

`CLAUDE.md` rule 1 states the asymmetry — scoped on a branch, forced `full` on
every push to `main`, and why keying on the mode line is the only safe reading.
What that leaves for here is the second job.

`closures` runs beside the gate on `main` and on the nightly: it re-derives
every closure from real instrumented runs and fails if `tests/closures.json`
misses anything a run actually touched (`closure.py check`). A closure that
lists *more* than a run touched only costs time and is reported rather than
failed. So the closures cannot silently drift out of date behind a refactor;
the run that would have caught the drift is the same run that reports it.

On a pull request, `closures` runs only when `closure-scope` says the diff can
move a closure; a diff it judges `skip` — every changed file INERT — leaves the
job **skipped**, not passed. Read that the way you read the mode line: a
skipped `closures` means the table was **not checked on this PR at all**, and
only the unscoped run after the merge re-derives and checks it. "Every check
success or skipped" is a correct merge rule, because some jobs legitimately
never run, and it is also how a clean-looking verification can be zero
re-derivation work.

Two CI jobs repair mechanical failures of this gate on same-repo pull requests:
`closures-autofix` for `UNDER-SCOPED`, `claims-autofix` for `INHERITED CLAIMS`.
**Do not open a second PR, run Darwin `--single`, or hand-empty a claim file
for either** — wait for the bot commit and the dispatched recheck, and key on
the job's summary line rather than its conclusion, because green covers both
"repaired and pushed" and "nothing was owed". `.cursor/rules/ci-autofix.mdc` is
the policy: which statuses mean a commit is coming, which mean none is, and
what to do in each case.

If you have changed what a test reaches — new fixture, new import, a script
that starts reading a file it did not before — push the code change and
let `closures-autofix` merge the Linux recordings. Local regenerate is
only needed when you are not on a same-repo PR, or when there is **no**
recording (a new selectable script the lanes never ran):

```bash
./tests/derive_closures.sh                # ~one full suite; rewrites tests/closures.json
./tests/derive_closures.sh --record-only  # record without rewriting it — what main does
```

A pull request that touches `tests/closures.json` is itself in the "changes
the gate" case above, so it runs the whole suite unscoped. The change that
redefines what may be skipped is never validated by the definition it is
introducing.

## The Home Assistant stub

`tests/hastub/` is a minimal stand-in for the parts of `homeassistant` the
integration imports, so the suite runs without a Home Assistant install. It is
deliberately small, and version-controlled: a fuller stub would drift from the
real thing without anyone noticing, and the job here is to let the integration
*import* and its entities be *constructed*, not to reimplement Home Assistant.

### When your change depends on how a Home Assistant API behaves

**Read that API's real upstream source and check the stub matches. If it does
not, fix the stub in the same pull request.** Every lane here runs with
`PYTHONPATH=tests/hastub`, so a green test proves your code works against *the
stub's* behaviour — and the stub is written from what the code under test
needs, which is exactly the shape that agrees with a wrong implementation.

This is not hypothetical: four divergences were found the expensive way, one
per seat, and each is now a `DIVERGENT` entry in `tests/ha_contract.py`'s
inventory carrying the issue that found it and the upstream behaviour it
misses.

`tests/ha_contract.py` is where that reading gets written down (#536). Its
docstring states what the file is for, what its three products are and what it
deliberately does not cover; the disposition constants near the top state what
each disposition obliges. What none of that machinery does is invent a contract
nobody wrote, so the rule at the top of this section still stands.

## A test must never re-implement what it is testing

A test may build inputs and expected *values*. It must never contain its own
copy of a production formula, constant or guard, and then assert against the
copy.

This is a distinct failure from a test that cannot fail, and it survives the
review that catches those. The assertion *can* fail — it just fails when the
test file's arithmetic changes rather than when production's does, so it looks
convincing under a mutation proof while pinning nothing. It has been found
twice, the second time in the round that was explicitly told to fix the first:
a test with its own copy of the coordinator's confidence curve, and a test with
its own copy of its materiality guard, whose epsilon assertions all ran against
the copy — deleting the constant from the real guard left the whole suite green.

The rule: **every assertion about a computed quantity imports and calls the
production symbol.** If production is awkward to call from a test — the value
is buried in a method, or needs a coordinator to exist — that is a finding
about production's shape, not permission to copy the formula. Extract it and
test the extraction.

The corollary for reviewers: "name a single-line production mutation that
kills this assertion" is necessary but not sufficient. Also ask *which file*
the mutation has to be made in. If the answer is the test file, the assertion
is measuring itself. Ask which **operator**: line deletion killed 0 of 8 on
`validate.py` and `optimality.py`; arithmetic killed 2 of 2 on `optimality.py`.
Sample arithmetic and off-by-one; delete nothing.

## The two guards

Most of these scripts ask "is the answer good?". Two ask something different,
and between them they cover the failures that are otherwise invisible.

**`golden.py` asks "has the answer changed?"** Its docstring says what it
records and why the rest of the suite cannot see what it sees; `resolve_mode`'s
docstring beside it says which comparison an environment gets and why an unset
`GOLDEN_MODE` means `drift` rather than `strict`; `assert_invariants`' says why
a physical-possibility layer runs on record as well as on check. Three facts
that live nowhere in that file: it pins 55 fixtures (49 plan scenarios, 5
coordinator captures and the config-flow schema); `run.sh` *exports* both
variables, so when the suite picks a mode the child sees the same one; and
`run.sh`'s own default is still `strict`, which is the only place the committed
fixtures are compared at all.

Five golden fixtures are non-convex valve/wood solves whose floats do not
reproduce across BLAS builds, so their exact comparison is meaningless off the
recording machine. **`env_drift.py`** is the answer: it captures scenarios
twice in the *same* environment — working tree against a worktree of a
reference commit — and requires byte-identity, so solver noise cancels and only
the branch's own footprint remains. Its docstring names the five, and states
the claim rules (`claims-for:` against `VERSION`, the refusal of a claim list
inherited from the baseline, `--claims-only`, stale versus not-evaluated), the
baseline cache and everything its key covers, and the refusal of a ref that
resolves to `HEAD`.

Two consequences of that refusal, for a run started by hand rather than by
`run.sh`: a checkout that *is* `main` needs a real baseline —
`GOLDEN_REF=HEAD^1 ./tests/run.sh` — because the default `origin/main` is there
this same commit; and a cache hit changes only where one side of the comparison
came from, never how a scenario is judged, so `DRIFT_NO_CACHE=1` must produce
an identical verdict and does (checked cold against warm across all 55
scenarios, the five sensitive ones included).

**Are the committed fixtures still current?** Everything above compares
computed against computed, so neither side of it is the committed file, and
until #347 no CI job compared a committed fixture at all: the fixtures were
guarded against *changing* and not at all against *being wrong*. `env_drift.py`
now also judges its own branch capture against the committed files in three
levels — exact, structural, values — and the comment block above `FIXTURE_DIR`
carries each level's definition, what it fires on, which signals were cut from
the structural projection and the measurement that decided each cut.

What that comment cannot say, because it is a rule about when a person runs the
script: `python tests/env_drift.py --fixtures` runs those three levels alone,
with no reference tree and no baseline capture, and is **what to run before and
after `golden.py --record`**. Given a capture file written earlier by
`--capture` it re-reads that instead of solving again.

`--record` re-records from current behaviour. **Read the diff before doing
that.** A change here is either a bug or a deliberate decision that belongs in
a commit message; the whole value of the file is that re-recording is a choice
rather than a reflex.

**`rolling.py` asks "does it hold up in the loop?"** Everything else solves
once; its docstring states which classes of failure only appear in the
re-planning loop.

## Running one script at a time

Every lane script also runs on its own:

```bash
export PYTHONPATH=tests/hastub

python tests/features.py     # the feature modules, driven directly
python tests/entities.py     # entities, platforms, options pages, translations
python tests/manual_plan.py  # manual plan pinning: parsing, solver interaction, safety release
python tests/open_meteo.py   # the irradiance client
python tests/solar_alignment.py  # irradiance lands on the right optimizer steps
python tests/golden.py       # behaviour, pinned; reads GOLDEN_MODE (default drift)
python tests/validate.py     # 22 seasonal scenarios, asserts invariants
python tests/edge.py         # degenerate inputs and boundary conditions
python tests/backtest.py     # replay against alternative strategies
python tests/stress.py       # 48 combinations, 17 edge cases, economics
python tests/rolling.py      # days of re-planning against a mismatched house
python tests/optimality.py   # solution-quality floor against cheap challengers
python tests/env_drift.py    # sensitive fixtures vs origin/main, same machine
python tests/env_drift.py --fixtures  # are the COMMITTED fixtures still current?
python tests/plan_view.py    # plan sensor payloads, writes HPO_PLANDATA (default /tmp/plandata-<hash>.json)
node   tests/card.mjs        # renders the dashboard card against that payload
node   tests/setup_qa_render.mjs  # setup-page SVGs off the same payload, for designer review
node   tests/card_drift.mjs       # the card's markup gate: this tree vs GOLDEN_REF, byte for byte
```

`profiles.py` holds Nord Pool SE3 price curves and Swedish weather profiles for
winter, summer and shoulder season, used by the end-to-end scripts.
`harness.py` holds the fakes the unit-style scripts share.

## What each script is for

Most scripts here carry a module docstring stating what they drive and why they
exist. Read it in the file; what follows is only what a script does not say
about itself.

- **validate.py**, **edge.py** and **plan_view.py** carry no docstring, so this
  is the only description of them. `validate.py` runs single-zone and two-zone
  houses through winter, summer and shoulder conditions, with and without hot
  water, and checks solver status, power bounds, per-step comfort bounds,
  savings range, hot water availability during demand windows, how much energy
  lands in the most expensive quarter of the day, that no heating step lacks a
  reason code, and that plans do not chatter; it prints `NO ISSUES` when
  everything holds, and reports compressor starts and projected peak per
  scenario. `edge.py` covers single-step and 48 hour horizons,
  flat/zero/negative prices, -25 °C and storm conditions, starting outside the
  comfort band, an overdue legionella cycle, a 1500 L tank, and a collapsed
  comfort range. `plan_view.py` runs a winter scenario and builds the payloads
  the two plan sensors publish, checking that the slot summaries reconcile with
  the raw step schedule and that every heating step carries a reason code and
  price provenance; it writes the result to `HPO_PLANDATA`, which defaults to
  `/tmp/plandata-<sha256(tests dir)[:12]>.json` — a per-checkout path, so two
  worktrees never collide. `card.mjs` alone falls back to an unhashed default
  under `/tmp` with a warning if the variable is unset; every other Node
  harness requires it.
- **stress.py**'s budgets and the reasoning behind every constant in them live
  in the `#:` comments beside the constants: why the solve-time guard is
  denominated in CPU time rather than wall clock, why `STRESS_SOLVE_CEILING_MS`
  stays on the wall clock and is not redundant, why every budget is checked
  from *both* sides against `STRESS_DETECTION_TARGET`, why a budget is a
  property of the recording and an observation a property of the machine, why
  the per-scenario factor is not portable under about 2.3× where the sweep
  ratio is, and the zero-range-bound scenarios (#286/#287) that were unsampled
  rather than under-budgeted. Read them there: a second copy of a budget's
  rationale is how a budget gets widened without its reason being reread.
  `optimality.py` carries the quality half of that sampling — a plan built with
  a fixed variable in it must still meet the comfort floor, honour its pin, and
  not be routed by a trivial challenger; a gradient that returns NaN at a fixed
  variable makes the solver give up at iteration zero, which is *faster*, so
  cost alone would never see it.
- **backtest.py**'s docstring names its three baselines. Not there: it also
  reconciles the savings the integration reports with the savings the replay
  measures, so the dashboard figure is the same quantity a user would compute
  themselves.
- **frontend.py** checks how the card reaches the browser: that a missing
  resource is created, a stale cache-busting query is refreshed rather than
  left to serve a cached card, a duplicate copy installed elsewhere is
  reported, and YAML mode is left alone.
- **card.mjs** loads the Lovelace card in Node against a DOM stub and the
  payload written by `plan_view.py`. The stub *parses* `innerHTML` rather than
  merely storing it: the card queries its own output for the controls it then
  wires up, so a stub that keeps the markup as an opaque string skips every one
  of those paths and reports a pass.
- **card_drift.mjs** is the card's markup gate; its header states what it
  renders, why it is differential rather than golden-based, and that a moved
  state must be claimed in `tests/golden/card_claimed_drift.txt`. Not there:
  `card.mjs` checks that file's `claims-for:` stamp too, so a strict local run
  without a ref still sees a stale stamp, and `run.sh` skips `card_drift.mjs`
  when `GOLDEN_REF` is unreachable or is this commit, exactly as it does for
  `env_drift.py`.
- **setup_qa_render.mjs** renders the three setup-page topologies to SVGs in
  `../setup-qa/`, outside the repository, for a designer to eyeball — but it
  is a wired check, not a manual errand. It is `run` from the card lane
  (v6.x, #101), off the payload `plan_view.py` just wrote, and fails when a
  topology's setup SVG comes out empty, so a dormant renderer cannot drift
  unnoticed. It shares `card_rig.mjs` — and through it `dom_stub.mjs` — with
  `card.mjs`, and is skipped alongside them when `node` is absent.

Some files in `tests/` are not tests at all and are excluded from the "every
script must be wired into `run.sh`" accounting. The exclusion list lives in
`tests/run.sh`'s `UNWIRED TEST` loop, with a reason on each entry — read it
there rather than from a copy. Two of those reasons constrain what you may do
here rather than only explaining an exclusion: `card_browser.mjs` and
`nightly_ha.py` are real tests that this gate must never run — Chromium and
Docker are not available to it — and neither may gate a pull request; see "Note
on browser checks" below for where the first one runs instead.
`derive_closures.sh` is not excluded because it was never in scope: the loop
globs `tests/*.py tests/*.mjs`, so a `.sh` is not a candidate for wiring.

## Note on browser checks

`card.mjs` renders against a DOM stub that returns a constant rectangle for
every measurement, so it cannot catch a visual overflow, a font that failed to
load, or anything else that depends on real layout. `tests/card_browser.mjs`
covers that gap: it drives the card in an actual Chromium (via Playwright,
resolved from `NODE_PATH`, under `PLAYWRIGHT_BROWSERS_PATH`) and is run by its
own `browser` job in `.github/workflows/tests.yml` on every push and pull
request — never scoped, and not one of the scripts `run.sh` lanes above. For
changes to the chart's geometry, that job is what actually verifies them;
running `card_browser.mjs` locally needs the same Playwright/Chromium setup
CI uses.
