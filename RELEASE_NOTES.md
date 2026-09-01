# Heat Pump Cost Optimizer — Release Notes

## v6.2.7

### The docs say what the code does (audit round 1, part 1)

The September 2026 audit verified every documentation claim against the
shipped tree and found six wrong. All six corrected, no behaviour
change:

- **configuration.md** — the "1 · Basics" table was missing the four
  pump-status fields shipped in v5.3.0 (`heat_pump_mode_entity`,
  `heat_pump_defrost_entity`, `heat_pump_online_entity`,
  `heat_pump_fault_entity`); the setup step offers **17** fields, not
  13. "17 assignable configuration keys" is **21**
  (`topology.ASSIGNABLE_KEYS`), and the Sensors-and-entities options
  page has **22** fields, 16 shared with setup step 1.
- **architecture.md** — 45 modules, not 42; `pump_mode.py` and
  `pump_signals.py` added to the module map (stale since v5.1.7).
- **plan-open-issues.md** — the delivery record now states what
  RELEASE_NOTES.md already did (all of #94–#101 shipped; the batched-FD
  gradient shipped in full in v6.2.0, not "in review").
- **tests/README.md** — `manual_plan.py` and `setup_qa_render.mjs`
  added to the individually-runnable script list; both were already
  wired into `run.sh`.
- **manifest.json** — `documentation`/`issue_tracker` pointed at a
  GitHub identity that does not exist (HTTP 404, verified); both, and
  `codeowners`, repointed at `tvofi/heatpump_optimizer`.

## v6.2.6

### The money and energy numbers say what they are

Reading "Hot Water Cost" next to "DHW Heating Cost" gave no way to
know one is a lifetime accumulator that never resets and the other is
the current plan's projection over the next 24 hours — the numbers
looked like the same figure at wildly different magnitudes, and
"Hot Water Energy" read as *very high* because nothing stated since
when.

**The names now carry the period:** Hot Water Cost (lifetime), Hot
Water Energy (lifetime), Space Heating Cost/Energy (lifetime), Total
Energy/Cost (lifetime), DHW Heating Cost (next 24 h), and both
heating-plan sensors (next 24 h). Entity ids do not change; only the
display names move. Swedish carries the same.

**The attributes say it in full:** the accumulators state "lifetime
accumulator; never reset. The state is the whole history, not today's
or this month's figure" and carry `this_month_kwh` /
`this_month_cost` — booked per settlement onto the monthly ledger's
new per-channel lines, from the same numbers the lifetime fold uses,
so the two can never disagree — plus `counting_since`, the date this
integration started recording (an upgrade states the upgrade day
honestly, never a claim about the install itself). The plan sensors
state "planned for the optimization horizon ahead; recomputed on
every replan. Not a measurement and not accumulated." with their
`horizon_hours`, on the no-plan-yet path as well.

**Upgrading**: display names move on existing installs; entity ids,
history and the Energy dashboard are untouched. The new month
attributes start accruing with the next settlement.

## v6.2.5

### Weekly hot-water windows: different days, different times

Hot-water demand windows applied identically to all seven days, so a
household whose mornings differ — weekdays early, weekends late, or
one specific day with its own pattern — could not say so. The window
spec now carries an optional day selector per range:

    weekdays 06:00-08:30, weekend 08:00-09:30
    Mo 05:30-07:00, Tu-Fr 06:00-08:00, Sa,Su 08:00-09:30

A selector is `daily` (the default when absent), `weekdays`,
`weekend`, or a comma/range list of two-letter day tokens (Mo Tu We
Th Fr Sa Su). A range without one applies to every day — exactly the
previous behaviour: **an existing flat spec loads unchanged and solves
through the same code path as before**; the whole feature activates
only when a day selector is present.

The optimizer chooses the window set per step from that step's own
weekday, including across the midnight the horizon spans. The
config-flow field help documents the grammar in English and Swedish,
and the service path normalises weekly specs through their own round
trip (the flat formatter would silently drop the day selectors).

**Upgrading**: nothing changes until you add a day selector to your
hot-water windows. When you do, a day with no segment genuinely has
no hot-water requirement that day — that is the point, and it is
visible in the plan.

## v6.2.4

### The optimization score explains where the points went

A score of 5/100 was a number and nothing else: no hint that it is an
average of three independent grades — house, machine, driving — let
alone which of the three the 95 points went missing from. The
sub-scores were already riding the score sensor's attributes,
published and unused.

**Hover** now lists all three with their values and invites the
click. **Clicking** opens a breakdown panel under the stats row: one
row per sub-score with a bar, its value, and a line of what it
measures and what a low value points at — the house grade at
insulation and the learned loss, the machine grade at the COP health
watch, the driving grade at whether yesterday's energy was bought
below the day's flat average price. An unmeasured part says "No
evidence yet — not a zero" and gets no bar. Enter and Space work
too, and the whole panel is in Swedish on a Swedish install.

## v6.2.3

### A mode-paused channel explains itself, in its own words

"The heat pump's mode cannot do this" was true and useless: it named no
channel, said where the setting lives, or what to do about it. A user
reading it against hot water that never gets hot had no way to know
the fix is the mode selector on the physical unit — heat-only makes no
hot water, hot-water-only heats no rooms — and not anything in the
integration.

The tooltip now shows a channel-aware explanation: "No hot water: the
pump's operating mode — set on the unit — cannot heat water (heat-only
or cooling). Switch the unit to a mode that includes hot water", and
the heating mirror image. Those steps carry no power, so the hover is
the only place the explanation can live. Swedish carries the same.

## v6.2.2

### The fix program, complete on the record

`docs/plan-open-issues.md` marks the program complete: all sixteen
open issues (#86–#101) and all eleven code-scanning alerts closed,
across nineteen releases from v5.6.0 to v6.2.2. The delivery-status
section names the release that carried each item, including the two
closed by measurement rather than code. Documentation only; no
behaviour changes.

## v6.2.1

### The options dialog stays open after a save

Changing settings in two sections used to mean opening the dialog,
saving, watching it close, and opening it again (issue #100). Every
saving page now offers the after-save choice — return to the section
menu (the default) or close the dialog — and since a Home Assistant
form renders exactly one submit button, a schema field is the only
mechanism that can express two outcomes from one submit.

The write goes through immediately via `async_update_entry` — the same
write a save-and-close always triggered — and never a deferral keyed on
flow liveness: HA's `_progress` dict has no TTL and no sweep, a leaked
flow id would suppress reloads permanently, and that is the
silent-save failure class this project has already been bitten by.

Details the issue demanded: the choice never persists (stripped before
the merge); the read-only overview offers no choice — it saves nothing
and the button would lie; advanced pages return to the *advanced* menu;
and the config-flow golden's 12 moved leaves are exactly the new field
on each saving page, claimed and justified.

**Upgrading**: after updating, opening any options page shows the new
"After saving" selector at the bottom. Existing entries load unchanged;
nothing about what gets saved changes.

## v6.2.0

### The solver's gradient arrives as one batched evaluation

Measured on issue #97: 9,998 simulate_trajectory calls per two-zone
solve, the finite-difference gradient and its line searches effectively
the whole cost — and scipy re-estimates the gradient at every trial
point, so 96 of every 97 evaluations reconstruct derivatives the physics
already implies.

Two pieces landed:

**`simulate_trajectory_batch`** — B schedules simulated as one
vectorized pass, the twin of the scalar step written under a
bitwise-parity contract: every row equals the scalar path to the last
bit, because anything coarser moves plans. Branches become `np.where`
selections of already-computed values, `min`/`max` become
`np.minimum`/`np.maximum`, and every expression keeps the scalar code's
exact operation order. `wood_share`'s three regions got an element-wise
twin. The parity is test-asserted across single-zone, two-zone, valve,
true two-tank and stability-substep configurations — and the harness
earned its keep three times on the way up (a 0/0 NaN from `np.where`'s
both-arms division, a Carnot COP boost applied below the reference flow
temperature, an array fed to a scalar branch).

**`jac=`** — the exact 2-point estimate scipy would compute itself
(same `eps`, same zero-step fallback, same one-sided bounds rule),
evaluated as one batched call instead of 97 sequential simulations.
Two guardrails keep it honest: solves whose bounds are anything but
uniform (capped, pinned, tariff-windowed — the CI drift gate caught the
capped-tariff scenarios moving on Linux, exactly what it exists for)
keep the historical path; and `tests/optimality.py` races the batched
jac against a control solve with it stripped, requiring bit-identical
schedules.

**Measured: two-zone solve CPU 11.5 s → 1.0 s, single-zone
0.8 s → 0.1 s, plans byte-identical across every suite.** On the
Pi-class host, the coldest solve's GIL hold drops from eleven seconds
to one — and with it the event-loop exposure the v5.1.1 freeze class
was made of.

## v6.1.2

### The visual-QA renderer runs in every gate, on one shared DOM stub

The renderer was referenced three times and every reference was an
exclusion — never ran, never could — while carrying a verbatim copy of
an *earlier* revision of the card test's DOM stub, already drifted
(issue #101): no `blur()`, terse `textContent`, none of the focus
semantics. A dormant file whose whole value is being right when
someone reaches for it.

`tests/dom_stub.mjs` now owns the stub; both harnesses build it
against their own document. The renderer runs in the card lane of
every gate, right after the card test, reading the payload
`plan_view.py` just wrote: three setup SVGs per run, failing if any
topology's svg comes out empty. It stays unselectable in the closures
roster (the rolling.py pattern) — its dependencies are the card source
and the payload, both already covered.

## v6.1.1

### The card's two clean seams leave the god class

The card file was a 7,900-line god class with 182 methods at the last
audit, growing ~50 % since the second audit flagged it (issue #95).
The two seams that audit identified — the stylesheet and the setup
diagram — are now top-level functions instead of members:

- `cardStyleBlock()`: the whole CSS as one pure string — 607 lines,
  zero instance state.
- `setupSvgHtml(topo, ctx)`: the setup diagram's own rendering path —
  515 lines — taking the layout-editing state explicitly and returning
  the laid-out boxes so the thin method keeps the one side effect the
  class owns.

The class proper shrank from ~7,600 to 4,895 lines. No behaviour
change: every literal-tested contract is unmoved, and the card test
suite plus the QA renderer's three SVGs pass unchanged. The browser
lane from v6.1.0 is the geometry net that makes a refactor of this
size safe, which is why this was queued behind it.

A 4,895-line class is still a god class; this takes the two seams that
extract cleanly, as the issue scoped, and leaves the rest for whoever
finds the third.

## v6.1.0

### The real-browser layout lane: geometry the DOM stub cannot see

Every layout defect this project has shipped was invisible to the
suite, because the card tests run against a DOM stub whose
`getBoundingClientRect` returns a constant 900×400. Three reached a
user: the zoom-limited editing trap (v4.0.5 hotfix), tooltip text
overflowing its box (inherited `white-space: nowrap` plus a clamp on
the left edge only), and three legend chips 0.33 px apart that read as
one chip hiding three traces (issue #96).

`tests/card_browser.mjs` runs the real card in real Chromium and
asserts geometry: the chart svg at real size on a dashboard tile,
legend chips pairwise separated with labels that fit, tooltips
contained on **both** edges with text inside the box
(`scrollWidth` vs `clientWidth` — the nowrap defect's exact
signature), and every setup-editor hit target at least 8×8 px and
inside its svg. A vacuous-pass guard refuses to report "tooltips stay
inside" from a run where no tooltip ever appeared.

Its own job in the workflow (Playwright, Chromium cached), excluded
from the run.sh lanes and the closures roster because nothing else
installs a browser. This lane is what makes the card refactor (#95)
safe, which is why it went first.

## v6.0.9

### The drift baseline cache warms on main, once per merge

A merge to main moved every open PR's merge-base at once, so they all
missed the drift cache simultaneously and each paid a full ~25-minute
cold capture — with several PRs open, the dominant CI cost (issue #94;
four merges in a day meant most of the day's minutes went on
re-capturing the same baselines).

The push-to-main run already captures the new main tree for its own
comparison; it now stores that capture under the key the following PRs
will compute — one capture that was happening anyway, saved once, hit
by every PR that forks from the merge commit. The nightly keeps the
entry fresh on quiet days. The entry keeps its built-in key re-check,
so a wrong restore is a miss, never a stale baseline.

No integration behaviour changes.

## v6.0.8

### Retention is measured, and the recorder stops writing what nothing
reads back

Nothing measured what the learners retained (issue #99): several
collections looked unbounded by construction, and the only detector was
a user's Home Assistant running out of memory.

The rolling suite — which drives the real coordinator round a multi-day
closed loop — now measures, after the run, every collection the audit
flagged: the lead-error maps, the pending-promise list, the accuracy
sample ring, the COP baseline and capacity-envelope buckets, the
step-response samples, and the retained buffer trajectory, each with an
asserted ceiling. First measurement: everything is bounded. The
lead-error maps sit at their bucket count (the float-keyed drift the
audit feared is not happening), the promise list is under its 512 cap,
the ring at its 672 maxlen, and the buffer trajectory is one horizon.

The recorder half: `manual_override` (a whole manual-plan dict) and
`dhw_windows` were written to the recorder database on every state
write. Both are card-facing and read live from the coordinator; they
join `forecast`, `slots` and `setup_topology` in the unrecorded set —
on Pi-class hardware with an SD card, recorder volume is a real cost.

## v6.0.7

### The plan file records what has been delivered

`docs/plan-open-issues.md` gains a delivery-status section: the eleven
items delivered across v5.6.0–v6.0.6, #98 closed by measurement, #99
and #97's `maxfun` cap in review, and the five still to build — plus
the two unplanned items that joined the program on the way (the v5.6.0
harness confinement and the `frontend.py` closure fix). Where the
status section and a wave body disagree, the status section is the
truth. Documentation only; no behaviour changes.

## v6.0.6

### BLAS threads are pinned to one for the duration of each solve

The solver's L-BFGS calls landed in numpy/scipy whose BLAS backend
spawned a pool sized to the machine's core count, and the arrays (96
steps) are far below any size where BLAS parallelism repays its
synchronisation — so roughly 21 % of solve CPU was spent spinning
(thread factor 1.26–1.27, measured on the real solve path), on the
Raspberry-Pi-class hardware where it matters most (issue #88).

`threadpoolctl` — now a manifest requirement, so Home Assistant
installs it with the integration — pins the pool to one thread around
each minimize call. Scoped to the call, never process-wide (other
components share this interpreter). Plan fingerprints are
byte-identical scoped and unscoped: no operation at these sizes is
threaded, which is precisely why the threads were pure overhead.

**Upgrading.** Home Assistant installs the new requirement on restart
or when the integration reloads. If it cannot (an unusually locked-down
install), the solve runs unscoped exactly as before — the pin is an
optimization, not a dependency.

## v6.0.5

### A test may no longer define a production symbol

The rule tests/README.md states — import the real thing, never
re-implement it — is now enforced (issue #91). `tests/closure.py
no-copies` fails when a test file defines a top-level symbol production
also defines, whatever the body looks like: the name is the copy claim.

The failure mode this guards against is subtle enough to have shipped
twice in one session: a test re-implements a production formula and
asserts against its own copy, so its assertion *can* fail — surviving
the review that catches tests that cannot — but it fails when the test
file's arithmetic changes rather than when production's does, and its
mutation proofs prove the copy. On the re-anchor branch that meant
deleting the real constant from the coordinator left the entire suite
green.

Mutation-proven by defining a local `house_loss_confidence` in
features.py — the exact shape that invalidated those proofs — which the
check flags on sight. It found two live collisions on landing, both
benign name accidents (local fixture builders called `build`, sharing a
name with `narrative.build`); renamed to `build_case`, with no
whitelist, so the next collision costs a rename rather than a judgement
call. Runs in the closures job on main. Test-only; no behaviour
changes.

## v6.0.4

### The options-flow tests can no longer pass by asserting nothing

The options pages are about to learn to return to the section menu
after a save (#100), and the test loops were not ready for it: the
untouched-save sweep silently skipped any page that did not return
`create_entry`, so flipping all pages to menu-return would have left
it reporting green while asserting nothing. That is exactly how the
feature would have shipped untested by construction — the failure mode
#100 itself records as its first prerequisite.

The sweep now classifies every page's outcome — save, menu (verified
to carry `menu_options`), or rejected — and accounts for all of them.
The accepts-displayed-values loop verifies a menu hand-back is a real
menu and a save carries data. And the sites that indexed
`["data"]` unguarded now fail the check instead of KeyError-ing the
suite when a page's shape changes. Test-only; no behaviour changes.

## v6.0.3

### An unrecorded test script fails loudly on main

Adding a test script used to leave the scoped gate silently running
FULL on every PR — the saving gone, the only symptom a reason string
in the run log (issue #90). The `closures` job on main now fails when
a selectable script has no recording at all: the omission costs one
red main run instead of weeks of quiet full gates.

Recording one script is now cheap. `./tests/derive_closures.sh --single
tests/<script>` records just it and overlays the result into
`tests/closures.json`, instead of a full re-derivation that runs the
whole suite — the ~25-minute friction that made people skip the step.
A partial overlay may only grow a closure, never shrink one.

The tool proves itself on landing: v5.6.0's submodule load made
`tests/frontend.py` genuinely read `const.py`, the committed closure
predated that, and main's closures job went red for exactly that
under-scoping — the gate working as designed. `--single` re-records
`frontend.py`; the overlay adds the one file.

## v6.0.2

### Day and night comfort temperatures are validated against the band

`comfort_temp_day` and `comfort_temp_night` were never checked against
`[min_temperature, max_temperature]`, so an out-of-band day or night
temperature saved fine. The plan itself was essentially unchanged —
but the reported savings were computed against a comfort reference the
user cannot actually experience (issue #92).

The rule lives in `comfort_band` with its fellow cross-field checks, so
all three write paths get it at once: the config flow, the
`apply_schedule` service, and the climate entity's slider.

Two traps from the issue are load-bearing in the implementation:

- **The night lower edge is demanded only while the night selector can
  express it.** The floor selector reaches 25 °C while the night slider
  stops at 24, and demanding the impossible dead-ends every form that
  pair reaches — exactly how a first attempt at this rule broke initial
  setup. A standing satisfiability sweep now walks every
  floor/ceiling pair the sliders can produce (0.5 °C steps, jointly
  rather than per-rule) and requires a submittable form for each.
- **An existing entry can already be in the forbidden state**, from a
  pre-v5.4 service write. The rule judges the pair a save would leave
  in force, so `apply_schedule` can no longer push a day temperature to
  30 °C on a 20–23 band — the regression the issue's second attempt
  introduced.

The selectors' own bounds moved to `const.py`, shared by the schema and
the rule, so the validation cannot drift from what the form offers.

## v6.0.1

### The crawl-space floor stops counting twice

A slab-bearing structure paired with a crawl-space foundation counted
the floor twice in the building questionnaire's derived physics: once
as the structure table's heavy slow store and once as the foundation's
loss path. The subtraction now removes the slab exactly once, derived
from the timber table's own slab-on-grade vs crawl-space rows so it
moves with a future table edit, floored at the crawl-space row
(issue #93).

Scoped to slab-bearing structures: "stone or masonry" makes no claim
about what is under the floor, so a stone house on a `torpargrund` is
two honest answers with nothing to remove — the shape the rejected
`min(slow, 0.010)` cap got wrong, which would have collapsed masonry
over crawl space to the same mass as bare timber.

Timber-on-slab over a crawl space now derives identically to the
crawl-space structure — which is also the test's mutation anchor. And
with the re-anchor from v6.0.0 in place, re-answering the questionnaire
now actually reaches an install that has already learned something:
the uplift survives the reload instead of being absorbed by the old
scale.

## v6.0.0

### The learned heat-loss scale survives an options edit

The coordinator learns a dimensionless `house_heat_loss_scale` fitted
against the *configured* heat-loss coefficient, and the store recorded
the scale but not the coefficient it was fitted against. An options
edit — above all a building-questionnaire re-answer, which rewrites
the coefficient without the user typing a number — reloaded the entry
and restored the old scale verbatim against the new nameplate,
leaving the model up to 1.94× wrong: measured as +87.8 kWh/day of heat
the plan buys at −5 °C, and a 12-hour coast predicted 2.72 K colder
than the house actually gets, so the optimizer refused coasts it could
safely have taken. The reverse edit coasts the house through its
comfort floor (issue #86).

The store now records the anchor, and the loader re-expresses the
scale with `U_eff' = (1 − φ)·nameplate_new + φ·measured_UA` — absolute
UA, on the zone-total basis, with φ the learner's own
`house_loss_confidence(samples)`. Two guards from the recorded
decisions:

- **Sub-threshold edits keep today's behaviour.** The re-anchor applies
  only when the coefficient change exceeds the learner's own step
  limit (`HOUSE_LOSS_MAX_STEP`); below convergence the ungated law was
  a measured regression on exactly that path, and the learner absorbs
  a small edit in one step anyway.
- **An inexpressible measurement resets, never clips.** If the
  re-anchored scale falls outside `[0.3, 3.0]`, the learner resets
  explicitly with a warning, so the next edit cannot read a clip bound
  as the learner's own signal.

Both collateral defects go with it: a drift rollback can no longer
re-install a pre-edit scale from a weekly snapshot (the restore runs
the same law), and the `set_thermal_parameters` reset records its
anchor so the restart self-heals instead of pairing a reset scale with
an unchanged option.

**Upgrading.** The first start after this release adopts an anchor for
any pre-existing learning store (one extra write) and re-anchors
immediately if the configured coefficient has changed since the
learning was last saved — the visible symptom is one
`Re-anchored learned house heat loss scale ...` log line, and
`house_heat_loss_learned` in the learning view finally meaning what it
says.

## v5.7.1

### The optimality gate can see the solver's iteration budget

Cutting the solver's budget from 300 to 3 iterations left
`tests/optimality.py` green (issue #89). Measured first: the cut costs
0.3 % on the single-zone scenario — genuinely almost as good — but
16.2 % on two-zone, a real regression the gate could not see.

The gate now races the production-budget solve against a second solve
with `maxiter` slashed to 3 (the exact cut from the issue) and requires
the production solve to be materially cheaper on two-zone. It pins a
property, not a number: if production's budget is ever cut, the two
solves coincide and the check fails by construction. Mutation-proven
against the exact cut in `optimizer.py` — the gap collapses to 0.0 %
and the check fails.

## v5.7.0

### The slab settlement cap is bounded by the plant's own ceiling

`slab_settlement_cap` ended in `target + q_demand /
max(slab_heat_transfer, 1e-6)` with no upper bound, which reaches
roughly 195 °C where `slab_heat_transfer` lands low — valuing slab heat
no physical slab can hold. The cap is now `min`'d with
`buffer_max_temp`: the slab is fed by store water that ceiling caps, so
it cannot stand above it however weak the coupling. The bound rides
existing configuration rather than a magic constant, so a future
ceiling change moves it (issue #87).

At default settings the bound is inert — the reporting owner's cap
measured 21.17 °C, and the worst raw cap across every coefficient
`presets.derive` can emit is about 63 °C under the 70 °C default
ceiling — but a reachable low-temperature store (the selector runs
40–90 °C) now clamps the cap to a temperature that plant can actually
put under the house.

## v5.6.2

### The eleven code scanning alerts are cleared

All open CodeQL findings, no behaviour changes:

- The solar-fetch failure warning no longer logs the coordinates —
  four decimals of geolocation is identifying, and the diagnostics
  payload already publishes rounded ones where they are wanted.
- The two test-harness findings are cleared by construction: the QA
  renderer splices its style block with `indexOf` + slice instead of a
  non-global `replace(/>/, …)`, and the card test reads tooltip labels
  through the DOM stub's `textContent` instead of regex tag-stripping.
- `hassfest.yml`, `validate.yml` and `tests.yml` declare
  `permissions: contents: read` — the convention the release workflow
  already followed.
- The two third-party actions (`home-assistant/actions/hassfest`,
  `hacs/action`) are pinned by commit SHA, with the upstream branch
  recorded in a trailing comment.

The QA renderer also executed end-to-end for the first time while this
was verified — three self-contained setup SVGs, written correctly.

## v5.6.1

### The fix program for everything currently open

`docs/plan-open-issues.md` records the delivery plan for all sixteen
open issues and the eleven open CodeQL alerts: five waves, one PR and
one release per item, with the two live design forks settled in
writing (the threshold-gated re-anchor law for #86, and wiring up —
not deleting — the QA renderer for #101). No behaviour changes in this
release; the document is the contract the next releases execute.

## v5.6.0

### The test harness's file and network sinks are confined

Five findings from a pre-commit security scan of the test harness, all
in code that runs on developer machines and CI rather than in the
integration itself:

- `tests/env_drift.py`'s capture worker writes exactly one file, and its
  only caller passes a path inside a `tempfile.mkdtemp()` directory — it
  now refuses a `--capture` output path outside the system temp root.
- `tests/plan_view.py` writes the shared plan payload to
  `HPO_PLANDATA` or a per-checkout default; an override outside the temp
  area is now refused rather than written. The default's checkout
  discriminator moved from SHA-1 to SHA-256, and `tests/card.mjs` and
  `tests/setup_qa_render.mjs` derive their identical defaults with the
  same change, so writer and readers stay in lockstep. Old payloads
  under the SHA-1 names are simply orphaned scratch.
- `tests/frontend.py` loaded the production module by `exec` of a source
  string with the relative import patched out. It now loads
  `frontend.py` as a genuine submodule of a namespace-only parent
  package, so `from .const import DOMAIN` resolves against the real
  `const.py` — still without importing the package `__init__` and its
  solver dependencies, which is what the standalone load was for.
- `tests/open_meteo.py`'s live-API check (run only with `HEATPUMP_LIVE`
  set) spells each request with its production endpoint directly in the
  request expression, so the check cannot be pointed anywhere but the
  endpoints the module under test itself uses.

No production code changes; all four touched suites pass unchanged.

## v5.5.0

### Sensors say what they know, and say nothing when they do not

Five published temperatures were `ThermalState` constructor defaults wearing a
temperature device class. On an install with only an indoor and an outdoor
thermometer — measured on a real coordinator — the hot water sensor published
55.0 °C for the life of the install, the buffer published 40.0 °C, the slab
22.4 °C on a 21.4 °C room, and both floor sensors published the indoor
reading. All six reported `available = True`. With `state_class=measurement`
on top, each drew a flat line in long-term statistics that an owner cannot
tell apart from a real probe.

The coordinator now publishes one `reading_ok` map saying which of those
numbers came from an entity that actually read this cycle, and the entities
gate on it. The floor return joins them: it held its last good value forever,
so a thermometer that died in January read 48.2 °C all spring with nothing
marking it.

**Upgrading.** Sensors that were showing a plausible constant will now show
*unavailable* until the matching thermometer is configured. That is the
correction, not a regression — but a dashboard card or template that read one
of them will change what it shows, so it is worth a look after upgrading.
Nothing is renamed and no entity id changes.

### Upper Floor Temperature keeps its name, and admits its source

There is no upper-floor input anywhere in the package: the coordinator assigns
it `indoor.value` in the same branch that sets the room temperature, so it has
always been the Indoor Temperature sensor under a second name. It now says so
in a `source` attribute and follows the indoor reading's availability. It is
kept rather than removed, because removing it would orphan every dashboard,
automation and long-term statistic pointing at
`sensor.heat_pump_optimizer_upper_floor_temperature`, and giving it a distinct
source needs a configuration entity that does not exist.

### Hot water entities only exist on installs that heat water

Six of them were offered either way. Two are Energy dashboard sources, so
`hot_water_energy` and `hot_water_cost` recorded a flat 0.0 forever —
indistinguishable from a working meter on a pump that never heats water. One
shared `dhw_enabled` gate now covers all six.

### No infinities on the wire

`PeakTracker.threshold_kw` answers `+inf` when the month has no reference peak
yet — which is the 1st of every month, for every install with a capacity
tariff, because the tracker starts each month with an empty peak list. That
sentinel reached the Monthly Peak sensor's `free_headroom_threshold_kw`
attribute verbatim, and orjson (Home Assistant's websocket and recorder
serializer) writes it as `null`. The frontend and the database recorded
"unknown" while a Jinja template reading the same attribute in-process got
Python's `inf` and compared `> 100` as true: one number, two meanings,
depending on the reader. Non-finite floats now map to `None` at the
publication boundary — the base class wraps every subclass's `native_value`
and `extra_state_attributes`, so the next attribute that divides by a zero
sample count is covered without anyone remembering to ask.

The same infinity had a second consequence. `_power_headroom` filters
non-finite limits out of its `min()`, so a capacity-tariff install with no
`main_fuse_amperes` — the default, since the fuse defaults to 0 — had both
candidates dropped and the entity disappeared entirely for the first metering
window of every month, which is exactly the hour the month's peak is set. The
infinity means "do not let the peak term distort the plan"; it does not mean
the house may draw freely, and this sensor asks a different question. With no
peak recorded the bill is set from the first window, so no kW is free and the
honest answer is 0.0. `limit_source` now names which of the three cases
produced the number. Installs with a fuse have a finite limit and are
untouched.

### Availability that narrows the coordinator's answer instead of replacing it

All eleven `available` overrides ignored `super().available`. With a payload
satisfying every one of their own gates and `last_update_success` False,
eleven entities still claimed to be available. They now conjoin it.

Observed COP, the frequency advisor and the contract comparison went available
the moment their source existed and then published `None` until the first
sample — hours, or a billing month. Home Assistant renders that as *Unknown*,
which is what it renders for an integration that has thrown. They now wait,
and name what they are waiting for.

### Device classes

The DHW setpoint advisor is a temperature. Mixed hot water is
`VOLUME_STORAGE` — a quantity held, not delivered. Thermal battery energy is
`ENERGY_STORAGE`, which accepts `MEASUREMENT`, where plain `ENERGY` would
demand `TOTAL` and be rejected. ECL110 Displace and Prediction Accuracy stay
bare and are now pinned that way: both are deltas in °C, and a temperature
device class would have Home Assistant convert a difference as though it were
an absolute reading. Valve Target Recommendation's missing state class is not
a violation — verified against Home Assistant's own
`DEVICE_CLASS_STATE_CLASSES`, which lists allowed pairs and is consulted only
when a state class is set — and the test stub now mirrors that table, so no
sensor can pair a device class with a state class Home Assistant forbids.

Behind all of it, `tests/entities.py` sweeps every entity of every platform
across five coordinator payloads, including one carrying the `+inf`. The sweep
is two-sided: nulling everything, or marking everything unavailable, fails it
just as loudly as the original defect did.
## v5.4.1

### The Setup tab is reachable before the first solve

`sensor.py` publishes `setup_topology` with no plan for exactly this case, and
says so in as many words — but both the expand affordance and the dialog were
gated on plan data. The one page that can tell you *which* sensor is missing
was reachable only after a solve that the missing sensor was preventing.

The dialog now renders whenever the card believes it is expanded, opens on the
setup page when there is no plan, and its Plan tab explains the absence rather
than drawing an empty box. An install with nothing published at all still
offers no expansion: no plan and no topology is nothing to expand to.

### A hot-water schedule that runs to midnight can be priced again

`dhw_schedule.format_windows` renders a window ending at the end of the day as
`20:00-24:00` on purpose, and `parse_windows` reads `20:00-00:00` straight
back to the same window — the round trip is lossless. The card's `hourOf` has
no `24:00`, and should not: it also parses `<input type="time">` values, where
no such time exists.

The consequence was narrow and total. The SAVE path and the Apply button were
never affected, because both call `_onSlotEdit` first and re-read the rows out
of the DOM. The slider path does not touch the DOM at all, so what
`_runWhatIf` validated was the memoised draft seeded straight from the sensor:
a household whose hot water is guaranteed until midnight could not price a
single change, and every simulate was refused by the card, blaming the
schedule the integration had just published. Normalised once, in the draft
seed. The refusal also names the window it is refusing now, so a house with
four windows does not have to check all four by hand.

### The slot menu stops leaking an Escape handler

The menu parks its Escape handler on the document, because a mouse-opened menu
leaves focus on the chart and the menu element never sees the key. Two paths
dropped the menu without dropping the handler: `_render`, which replaces the
shadow root on every plan refresh, and `disconnectedCallback`, which never
closed the menu at all. One leaked listener per card visit, for the lifetime
of the page. One `_teardown()`, called from both.

### The setup picker's safeguards are now actually tested

The picker already prepends a missing assigned entity as the selected option
labelled with its raw id, already applies the 200-option cap after the text
filter, and already confirms an Assign that would clear a configured slot —
all of it landed in v5.1.4. The scenario claiming to cover the prepend did
not. It assigns `sensor.vedpanna_temperatur_temperature_2`, which sorts
*before* the 400 `sensor.zz_probe_*` it was supposed to be buried under, so it
landed inside the cap on its own merits: replacing the entire prepend with
`if (false)` left the whole suite green — a production line with no assertion
behind it, in the one place where its absence rewrites the user's
configuration.

Three cases reach it now: an assignment last of 400 alphabetically, one
excluded by the filter the user is typing, and one that is not a candidate at
all because the entity has been renamed away. Each dies under that mutation.

### The expected device class moves to where the slot is defined

It lived in a second table inside the card, keyed by slot id, that no test
reached. It now sits in `topology._SLOTS`, in the same row as the domains it
belongs beside, and is published on every slot. It stays a *ranking*, not a
filter: a house full of sensors carrying no device class is normal, and a
picker that hid those would hide the very probe the user came to assign.

Every assertion added across these four surfaces was killed by a named
single-line production mutation before being kept.

## v5.4.0

### Stored heat is credited at what the next window can actually spend

The optimizer values heat still in the buffer tank at the end of its 24-hour
horizon as heat the next window does not have to buy. That credit was
undiscounted, and in warm weather it was the only term in the objective with
any gradient at all — so the plan bought space heat to collect it.

Reported by an owner running two zones, a mixing valve and a 750 L tank, with
comfort 17–23 °C and a target of 21 °C: at 25 °C outside by day and 11 °C at
night, the house coasts from 27 °C down to about 21 °C over a full day with no
heating whatsoever — six degrees clear of the comfort floor — and the plan
still scheduled space heating. Comfort weight could not restrain it, because
the bought heat never reached the rooms: the room trajectory was identical to
six decimal places with and without those slots, so the comfort term had a
gradient of exactly zero and the comfort weight was multiplying a constant.

Two independent signs it was not economics. Buying *rose* as the weather got
warmer — a 13 °C day planned 0.000 kWh while an 18 °C day planned 5.512 kWh —
and a flat-price null control, where no arbitrage is available at all, still
planned 5.035 kWh, spread over more steps rather than fewer. After the fix
both the varying-price and the flat-price case plan 0.000 kWh.

A tank loses heat to its surroundings whether or not anyone draws on it. Heat
stored against a demand that will not arrive for days is largely gone before
it is wanted, so crediting it at face value is wrong. The terminal credit is
now discounted by the fraction that survives until the heat is actually spent:

    survival = exp(-UA (cap - ambient) / (2 x hold demand))

which is the tank's half-drain time measured in its own time constants. The
`UA` is the tank's **learned** standby loss — the `buffer_cooling_rate` the
coordinator already fits from observed cooling and clamps to this tank's
insulation bounds — so a well-insulated accumulator is discounted far less
than a bare cylinder. The discount is this tank's own physics, not a tuning
constant, and there is no new setting to configure.

The hold demand is what the house needs to hold target at the horizon's mean
weather, net of internal and solar gains. When gains cover the whole loss it
is zero, the hold time is unbounded, and the credit goes to zero with it —
which is exactly the owner's case, and the behaviour asked for: heat is not
bought when coasting unheated does not bring the house anywhere near its
comfort floor.

Winter is preserved by construction, because the discount divides by the
demand it is waiting on. Across a seasonal sweep of the same house:

| Outdoor | Discount | Space heat before | after |
|---|---|---|---|
| −8 °C | 3.0% | 28.750 kWh | 27.500 kWh |
| −2 °C | 4.0% | 28.423 kWh | 27.500 kWh |
| +7 °C | 8.4% | 16.549 kWh | 9.493 kWh |
| +13 °C | 31.5% | 0.000 kWh | 0.000 kWh |
| +18 °C | 100% | 5.512 kWh | 0.000 kWh |

The suite now carries the case. `tests/validate.py` gains four valve +
storage scenarios — every scenario before this release left the mixing valve
unset, so the buffer was never a planning store in any of them — and a
standing check that fails any plan buying space heat while the house, left
entirely unheated, would never drop below its comfort target. On v5.1.9 the
flat-price control bought **8.73 kWh** with no price spread to exploit, while
coasting to exactly 21.0 °C against a 21.0 °C target, and reported **100 %
savings** for it. It now buys 0.00 kWh and reports 7 %. The room peak is
27.3 °C either way: those 8.73 kWh did not raise the house by a tenth of a
degree.

The check is deliberately written against the symptom rather than this
mechanism, so a future term that pays the objective to run the pump while the
house is already comfortable cannot ship green. It is measured against the
comfort *target*, not the floor: a floor-relative test also flags plans that
coast to 19.9 °C or 20.5 °C, and those are legitimate — the optimizer pulls
toward target, so heat bought there buys real comfort.

Installations without a mixing valve, and tanks below the store threshold,
are unaffected: the discount is exactly 1.0 there and those paths stay
byte-for-byte identical. The golden fixtures agree — exactly three move, all
of them valve + storage, and `valve_storage_small_tank` (below the store
threshold) is byte-identical.

## v5.3.0

### The heat pump can now tell the optimizer what it is doing

Four new optional entity slots on the setup page, all read-only — the
integration never writes any of them:

**Operating mode.** Many units cannot heat the house and make hot water at
the same time, and some cannot do both at all in the mode they are currently
in. If you point this slot at the pump's mode entity, the plan stops
promising heat the pump cannot deliver: a cooling or hot-water-only mode
suppresses space heating, a heating-only mode suppresses hot water, and the
affected hours are labelled *"The heat pump's mode cannot do this"* in the
plan rather than reading as an ordinary idle hour. The comfort floor is left
visibly unmet rather than quietly relaxed, because the fact worth showing you
is that the mode selection is costing you comfort.

**Defrosting.** Between roughly 0 and +5 °C in damp air, an air-to-water unit
periodically reverses to clear frost off the evaporator, and both capacity and
efficiency fall while it does. Until now that loss could only be inferred from
a power ratio that cannot actually see a defrost. With a real defrost flag it
is measured: how much of each interval the unit spent defrosting, per
temperature and humidity band. Two honest caveats — a cloud connection that
polls every few minutes will miss short defrosts, so the measured figure is
biased low; and the number of defrosts actually witnessed is reported next to
the duty, so a coarse estimate can be recognised as one.

The same flag also unblocks the efficiency learner. It used to sit out the
entire 0–5 °C band to avoid double-counting the defrost loss, which in a
Swedish shoulder season is a large share of all heating hours. With a flag it
sits out only the intervals that actually contained a defrost.

**Online status** and **Fault alarm.** Both pause the learners rather than
change the plan. The online signal closes a specific gap: some cloud
integrations, when the vendor's API answers successfully but the device's data
is stale, mark the device offline and hand back the stale data anyway. Every
entity stays available and keeps looking freshly reported, so nothing about
freshness can see it — only the signal's own value can.

**None of this is required, and nothing changes if you configure none of it.**
An empty slot, an unavailable entity, a word the mode table does not recognise
and a reading past its age limit all mean *no evidence*, and no evidence is
exactly the previous behaviour. The reverse is never true: silence is never
read as bad news, because a pump that pushes updates only when something
changes can leave all four entities untouched for hours while running
perfectly.

### What the mode entity will and will not do

Three limits worth knowing before you configure it, because each one is a
deliberate refusal rather than an oversight:

**It never switches your heat pump off.** A mode that blocks both channels —
cooling, most obviously — leaves the plan with nothing to run, and it would be
easy for the integration to read that as "turn the pump off". It does not: it
stops *planning*, and leaves the supply switch exactly where your mode
selection left it. Turning the pump off because you set it to cool would
defeat the cooling you asked for.

**It only trusts a mode entity that names its own choices.** A `select`, or an
`input_select` you built listing your pump's modes, states which options exist,
so "Heating" from one of those is the mode. A general-purpose *status* sensor
cycling heating / cooling / defrosting / idle does not, and there "heating"
means the compressor is running this minute, not that the unit cannot make hot
water. Words like that from a sensor are ignored rather than guessed at, and
the diagnostics show the word that was not understood. The same applies to the
defrosting, online and fault slots: from a plain sensor, activity words like
"idle" or "running" are not read as flags.

**It stops believing a mode entity that has gone quiet.** If the entity
becomes unreadable, the last mode it reported keeps acting for up to three
hours — long enough to ride out a restart or a slow reporting cycle. After
that the plan goes back to assuming your pump can do everything, and a repair
notice tells you the entity has stopped reporting. Suppressing your heating
indefinitely on the last word of a sensor that has since died is the one
outcome this feature must never produce.

### Notes on the above, and one deliberate change

**The frost-band derate is now bounded at 1.0, not 1.05.** This module models
a *loss*: it exists to stop the plan over-promising between 0 and +5 °C. The
old bound let it learn "5 % better than the model", which is not a thing frost
does to a heat pump. If your system had learned a value above 1.0 there, it is
brought back to 1.0 when the store loads — the rest of what it learned is kept
— so plans in that band become slightly more careful and never less. Nothing
else about an existing derate is discarded.

**The stove or flue override reads its two kinds of entity differently.** If
you point it at a switch or a helper toggle, that setting stands until you
change it. If you point it at a *flue temperature probe*, it is trusted for an
hour after its last report, and the log now says when it stops being trusted —
a probe stuck reading hot on a flat battery would otherwise hold your heating
back indefinitely. (This distinction was introduced and corrected during this
release's development; no released version behaved otherwise.)
## v5.2.0

### The hot water line now shows how sure it is

The plan chart draws a dashed pair either side of the **hot water tank
temperature**. That pair is the *expected error* of the prediction: how far
the tank curve has actually been out, in the past, at that distance ahead.
Read it as "the tank is probably in here somewhere", not as a plan.

It widens the further right you look, and it should — a promise about two
hours from now is a much safer promise than one about tomorrow evening, and
the band says so instead of pretending otherwise. The tooltip names it in
words: *Hot water, expected error ±1.2 °C*.

**It only appears once there is something to base it on.** A brand new
install has never had a prediction come true or fail, so there is no error
to report and no band is drawn at all — you just get the solid line, as
before. It fills in over the following days. A house with no hot water tank
sensor configured never gets one, because there is nothing to check the
prediction against; the same goes for stretches where the sensor is
unavailable or stuck, which are not measurements and are not counted.

### It shares the room's dashed-line vocabulary rather than inventing one

v5.1.7 gave every trace on the house-temperature series its own name, its own
tooltip row and its own legend chip. The hot water band rides exactly that
machinery — same dashed stroke, same colour, same single chip that toggles the
whole series — so the chart has one visual language for "this line is a
companion, not a plan", and the two dashed pairs cannot be confused for being
the same *kind* of thing.

One deliberate difference. The room's two dashed lines are two real predicted
temperatures, one per floor, and are named and reported separately. The hot
water pair is a single symmetric envelope, so it gets **one** legend chip and
**one** tooltip row stating one ± figure, rather than two absolute temperatures
nobody asked for.

Two things follow for free. Where the band has no value the dashed lines stop
rather than bridging the gap. And a band with no width at all — a record that
has scored predictions but never been wrong — is not drawn, caught by the same
rule that already stopped a single-zone house drawing two dashed copies of its
own room line.

### Under the hood

The hot-water plan sensor's forecast gains two additive keys,
`dhw_temp_lo` and `dhw_temp_hi`, alongside the existing `dhw_temp`. They are
`null` whenever there is no band to draw. Nothing that was already published
changed shape or value. The tank's accuracy record is stored alongside the
existing one; upgrading and downgrading both read the store without
complaint.
## v5.1.10

### Your hot water charge limit is now actually a limit

"Highest tank temperature to charge to" says, in its own help text, that it
is *an upper limit on charging, not a target* — and that the tank "is never
heated to this just for the sake of it". It was not behaving that way. The
anti-legionella temperature — 60 °C by default, and switched on by default —
was quietly being used as the planning ceiling every day of the week, not
just on the day a disinfection cycle was due. So if you had set your charge
limit to 52 °C, the plan still ran your tank up towards 60 °C most nights,
because buying hot water at the cheap night hours pays off and the ceiling
was the only thing telling it where to stop.

On the stock settings — a 55 °C charge limit and a 60 °C disinfection
temperature — this affected every installation, not just the ones that had
lowered the limit.

From this release the two numbers do what they say:

- **The charge limit is the highest temperature the plan charges to**, on
  every ordinary day.
- **The disinfection temperature applies during disinfection**, and only
  then. When a cycle is due, the tank is taken up to it for that cycle — and
  it is allowed to reach it, including the run-up needed to get there — then
  left to cool back under your limit.

You do not need to change any settings. If you have *set* a disinfection
temperature above your charge limit yourself, you will see a note in Home
Assistant's **Repairs** explaining that the tank goes above the limit for the
cycle and how often that happens. It is a note, not a problem, and you can
change the pair either way if you would rather it did not. The stock pairing
— a 55 °C limit and a 60 °C cycle — says nothing there: nothing about the
settings you were shipped with is a surprise worth a card in Repairs. It is
still written to the log when you save the setup pages.

**Your hot water plans will change.** The tank is charged less high, so less
heat leaks out of it overnight. It also means the plan has less room to store
cheap night electricity for the evening, and that side is worth being straight
about: on a winter day with a big day/night price spread, hot water can end up
costing a little more than it did — across our test scenarios the hot-water
part of the bill moved by roughly plus or minus a tenth, and the whole day's
plan by a few percent. The extra was never free: it was bought by heating your
tank to a temperature you had asked it not to.

If you would rather have the saving than the lower tank temperature, raise
**Highest tank temperature to charge to**. That is now exactly the dial that
controls it — which is the part that was broken.

If you had switched the disinfection cycle **off**, the published hot-water
schedule gets markedly smaller: with the cycle off the tank's limit was also
the temperature the plan's own tank model refused heat at, so the plan kept
asking for heat the tank had no room for. On our reference day the schedule
falls from 13.34 kWh to 6.53 kWh — and the tank ends at exactly the same
temperature, because the difference was never heat that went in. What changes
is that the plan, the cost estimate and the graph now show what the tank
actually takes.

Comfort is unchanged either way: the temperature you need, when you need it, is
the same setting it always was, and the plan still guarantees it.

### The disinfection cycle could get stuck, and never disinfect

The anti-legionella timer only ever reset by *seeing* the tank at the
disinfection temperature. If your heat pump could not get the tank that hot
on its own — many cannot, without an immersion heater — or if you have no
tank temperature sensor configured, the timer could never be reset. Once it
went past its interval, the plan pinned a 60 °C requirement to the very first
step of every plan it made, for ever: a cycle demanded every fifteen minutes,
never completed, and the water never disinfected. Nothing said so.

The fixes:

- An overdue cycle is now scheduled at the first moment the tank can
  physically be at temperature, at the cheapest hour from there — not on the
  first step of the plan, which is the one step it provably cannot reach.
  Whether the tank can get there is worked out by running the plan's own tank
  model forward at full power, so the hot water drawn and the heat lost on the
  way are both counted — which matters most on a large tank with a small pump,
  where the difference between an estimate and the real thing is hours.
- If the tank cannot reach the temperature *anywhere* in the plan's horizon,
  the cycle is scheduled to start **now** rather than at the far end of the
  plan. Parked at the end it was never the step being acted on, so nothing
  ever ran, nothing was ever observed, and you were never told.
- A cycle the plan actually commanded now completes: it is followed to its
  end whether or not the tank ever reaches temperature, so the countdown can
  never latch. A boost that is still being commanded twelve hours later is
  closed out and judged on what it managed, so a tank that cannot finish
  reports the problem instead of heating indefinitely.
- **If the pump cannot reach the disinfection temperature, you are told.**
  A note appears in **Repairs** saying how far the tank actually got, so a
  cycle that is quietly failing stops being invisible. It clears itself as
  soon as a cycle reaches temperature.

If you have **no tank temperature sensor**, the countdown still resets so your
plans are not wedged — but it is recorded as an *attempt*, not as a cycle that
worked, and a note in **Repairs** says so. Nothing watched the tank, and this
integration publishes a plan: whether your pump acted on it is something only
a temperature can answer. Point the "Hot water tank temperature" setting at a
real sensor and the cycle is verified from then on, and the note goes away.

### The cycle still reaches temperature, from a much cooler tank

Because the tank is no longer held near 60 °C all week, a disinfection cycle
now has further to climb: on a summer day the tank may quite correctly be
sitting at 37 °C when the weekly cycle comes due. The plan charges that run-up
deliberately in the hours before the cycle, so the tank *arrives* at the
disinfection temperature rather than a degree or two short — which would be no
disinfection at all, and would have your pump reported as unable to reach a
temperature it can reach perfectly well.

This is pinned by tests across every charge limit from 41 °C to 49 °C on four
tank-and-pump combinations, and on twelve tank, pump and season combinations
besides: the cycle lands on 60.00 °C every time.

Hot water availability is unchanged by any of this. Across a sixteen-plan
matrix the worst shortfall against the minimum temperature you set is 0.04 °C
— the same as before the charge limit started being honoured.

## v5.1.9

### One legend entry for the house temperature line

The house-temperature series draws up to three traces in one colour: the room
average solid, the upper and lower zones dashed. v5.1.7 gave each of them its
own name so that hovering a zone line stopped reporting the room's value — a
real fix, and it stays. It also gave each of them its own legend chip, and
that part was wrong.

Every chip carries the series it belongs to, because visibility is per series:
there is no way to hide one line of a series and keep the others. So the card
showed three chips in the same colour, all of them saying "house temperature"
in one form or another, and clicking any one of them hid all three lines
together. Three controls doing one job read as a bug, and it was reported as
one.

The legend is back to one entry per series. Naming individual traces moved
entirely to the tooltip, which is where it works: hovering the chart still
gives a row per line — "House temperature", "Upper floor" and "Lower floor",
or "Lower floor (modelled)" where no lower-floor thermometer is assigned —
each with its own value and a dashed swatch for the dashed lines. The legend
chip's hover text lists the extra traces that ride on the line it toggles, so
the legend still describes what is drawn without adding a second control for
it.

A single-zone house is unchanged: it publishes the zone traces as exact copies
of the room average, those duplicates are dropped rather than drawn, and its
chip claims no extra traces.

*Card-only.* No planning behaviour changes and no fixture moves.

## v5.1.7

### The house was never planned to 28 °C. The chart was drawing water.

An owner reported that heating slots were being planned that would take the
house to 28 °C, with a comfort maximum of 23. Reproducing it showed something
different, and worth saying plainly: **the plan was correct all along.** Across
the whole characterization matrix the planned room temperature peaks between
21.0 and 21.9 °C, and a fixture built specifically to test this — the comfort
ceiling raised from 23 to 28, everything else identical — plans the room to
exactly the same peak. The ceiling is a limit the plan stays under, never a
target it aims for.

What was wrong was what the chart drew, what a slot called itself, and what
the setup page promised.

**The "house temperature" line was, downstairs, a water temperature.** In a
two-zone house with a floor-return sensor but no lower-floor thermometer, the
lower zone's *air* temperature was taken from the floor-return *water*, plus
half a degree. In an underfloor-heated house in a cold snap that return sits
at 26-30 °C, so the lower zone was published — and plotted, in the same colour
and under the same label as the room — at 28.0 °C while the upstairs zone sat
at 22.1. That number then went to the model and was judged against the same
comfort band as the measured zone.

The floor return keeps the job it is genuinely a proxy for: estimating the
slab. The lower zone now starts from the room sensor and is carried forward by
the thermal model, which is what "the modelled indoor temperature" means. A
repair notice says so, so a modelled zone is never mistaken for a measured
one, and it explains what a lower-floor thermometer would add: the model
running open-loop cannot correct itself, so over a long cold spell it can
drift from the real downstairs.

**The chart now names every line it draws.** The house-temperature series
draws up to three traces — the room solid, the two zones dashed — and all
three shared one label, one legend chip and one tooltip row. Hovering the
28 °C line reported the room's 21 °C, which is precisely how a display defect
reads as a planning defect. Each trace now has its own legend chip and its own
tooltip row with its own value, named "Upper floor" and "Lower floor" (or
"Lower floor (modelled)" where no thermometer is assigned), in English and
Swedish. A single-zone house publishes the two zone traces as exact copies of
the room; those duplicates are now dropped rather than drawn and labelled
three times.

**An ordinary slot stopped calling itself weather pre-heating.** "Pre-heating
before colder weather" was not only the reason for a step that anticipates a
cold spell — it was also the *default* for any heating step that was none of
the other cases. So a mid-price hour on a mild afternoon told the user the
optimizer was stocking up for weather that was not coming. Those steps now say
**"Keeping the house at target"**; `preheat_weather` is kept for the branch
that has actually looked at the heat-loss forecast. Thirteen characterization
fixtures relabel at least one step; the four weather-driven scenarios
(`cool_rainy_summer`, `mild_windy_rain`, `precip_snow`, `shoulder_two_zone`)
are unchanged, which is the check that the genuine branch survived.

*If you automate on this:* the **Plan Narrative** sensor's state is the
dominant reason code, so an automation matching `preheat_weather` will stop
matching on ordinary heating hours and should match `scheduled` instead. The
code still appears for genuine weather pre-heating.

**The comfort bounds are described honestly.** The setup page called the
warmest and coldest acceptable temperatures "a hard ceiling" and "a hard
floor… never allowed below this", while the documentation, the config flow's
own code and the integration's setup all say the opposite: the bounds are
priced, not fenced. A hard band would make a cold morning the pump cannot heat
through unsolvable, and an unsolvable problem produces no plan at all. So
breaching a bound is made very expensive instead — expensive enough that
breakeven sits about two orders of magnitude beyond any real Nord Pool spread.
The four descriptions now say that, and say that the maximum is a limit rather
than a target and cannot hold back heat the house gets for free from the sun.

**Two ways into the comfort band skipped its checks.** The setup and options
forms have always refused to store a band that contradicts itself. Two other
paths write the same fields and did not: the `apply_schedule` service writes
the daytime comfort temperature, and the thermostat card's slider writes the
target temperature — with the slider's own maximum a degree *above* the
configured ceiling, so its top notch stored an impossible target by
construction. Both now run the same rules the forms do.

Two details matter for anyone with an automation calling `apply_schedule`. The
service refuses only contradictions **your call introduces** — a call carrying
only hot-water windows is never judged against comfort temperatures it never
mentioned, even on an entry whose stored band is already inconsistent. And a
band that is *already* inconsistent is reported as a repair notice rather than
corrected for you: which of the two numbers is the wrong one is yours to say.
That case is real rather than theoretical, because the old slider could store
it.

The slider itself now offers exactly the comfort band. It used to run a degree
past both ends, and with the new checks in place those outer degrees would have
been positions the control advertised and then refused. A refused setpoint no
longer trains the comfort learner either.

This meets v5.1.6's change from the other side, and the two are complementary.
That release made a settings page stretch a field rather than refuse to save
when a stored value falls outside it — naming `apply_schedule` and the
thermostat as two writers with limits of their own. This one narrows what the
thermostat can write in the first place. Neither replaces the other: the
stretching handles a value outside a single field's *range*, which is still
reachable (a thermostat on a house whose comfort floor is 14 °C can store a
target below the temperature page's own minimum), while the band rules handle
fields that contradict *each other*, which no single field's range can see.

The measured effect on planning is small (a daytime comfort temperature of 30
against a maximum of 23 moved the planned room peak by 0.01 K); this is a
correctness fix, not a planning change.

**The virtual battery reports the slab against the optimizer's own cap.** The
slab component's ceiling was `comfort maximum + 6` — a leftover magic offset,
a fixed 29 °C where the optimizer's settlement cap is sized from the demand
the weather actually creates and from how well your floor moves heat into the
room.

**Which way your figures move depends on your system, and both directions are
the same correction.** With underfloor heating the cap sits *below* 29 °C, so
usable capacity falls and the reported charge rises: on the characterization
fixtures 60.0 kWh becomes 33.1 (26.1 two-zone) and 41.7 % state of charge
becomes 75.5 % (95.9 %). With radiators the emitter is weak and the loop has
to run *hot* to hold the target, so the cap is far above 29 °C: a pre-1960
250 m² radiator house at −15 °C goes the other way, 5.0 kWh of capacity
becoming 14.6 and 50 % state of charge becoming 17 %. The old fixed number was
not "a bit high" — it was simply a different number from the one the optimizer
uses, in whichever direction your house happens to lie.

The reported ceiling is clamped to the buffer tank's rated maximum. The cap is
`target + demand ÷ floor heat transfer`, which grows without limit as that
coefficient falls: at the lowest value the `set_thermal_parameters` service
accepts it reaches 531 °C, which would have published 2560 kWh of "usable
capacity" for a floor loop. Nothing in this system can be hotter than the
tank, so that is the bound — and it applies to the report only, leaving the
optimizer's own arithmetic untouched.

This whole view is report-only: no plan changes.

**Golden fixtures, and a new kind of claim.** The reason-code change moves
`space_reasons` on the twelve reproducible fixtures that carried the old
fall-through label, and the battery ceiling moves `data.battery` in the five
coordinator fixtures. Every one is claimed with its reason; the rest are
byte-identical, trajectories and costs included.

Five fixtures could not be handled that way. The drift gate already declares
them non-reproducible — they are non-convex solves that land on a different
local optimum per BLAS build — and this release's change happens to be one
whose footprint *inside* them is decided by that optimum: all five run weather
whose heat-loss factor never crosses the pre-heat threshold, so every
`preheat_weather` they carry is a fall-through, and which steps fall through
differs per machine. A claim naming this machine's fixture is unclaimed drift
on another; naming another's is a stale claim here. Both spellings fail the
gate, for a change that is correct on both machines.

So the claim file gains a **may-drift** category for exactly those five: their
diffs are printed in full for a human to read, and are not judged by the
runner either way. It is deliberately narrow — the gate refuses a may-drift
entry naming any fixture whose numbers *do* travel, so it cannot become a
standing exemption for a real regression.

## v5.1.6

### The expert thermal page can be saved again

Changing a number under **Thermal model (expert)** and pressing Submit did
nothing, most of the time. No error, no message — the dialog simply stayed
open and nothing was stored. Turning *Derive thermal values from the
building type* off did not help, and the occasional save that did stick
made it look random.

It was not random. The page pre-fills every box from what is stored and
your browser posts all of them back, so one stored value the page refuses
to accept blocks the whole form, whichever field you were actually
editing. And the values the building questionnaire works out are scaled by
your heated area, while the ranges those boxes accepted were guessed
around a single 140 m² house with floor heating. A house with radiators
only is the clearest case: its "slab" store is the water and steel of the
radiator circuit, about 0.2 kWh/°C for 100 m², against a box that started
at 1. Sweeping every building the questionnaire can describe between 40 and
400 m², three quarters of them produced at least one value their own page
would not take back.

Three things changed.

**The ranges now match the physics.** They cover everything the
questionnaire derives for a house of 40 to 400 m², of any construction,
era, foundation and emitter, with a little headroom — and no more than
that, so a mistyped number is still caught.

**A value already stored can always be shown and saved.** If a value falls
outside its field's range anyway — a very small or very large building,
or a number written by the `apply_schedule` service — that one field
stretches to fit it and the page tells you which field it was and why. The
rest of the page keeps its normal limits. This applies to every page and to
first-run setup, not just the expert one.

**Editing an expert value now means it.** While derivation from the
building type is on, saving *Building type and emitters* recalculates all
ten derived numbers and overwrites whatever you typed. Changing any of them
to a different value on the expert page now switches the derivation off, so
your value stays, and the page says so while the derivation is armed. Only a
real change counts — pressing Submit without touching anything leaves the
derivation exactly as it was.

### Two captions that were giving wrong advice

*House thermal mass* said "roughly 3 kWh/°C for a light timber house, 8 or
more for heavy masonry". Those figures describe one 140 m² house with floor
heating, on a field that scales with your area — and this field only holds
the fast store, the room air, furnishings and light fabric; heavy floors are
counted separately under *Slab floor thermal mass*. A 100 m² timber house
belongs near 2, and "correcting" it up to 3 tells the optimizer the house
coasts about a quarter further than it does. The advice is now given per
square metre and says where the rest of the building is counted. The two
slab captions, which described a concrete slab only, now also say what the
field means for a house with radiators.

*Derive thermal values from the building type* said it overwrites values
"on the House and heating system page". There is no such page — the values
it overwrites are all on *Thermal model (expert)*, and it overwrites them
each time the questionnaire is saved, not continuously. It now says both.

Nothing about how plans are computed has changed: every optimizer
characterization fixture is byte-identical.

## v5.1.5

### Undo, while you are rearranging the system layout

Rearranging the layout on the setup page — dragging the boxes around,
drawing and removing pipes — had one way back: Cancel, which throws the
drawing away *and* closes the editor. If you had made a mess and wanted to
start from the layout your system actually runs, you had to close the
editor and open it again.

There is now an **Undo** button next to Save. It puts the drawing back the
way it was when you opened the editor — the pipes and where the boxes sit,
both — and leaves you in the editor, ready to try again. It stays greyed
out until you have actually changed something, so it can never surprise
you, and it never writes anything: the layout your system runs only ever
changes when you press Save.

Undo goes back to the layout that was in force when you opened the editor,
not one step at a time.

## v5.1.4

### The setup page, after a round of field reports

Six things the owner of a real install ran into, all fixed.

**The sensor picker could unassign a sensor while you were trying to fix
one.** If your entity was not among the 200 the list offered, the dropdown
quietly showed "(not configured)" — and pressing Assign then saved that
emptiness and reloaded the integration. The list now always contains the
entity the slot already holds, pre-selected; a search box narrows the
candidates as you type, so an entity is reachable however many sensors you
own (the list says "Showing 200 of 412 — type to narrow" when it is
trimmed); every option shows its entity id next to its name, so two probes
whose names differ only by a "_2" can be told apart; and an Assign that
would clear a slot asks a second time first. Two further faults in the same
control went with it: Assign read the dropdown after the filter had rebuilt
it, and the filter box had no styling of its own and would have been
unreadable on a dark theme.

**The flow arrows pointed the wrong way.** Each pipe's arrow was drawn
horizontally regardless of where the pipe went, so on a pipe that runs
diagonally it looked perpendicular to the flow. Arrows now follow the pipe's
own direction — measured against the drawn curve, the worst case went from
about 87 degrees off to 0.012.

**Text was cramped against the outlines.** Labels and readings sat 8 units
from the contour walls; they now sit 14. Nothing else about the layout
moved.

**The solar row's label and reading overlapped** when Open-Meteo was the
source, because the reading's width was under-estimated. The label is now
measured against the real reading and shortened if it must be — the reading
itself is never cut.

**Two stray lines at the bottom-left of the heat pump** were meant to be
cabinet vents and read as a rendering artifact. They are gone.

**A focus outline lingered beside a sensor field** after cancelling the
picker: it was drawn as an outline on an SVG shape and clipped, so only its
top and left edges showed. It is now drawn as part of the shape, fully
visible, and cancelling with the mouse no longer leaves it behind — while
keyboard users still get a clear ring.

The Outside box is deliberately unchanged.

## v5.1.3

### Fix: a broken sensor no longer teaches the model the wrong house

If one of the temperature sensors the optimizer depends on stopped working —
a flat battery in a room sensor, a Zigbee node dropping off, an entity that
got renamed — the integration kept planning from that sensor's last known
reading. That part is deliberate: steering from the last good number is
better than steering from nothing.

What was wrong is that the *learning* kept running too. The optimizer
continuously refines a model of how fast your house loses heat, and it was
doing that against a number that had not changed since the sensor died. A
frozen reading looks, to the model, like a house that barely loses any heat
at all, so the learned figure walked steadily downward — in testing, from its
starting value to roughly a third of it inside two days — and it is written to
disk as it goes. The damage therefore outlived the sensor outage: the sensor
came back, and the house model stayed wrong for weeks. The same frozen reading
also made the heating curve look permanently comfortable, which quietly biased
the standing curve adjustment downward.

The integration already knew how to handle one version of this: a sensor that
keeps reporting the same value for too long ("stale") froze the learners
correctly. Every *other* way a sensor can break — reporting `unavailable`,
having its entity disappear, or reporting something that is not a number — did
not. That gap is what this release closes.

**What changes now**

- Any sensor a learner depends on that is unusable for any reason pauses that
  learner until the sensor recovers. Planning is unaffected — it still uses the
  last known reading, as before — and learning simply resumes where it left off.
- A sensor you never configured still does not pause anything. Only a sensor
  you *did* configure and that is currently broken counts.
- The diagnostic now says which problem and which sensor caused the pause
  (for example `unavailable:indoor_temp_entity`), instead of only ever saying
  "stale".

**If your model already drifted**

An installation that ran through a sensor outage before this release may have a
house model that is already wrong. Call the **Restore Learned Snapshot**
service (`heatpump_optimizer.restore_learned_snapshot`) to roll every learner
back to the most recent weekly snapshot taken while all inputs were healthy.
Nothing is lost permanently — learning continues from the restored point.

## v5.1.2

### Maintenance: the test suite's own gates can now fail

No integration behaviour changes in this release — nothing about how your
heat pump is planned, priced or controlled is different. What changed is the
test suite that guards those behaviours: an audit found that several of its
gates could not actually fail, so a regression in the areas they cover would
have passed unnoticed.

- Two test suites (`validate.py` and `edge.py`) printed their failures but
  always exited successfully; they now report a failing exit code.
- The runner's "is every test wired in?" guard counted a test as wired even
  when it was only mentioned in a comment; it now requires a real invocation
  line, and covers the JavaScript tests too.
- Several checks were tautologies or compared a value against itself — the
  external-heat hot-water suppression check compared two identical plans, the
  plan-view energy cross-check printed numbers without comparing them, and a
  climate-entity check was written so it could never be false. All now assert
  something that can fail, verified by injecting each defect and watching the
  suite catch it.
- The card test could read a plan file left behind by a different checkout;
  the plan payload path is now derived per-checkout (or set explicitly via
  `HPO_PLANDATA`).
- The Home Assistant test stub now validates number selectors (coerce and
  range, as the real one does) and models coordinator availability
  (`last_update_success`), so future tests can exercise entity availability.

## v5.1.1

### Hotfix: options saves no longer freeze Home Assistant

Leaving the integration's options pages — even without changing anything —
could make the whole Home Assistant instance unreachable for minutes. Every
save triggered a full reload of the integration, and the reload would not
finish until it had read every sensor, fetched prices and weather, and run a
complete optimization from scratch. On modest hardware that adds up, and the
heavy math starves everything else running in the instance while it does.

Three changes, all in how the work is scheduled — no plan, price or comfort
behaviour is different:

- **A save that changes nothing no longer reloads anything.** The options
  pages used to rewrite their settings on every visit, so backing out of an
  untouched form counted as a change. The integration now compares the saved
  configuration against the one it is already running with and only reloads
  when something actually differs.
- **A real reload comes back in seconds.** The previous plan is kept across
  the reload and published immediately, so your entities never go blank and
  nothing waits on price or weather services. The fresh optimization runs in
  the background and replaces it within the next update cycle. On a genuinely
  fresh start the integration comes up with live sensor readings first and
  likewise solves in the background.
- **Long optimizations yield to the rest of Home Assistant.** The solver now
  pauses for a moment at its internal stage boundaries so the user interface
  and other integrations keep responding on slower hardware while it works.

## v5.1.0

### Documentation you can actually read

The README had grown to 1,594 lines in an order nobody would choose: a
93-line legal disclaimer before any description of what the integration
does, an 843-line theory essay between you and the reference material,
and the installation instructions at line 1,515. It is now 632 lines in
the order you need them — what it does, requirements, install, a quick
start covering your first thirty minutes, then the entity, service and
configuration reference, with the depth moved into documents of its own.

**New documents.** `docs/how-it-works.md` carries the full theory, rewritten
against the current code rather than the version it was written for.
`docs/configuration.md` documents every setup step and all thirteen options
pages field by field. `docs/architecture.md` maps all 42 modules.
`docs/ecl110.md` gives the Danfoss ECL110 integration its own page.
`DISCLAIMER.md` holds the legal text in full, with a condensed paragraph
and a link left in the README.

**Diagrams.** Architecture and data flow, the optimization cycle, the
config-flow branch map and the hydronic topology catalog are drawn as
diagrams that render on GitHub.

**Claims checked against the code, not against the last README.** Every
factual statement was verified line by line and the false ones corrected:
the sensor table listed 53 rows under a "55 total" heading (the two
ECL110 displace sensors were missing), the options flow was described as
11 pages when it has 13, three services were undocumented, the module
tree was missing modules, the feature list still described v2.8, the
weather forecast was attributed to Open-Meteo when it comes from your
weather entity, the system-identification button was described as working
out of the box when the option must be enabled first, and the accuracy
claim ("99% in two days") stated more than the test suite measures — it
now states exactly what the suite enforces.

Documentation-only release: no code, entities, or plans change.

## v5.0.0

### Entity names in your language, and one duplicate sensor merged

This is a major-version release because it changes what entities exist and
how they are named. Read the migration notes below; for almost everyone the
answer is "nothing to do".

**Translated entity names.** Every entity now takes its display name from
the integration's translation files instead of a hardcoded English string:
English and Swedish ship in this release, following your Home Assistant
language. The English names are the same names as in v4.x, so an install
running in English looks unchanged. Any entity you renamed yourself keeps
your name — a user-set name always wins over the integration's.

**One sensor instead of two for solar.** "Solar Radiation (Optimizer)" and
"Solar Irradiance" published the same number (the irradiance the optimizer
is currently planning with). They are now one sensor: **Solar Irradiance**,
the one the dashboard card, the documentation and the attributes (forecast,
source, `plan_kind` marker) always lived on. The sensor total goes from 56
to 55.

**A `stat_kind` attribute on the headline sensors.** Predicted Savings,
Savings Percentage, Optimization Score and Plan Narrative now advertise a
stable `stat_kind` attribute, like `plan_kind` on the plan sensors, so the
dashboard card (and your own templates) can find them without depending on
entity ids. The card needs no update — this is future-proofing.

### Migration notes

**Existing installs:**

- **Entity ids, unique ids, history and long-term statistics are all
  preserved.** Unique ids never changed, and Home Assistant keeps a
  registered entity's id across renames. Automations, dashboards and
  recorded statistics keep working untouched.
- **Display names only change if your HA language is not English** (Swedish
  installs get Swedish names) — and even then, never for entities you
  renamed yourself.
- **The "Solar Radiation (Optimizer)" sensor is removed.** Its registry
  entry is cleaned up automatically at startup, so it will not linger as an
  unavailable entity. Its recorded history is *not* merged into Solar
  Irradiance — the two sensors always recorded the same value, so Solar
  Irradiance's own history already tells the same story; the retired
  series simply stops. Its long-term statistics remain visible under
  Developer Tools → Statistics until you dismiss the orphaned series
  there (one click on "Fix issue"). If anything of yours references
  `sensor.…_solar_radiation_optimizer`, point it at
  `sensor.…_solar_irradiance`.
- **The climate entity's displayed name improves.** It becomes formally
  "device-named" (the idiomatic Home Assistant pattern for a device's
  main entity). Under v4.x it displayed with the device name doubled
  ("Heat Pump Optimizer Heat Pump Optimizer"); it now displays as just
  the device name. Existing installs keep their entity id.

**New installs:** identical entity ids to v4.x for every sensor, binary
sensor, button and switch, in every Home Assistant language. The
integration pins its English object ids explicitly
(`sensor.heat_pump_optimizer_optimal_setpoint`, …), so docs, automation
examples and the dashboard card's discovery keep matching even on a
Swedish-language HA, where translated names would otherwise produce
Swedish entity ids. The one exception is the climate entity: a fresh
v5.0.0 install creates `climate.heat_pump_optimizer` where v4.x created
the doubled `climate.heat_pump_optimizer_heat_pump_optimizer` — the
corrected id, and nothing in the integration, card or docs references
the old one.

### Also: the test gate stops crying wolf

Three recent releases (v4.0.7, v4.2.0, v4.3.0) showed a red CI badge for a
reason that had nothing to do with their code. The golden-fixture gate lets
a release declare "these fixtures move on purpose" in a claim file, and
fails any claim that turns out to move nothing — so claims cannot outlive
the release that needed them. But the file is committed, so a release that
moves no fixtures inherited the previous release's claims and failed on
every one of them.

The claim file now stamps itself with the release it belongs to and is
rejected if that does not match `VERSION`, and in CI it must also differ
from the release it is being compared against — so an inherited list is
caught in a fraction of a second, with one sentence saying what to do,
instead of a wall of misleading "regression" output after a half-hour run.
Three further faults in the same gate went with it: a valid claim file
could fail a local run, a release that added and claimed a new fixture was
failed for it, and a mis-resolved comparison could silently compare the
tree against itself and pass. `VERSION`, `manifest.json`, the release-notes
heading and the card version are now pinned to each other as well, so a
half-finished version bump fails the suite rather than shipping.

Integration-only release: the dashboard card is unchanged.

## v4.3.0

### The setup page looks like your heating system now

The Setup tab's identical rounded squares are gone. Each component is drawn
as a thin line-art contour of the thing it represents: the house has a
gable roof and a chimney, tanks are domed cylinders, the heat pump is a
cabinet with its fan and louvres, the mixing valve is a chamfered block
with a proper valve symbol sitting on its own pipe, the floor slab stands
on hatched ground, and outside air is an open composition under a cloud —
unbounded, because it is.

**The DHW pre-heating coil is finally visible.** When the wood tank
pre-heats hot water through an immersed coil, the coil is drawn as a
spring on the tank's upper-right wall with its own connector stubs, and
the hot-water pipe departs from the coil instead of the tank's edge. Draw
or remove the wood-to-hot-water connection in the layout editor and the
coil appears and disappears live.

**Pipes read like plumbing.** Endpoints carry small connection dots
welded to the component walls, each pipe shows a chevron for flow
direction, and the routing sweeps a little rounder. Decorations get out
of the way while the layout editor is open.

Everything underneath is untouched: the same assignment rows live inside
the new contours, clicking or keyboard-navigating them works as before,
the drag-and-connect layout editor is unchanged, and all colors follow
your Home Assistant theme in light and dark mode. Shapes stretch with
their sensor rows, and the whole page was geometry-checked shape by shape
(arcs meet their walls, ink stays clear of text) rather than eyeballed.

Card-only release: no integration behavior, entities, or plans change.
Bump the card resource query string (`?v=4.3.0`) or clear the browser
cache to pick up the new card.

## v4.2.0

### The card grows up: editor, headline, your language, your currency

**A visual editor.** The card can now be configured entirely from the
dashboard UI — no YAML needed. Adding or editing the card offers entity
pickers filtered to this integration's sensors, the plot window, the
what-if editor and headline toggles, a currency override and per-series
visibility, and the emitted config stays minimal: options left at their
defaults are not written into your dashboard.

**A headline that answers "is it working?".** A compact row under the
header shows the projected savings (in the sensor's own currency), the
optimization score and the plan narrative — the figures the integration
already computed but the card never showed. It hides itself entirely when
the backend doesn't publish them, and `show_stats: false` turns it off.

**The card speaks Swedish.** Every label, menu, tooltip, dialog, error and
spoken (screen-reader) string — about 200 of them — now follows Home
Assistant's language: Swedish when HA is set to Swedish, English otherwise,
dates and weekdays included. Unknown languages fall back to English.

**Prices in your currency.** Nothing is hardcoded to SEK any more: the
axis, tooltips and cost figures use the currency the integration publishes
on the plan sensors (v4.1.0+), falling back to Home Assistant's configured
currency, with `currency:` in the card config as a manual override. SEK
remains the last-resort fallback, so existing dashboards look unchanged.

**Keyboard and screen-reader access.** Plan slots and lanes are focusable
buttons with spoken labels — Enter opens the same menu a tap does, Delete
removes the focused slot, Escape closes menus however they were opened,
and focus lands somewhere sensible afterwards instead of vanishing. The
setup page's rows and entity picker work the same way, and the card honors
`prefers-reduced-motion`. Saved view preferences are now keyed per card
config, so two cards on one dashboard stop overwriting each other's
settings (existing saved settings are migrated).

Card-only release: no integration behavior, entities, or plans change.

## v4.1.0

### A setup a homeowner can finish, and sensors that say what they mean

**New setups get a questionnaire instead of physics homework.** Initial
setup used to walk everyone through six required pages, including raw
thermal values in kWh/°C that nobody knows and eight Danfoss ECL110 MQTT
fields that only ECL110 owners can answer. Setup now branches after the
temperature page: *Describe my building* (recommended) asks what the house
is made of, roughly when it was built, its foundation, heated area and
emitters — the same questionnaire the options flow has had — and derives
the thermal starting values, leaving only three nameplate numbers for the
heat pump. *Enter thermal values directly* keeps the old pages verbatim
for anyone holding real figures. **Existing installs keep their
configuration exactly as it is**; only new setups see the new path.

**The ECL110 fields moved, they were not removed.** They live on the
options page *Heat curve control (ECL110)*, where they always also were.
An install that configured them keeps them; every reader falls back to
the same defaults when they are absent.

**Contradictory settings are now rejected at the form.** A minimum
temperature above the target, a night temperature above the day one, a
day that ends before it starts, or a heat pump minimum power above its
maximum could all be saved — and the optimizer treats those bounds as
soft penalties, so the plan just sat in permanent violation with nothing
to point at. Both the setup and the options forms now refuse the
contradiction on the field that caused it, in plain language.

**Sensors follow your Home Assistant currency.** Every cost figure was
hard-coded to SEK. Sensors now use the currency configured on the
instance (SEK stays the fallback, so existing installs and their
long-term statistics are unchanged), and the published data carries the
currency so the dashboard card can read it. Sensor displays also gained
sensible rounding — temperatures to a tenth, money and COP to two
decimals — without changing any recorded value.

**Fewer dead entities on fresh installs.** Six sensors that only mean
something with opt-in hardware or long-collected evidence — the two
ECL110 sensors, the valve target recommendation, the compressor frequency
advisor, the contract comparison and the DHW heavy-day demand — are now
disabled by default on new installs. Existing installs are unaffected;
any of them can be enabled from the entity registry in one click.

## v4.0.7

### Card: the plan is editable on a phone now

Reported on mobile: existing plan slots could not be modified or removed at
all. Two causes, both fixed.

**Tap opens the slot menu.** The add/change/remove menu was bound to the
`contextmenu` event — a desktop right-click. iOS Safari never fires it, and
long-press on the card was swallowed by the drag handler, so a phone had no
path to the menu at all. A tap (press and release without movement) on a
lane now opens the same menu: on a slot it offers force/remove, on empty
lane it offers adding a slot. A real drag still drags — the menu only opens
when the pointer hasn't moved — and desktop right-click keeps working
exactly as before.

**Finger-sized grab handles.** The edge-resize grab zones were 6 SVG units
wide, tuned for a mouse cursor. On a coarse pointer (`pointer: coarse`
media query — touch screens) they are now 16 units, so grabbing a slot edge
to resize it works with a finger. Fine pointers keep the 6-unit zones so
precise mouse edits don't get sloppier.

Card-only release: no integration behavior, entities, or plans change.
Bump the card resource query string (`?v=4.0.7`) or clear the browser cache
to pick up the new card.

## v4.0.6

### Physics from the audit's fifth pass: one price of heat, honest tanks

This release deliberately changes plans. The simulation and the optimizer's
valuations disagreed about what a stored kilowatt-hour costs, the DHW model
could create energy at its floor clamp, and two learners were booking the
pump's failure to follow the plan as the pump being inefficient. Fixing any
of those moves numbers; here is which, and in which direction.

**Every store now has one marginal price of heat, shared with the
simulation.** The dynamics charge a throttled buffer tank at the
flow-derated COP of the tank's own temperature — charging a 70 °C tank at
−5 °C outdoor costs roughly twice the electricity per kWh the plain curve
claims — and charge the DHW tank at the DHW COP. But the terminal cost and
the savings settlement priced every stored kWh at the plain space curve, so
the marginal value of stored heat sat below its marginal cost and the
solver only stored when the price spread also paid for a COP gap the
physics never charged. A shared `marginal_cop` helper now sits next to the
COP curves, and the terminal cost, the deferred-energy settlement and the
cap-refusal loop all draw each store's conversion from it. Valve-storage
plans charge the tank somewhat less eagerly and somewhat more honestly;
the reported savings no longer overstate themselves when a plan ends with
a cold tank. Unthrottled configurations keep the historical arithmetic bit
for bit — the derate gate makes the helper collapse to the plain curve
there, and the tests pin the equality exactly.

**Settlement ceilings are what the plan can reach, not what the nameplate
says.** The two-zone slab cap was sized from the whole house's demand, but
the slab feeds only the lower zone — the upper floor is radiator-fed — so
hot-slab end states were over-valued by the upper zone's share; it is now
sized from the lower zone alone, through the learned loss split. And the
buffer was settled against its 70 °C safety rating even when a small pump
against a cold day cannot push the tank anywhere near it: the cap is now
the temperature at which the pump's flow-derated output stops out-running
the house's draw plus the tank's standby loss, capped at the rating. Strong
pumps and mild weather see no change; every two-zone plan's terminal
numbers move a little.

**The DHW tank can no longer pour hot water it does not hold.** The draw
debited from the tank was the nominal demand — volume heated from inlet to
setpoint — regardless of the tank's actual temperature, and the inlet floor
silently refunded the fabricated deficit: created energy, with no ledger.
The debit now scales with the rise the tank can deliver, which is exactly
the existing mixed-at-tap convention (a tank at or above the setpoint still
draws the nominal constant, so hot tanks are unchanged, baselines
included). The tank rating is enforced inside the simulation with
refused-heat accounting, the buffer clamp's pattern, instead of trusting
every caller to pre-clamp. Direction: every DHW plan whose tank dips below
the setpoint reheats slightly less (a cold tank also empties slower), so
`dhw_heating_cost` drops a few percent and the temperature trajectories
shift from the first draw onward. Demand-side targets stay nominal on
purpose — a cold tank does not get to lower its own requirement. The
wood-coil split and the wood-tank floor also stop hard-coding a 10 °C
inlet and use the shared seasonal/live inlet reference; byte-inert at the
default annual mean.

**Learners stop booking tracking error as efficiency.** The observed-COP
learner reads commanded-versus-measured electrical power, but delivered
heat is not measured, so a large gap means the pump is not running the plan
(compressor limits, cycling, ramp lag), not that it is inefficient — those
samples are now discarded instead of folded into `cop_scale`. The interval
heat-loss learners replayed the *commanded* power through the model, so a
delivery shortfall was blamed on the house's heat loss coefficient; where a
power entity exists they now replay the measured draw net of the hot-water
allocation, and skip the interval when the meter is stale or the immersion
element is latched. Installs without a power entity keep the commanded
figure — there is nothing better to use, and that is now written down.

**System identification learns the gains it was smearing.** The step-fit
regressed `C·dT/dt = Q − UA·ΔT` with no intercept, so internal gains
(~0.3 kW of people and appliances) leaked into both fitted parameters —
relax-phase samples carry zero input while the gains keep heating. The fit
gains a constant column, recovers the free heat explicitly (reported as
`internal_gains_kw`, sanity-bounded), and degrades to the old two-column
form when the data cannot separate three. On synthetic data with known
parameters the old form misses UA by more than 15 %; the new one is exact.

**The battery view shares the optimizer's caps.** The buffer component was
capped at `comfort + 20 °C` (43 °C by default), so a 40 °C tank published
88.5 % state of charge while the settlement valued it against 70 °C; it
now reads the tank's configured rating, the same constant the simulation
clamps at, and a 40 °C tank honestly reads about 43 %. The zone losses use
the learned split and scale the dynamics actually run (inert at the 1.0
defaults). The five `coord_*` fixtures move in their `battery` leaves.

Golden movement, claimed: every `dhw=True` scenario's DHW trajectory and
cost (measured on `winter_single_dhw`: `dhw_heating_cost` 6.66 → 6.04,
one fewer compressor start; on `dhw_cold_tank`: 8.53 → 8.31), every
two-zone scenario's terminal/settlement figures, and the valve-storage
family's plans. Single-zone space-only scenarios are byte-identical, and
`tests/features.py` pins the identities that guarantee it.

### After the adversarial review

Three verifiers attacked the physics commit before release; what survived
them is stronger than what went in:

- **The draw debit now references the 40 °C mixed-use temperature, not
  the setpoint.** Mixing at the tap keeps the enthalpy per draw constant
  for any tank at or above what people actually use; the setpoint ramp
  under-debited the 40..setpoint band — the very band cost optimization
  rides — by up to a third and booked the deleted demand as savings.
- **Pre-stored buffer heat cannot be drained for free**: the settlement
  value floors at the solve's starting tank temperature, so a tank
  charged before a cold snap settles what a plan drains from it.
- **The COP tracking gate no longer deadlocks**: outliers are judged
  against a walking ratio average that persistent shifts can move, so a
  genuinely degraded pump teaches the model — and reaches the
  degradation watchdog — instead of being filtered forever.
- **The meter split is gated the same way**: an interval where the pump
  visibly is not running the plan yields no heat-loss sample, instead of
  booking the whole gap onto the house.
- **System identification survives real sensor noise**: the intercept is
  anchored to the configured gains with a weight calibrated by the
  night's own residual scatter — clean data recovers the truth exactly,
  a noisy night leans on the prior, and a hopeless one abstains
  (measured: the unregularized fit adopted a +34 % biased loss
  coefficient or nothing at all).


## v4.0.5

### The zoom that quietly capped your editing

A field report, run to ground with a console probe: slots could only be
added, removed or moved "up until midnight". The plan was fine and the
20-hour window was in force — the card was **zoomed in**, and the editable
ceiling clamps to the visible window so a slot can never be dragged to
where the pointer cannot reach. A pinch or ctrl-wheel zoom is easy to make
without noticing, it never expires, and nothing said the view was the
limit; the invisible remainder read as an arbitrary rule.

Three changes, all in the card:

- **Dragging a slot against the plot's edge now pans the view under it**,
  so the visible window stops being a wall. The gesture survives the
  re-renders panning causes, the same way the chart's own pan drag does.
- **The card says when zoom is the limit.** The lanes grow a chevron at
  the clipped edge, and the what-if panel explains it — with a one-press
  "show the whole plan" button — whenever the visible edge undercuts both
  the 20-hour window and the plan's end. An unzoomed card shows nothing
  new.
- The editable ceiling's three inputs (visible window, 20-hour apply
  window, plan end) are now computed in one place the diagnostics can
  read.

- **The view no longer outlives its session.** Closing the expanded
  dialog discards any pan/zoom, so the next open always shows the whole
  plan. This is the fix for "but I never zoomed": on a long-lived
  dashboard tab the old view persisted for days, re-anchoring itself to
  "now", so one unnoticed gesture weeks ago was still capping editing
  today.

### And the chart stopped eating your clicks

The same field report, dug one layer deeper, found a second and older
fault: the chart's series — the price area, the power bars, the
temperature lines — are painted **after** the editing lanes, and SVG
fills capture pointer events by default. Wherever a filled series body
lay over the lane strip, hovering showed no highlight, slots would not
drag, and right-clicking got the browser's own menu instead of "Add a
slot here". Depending on where a series' data began, that dead zone
could start exactly at midnight — which is precisely how it read.

Every chart-body overlay (series paths, the estimated-prices shading,
the crosshair) is now pointer-inert, so the lanes underneath always
receive the hover, the drag and the right-click. A markup-level check
pins this: the test harness fires synthetic events and cannot see real
hit-testing, which is how this shipped in the first place.

Card version 4.0.5; hard-refresh the browser if the hint does not appear
after upgrading.

## v4.0.4

### Time alignment and price math from the audit's fourth pass

The plan's clock and the market's clock now agree. On a healthy install
with common settings nothing moves: every plan fixture is byte-identical,
and the guards below only wake on inputs that were already producing wrong
answers.

**Plans are anchored to the quarter-hour they actually describe.** The
price and weather arrays have always been built on the midnight-anchored
quarter grid, but the solve stamped its timestamps with the raw instant it
happened to run at — a 12:07 solve published a "12:07" step whose price
was the 12:00 quarter's. Every consumer inherited the seven-minute lie:
card and sensor timestamps, manual-plan pins, capacity-window folding, and
the filed accuracy promises. The solve anchor is now floored to the grid
once, from a single clock reading shared with the forecast assembly, and
the same snap covers the what-if simulator and the manual-plan step count.
Wall-clock lookups into the plan — "what applies right now" — deliberately
stay on the raw clock. One visible edge: an override expiring at 12:05
still pins the [12:00, 12:15) step of a 12:07 solve, which is the grid's
own semantics — the override covered that step's start.

**Days with a DST transition no longer train the price prior.** On the
autumn fold the repeated local hour's second batch of entries silently
overwrote the first, so a 25-hour day slipped through the completeness
gates as a well-formed 24-hour day and trained the shape, the quarter
factors and the residual variance on a fabricated hour. A local day whose
entries change UTC offset mid-day is now excluded from all price learning
at the single bucketing chokepoint — two days a year, both directions,
every learner seeing the identical exclusion. Prediction-time lookups were
already wall-clock-safe and are unchanged.

**Metering windows longer than an hour now meter longer than an hour.** The
peak tracker's window snap could only move the minute field, so a 90- or
120-minute capacity tariff degenerated into hourly windows: less burst
dilution than the DSO's meter grants, inflated recorded peaks, and the
live guard projecting over the wrong remaining time. All three snap sites
now share one midnight-anchored helper, matching the optimizer's own
window-offset arithmetic. For 15/30/60-minute windows the result is
bit-identical, persisted window keys included.

**Negative price days no longer invert the solver's starting guess.** The
smooth initial guess normalises by the horizon's mean price; a negative
mean (a real Nordic spring day) flipped its sign, so the guess ran lowest
in the cheapest hours, and a near-zero mean saturated it into bang-bang at
arbitrary steps. Below a small positive mean the guess now falls back to a
price-rank mapping onto the same band — cheapest step, highest start.
Three coordinator consumers of the mean price got the same respect for
sign: a setpoint override during a negative-mean spell records a neutral
relative price instead of a sign-flipped one, the DHW setpoint sweep ranks
against a floored positive level instead of crowning the hungriest
candidate, and the elastic legionella ceiling honestly reports "no
opinion" rather than a ceiling below every possible price.

**A 100× grid fee gets a warning, not a silent plan.** 25 öre typed as
`25` in a SEK/kWh field — rules, fixed component, or a fee sensor
publishing öre — now raises a warn-only repair issue naming the value and
its source. Nothing is mutated or capped: the plan keeps pricing with
exactly what was configured, and the notice clears on the first planning
cycle after the value returns to plausible.

## v4.0.3

### Guards from the audit's third pass

Six fixes for the moments things go wrong — a solver that keeps failing, a
clock that steps backwards, a sensor that froze last winter. On a healthy
install nothing changes: every plan fixture is byte-identical, and the only
new coordinator data are two staleness fields.

**A clock before the plan no longer executes the end of it.** If the system
clock stepped back past the plan's first step (NTP correction, a restored
stale plan), the current-action lookup fell through to the *last* step of
the horizon — the 24-hours-ahead slot where terminal-value charging lives.
A small skew now clamps to the first step; anything larger idles, exactly
as if there were no plan.

**A plan that keeps failing to refresh now says so — and stops steering.**
A failed solve has always kept the last good plan, deliberately; but it
kept it silently and forever. The coordinator now publishes the plan's age
(`plan_age_minutes`) and a staleness flag (`plan_stale`, tripping after
three missed solve cycles, at least 90 minutes). A stale plan is no longer
actuated — the heat pump falls back to its own heating curve, the same
behaviour as having no plan at all — and three consecutive solve failures
raise a repair issue that clears itself on the next success.

**A learner rollback no longer un-remembers billed peaks.** The weekly
snapshot insurance restored the month's realised peak list along with the
learners — but those peaks are facts the grid company already metered, not
learned state. A rollback could lower the capacity-tariff threshold and
mis-arm the live peak guard against a ceiling that no longer exists. Peaks
now stay out of snapshots entirely; old snapshots carrying them are ignored.

**Thermal masses can no longer divide the model to pieces.** A zero or
near-zero thermal mass — a typo in config, an aggressive
`set_thermal_parameters` call — put infinities inside the objective. Every
mass is now clamped to a physical floor (0.1 kWh/°C) at the parameter
boundary, and the per-step simulation subdivides any step whose
coupling-to-mass ratio would make plain Euler integration oscillate. No
sane configuration ever triggers either guard; the fixtures prove it.

**Frozen sensors fail safe.** A humidity sensor that stopped reporting held
a raised mold-guard floor forever; it now reads as absent after two hours
and the floor vanishes. A dead cold-water inlet probe pinned the hot-water
model at its last reading; after a day it degrades to the seasonal model.
And a legacy stored timestamp without a timezone no longer crashes the
open-window detector's staleness release on restore.

**Setup now tells the truth about Tibber.** A network failure during token
validation reported "invalid token", sending users to retype a token that
was never wrong. Connectivity problems now get their own message, in both
the initial setup and the options page.

## v4.0.2

### Lifecycle housekeeping from the audit's second pass

Nothing here changes a plan — same solves, same setpoints, same money.
Four fixes to how the integration lives alongside Home Assistant.

**Removing the integration now removes all of it.** Unloading the last
config entry left the `restore_snapshot` and `diagnose_interval` services
registered — the same registration-list drift a previous release fixed for
`apply_schedule`. Removal now asks the service registry itself what the
integration registered, so the two lists cannot drift apart again.

**One HTTP session, Home Assistant's.** Every price fetch and every Tibber
token check opened its own connection pool and threw it away. Both now ride
the shared session Home Assistant provides — the weather client always did —
which is faster and stops the churn of sockets on every update.

**Each solve works on a frozen copy of the world.** The optimizer runs in a
worker thread while the learners, the live peak guard and the thermostat
card keep writing on the event loop; a write landing mid-solve could hand
the solver a state that never existed. Every solve now snapshots the
thermal state, the learned parameters and the tuning configuration at
dispatch, so what the plan was built from is exactly what the moment held.

**Fewer writes to your SD card.** The accuracy history was rewritten every
update cycle whether or not anything in it had changed. An unchanged
payload is now skipped — a failed write still retries on the next cycle —
which matters on the flash storage most installs run on. Stored formats
are unchanged.

## v4.0.1

The test suite now runs itself. This release contains no behaviour change
to the integration — every golden fixture is byte-identical — but the
18,000 lines of tests that guarded v4.0.0 were only ever run by hand;
now they run on every push and pull request.

### Continuous integration

- **`.github/workflows/tests.yml`**: the full suite on every push and PR
  (~15 minutes), and nightly with the closed-loop learner simulation
  (`SLOW=1`). Dependencies are pinned in `tests/requirements-ci.txt` so
  two runs cannot disagree for reasons unrelated to the code.
- **Golden fixtures are checked environment-proof.** Solver floats are not
  bit-stable across BLAS builds, so CI never compares this runner's output
  against fixtures recorded on another machine. Instead `tests/env_drift.py
  --all` captures every scenario twice in the same runner — once from the
  tree under test, once from the PR's merge-base — and requires the two to
  be byte-identical. A PR that deliberately changes behaviour claims the
  moved scenarios in `tests/golden/claimed_drift.txt`, which is visible in
  review; stale claims fail the gate.

### The suite got teeth where it had gaps

- **Golden captures now enforce physical invariants** on both record and
  check: finite values everywhere, electrical draw within the compressor
  maximum, trajectories inside −40..120 °C, savings never above 100 %.
  `--record` can no longer bake an impossible plan into a fixture.
- **`tests/optimality.py` can now fail.** It used to print a comparison
  and exit 0 regardless; it now asserts the plan meets the comfort floor
  and that neither a greedy same-energy schedule nor 300 comfort-safe
  perturbations find a materially cheaper plan — and it runs in
  `tests/run.sh`, which it never did.
- **`tests/run.sh` audits itself**: a test script added to `tests/` but
  not wired into the runner now fails the run instead of silently never
  executing (exactly what happened to `optimality.py` and
  `env_drift.py`).
- **The Home Assistant stub learned real timezones**: set `HASTUB_TZ`
  (e.g. `Europe/Stockholm`) and `as_local`/`now` do real conversions via
  `zoneinfo` instead of being identity functions. The default remains the
  identity, so nothing changes for existing fixtures — this is the
  foundation the upcoming DST regression tests build on.

### Notes

- `tests/README.md` documents the new modes, and its fixture count is
  correct again (53, not 37).

## v4.0.0

Thirty-six features in seven tranches, and one rule held through all of
them: **everything new is off, inert, or purely observational until you
turn it on.** A 3.16.0 install upgrades to a byte-identical plan — same
solves, same setpoints, same money — plus a set of switches, each of which
was built, reviewed and tested to earn its place before it earns your
trust. No store migrations are required; every persisted format is
additive, and a downgrade reads its own keys and ignores the rest.

### The bill beyond spot (T1)

The optimizer used to price a kWh at its spot price. Your bill does not.
Grid transfer fees now ride every priced kWh — flat, by rules
(day/night/season), or from a sensor — and capacity (effekt) tariffs can
be masked to the months, hours and weekdays your DSO actually bills.
Prices past the published horizon come from a learned 96-bin quarter-hour
prior instead of a flat guess, with an optional risk premium on the
guessed steps. And a monthly ledger settles every interval as it happens,
so the **Contract Comparison** sensor can show what this month's metered
kWh would have cost under hourly spot, monthly-average spot and a fixed
contract — and what your load shifting actually earns per kWh.

### Power is a budget (T2)

Tell it your main fuse and the optimizer treats amps as the hard budget
they are: an opt-in fuse guard caps every planned step at what the fuse
leaves after the rest of the house, a live peak guard watches the billed
metering window in real time and holds discretionary hot water back
before a new monthly peak is set, and outage recovery staggers the
restart draw. The **Power Headroom** sensor broadcasts the kW the house
can take right now — a number an EV charger's dynamic limit can follow —
and a monthly fuse advisor prices what a smaller main fuse would cost you
in comfort, using the optimizer's own solver as the judge.

### Hot water that knows your house (T3)

Hot water demand stopped being one number: weekday and weekend draw
profiles are learned separately, quantile ready-targets size the tank for
your actual heavy days (opt-in), the anti-legionella cycle can ride free
external heat or shift within a safety window to cheap hours (both
opt-in), and the plan can run circulation pumps on schedule with safety
rails. The tank also learned to speak shower: the **Mixed Hot Water**
sensor translates tank state into litres of 40 °C water and minutes of
shower, and a setpoint advisor sweeps the candidates and prices each.

### A model that checks itself (T4)

The learners got insurance and the forecast got richer. Weekly snapshots
of every learned parameter are captured only when all inputs were healthy
and accuracy was in band; a drift watchdog rolls back automatically when
it can prove the inputs were healthy throughout, and a service/button does
it on demand. Detectors watch for open windows (learning pauses while
one is tripped), immersion-element draw (so resistive heat never poisons
the COP learners or the start counter), and long-term compressor
efficiency drift (with the monthly cost of the shortfall in the repair
issue). The forecast gained humidity (better defrost prediction, ungated
— it only refines an existing input) and snow (opt-in: precipitation
splits rain from snow by temperature, and a roof-snow memory shades solar
gain until melt). Four new gated learners: a capacity envelope that
learns what the machine can actually deliver per outdoor temperature, a
solar aperture scale, an hourly internal-gains profile, and a heat-curve
bias that creeps the ECL110 down while comfort holds and resets the
instant it does not.

### Comfort floors with reasons (T5)

Two gated adjustments move the comfort floor inside the objective through
one optimizer channel. **Confidence margins** raise the floor by the
model's own expected error at each step's lead time — a per-lead-bucket
error statistic the plan earns by filing predictions and being scored on
them — damped by trust and hard-capped, so a trusted model margins
nothing. The **mold guard** computes, per forecast step, the lowest room
temperature that keeps your coldest surface under 80 % relative humidity
(Magnus, closed form, from a measured indoor humidity and your worst
thermal bridge's fRsi), capped at the configured comfort target: heating
past target to fight a ventilation problem is the runaway it refuses.

### The system explains itself (T6)

Every settled interval books its money under the reason the plan drew it,
so the **Plan Narrative** sensor tells the day in sentences ("6.2 kWh in
the cheapest hours for 8.40 kr"), month-end receipts itemise where the
money went with a published reconciliation flag, and the **Optimization
Score** grades envelope, machine and operation 0–100 — the operation
grade replaying each day's kWh against the day's own prices. The
**Compressor Starts** sensor counts realised starts from the meter
(debounced, immersion-blind), prices them against a replacement cost if
you give it one, and can — opt-in — floor the cycling penalty with that
realised wear price. A **Diagnose Last Interval** button explains the
last interval's temperature error input by input, and opt-in price tiles
re-price the plan under a target ±1 °C and a 75 % power cap after each
scheduled solve.

### Hardware, observed before trusted (T7)

If your pump's compressor frequency is exposed as a `number` entity, the
optimizer learns a kW-per-Hz map and the **Compressor Frequency Advisor**
shows what frequency the plan's power would ask for — observation only.
Switch to control (a deliberate, separate step) and it writes the
recommendation: one write per five minutes, clamped to the entity's own
range, with a watchdog that stands control back down to observe if the
reported frequency stops following the commanded one — and a documented
caveat about setpoint-echo registers, with an optional actual-frequency
sensor for real feedback. Plans stay power-denominated in both modes.

### Every new key, and its inert default

| Key | Default | Turning it on means |
|---|---|---|
| `grid_fee_mode` | `none` | Grid transfer fees ride every priced kWh |
| `grid_fee_rules` / `grid_fee_entity` / `grid_fee_fixed` | empty / unset / 0.0 | Where the fee comes from |
| `peak_tariff_months` / `peak_tariff_hours` | empty | Mask the capacity tariff to billed periods |
| `peak_tariff_weekdays_only` | off | …and to weekdays |
| `peak_tariff_offpeak_factor` | 1.0 | Off-peak peaks billed at a fraction |
| `price_risk_lambda` | 0.0 | Risk premium on prior-guessed prices |
| `contract_fixed_price` | 0.0 | Fixed contract column in the comparison |
| `main_fuse_amperes` / `main_fuse_phases` | 0 / 3 | The house's electrical budget |
| `fuse_guard_enabled` | off | Hard per-step cap at what the fuse leaves |
| `peak_guard_enabled` (+ `peak_guard_margin_kw` 0.5) | off | Live billed-window guard |
| `outage_recovery_enabled` | off | Staggered restart after an outage |
| `dhw_inlet_temp` / `dhw_inlet_seasonal_amplitude` / `dhw_inlet_entity` | 10.0 / 0.0 / unset | Cold-water inlet model or sensor |
| `greywater_recovery_effectiveness` | 0.0 | Drain heat recovery in the energy math |
| `dhw_quantile_targets_enabled` | off | Ready targets sized to learned heavy days |
| `dhw_free_disinfection_enabled` | off | Legionella credit from external heat |
| `dhw_elastic_legionella_enabled` (+ `dhw_legionella_min_interval_days` 5) | off | Price-aware cycle timing in a safety window |
| `shower_flow_lpm` | 8.0 | The Mixed Hot Water sensor's shower maths |
| `vvc_pump_entity` / `vvc_lead_minutes` / `space_circulation_pump_entity` | unset / 20 / unset | Pump scheduling |
| `open_window_relax_enabled` | off | Floor relaxes 1 °C while a window is open |
| `immersion_feedback_enabled` | off | Immersion detector may act, not just report |
| `precip_type_enabled` | off | Rain/snow split by temperature |
| `snow_roof_factor_enabled` | off | Roof-snow memory shades solar gain |
| `capacity_curve_enabled` | off | Learned capacity envelope caps plans |
| `solar_aperture_learning_enabled` | off | Learned solar aperture scale |
| `internal_gains_learning_enabled` | off | Learned hourly internal-gains profile |
| `curve_learning_enabled` | off | Heat-curve bias creep (ECL110) |
| `confidence_margins_enabled` | off | Floor rises by the model's expected error |
| `mold_guard_enabled` (+ `indoor_humidity_entity`, `thermal_bridge_frsi` 0.75) | off / unset | Per-step mold-safe floor |
| `compressor_replacement_cost` / `compressor_rated_starts` | 0.0 / 100000 | Wear price per realised start |
| `wear_autotune_enabled` | off | Realised wear floors the cycling penalty |
| `price_tiles_enabled` | off | What-if tiles after each scheduled solve |
| `compressor_freq_entity` / `compressor_freq_sensor` | unset | Observe stage: learn and recommend only |
| `freq_control_mode` | `observe` | `control` writes the frequency, with rails |

### Upgrading

Install, restart, done. **No store migrations are required** — every
persisted store (learned parameters, accuracy history, the ledger,
snapshots) gained only additive keys, loaded with corruption barriers, so
pre-4.0 state is read as-is and missing keys mean inert defaults. New
sensors appear (56 sensors, 4 binary sensors, 4 buttons); nothing you
configured changes behaviour until you visit the options flow and say so.

## v3.16.0

### Draw your plumbing, and the model follows

The Setup page gained an editor. Toggle *Edit layout*, drag the boxes where
you like, drag a pipe from one box's port to another, click a pipe to
remove it — and the diagram tells you, live, which supported layout your
drawing is. A drawing that matches one can be saved; the model then runs
exactly that layout's physics. A drawing that matches none says so in
plain words: which supported layout is closest, and which pipes differ.

Free-form plumbing is deliberately impossible. The editor snaps to a
**catalog of supported layouts** — no valve; one tank behind a valve; two
tanks on a 4-way valve; valve on the radiators with the slab fed direct —
and only the layout's *name* is stored, never a raw graph, so the drawing
can never again claim physics the model does not run. The catalog also
knows the slab-shunt layout exists; it says so, and refuses to select it
until physics for it is written. The same catalog drives the drawing
itself: every pipe on the Setup page is now derived from it.

New in the same stroke: **valve on the radiators, slab fed direct** is a
modelled layout. It is exactly what the pre-v3.14.1 diagram used to show —
and some houses genuinely have it. If yours does, select it: the slab then
drinks raw tank water in the model, with no weather-curve cap, while the
radiators stay behind the valve. (Choosing *one tank behind a valve* on a
two-tank system is also honored — it is the off switch for the two-tank
model.)

Box positions are saved too, cosmetically. Everything goes through one
validated service (`apply_topology`), which refuses a layout your
configuration cannot honor and explains what is missing. No stored layout
means the derived default — every existing install is byte-identical.

### Fixed

- The editor's connection ports were nearly untappable (about two pixels
  at card scale, measured in a real browser) and a drag begun a frame
  after a re-render could grab the box instead of the port. Ports carry a
  large invisible hit target now, and a gesture that claims empty canvas
  at a port's coordinates is re-tested against the live drawing.

## v3.15.1

### Hot water refilled through the wood tank

Some two-tank installations refill the hot water tank through a coil
immersed in the wood buffer tank, so cold mains water arrives preheated
whenever that tank is hot. A new option on the learning page — *Hot water
refilled through the wood tank*, off by default — tells the model about
that plumbing.

With it on, every hot-water draw costs less electricity while the wood
tank is warm: the refill water enters at the coil's outlet temperature
instead of at mains temperature, the electric side only covers the
remaining rise, and exactly the difference is drawn out of the modelled
wood tank — the reduction and the coil heat are one identity, so energy
is conserved by construction. A 70 °C wood tank against a 55 °C hot-water
setpoint covers about two thirds of each draw. The savings baseline gets
the identical coil (the plumbing is not optimizer cleverness), evaluated
generously in the baseline's favour, so reported savings err low.

The coil only acts when the wood tank is modelled as its own store
(v3.15.0): it needs a real tank temperature to compute a preheat from. No
probe, or a stale one, and everything behaves exactly as before. The
Setup diagram draws the coil as its own pipe from the wood tank to the
hot water tank, with a caption on the tank it preheats.

Coil effectiveness is a deliberately conservative constant (half the
tank-to-mains temperature difference) — a generous value would promise
free hot water a mediocre coil cannot deliver, and the failure directions
are not symmetric.

## v3.15.0

### Two tanks, modelled as two tanks

If your wood furnace charges its own buffer tank beside the heat-pump tank
— with a 4-way valve blending the two into the house — the model now
simulates exactly that (issue #40). Activated automatically when a two-zone
house has a mixing valve and the wood tank's top probe is configured;
otherwise nothing changes, byte for byte.

What the split fixes, measured on v3.14.1 (the numbers that motivated it):
a burn used to raise the *modelled* heat-pump tank temperature, dragging
the modelled COP down by up to **0.52 at the worst step** (+24 % phantom
electricity when a fire overlapped cheap-hour charging) and falsely
consuming the tank's safe-temperature headroom — on smaller tanks the
hard-cap loop refused up to 15 kWh of real charging because the *wood* had
filled the modelled tank.

With the two-tank model, on the same synthetic burn day at winter prices:

- The plan buys **15 % less heat-pump electricity** (41.3 vs 48.4 kWh) at
  slightly better comfort — the wood tank's stored heat is finally planned
  around instead of half-lost inside a blended abstraction.
- **Storage works during burns again.** The old model charged its buffer to
  only 41 °C on a burn day (the fire had "filled" the modelled tank); the
  new one charges to 62 °C at a winter price spread and does not bother at
  flat prices — buying concentrated in cheap hours exactly when a spread
  exists, which is the behavioural signature of genuine storage.
- A burn causes **zero refused heat and zero cap tightening** while the
  heat-pump tank is below its own ceiling.

The valve in the model draws **wood-first while the wood side is usable**
(the ESBE behaviour), shifting to the heat-pump tank as the wood depletes,
and its blend law is algebraically identical to the fraction the
valve-outlet sensor measures — one law for model and measurement, so they
cannot drift apart. Wood heat left at the end of the day now counts in the
savings settlement and the storage battery view (up to 95 °C). The plan and
card show the planned wood-tank temperature alongside the buffer's.

The Setup diagram follows the physics, as v3.14.1 promised it always
should: two tanks side by side feeding one 4-way valve, no more phantom
"wood mixing valve" box, and the *"modelled as heat into the heat-pump
tank"* caption disappears exactly where it stopped being true (it stays
for wood setups without the probe, which keep the old abstraction).

Guardrails, because free heat is dangerous to promise: the model activates
only from a real probe reading and falls back to the old behaviour the
moment the probe goes stale; a tank too cold to meet the flow temperature
is never drawn on (verified byte-identical plans against a no-wood
configuration); and per-step energy conservation across both tanks is
asserted to fourteen decimal places in the test suite.

## v3.14.1

### The setup diagram stops contradicting your plumbing

Testing v3.14.0's Setup page against a real two-tank installation (issue
#40) showed the drawn topology disagreeing with the physical system — and
the investigation split the error in two.

**The house side was purely a drawing bug, and is fixed.** The model already
does what the real system does: the mixing valve produces one flow
temperature and feeds *both* floors in parallel. The card drew the valve
feeding the upper floor only, with the tank running straight to the slab —
a different system that nobody's model was simulating. The valve (or the
tank, where no valve exists) now feeds both floor boxes.

**The wood side is model-deep, and is *labelled* rather than hidden.** The
drawing was faithful: the model really does fold wood-furnace heat into the
heat-pump buffer tank as if the two tanks were one. Until v3.15.0 replaces
that abstraction with a real two-tank model, the wood box carries the
caption *"modelled as heat into the heat-pump tank"* — on the card and in
the config-flow overview — so the picture admits what the physics does.

What the single-tank abstraction costs on a real two-tank system was
measured on a synthetic winter burn day (9 kW fire for 4 h, two-zone house,
500 L buffer behind a throttling valve, identical electrical schedule in
both arms so only the COP coupling differs). The numbers motivate v3.15.0:

- A fire overlapping the plan's cheap-hour charging drags the modelled COP
  down by **0.23 on average and 0.52 at the worst step** — the model
  believed 1.02 where the isolated reference says 1.53, a 33 %
  understatement — booking **2.8 kWh (+24 %) of phantom electricity** over
  the burn and the six hours after it.
- The same fire in the evening, when nothing is charging, distorts
  **nothing at all**, and at flat prices the distortion measures 0.0 %.
  The coupling is price-independent physics whose *exposure* is
  price-driven: only a price spread makes the plan charge the tank hot
  enough for the false penalty to engage — so it strikes exactly the
  behaviour storage exists for.
- The planned bill barely moves, but the plan's shape does: with the
  modelled COP collapsed, the plan switched the pump off during *cheap*
  early-morning hours and ended the day slightly colder.
- The false `buffer_max_temp` headroom consumption is real and, in
  isolation runs, 100 % attributable to the wood heat. It does not bind at
  500 L with a 9 kW fire, but a 200 L tank with a 12 kW fire has
  **4.7 kWh of heat-pump charging refused** and the hard-cap loop
  tightening power ceilings because the *wood* filled the modelled tank
  (15.4 kWh at 15 kW).
- Neither distortion exists without a throttling mixing valve, and the
  isolated figures are upper bounds — a real wood tank also carries part
  of the emitter load.

(A plan-level cost delta was measured too, but its flat-price null control
came back dirty — multi-start solver noise, not physics — so per this
repo's measurement discipline it is not quoted.)

### Fixed

- Setup-page captions longer than their box overflowed it (the no-valve
  buffer caption ran past its border by 19 viewBox units, measured in a real
  browser). Long captions now wrap inside the box.

## v3.14.0

### A commanded valve can now wait for the peak

If your mixing valve is set to *Commanded by the optimizer*, the plan can do
something a hand-set valve physically cannot: **hold stored heat back**.

A fixed valve starts feeding the house the moment the tank is warmer than its
curve, so heat bought cheaply mostly gets used in the hours right after it was
bought — which is why storage has been worth less than the theory suggested.
The optimizer now works out a *schedule* for the valve: lower its target
between charging and the expensive hours, so the house coasts on what the
building itself holds and the tank keeps its heat, then raise it again for the
peak so the tank carries the house through it.

Worth roughly **1–2 SEK a day** on a winter price curve on top of what storage
already saves — and, importantly, comfort gets slightly *better* rather than
worse, because the plan stops dumping heat into an already-warm house.

Two things it deliberately will not do. At flat prices it does not schedule
anything at all, because there is nothing to gain. And it never plans the
house below your comfort floor to hold heat back: the lowest target it will
ask for is the floor the optimizer already plans against.

The schedule is not a rule of thumb applied blindly. The optimizer works one
out, re-plans the whole day against it, and keeps it only if that day comes
out cheaper on the same measure it uses for every other decision. If it does
not, the schedule is discarded.

### Click a sensor on the card to assign it

The Setup page added in v3.12.0 was read-only. Now clicking any sensor on the
diagram — including an empty slot — opens a picker and assigns it, or clears
it. The picker only offers entities that make sense for that slot, so a switch
cannot end up where a temperature sensor belongs.

This does exactly what the options pages do, and reloads the integration the
same way; it is simply reachable from the picture of your system rather than
eleven pages of settings. Assignments are made through a new
`heatpump_optimizer.assign_entity` service, which validates every call, so an
automation can use it too.

### Fixed

Outdoor humidity was read from the first entry of the weather forecast rather
than the entry covering the current time. On a stale or offset forecast that
could be hours out of date, which slightly mis-aimed the defrost derate.

## v3.13.0

### Economy mode finally is one

Until now, *economy* ran exactly the same plan as *auto* — verified to
thirteen decimal places. It now does what its description has always
promised: the plan may let the house drift up to **1.5 °C below your comfort
floor** to ride out expensive hours, never below 15 °C. Measured savings:
about **25 % on a typical winter day**, 19 % on a narrow-spread day, and only
4.5 % at flat prices — the right shape for a mode that trades comfort for
money. The mode also survives restarts and options changes now (it used to
quietly revert to auto), and the optimizer switch no longer stomps a live
economy or comfort selection when something toggles it on again.

### The optimizer can command a smart valve

*Commanded by the optimizer* is a new mixing-valve mode: point it at the
number or climate entity your valve's controller exposes, and the integration
writes its recommended target there after each planning cycle — the same
number the Valve Target Recommendation sensor shows, sent only when it
actually changes. No more copying the recommendation across by hand, and a
changed comfort band reaches the valve on its own.

### Honest savings when the day ends warm

The reported savings settlement charged the plan for ending the day with less
stored heat than a thermostat would have, but paid nothing for ending with
*more*. The result understated your savings precisely when the plan chose to
end the window warm — by 8 % on a shoulder day and up to 62 % at flat prices.
It is symmetric now. This changes only the reported numbers; not a single
plan is different.

### Small fixes and speed

- A tiny buffer tank (a 10 L separator) could be simulated discharging to
  **−8 °C** — heat it never had. Delivery is now bounded by the energy the
  tank actually holds; realistic tank sizes are unchanged to the last digit.
- A hot-path property recomputed a constant a few million times per solve;
  planning with a mixing valve is now roughly a quarter faster.
- The planned buffer-tank temperature is now part of the optimization result,
  and four golden scenarios pin the mixing-valve behaviour that four releases
  of storage work had no recorded coverage for.

## v3.12.0

### A picture of your system, in two places

The integration now shows you what it believes your system *is* — house,
zones, tanks, valves, furnace, and every sensor at its physical place.

**On the card**, the enlarged view gains a second page: next to the plan, a
**Setup** tab draws the configured system as a diagram, with each sensor's
live reading shown where the sensor sits — tank temperatures on their tanks,
zone temperatures in their zones, the valve outlet on the valve. This is the
diagnostic view the integration has lacked: until now those numbers were
spread across 47 sensor entities with no picture of how they relate.

**In the options**, a new first entry — *Your system, as configured* — shows
the same description as a read-only overview, so a mis-assigned sensor ("no,
my hot water sensor is on the wrong tank") is visible at a glance rather than
found by reading eleven pages of settings.

Both views are drawn from one description, emitted in one place, so they can
never disagree about what the system looks like. And both show **empty slots
as empty, on purpose**: a sensor this setup could use and does not have is
exactly what the picture exists to reveal. A diagram that silently omits an
unconfigured sensor merely looks complete.

Clicking the diagram to assign entities is deliberately left for later, as
the backlog records: the read-only view carries most of the value, and it
should earn its place first.

## v3.11.0

### The wood furnace becomes a number, not a boolean

If you have a wood furnace on its own buffer tank with an automatic mixing
valve, three optional sensors now let the optimizer treat a fire as what it
is: a partial, measurable, fading source of free heat.

**The valve outlet sensor is the step change.** It is the only sensor that
measures what the house actually receives, and together with the two tank
temperatures it identifies the mixing fraction directly — "the furnace is
covering 70 % of the heating right now". Electric space heating then stands
down by exactly that much. Until now a detected fire only ever suppressed
discretionary hot water; space heating carried on paying as if the fire did
not exist. Measured on a typical winter day, knowing about an evening fire is
worth about **4 SEK/day** on its own.

**The wood tank's top and bottom probes replace a guess with a measurement.**
The fixed keep-assuming-the-fire window assumed every fire is good for about
another 90 minutes. The pair measures it: a hot top over a cold bottom means
the charge is nearly spent, and both the free-heat promise and the
suppression end there.

**The promise of free heat is deliberately hard to earn.** A wrongly promised
burn is a cold house in winter, so the forecast is bounded three independent
ways: never further than two hours ahead whatever the decay setting says,
fading over that window, and never more energy than the wood tank measurably
holds. It is zero unless a fire is actually burning or fading — when you
*will* light one is your business and is never predicted — zero when any
needed sensor is missing or has gone stale (a stalled hot probe would
otherwise look like an indefinite free fire), and zero when the wood side is
too close to the heat-pump side to tell the mix apart. Measurement may argue
for trusting a fire less, never for trusting it more.

The savings figure stays honest: the reference thermostat is granted the same
free heat, so a burn is never booked as optimizer savings.

All three sensors and the wood tank volume are optional, on the
"Self-learning and diagnostics" page. Without them nothing changes at all —
every golden scenario is byte-for-byte identical with the feature off.

## v3.10.0

### The buffer tank finally charges

If you have a mixing valve and a real buffer tank, the optimizer now does what
the storage feature has promised since v3.7.0: it buys heat in the cheap hours,
stores it in the tank, and coasts the expensive ones. Measured against a tank
too cold to coast for free, it fills the entire cheap night block, lifts the
tank deliberately, and buys nothing at all through both the morning and the
evening price peaks — and at flat prices it correctly does none of this,
because with no spread there is nothing to gain.

**What was wrong.** The model discharged the tank as if the valve were fully
open: the emitters saw raw tank water, so a 40–45 °C tank dumped 22–26 kW into
the house and anything stored was gone within half an hour of the pump
stopping. Every plan ended with the same empty tank no matter what it did, so
storing heat could never look worthwhile. The valve is now modelled as what it
physically is — a flow-temperature regulator on a weather-compensation curve.
It mixes return water into the flow, the house receives what it needs at the
curve temperature, and stored heat lasts hours instead of minutes: a 60 °C
tank now carries the house on its own for about six hours at −5 °C.

This also confirms the setting recommendation: the valve capped at the top of
your comfort band, exactly as the options page has advised since v3.7.0.

**What it is worth.** On this release's backtest fixture (750 L, a cold
start, winter weather), storage is worth on the order of **5 SEK/day on a
typical winter price curve and 17 SEK/day on an extreme one**, beyond every
measurement artefact — the flat-price control is subtracted, so only value a
price spread can produce is counted. That is real money, but smaller than the
theoretical sizing table suggested, and the reason is honest physics: a fixed
valve cannot *hold* its charge for the evening peak. The tank starts feeding
the house the moment it is warmer than the curve, so it mostly shifts the
hours right after charging. Squeezing out the rest is what a commandable
valve (`smart_write`, still to come) would be for.

### The tank's ceiling is now a promise, not a suggestion

The optimizer can no longer plan to push the tank past its maximum
temperature, even when electricity is effectively free. Previously the model
quietly discarded heat charged into a full tank — harmless in simulation,
a boiled tank in reality. Plans that try are now re-solved with those steps'
power capped to what the tank can actually accept.

### Small tanks stop pretending to be stores

The default 35 L buffer holds less than one planning step of heat. Below
100 L the tank keeps its physics — valve delivery, standing loss, the
temperature cap — but the planner no longer credits it as storage, so it
cannot plan around charge that could never meaningfully exist.

### A new diagnostic sensor: Valve Target Recommendation

What to set a hand-adjusted valve to, with the reasoning in the attributes —
including when nearly-flat prices mean storing is not worth much today.
Appears only when a mixing valve mode is configured.

Nothing in this release changes any behaviour unless a mixing valve mode is
set: all 37 golden scenarios are byte-for-byte unchanged with the feature off.

## v3.9.0

Two things the planner was quietly charging you for, and neither was ever
something you asked for.

### Your comfort band is what the plan owes you

You give the optimizer a temperature *range* — 17 to 23 °C by default — and
a target inside it. The target was being treated as far more binding than it
reads: the plan would spend real money keeping the house near 21 °C even when
your band gave it four degrees of room and the house was never close to being
too cold.

Measured on a cold January day, that preference cost 18 % of the bill — 28.55
SEK against 23.28 — to hold the house 0.32 °C warmer on average. The band was
never in danger either way.

The pull towards the target is now half as strong, which is the point where
the saving stops improving and a genuine preference for your setpoint still
survives. The band itself is unchanged and is still defended exactly as
before: the plan will not take your house below your minimum to save money.

**What you will see.** Slightly more savings and a slightly cooler house. At
the default comfort weight, a cold winter day now averages 19.4 °C and saves
53 %, where before it averaged 19.8 °C and saved 51 %.

| Comfort weight | Average room temp | Savings |
|---|---|---|
| 5 (default) | 19.4 °C | 53% |
| 10 | 19.8 °C | 51% |
| 20 | 20.2 °C | 49% |
| 40 | 20.4 °C | 47% |

If you preferred the old behaviour, raise **Comfort weight** on the Savings vs
comfort page — one step up, from 5 to 10, reproduces it almost exactly.

### A term that discouraged change for its own sake is gone

The planner has always avoided switching the pump on and off more than
necessary. It did so through a term with no units — not money, not starts,
just a number that penalised change. That term was expensive: removing it cuts
about 9 % from the electricity cost across the full set of test scenarios,
while the total number of compressor starts rises about 5 %.

The obvious follow-up was to move that job to the **Compressor cycling cost**
setting, which is denominated in kronor per start-stop cycle and so can be
weighed against electricity honestly. That was tried and rejected on the
measurement: sweeping it from 0 to 0.20 SEK per cycle moved the cycling charge
itself by at most 0.5 SEK, but moved the electricity cost by up to 2.2 SEK —
and not even in a consistent direction, with 0.10 producing *fewer* starts
than 0.05 on the same day. At those sizes the setting does not steer the plan
so much as jostle the solver into a different solution, so shipping a non-zero
default would have been churn dressed up as tuning.

It therefore stays at zero and opt-in, exactly as before. If your unit is one
you want to protect from short cycling, set it — and now it is the only thing
doing that job, rather than competing with a hidden term.

**Being straight about the limits.** These two changes pull in opposite
directions on the same dial, and the net effect on your bill depends on your
prices and your house. The comfort change is the larger of the two.

## v3.8.0

This is an audit release. The whole codebase — the planning economics, the
thermal physics, the self-learning model and the timekeeping — was reviewed
end to end, every finding was verified against the code and against
simulation before being touched, and everything that survived verification is
fixed here. There are no new features. What there is instead is a planner
whose numbers you can trust further than before, and several long-standing
errors that were quietly costing money or comfort.

Some of the figures you are used to will change, and each case is explained
below. The full technical record is in `docs/audit-2026-08.md` in the
repository, with one commit per finding on the audit branch.

### Fixed: a sliver of solar surplus made whole hours look free

If you have solar panels configured, the planner priced any step with *any*
forecast surplus — even 50 W of winter sun — as though the entire step cost
only your export compensation. A full compressor draw in a barely-sunny
quarter-hour looked nearly free, so plans piled consumption into exactly the
wrong steps, and the cost figures were priced on the same fiction.

Consuming is now priced the way your meter prices it: energy up to the
forecast surplus costs the export compensation you give up, and everything
beyond it costs the import price. That applies in the planning itself, in how
hot water picks its hours (a genuinely sunny midday can now win a slot over a
merely cheap night), and in every reported cost. A live production sensor, if
you have configured one, is now actually used for the current step.

### Your savings are now measured against your own schedule

The savings figure compares the plan against a conventional thermostat. That
thermostat used to hold your daytime temperature around the clock, even if
you have a night setback configured — so whatever your setback was worth was
silently mixed into the "savings".

The reference now follows the same day and night schedule you gave the
optimizer. Expect the percentage to change. In winter it often goes *up*:
a conventional setback thermostat recovers at full power straight into the
morning price peak, and dodging that peak is genuine value the old
comparison hid. Either way, the number now answers the question you actually
have — what does the optimizer save compared to a normal thermostat running
my schedule.

### Windy forecasts no longer panic the plan

The default wind sensitivity claimed a 10 m/s wind raises your heat loss by
150 %. Only the draught-driven share of a house's loss responds to wind at
all; measured studies put that wind at roughly +20–40 % for typical houses.
Every windy forecast therefore over-bought heat, and the self-learning model
spent weeks slowly compensating for it.

The default is now 3 % per m/s, and the README gains a table for choosing a
value by how tight and how exposed your house is. If you ever saved the
thermal options page, the old 0.15 is stored in your configuration — it is
worth lowering it to about 0.03 yourself.

### Fixed: radiator-heated houses were modelled as nearly unheatable

The building presets gave a radiator house the thermal properties of a
floor-heating loop: all the heat was routed through a huge, sluggish store
that could barely pass it on, as though your radiators were a concrete slab
with the circulation of a teacup. The model compensated in strange ways, and
the plan inherited them. A radiator circuit is now modelled as what it is —
a small, well-coupled loop — and the building's heavy structure contributes
to coasting instead of blocking delivery.

Separately, a floor-heated lower floor had its heavy mass counted twice, so
plans coasted on stored heat the building does not have.

Presets only apply when you run the building step, so an existing setup keeps
its old numbers: if your house is radiator-heated, or two-zone with a heated
floor downstairs, re-running the building preset in the options is worth
doing.

### The self-learning model stops drifting on sensor noise

Several of the passive learners had asymmetries that turned pure sensor noise
into slow, one-way drift — the heat-loss estimate ratcheted upward by about
20 % over two simulated months on noise alone. All of them now treat both
sides of a measurement equally. Alongside that: the learned efficiency
correction now survives a restart instead of silently resetting to the
nameplate figure, frost losses and efficiency losses are no longer both
blamed for the same shortfall, and the hot-water usage pattern no longer
mistakes the tank's ordinary standby cooling for someone showering at 3 am.

### Prices, weather and the capacity tariff now follow the clock

Data was matched to the plan by list position, which assumed everything was
fresh and hourly. If a price fetch had been failing since yesterday, the
whole plan silently ran on yesterday's prices; a weather forecast fetched two
hours ago read the entire day two hours out of phase; and Tibber's 15-minute
prices would each have been stretched to a full hour. Everything now aligns
by its own timestamps — which also makes the integration ready for
quarter-hourly pricing.

The capacity tariff's metering windows now sit on your grid company's clock
rather than the plan's. A one-hour burst that the meter bills inside a single
window was previously split across two and half-forgiven, which under-priced
exactly the plans a capacity tariff exists to discourage.

### Hot water plans are deliverable, and pinned steps are honoured

Steps you force off in a pinned plan now reach the hot-water planners as
constraints, so the energy they displace is re-bought in the hours that
remain instead of silently vanishing from the tank. Schedules no longer
contain trickle steps below the power the pump can actually run at. And the
safety check that releases a pin rather than let the tank or the house go
cold now watches the whole day, not only the first hours.

### Away mode plans with the house it actually has

The time-to-warm estimate used a fixed rate; it is now a real simulation of
your house recovering at full power, so returning to a warm home is planned
with your building's actual sluggishness. Presence sensors that report the
"wrong way round" (occupancy-style devices) are read correctly, and the
setback now also lowers the temperature the plan aims for, not just the
comfort floor.

### Smaller fixes worth knowing about

- The daily cost and savings sensors are now valid long-term statistics in
  Home Assistant (they were silently rejected before).
- The mixing-valve options page no longer resurrects a cleared valve entity,
  and with no target set the valve now defaults to the top of your comfort
  band — the setting that actually lets a tank charge.
- An over-hot buffer tank no longer has its extra heat deleted by the
  temperature cap in a single step.
- The "Optimize now" button visibly disables while a solve is running.
- Dragging a slot on the card no longer pops the slot dialog when you let
  go, and the dialog's text no longer shrinks after re-renders.
- Service calls from automations are validated with real bounds and real
  error messages.
- The external-heat detector was blind at 60-minute update intervals; it now
  scales its sampling window with your update interval.
- The two-zone floor-area split you configure is now actually used (it was
  silently fixed at 50/50).
- The "Heat pump thermostat" option is gone. It was collected and translated
  and never read; nothing you configured there ever did anything.

### Why the buffer tank still does not charge — answered

The open question from v3.7.1 is answered, and the answer is recorded in the
backlog. Half of it is fixed in this release: with no valve target configured
the model chased a target that receded as the house warmed, so surplus never
diverted to the tank. The decisive half remains and is now precisely
understood: the model lets stored heat *leave* the tank far faster than the
house can accept it, so every plan ends with the same empty tank and charging
looks pointless to the solver. The fix is designed and written up in the
backlog; it is the next piece of the storage work rather than part of an
audit release.

**Being straight about what changed under you.** Plans will differ from
v3.7.1 — that is the point of most of the fixes above. If a number surprises
you, `docs/audit-2026-08.md` names the change that moved it and the reasoning
behind it.

## v3.7.1

### Fixed: heat left in the buffer tank was treated as worthless

If you have a mixing valve configured, the planner now understands that heat
sitting in your buffer tank is heat you do not have to buy again.

It did not before, in two separate ways. The tank's stored heat was measured
against the ceiling used for the concrete slab — around 28 °C, because a slab any
hotter than that would overheat the house. A tank does not work that way: it is
insulated, and the valve decides how much of it reaches the rooms. Judged against
the slab's ceiling, a tank at 70 °C counted for no more than one at 45 °C, so
filling it appeared to achieve nothing at all.

Separately, the tank was left out of the end-of-day accounting entirely, so a
plan that ran it down to nothing looked as good as one that left it full.

Both are fixed, and the effect is visible: plans now leave the tank meaningfully
warmer at the end of the day rather than draining it, which is heat carried into
tomorrow instead of bought again.

**Being straight about the limits.** This does not yet make the planner
deliberately fill the tank during cheap hours. It has stopped treating a full
tank as worthless, which was a prerequisite, but something still prevents it
choosing to charge — that is being investigated. Nothing changes at all unless
you have a mixing valve configured.

## v3.7.0

If you have a mixing valve, the optimizer can now use your buffer tank as a
store — charging it when electricity is cheap and drawing it down when it is
expensive.

### Why a valve is what makes this possible

Until now the model assumed everything the heat pump produced went straight to
your radiators and floor loops. For a system without a mixing valve that is
exactly right, and it stays the default.

But it also means the buffer tank could never fill: whatever went in came
straight back out, so the tank only ever cooled. A mixing valve is precisely the
part that changes this. It limits how much heat reaches the house, and once the
house has what it needs the surplus has nowhere to go but the tank.

Set **Mixing valve and heat storage** in the options to match your system.
Leaving it at *No mixing valve* changes nothing at all.

### Setting a valve you adjust by hand

If your valve is a fixed one you set yourself, the recommendation is to set it to
the **top of your comfort band**, and the reasoning is worth knowing.

A high setting keeps the valve open until the house reaches its ceiling, so the
building itself charges first. That storage is free: the building holds heat at
room temperature, so there is no efficiency penalty. Only once the house is
satisfied does the valve begin to throttle, and only then does the tank take the
surplus — which is stored hot, and does cost efficiency.

Building first, tank second, is the cheap order. Setting the valve low reverses
it, filling the expensive store while the free one sits empty.

One thing you give up: at that setting the valve is no longer what stops your
house overheating. The optimizer's own comfort limits do that instead.

### Storing hot costs efficiency, and the model now knows

A heat pump is less efficient the hotter it has to push water. Charging a tank to
60 °C costs noticeably more per unit of heat than running a floor loop at 35 °C,
and that penalty is the entire economics of storage: it is what decides whether
shifting heat into a cheap hour is actually worth it.

The model now accounts for it, so it will only fill the tank when the price
difference genuinely pays for the loss. On a day with little variation, it will
leave the tank alone.

The tank is also never charged above the maximum you set, however cheap
electricity happens to be.

## v3.6.1

### Fixed: large buffer tanks were modelled as losing far more heat than they do

If you have an accumulator rather than a small buffer, the model believed it
leaked roughly ten times as fast as it really does — and the correction the
integration learns from your own tank sensor was not allowed to find the truth
either.

The standby loss was described as a cooling rate in degrees per hour, and the
same rate was applied at every tank size. But heat escapes through a tank's
*surface*, and a big tank has far less surface for the water it holds. A
750-litre accumulator loses proportionally much less than a 35-litre buffer, so
one rate cannot describe both. Applied to 750 litres, the old number modelled
more heat lost in six hours than the tank can hold.

The loss now follows the tank's size the way the physics does, and the limits
the learning is allowed to move between are derived from how well a tank of that
size could plausibly be insulated. A well-insulated accumulator now sits
comfortably inside that range instead of being pinned several times above it.

The prior itself is also more honest. The old default worked out worse than an
uninsulated bare cylinder, at any size.

**What you will see.** If you have a buffer tank configured, its standing loss
drops and its hours of autonomy rise on the battery view. If you have a *large*
tank the change is substantial. Nothing changes if you never configured one.
A rate you set yourself is still respected.

## v3.6.0

The two-zone model now learns how your heat loss actually splits between the
floors, and a long-standing bias in the existing learner is fixed.

### Learning the split, not just the level

The correction the integration learns from prediction error multiplies *both*
zone losses, so it could move the total but never the balance between the
floors. If your lower floor loses more heat than the configured split assumes,
nothing could ever discover that.

There is now a second learned value that owns the split, fitted from the lower
floor while the existing one is fitted from the upper. Two numbers, two
independent measurements, so neither can quietly absorb the other's error.

It only moves when a **real lower-floor sensor** is configured (added in v3.4.0).
Without one the lower zone is inferred from the floor return water, and that
inference comes from the same sensor as the slab estimate — so there is nothing
independent to learn from. Watch `lower_floor_loss_ratio` and
`lower_floor_loss_samples` on the learning sensor.

Deliberately not learned: the inter-zone transfer coefficient. One pump, one
water temperature and a fixed radiator/floor split mean the two floors move
together and rarely diverge, so a passive fit would mostly track noise. It stays
where you configured it.

### Fixed: the heat loss learner was comparing two different things

On a two-zone system the learner compared the indoor sensor — which is the
*upper* floor — against the model's average of both floors. The difference
between your two floors was therefore being read as heat-loss error.

It is a systematic offset, not noise, so it did not average out: measured
against the real model, floors 1.5 °C apart injected about 0.53 °C into every
sample, more than half the point at which a sample is rejected as implausible.
Houses with a larger difference between floors had their samples thrown away
entirely and learned nothing at all.

The learner now compares the upper floor against the predicted upper floor.
## v3.5.0

A pinned plan now lasts 20 hours from when you apply it, instead of expiring at
midnight.

### Your plan no longer evaporates in the evening

**Apply this plan** used to pin your arrangement until the next midnight. That
made the feature least useful exactly when people reach for it: a plan made at
nine in the evening lasted three hours, and one made at half past eleven barely
survived the click. It now runs for **20 hours from the moment you apply**, and
applying again restarts the clock — so an evening plan carries through the night
and well into the next afternoon.

The chart's editable region follows the same rule, which is the point: the
backend releases every pinned step at or after the expiry, so a slot drawn
beyond it would have been shown as pinned while quietly doing nothing. The two
now read the same number from the same place rather than each keeping a copy.

It is deliberately 20 rather than 24. The optimizer plans 24 hours ahead, so a
full-day override would cover every step it was looking at, and re-applying each
day would leave it nothing left to decide — switching it off while appearing to
leave it on. At 20 there is always a few hours' tail the optimizer still owns.

The expiry is now written with a day when it is not today. Under the midnight
rule "pinned until 08:30" could only mean one thing; with a 20-hour window it
usually means tomorrow, so it says so.

The **Apply for the rest of today** button is now simply **Apply this plan**,
which is what it does.
## v3.4.1

### Fixed: two axis labels ran into each other

In the enlarged chart, with solar irradiance switched on, the electricity price
axis is labelled **SEK/kWh** and the solar axis **W/m²** — and the two ran
through each other, overlapping by about a fifth of the price label.

The space between those two axes is a fixed width, but the text is not: the
enlarged view uses a larger font, and at that size the price label no longer
fits the gap. The label is now measured, and when it will not fit it is placed
on the other side of its own axis line, where there is empty space above the
chart. Nothing moves when there is room, and the solar label never moves at all.

## v3.4.0

Two-zone houses can now tell the optimizer what the lower floor is actually
doing, instead of having it guessed from the floor return water.

### A real lower floor sensor

Two-zone mode plans against two room temperatures, but only the upper one ever
had a sensor. The lower zone was inferred as the floor return temperature plus
half a degree — and that is a *water* temperature standing in for an air
temperature. A floor loop returns at roughly 24–30 °C while the room it serves
sits near 21, so the model believed the lower floor was several degrees warmer
than it really was. Because both zones are judged against the same comfort band,
the lower one looked like it was permanently overshooting, and the optimizer
under-heated the room it could not see.

There was a quieter problem underneath. The slab estimate came from the *same*
sensor, as the return plus one degree, so the gap between slab and room was
always exactly 0.5 K no matter what the sensor read. The main heat path into the
lower zone was therefore stuck at a constant value and could not respond to
anything.

Set **Lower floor temperature sensor** in Step 1, or under Options → Entities,
and both problems go away. It is optional and two-zone only; without it the old
estimate is still used, so nothing changes until you add one. The order of
preference is a real sensor, then the return-temperature estimate, then the
upper floor's reading.

### Fixed

- **The house heat loss learner was silently dead on these houses.** It compares
  the upper sensor against the model's area-weighted average of both zones, so
  the inflated lower zone introduced a structural error of about 3.7 °C — well
  past the 1 °C residual it refuses to learn from. On a two-zone install with a
  floor return sensor it therefore rejected every sample and never learned
  anything, with nothing but a debug log to say so. With a real sensor the
  residual is back in range. If `house_heat_loss_samples` has been stuck near
  zero on your system, this is why.
- A floor return sensor that was configured but had gone stale or unavailable
  used to leave both the slab and the lower floor holding whatever they were
  last set to, with nothing marking them as unfreshened. Both now fall back
  cleanly.
## v3.3.1

### Fixed: the enlarged card could render outside its own edge

On a desktop browser, at some window sizes, everything below the chart — the
delta calculator, the buttons, the schedule editor — was drawn past the bottom
of the dialog's own background instead of inside it. At 1400x700 with a pinned
plan active, the overflow measured 449 pixels.

The dialog's width was derived from a fixed guess that the surrounding chrome
needed 168 pixels of height. That guess was made when the enlarged view was just
a title, a legend and a chart, and it never grew as the editor did. Worse, it
fed back on itself: a shorter window made the dialog *wider*, and the text
around the chart is sized from the dialog's width, so the chrome grew in the
same direction as the overflow.

The guess is gone. The dialog is now bounded by the window, and anything that
does not fit scrolls, so a panel added later costs a scrollbar rather than
spilled content. Your position in the panel is kept when the plan refreshes
underneath you, which happens every few minutes.

The chart still keeps its exact proportions rather than being squeezed to fit —
squeezing it would stretch every axis label sideways.

Phones were never affected and are unchanged: the narrow-window path never
consulted the faulty budget.

## v3.3.0

The schedule editor gained a hot water minimum, and the plan chart can be panned
and zoomed.

### A home for the temperatures

The comfort slider used to sit on its own in the middle of a section about
scheduling, with nothing around it to say what it was. It now shares a
**Temperatures** section with a second slider, **minimum hot water** — the lowest
the tank may fall to inside a demand window. Both are priced the same way as the
rest of the editor, so the cost of asking for warmer water is visible before you
save it, and **Save as my schedule** stores them along with your heating hours.

The hot water minimum is capped a few degrees below your hot water setpoint. A
minimum equal to the setpoint would leave the tank no band to work in and the
pump would short-cycle against its own hysteresis. The cap follows the setpoint
if you change it, and a stored value above the cap is lowered with a note on
screen rather than quietly corrected.

The same limit is enforced in `apply_schedule`, which now accepts
`dhw_min_temperature`, because an automation can call the service directly. It is
checked per heat pump, before anything is written, so a call covering two heat
pumps either applies to both or fails whole. This matters more than it sounds:
the solver treats tank limits as *soft* penalties, so an impossible minimum is
not refused downstream — the plan would simply sit in permanent slight violation,
which is close to undiagnosable from the outside.

### Panning and zooming the plan

Pinch to zoom, hold Ctrl and scroll, swipe sideways to pan, or drag the chart
background. There are buttons too, for touch and for the keyboard. A plain scroll
still scrolls the dashboard — a chart that swallowed the wheel would trap the
page under the pointer.

It only goes forward. Plan forecasts are deliberately kept out of the recorder,
so there is no history to scroll back into; the window stays between now and the
end of the plan, and zooming out stops where the plan does instead of showing
empty chart. Zooming moves the axis the slot lanes are drawn against rather than
just their appearance, so dragging a slot still lands on the time under your
pointer at any zoom level.

### Fixed

- A plan attribute the integration published as "unknown" was read by the card as
  a real measurement of zero, because `Number(null)` is `0` and zero is a finite
  number. This could show a 0 °C comfort target, and would have capped the new
  hot water slider at nothing.
- Dragging the chart to pan no longer opens the enlarged view when the drag ends.
  A click that never moved still opens it.

## v3.2.0

You can now rearrange today's plan by hand, and the optimizer will work around
you.

### Rearranging slots on the card

The enlarged card draws today's plan a second time as two editable lanes, hot
water above heating. Drag a block to move it, drag an edge to stretch it, and
right-click a lane to add a slot or remove the one under the pointer. A running
total at the bottom prices your arrangement against the plan in force, in the
currency Home Assistant is configured for, and updates as you drag — so the cost
of moving the tank reheat out of the evening peak is visible before you commit
to it.

**Apply this plan** pins the arrangement until midnight. The optimizer keeps
re-solving every few minutes as prices and weather move, but it now has to
schedule around your slots rather than through them. **Back to automatic**
releases it, and the pins are persisted, so they survive a restart.

The past is shaded and locked, because it cannot be rescheduled, and so is
anything beyond tonight's midnight, because the override does not outlive the
day it was made.

Until now the card could show you the plan and simulate a different *comfort
setting*, but the plan's shape was not yours to touch. If you knew something the
optimizer did not — a guest arriving, a bath at four, a car to charge — there
was no way to say so.

### Timing is yours; safety is not

Applying a plan does not promise every slot runs exactly as drawn, and the card
says so rather than pretending otherwise. If your arrangement would let the tank
fall below its minimum, miss a legionella cycle, or take the house under its
comfort floor, the integration releases just the slots it has to, re-solves, and
names them in the banner and in the `manual_override` sensor attribute.

This matters more than it might look. Comfort and tank limits are *penalties* in
the objective, not hard constraints, so pinning heating off does not make the
solver find another way — it makes it accept a cold house. Every release is
therefore followed by a fresh solve, and if a channel still cannot be made safe
after several rounds its forced-off pins are abandoned wholesale and the channel
is planned freely. Only the breaching channel is given up; an arrangement that
was never unsafe is kept, so an impossible hot water request cannot quietly
discard your heating plan and let the pump run in the hours you excluded.

### New services

* `heatpump_optimizer.apply_manual_plan` — pin `space_slots` and/or `dhw_slots`
  until `expires_at` (default: next local midnight). A channel you omit stays
  automatic; an explicit `[]` means "off until this expires". Returns the
  applied plan and how many horizon steps it pinned.
* `heatpump_optimizer.clear_manual_plan` — drop the override and re-solve.

Both plan sensors gain a `manual_override` attribute describing the active plan,
its expiry, and any slots released for safety.

### Fixes

* An `expires_at` without a timezone — exactly what the service UI's free-text
  field produces — crashed with an opaque `TypeError` instead of being handled.
* The applied-step counts were measured in hourly price entries against a
  15-minute horizon, so they covered only a quarter of the day and reported zero
  for an evening plan that had in fact applied perfectly well.
* A corrupt or hand-edited stored plan could raise during setup rather than
  simply being discarded.
* The card's chart lookup matched the header's expand-button icon instead of the
  chart itself, which mis-measured the plot area used for hit-testing.
* An untouched slot draft no longer goes stale when a new plan is published: the
  lanes follow the refresh, while an edit in progress survives it.

## v3.1.2

Three real bugs behind the symptoms reported against v3.1.0 and v3.1.1.

### Chart labels no longer overlap in the enlarged view

The enlarged chart labelled the time axis every hour. Over a 48-hour horizon
that puts labels about 15 units apart in a chart whose labels are 40 units
wide, so they simply ran into each other. Label spacing is now worked out from
the room available and the width of the labels themselves, which also fixes
12-hour locales, where `12:00 AM` is over half again as wide as `13:00`.

### The comfort slider showed an unrelated thermostat's setpoint

The what-if panel picked the first `climate.*` entity it found and used its
target temperature. In a home with more than one thermostat that is an
arbitrary choice, and a valve sitting on frost protection made the slider open
at 5 °C. It now reads the comfort temperature from the optimizer's own plan,
as the heating-hour and hot-water fields already did.

### An old copy of the card could silently keep running

If a second copy of the card was installed — usually a leftover manual install
under `/local/` — it claimed the custom element first, and every later version
loaded and did nothing at all. There was no error and no clue: upgrades simply
appeared to have no effect, and the schedule editor added in v3.0.0 stayed
invisible. Now:

- a duplicate registration logs a clear console error naming both versions and
  where to remove the extra resource;
- Home Assistant warns in the log when it finds another resource pointing at a
  different copy of the card;
- the card is served without long-lived cache headers, so a browser cannot hold
  an old copy after an upgrade. This matters most in YAML dashboard mode, where
  the integration cannot refresh the resource's cache-busting query itself.

If you are affected, check Settings → Dashboards → Resources and keep only the
entry under `/heatpump_optimizer_static/`.

## v3.1.1

Fixes for three things v3.1.0 got wrong or left hidden.

### The schedule editor is now visible without extra configuration

The editor added in v3.1.0 was gated behind `what_if: true` in the card's YAML,
off by default and documented as a comfort-temperature slider. Several people
looked for it and concluded it did not exist.

It is now shown by default. The reasoning that made it opt-in does not hold:
holding a draft costs nothing, because the draft lives in the card. Only
**Simulate these slots** runs a solve, and only **Save as my schedule** changes
any configuration. `what_if: false` still hides the panel.

### Chart labels no longer overlap

v3.1.0 tried to make chart text render at a constant pixel size by converting a
pixel target through the chart's measured width. That was the wrong model. The
chart's whole geometry — the 92-unit left margin, the 34-unit bottom margin, the
tick spacing, the legend rows — is authored in the same coordinate units as the
font, against a font of about 10. Converting for pixel size pushed it to about
20 units in a typical dashboard column, so labels ran into each other.

The font is part of that geometry and is fixed again. Nothing is lost: the chart
is stretched from a fixed coordinate system, so its text already grew roughly
3.5× when the card was enlarged. That was never the part that failed to scale.

### The enlarged view's chrome scales without side effects

The header, legend, tooltip and editor are plain HTML and do need help scaling.
v3.1.0 did that with container query units, which required
`container-type: inline-size` on the dialog — and that also applies inline-axis
containment, a large and easily-missed side effect for a font size.

The dialog's font size is now set directly from its measured width, clamped so a
phone-width dialog stays legible and a very wide one does not turn the legend
into a headline. Everything in the chrome is in `em`, so one value sizes all of
it. The dialog's width comes from the viewport rather than its contents, so this
cannot feed back into a resize loop.

### Not fixed: creating a helper from an entity picker

Creating an `input_datetime` helper from the away page's picker can still fail
with `required key not provided @ data['name']`. This is in Home Assistant's own
helper dialog rather than in this integration — the create request is sent with
no name, and `input_datetime` requires one. Until it is fixed upstream, create
the helper from **Settings → Devices & services → Helpers** and then select it
in the away page.

## v3.1.0

Edit your schedule from the card, and two fixes in the configuration pages.

### Change the schedule from the card, not just simulate it

The what-if panel could already move the heating day and the hot water windows
and tell you what the change would cost — but there was no way to keep the
answer. You had to read the number, close the card, and retype the same
schedule in the options pages.

The panel now has a **Save as my schedule** button next to **Simulate these
slots**, backed by a new `heatpump_optimizer.apply_schedule` service. Saving
writes the schedule into your configuration and reloads the integration, so the
next plan is made against it.

Because saving replaces what the house actually runs on, it asks first: the
button turns into *Confirm: overwrite my schedule* and only saves on a second
press. Editing anything in between disarms it, so you cannot confirm one
schedule and save another, and an armed confirmation lapses after a few seconds
rather than sitting waiting for a stray click. Windows are validated before they
are stored, so a malformed schedule is refused at the button instead of failing
on every later reload.

The README now says how to reach the panel: it lives in the enlarged card and
needs `what_if: true`, which was documented only as a comfort-temperature
slider and was easy to miss.

### Chart text no longer changes size when you enlarge the card

The chart is drawn in a fixed coordinate system and stretched to fit its
container, so text sized in those coordinates renders at whatever pixel size the
stretch happens to produce — around 5 px in a narrow card and around 30 px in a
full-width dialog. Enlarging the card did not scale the text so much as distort
it, and the surrounding labels, legend and tooltip did not follow at all,
because they are ordinary HTML sized against the card's own font.

Both halves now aim at a pixel size instead of a coordinate size. The chart
measures its own width and converts the target back through it, clamped so a
pathologically narrow or wide chart still produces readable text. The HTML
chrome uses container-query units so it tracks the dialog's width, with the
previous fixed sizes kept as a fallback for browsers without them.

### Fixes

* **The capacity tariff window could not be submitted.** Choosing *1 hour* on
  the grid page failed with `expected str`. The dropdown's options are strings
  but its default was the number `60`, and leaving the already-selected option
  untouched submits that default — so the one option most people want was the
  one that could not be saved.
* **Creating a helper from an entity picker failed.** Adding a return-time
  helper from the away page failed with
  `required key not provided @ data['name']`. The pickers declared their domains
  using Home Assistant's legacy top-level `domain` key; the frontend reads only
  the newer `filter` key when it works out which helper type to create, so it
  had no type to create and submitted the new helper without a name. All entity
  pickers now use `filter`, which also restores domain filtering in the picker
  itself.

Both failures were invisible to the test suite because its Home Assistant stub
accepted any value a selector was given. The stub now enforces the same rule the
real one does, and the suite renders every options page and submits it back
untouched — the cheapest thing a user can do, and the case that broke.

## v3.0.0

The three releases developed since v2.6.1 — v2.7.0, v2.8.0 and v2.9.0 —
collected into one major release. Everything below is included.

The theme across all three is the same. The optimizer used to reason about a
*model* of the house and a *plan* for the heat pump, with almost no way to find
out whether either was true, and no way for a user to see why it had decided
anything. Most of what follows closes those two gaps.

Upgrading is safe: every new capability is off or neutral by default, and an
existing config entry migrates without a behaviour change.

---

## Added

### Knowing when an input has gone bad

- **An input staleness watchdog.** Every sensor read was guarded against
  `unavailable` and `unknown` — the visible failures, which every call site
  already handled. The dangerous failure is a sensor that stops updating while
  still reporting its last value. A dead battery in a tank probe or a dropped
  Zigbee room sensor leaves a perfectly valid-looking constant in the state
  machine indefinitely.

  The optimizer then plans against a fiction, but the worse consequence is that
  the learners observe a flatline, attribute it to thermal behaviour, and
  persist a corrupted parameter that survives a restart. Over-age values are
  now treated as *missing*, learning freezes rather than training on them, and
  a new **Input Problem** binary sensor names which inputs are stale and why
  the learners paused. Limits are per input: a room temperature may reasonably
  be minutes old, an outdoor forecast hours.

- **An optional measured power entity**, plus whole-house power and a
  cumulative energy meter. `CONF_HEAT_PUMP_MAX_POWER` is a nameplate limit and
  "Recommended Power" is what the optimizer is *commanding*; neither is a
  measurement. With a real meter, COP becomes observable rather than assumed —
  and since every plan is priced through COP, an error there was an error in
  every cost reported. New **Measured Power** and **Observed COP** sensors.
  Watts, kilowatts and megawatts are all accepted and normalised; an
  unrecognised unit is refused rather than guessed, because a wrongly scaled
  power value is worse than none.

- **Closed-loop accuracy reporting.** Predicted versus realised temperature,
  power and cost are recorded per interval and published on a **Prediction
  Accuracy** sensor. The *signed* bias is published alongside the magnitude,
  because a mean absolute error cannot distinguish random noise from a model
  that is consistently half a degree optimistic — and it is the second that
  indicates drift.

### Costs the optimizer could not previously see

- **Capacity (effekt) tariff awareness.** Swedish and increasingly Nordic DSOs
  bill a monthly capacity charge, typically the mean of the three highest
  hourly peaks. Nothing modelled this, so the optimizer would happily stack hot
  water and space heating into the same cheap hour — and one new monthly peak
  can easily cost more than the energy that stacking saved.

  The penalty is soft rather than a hard cap, so it trades off against comfort
  like everything else, and it charges only for exceeding the peak *already
  billed this month*: if the month has a 9 kW peak, an 8 kW hour is free, and
  modelling it as "keep power low" would give away savings for nothing. A
  **Monthly Peak Power** sensor shows the billed peak and the free headroom.

- **PV self-consumption.** For a house with solar, heating hot water or the
  buffer from surplus beats exporting it. While the array is in surplus, an
  extra kWh does not cost the import price — it costs the export compensation
  foregone. Substituting that marginal price is all that is needed: the
  hot-water LP, the space-heating objective and the savings settle-up all keep
  working unchanged.

- **Compressor cycling cost.** An optional per-start cost, expressed as a
  smooth term on the step-to-step power difference. That keeps the problem
  continuous; a true minimum-runtime constraint would make it a MILP, which is
  not affordable inside a Home Assistant update cycle. It defaults to **zero**,
  because the measurement came first: realistic plans make two to four starts a
  day, so most installs have nothing to fix and should not pay savings for
  smoothness they do not need. The planned start count is published so the
  decision can be made from evidence.

- **The unknown price horizon is modelled instead of repeated.** Prices past
  the published horizon were filled with a flat repeat of the last known value.
  Nord Pool and Tibber publish tomorrow around 13:00, so before then a large
  part of the horizon was a constant — and a flat tail has no trough, so the
  optimizer could not see a cheap period worth waiting for and systematically
  under-deferred load in the morning.

  A normalised diurnal shape is now learned from the prices actually seen,
  split weekday/weekend, and scaled to the recent price level. It never
  displaces real data, it is heavily damped until several days have been
  observed, and the plan marks which steps rest on it — the dashboard card
  shades that stretch.

### Understanding the house

- **Building type presets.** The thermal page asked for `house_thermal_mass` in
  kWh/°C, which no homeowner knows, and the shipped defaults quietly encoded
  one specific house. Every other building started from a wrong prior, and the
  learners then spent weeks walking away from it. Three answerable questions —
  what the house is built from, roughly when, and what the heat comes out of —
  now derive the physics, scaled by heated floor area. Presets set *starting
  values only*, which is stated in the UI, and the numeric path remains for
  anyone with a real energy declaration.

- **Active system identification.** Every learner was passive: each waited for
  the house to happen to do something informative, which is why parameters took
  weeks and why the guard thresholds had to be so conservative. Opt-in, the
  optimizer will now run a deliberate step change on a mild, cheap night and
  fit the response. Comfort is a hard constraint on the experiment rather than
  a cost term: it aborts if the room drifts past the allowed excursion, and it
  will not repeat on a house that has already converged.

- **A learned defrost and cold-humid derate.** Air-source units lose real
  capacity between roughly 0 and +5 °C in humid air, which is precisely the
  Swedish shoulder season and precisely where the plan is most aggressive about
  coasting. Plans made there quietly under-delivered. The derate is *learned*
  per temperature and humidity bucket from the closed-loop accuracy signal, not
  taken from a datasheet, because between-unit spread is larger than the effect
  being modelled. With no evidence it is exactly 1.0.

- **Revealed-preference comfort tuning.** `comfort_weight` is the most
  consequential number in the configuration and the least knowable; it has no
  intuitive units. But users reveal the answer constantly — every manual
  override says the plan went too far in one direction. Opt-in, the value is
  now nudged from that evidence, slowly, only on consistent signals, and with a
  quiet-period signal so it can come *down* as well as up. The learned value
  has its own sensor and a reset button, because an invisible self-adjusting
  objective would be alarming.

### Reacting to the world

- **External heat source detection.** A wood furnace tied into the same buffer
  heats the tanks for free, and burning electricity to heat water that is
  already being heated is the single most expensive mistake available.
  Detection is inferred from sensors that already exist: a tank warming while
  the compressor is off, or warming faster than the compressor could manage. An
  explicit stove or flue entity overrides the inference.

  The detector is deliberately reluctant, because the costs are asymmetric:
  wrongly believing a fire is lit means skipping a cheap-hours charge and
  either paying peak prices later or running out of hot water, while missing
  one costs a single unnecessary charge. So it needs consecutive
  confirmations, and a decay window keeps it from flapping as a fire dies down.
  While active, discretionary electric hot water is suppressed — but only while
  coasting still meets the requirement — and the learners freeze with the
  reason recorded.

- **Away and holiday mode.** A week away is the largest single saving a heating
  system can offer. What makes this more than an `input_number` is the *return
  time*: knowing when the house must be comfortable again lets the recovery
  heat be bought in the cheapest hours beforehand instead of panic-heating on
  arrival. Away state can come from a person, device tracker, calendar or plain
  toggle — the polarity differs by domain and is handled for you. Recovery
  starts deliberately early, because a wrong return time is a comfort failure
  the user will notice.

### Seeing what it is doing

- **Plan reason codes.** The plan sensors published which slots were chosen but
  never why. A slot could be cheapest-price, deadline-driven, legionella,
  terminal-value or a comfort floor, and nothing distinguished them — so an
  unexpected slot was indistinguishable from a bug. Every step now carries a
  reason code, carried through to the sensor attributes and shown in the card's
  tooltip.

- **Energy dashboard and long-term cost statistics.** Every monetary sensor was
  `MEASUREMENT`, so none of it reached Home Assistant's Energy dashboard and
  there was no long-term cost history. The integration's central claim — that
  it saves money — was invisible in the one place users look for exactly that.
  There are now `TOTAL_INCREASING` energy and cost accumulators, split hot water
  versus space heating. The split is apportioned from the planned power split
  and says so in its attributes, because one meter cannot separate two circuits
  and pretending otherwise would be worse.

- **The house published as a virtual battery.** State of charge, usable
  capacity, charge and discharge rates and round-trip efficiency, so other Home
  Assistant energy automations can reason about the heat pump alongside a real
  battery. State of charge is measured against the comfort band, since energy
  below the minimum acceptable temperature is not actually available.
  Round-trip efficiency is reported in thermal terms; an electrical figure
  would exceed 100% because charging happens at COP > 1.

- **Buttons**: force an optimization run, arm the identification experiment,
  and reset the learned comfort weight. Buttons rather than switches, because
  these are momentary actions with no lasting state; a toggle would have to
  bounce itself back and until it did the UI would imply a state that does not
  exist. The run button goes unavailable while a solve is in flight, so a
  control that appears to do nothing for several seconds does not invite
  repeated presses.

### Solar forecasting

- **Solar irradiance can come from Open-Meteo.** Solar gain was only as good as
  the irradiance behind it, and most weather integrations never publish a
  `solar_irradiance` field, so for many installs the term silently evaluated to
  zero and the optimizer could not anticipate a sunny afternoon. Set *Solar
  forecast source* to Open-Meteo and pick the location on the map. No API key
  or account is needed.

  Two endpoints are used because they do different jobs: the forecast API
  supplies the planning horizon at 15-minute resolution, matching the
  optimizer's grid exactly, while the satellite archive supplies *observed*
  current irradiance so the house heat-loss learner trains against what
  actually happened. Open-Meteo timestamps mark the **end** of the averaging
  interval — verified against sunrise and sunset rather than assumed, since
  reading them as starts shifts all solar gain by one interval, which at dawn
  and dusk is the difference between darkness and full sun.

- **A Solar Irradiance sensor** exposes the current value, with the full
  horizon and source diagnostics in its attributes.

### Dashboard card

- **Clicking the card opens a large version of the chart.** A card in a
  dashboard column is too small to read a 48-hour plan comfortably. Clicking
  anywhere, or the expand button, opens the same chart in a modal that labels
  the time axis every hour instead of every third. It is a native `<dialog>`
  shown with `showModal()`, so it renders in the browser's top layer and cannot
  be clipped by a dashboard column or hidden behind another card.

- **A solar irradiance series**, discovered by the same `plan_kind` marker the
  plan sensors use rather than by a hardcoded entity id — that exact mistake
  caused the v2.6.1 bug where the card never found its sensors. W/m² is a
  fourth unit and both plot edges were already occupied, so it gets an inner
  right-hand axis that only appears when the series is on.

- **Reason codes in the tooltip**, and the estimated-price stretch of the
  horizon shaded and labelled.

- **A what-if simulator** in the expanded view, off by default. Drag the
  comfort temperature, edit the heating hours, and add, remove or retime the
  hot water demand windows — then see what each would cost per month. It
  reports the comfort consequence next to the money, because a plan is always
  cheaper if it is allowed to be colder or to let the tank run down, and a
  simulator showing only the saving would invite exactly that mistake. It runs
  against a *copy* of the configuration, so an exploratory drag never disturbs
  operation, and it is debounced in the card and rate-limited in the
  integration.

---

## Fixed

Most of these were found by tests written to check a mechanism rather than an
outcome. Every one produced output that looked entirely plausible.

- **The capacity tariff raised the peak it was supposed to lower.** The charge
  was the marginal price times the single largest excess. That is wrong twice:
  it under-states a bill that averages the month's top few peaks, so a plan
  with several high hours — exactly what the tariff exists to discourage — was
  charged as if it had one; and `max` has zero gradient everywhere except at
  that one window, so a gradient-based solver saw the term at 1 step in 96 and
  it was effectively inert. It is now the marginal price times the sum of the
  top-k excesses, which is algebraically identical to the bill and gives every
  one of those windows a gradient.

- **On a fresh install the capacity tariff dwarfed the entire energy cost.**
  With no peaks yet recorded the threshold was zero, so every kilowatt counted
  as a brand-new monthly peak — a normal 6 kW day was charged around nine times
  its own energy cost, which would have contorted the plan to avoid a peak the
  house sets on any ordinary day regardless. The threshold now measures against
  what has actually been observed, and the charge stays off until there is
  something real to compare against.

- **The hot water planners could push the tank past its rating.** The
  minimum-run rounding, which raises a sub-minimum slot to a power the hardware
  can really deliver, overshot a 20 litre tank by 28 °C; and with negative
  prices the cost term rewards consumption, so the linearised planner pushed
  through its own temperature ceiling. A capacity clamp now runs after the
  economics, because the tank's rating is physics rather than a preference.

- **System identification fitted the wrong quantity.** The step-response fit
  regressed the room's energy balance against *electrical* draw rather than
  thermal output. Both identified parameters came out scaled by the COP while
  their ratio — the time constant — stayed correct, which is exactly the kind
  of error that looks entirely plausible.

- **The COP learner erased its own learning.** `cop_scale` multiplies the
  nameplate curve, but the modelled COP it was compared against already had the
  current scale folded in, so the update used a *relative* correction as an
  *absolute* target. That makes 1.0 the only fixed point: a sample that
  perfectly confirmed the model still dragged the learned value back towards
  "trust the nameplate".

- **Space-only power was compared against a whole-pump meter.** The current
  action carries space heating in `power` and hot water in `dhw_power`, but an
  electricity meter sees only their sum. Three places compared the space figure
  alone against the measured total, so an ordinary planned hot-water charge
  looked like the pump drawing power nobody asked for — registering as an
  external heat source (freezing every learner and suppressing hot water for
  the decay window), as a collapsed COP, and as a defrost derate, all at once.

- **The defrost derate's humidity dimension was never applied.** The learner
  recorded observations against the real humidity, but every lookup fell back
  to a default that landed in the dry bucket. Everything observed in humid
  frosting conditions — the conditions the feature exists for — was written
  down and then never used.

- **A heated basement's thermal mass was inflated by 25%.** The foundation
  adjustment was applied twice to the lower floor's slow store, in the branch
  used by the most common Swedish two-zone layout.

- **A naive datetime could crash the update loop.** `dt_util.now()` returns a
  timezone-aware value, and comparing it against a naive one raises.

- **The chart tooltip is now anchored to its own chart** rather than to the
  card, so it positions correctly in the expanded view.

- **`strings.json` had drifted from the translations**, so several settings
  showed raw keys instead of labels. All three files are now generated from one
  source and their keys are asserted equal by a test.

- **The what-if debounce timer survived card removal**, firing a multi-second
  solve into a detached DOM after the user had navigated away.

---

## Refactored

The backlog's precondition for this work was a characterization harness, on the
grounds that the existing tests assert on outcomes and would not catch a change
that quietly shifts a plan by one interval or drops a constraint in a rare
branch. That harness was built first, and every change below was made with its
diffs empty.

| | before | after |
|---|---|---|
| `_optimize_with_dhw` / `_optimize_space_only` | 514 / 345 lines | 362 / 175 |
| duplication between them | 162 lines in 17 runs | 37 lines |
| `coordinator.__init__` | 254 lines | 41 |
| `_build_data_dict` | 235 lines | composed from domain views |
| `ThermalParameters.from_config` | 196 lines | a table |
| `config_flow.py` | 1,932 lines | 1,417 |

The optimizer duplication had already caused a real bug — enabling hot water
silently changed the space-heating objective — so the shared cost terms are now
shared in fact. Two eighteen-parameter signatures became one `_Horizon`
context, so adding a per-solve input is one edit instead of four. The config
mapping is a table with a test that probes every declared field for a config
key that actually reaches it, since a forgotten row silently ignores a user's
setting forever.

---

## Tests

- **`tests/golden.py`** records the complete output of 37 scenarios — every
  schedule, trajectory, setpoint, cost, reason code and option-flow field — and
  diffs byte for byte. Its sensitivity is demonstrated rather than assumed:
  shifting a fixture by one interval makes it fail and say so.
- **`tests/stress.py`** sweeps 48 combinations of season, building archetype,
  zoning and feature flags, plus 17 edge conditions, checking physical,
  economic and comfort invariants. It found three of the bugs above. Its
  comfort check compares against what running flat out would achieve, because
  an undersized pump in a leaky house cannot hold the floor and calling that a
  planning bug would be blaming the optimizer for physics.
- **`tests/rolling.py`** drives the real re-planning cycle for several
  simulated days against a plant deliberately mismatched from the model — the
  only test that exercises the self-learning heat-loss correction against a
  house that genuinely differs from its model. Given a 35% error it recovers
  99% of it within two simulated days, converges rather than oscillating, and
  leaves an already-correct model alone. Opt-in via `SLOW=1`.
- **`tests/features.py`** and **`tests/entities.py`** drive the feature modules
  and every entity directly, catching failures that produce no error anywhere:
  a platform registered in one list but not the other, an options menu row with
  no handler, a translation file drifting from `strings.json`, an accumulator
  declared `MEASUREMENT` and therefore invisible to the Energy dashboard.
- The Home Assistant stub is version-controlled in `tests/hastub/` instead of
  living in `/tmp` and vanishing on reboot, and the card's DOM stub now
  *parses* `innerHTML` — storing it as a string was silently skipping every
  path where the card wires up its own controls.
- The README's comfort-weight table and entity counts are asserted, so the
  documentation cannot drift from the code unnoticed. Both had.

---

## Notes

**Attribution.** This project is a fork of
[strutsfarm/heatpump_optimizer](https://github.com/strutsfarm/heatpump_optimizer)
at v2.2.0. The MPC formulation, two-zone thermal model, Tibber and weather
integration, config flow and ECL110 control path are originally strutsfarm's
work, and the upstream copyright is now recorded in `LICENSE`. The README
carries a full acknowledgement and a disclaimer: no warranty, no
responsibility or liability of any kind for any effect, behaviour, function,
failure or damage arising from use of the software, plus specific notes on
safety, legionella, savings claims, equipment responsibility and third-party
services.

**Two things deliberately left alone.** Adjacent comfort weights can invert on
cost by around a percent, because the objective is non-convex and two nearby
settings can land in different basins; neither a third multi-start solve nor a
polishing pass closed the gap, and both cost 25–30% more time. The user-facing
contract — the README's published table of what comfort weight buys — holds
exactly and is tested. Separately, the coordinator's private attribute names
were left as they are: grouping forty of them into dataclasses is a large
mechanical diff across 3,700 lines for no functional gain, and the readability
was obtained by splitting the constructor instead.

## v2.6.1

### Fixed
- **The dashboard card showed "No plan data available yet" on a stock install.**
  The plan sensors use `has_entity_name`, so Home Assistant prefixes them with
  the device name and the real ids are
  `sensor.heat_pump_optimizer_space_heating_plan` /
  `sensor.heat_pump_optimizer_dhw_heating_plan`. The card defaulted to the
  unprefixed ids, which never exist, so a default configuration could not work.
- **The card no longer depends on entity ids being stable.** The plan sensors
  publish a `plan_kind` attribute (`space` / `dhw`) and the card discovers them
  by that marker when the configured id is absent, so renaming an entity no
  longer breaks it. A name-suffix match keeps older setups working.
- **Upgrades kept serving the cached old card.** The Lovelace resource is
  registered with a `?v=<version>` cache-buster, but the existing-resource check
  matched on the base URL only and left the stale query in place, so browsers
  reused the previously cached JavaScript after every upgrade. The resource is
  now updated in place when the version changes.
- **The empty-state message is now actionable.** Instead of naming two entities
  it was only guessing at, the card reports per circuit whether the entity was
  not found, is unavailable, has no forecast yet, or has data outside the
  selected window.

## v2.6.0

### Summary
Follow-up to the hot water rework in 2.5.0. Space heating gets the same
scrutiny, the two circuits are now planned against each other instead of one
after the other, three invented cost terms that were distorting the objective
are gone, and the model learns two more of its own parameters. There are also
two new sensors that publish the full heating plan and a dashboard card that
charts it.

### Changed
- **Hot water and space heating are now co-optimized.** They share one
  compressor, so the old sequential decomposition — plan hot water first, then
  give space heating whatever capacity is left — let hot water fill the cheapest
  hours to the ceiling and push space heating into dearer ones. Measured on the
  winter scenarios that displaced 2.6 kWh (typical) to 4.7 kWh (extreme prices)
  of space heating out of the cheap block. The hot water LP now carries a
  congestion premium: taking capacity in a contended step is charged the extra
  cost of buying the displaced space heating at the cheapest price within a
  6 hour window instead. Because the displacement is piecewise-linear in hot
  water power this stays an exact linear program. A second pass then re-plans
  hot water against the space heating profile that resulted, and adopts it only
  if it scores strictly better on the same objective. Contended steps drop from
  22 to 4 and winter cost falls about 0.6%.

- **Three heuristic cost terms have been removed from the space heating
  objective.** `solar_anticipation_cost` and `pre_heat_incentive` were invented
  currency layered on top of physics the simulation already models: the
  trajectory itself shows that heating before sunshine is wasted and that
  coasting into a windy night is expensive, because solar gain and the weather
  heat loss factors are applied to the real dynamics. Restating that as an extra
  cost double-counted it, and `pre_heat_incentive` was worse than redundant — it
  was a *negative* cost, effectively paying the plan to burn electricity.
  `pre_heat_incentive` also existed only on the no-hot-water code path, so
  simply enabling hot water silently changed the space heating objective.
  Removing them cuts cost 1.1% (mild windy winter) and 4.3-5.6% (shoulder
  season) with no change in comfort. The anticipatory weighting still shapes the
  solver's initial guess, where being wrong costs nothing; it no longer
  discounts real minimum-temperature breaches.

- **The comfort floor is now enforced with an exact penalty.** A purely
  quadratic undershoot penalty has vanishing gradient at the boundary, so the
  solver would park a few hundredths of a degree below the configured minimum
  where the electricity saved outweighed the penalty. A small linear term
  restores a non-zero slope at the bound. Residual violations across the
  validation scenarios go to zero.

- **The solver starts from several candidate schedules instead of one.** The
  space heating objective is not convex, and from a single starting guess the
  two-zone model settled on schedules that random perturbation could beat by
  around 3%. Candidates are scored on the objective first, which is cheap, and
  only the two most promising are actually optimized, so this costs roughly one
  extra solve. Two-zone winter cost falls 2.2%.

- **Buffer tank standby loss is stated as a cooling rate.** Like the hot water
  tank in 2.5.0 it is now expressed in °C/h at a reference temperature
  difference and the UA value is derived from it, which is what makes it
  observable and therefore learnable. The default reproduces the previous fixed
  coefficient.

### Added
- **Self-learning buffer tank cooling rate.** If you point the new *Buffer tank
  temperature sensor* option at a sensor, the integration estimates the tank's
  standby loss from quiet decay, using the same lower-envelope estimator as the
  hot water tank: every contaminating effect can only make a tank look leakier
  than it is, so the estimate drops quickly towards a quieter reading and only
  creeps upward.

- **Self-learning house heat transfer.** The configured heat loss coefficient is
  a nameplate estimate; what the optimizer needs is how fast *your* house loses
  heat. Each update replays the interval that just elapsed through the same
  model the optimizer uses, with the power that was actually applied, and
  attributes the difference between predicted and measured indoor temperature to
  the heat loss coefficient. Everything the model already accounts for — slab
  transfer, solar gain, internal gains, wind, rain — is therefore excluded, and
  a Newton step on the remaining residual gives the correction directly. Unlike
  the tanks the bias here is two-sided, so this uses a symmetric slow average
  rather than a lower envelope, plus a per-interval rate limit and a residual
  cutoff so an open window or a wood stove cannot run away with the model. It
  is learned as a dimensionless scale, which also handles the two-zone case
  where a single indoor sensor cannot identify the two floors separately.

- **Two plan sensors: `Space Heating Plan` and `DHW Heating Plan`.** Each
  publishes the contiguous heating slots the optimizer intends to run, with
  start, end, duration, energy, average price and cost, plus a step-by-step
  `forecast` covering the whole horizon. The existing schedule attributes are
  truncated to 24 steps, which at the default 15 minute resolution is only the
  first six hours; these sensors carry the full 24 hours. The bulky series are
  declared unrecorded so they do not bloat the recorder database.

- **A dashboard card.** `custom:heatpump-optimizer-card` plots electricity
  price, planned hot water slots, planned space heating slots, outdoor
  temperature, predicted tank temperature and predicted house temperature on one
  shared time axis, with per-series legend toggles that persist across reloads.
  It is hand-written inline SVG with no external chart dependency, and the
  integration registers it automatically. See `docs/dashboard-card.md`.

## v2.5.0

### Summary
Hot water is now planned as what it actually is — a battery. Previously the
tank was only heated shortly before the water was needed, which meant a
17:00–22:00 demand window was largely paid for at 17:00–22:00 prices. The
planner can now buy hot water at *any* hour of the horizon and store it, and it
learns how quickly your particular tank loses that stored heat instead of
assuming it. In the validation scenarios hot water costs 10–15% less, uses less
energy, and the tank runs slightly warmer at its lowest point.

### Changed
- **Hot water is scheduled by a minimum-cost plan over the full horizon.** The
  old planner walked forward, found the first moment the tank would fall short,
  and bought the missing energy from the cheapest *preceding* hours — subject to
  a hard cap of at most 18 hours of lead time, and to a headroom rule that let a
  single already-scheduled slot block every cheaper slot before it. In practice
  that pinned heating to the demand windows themselves. The tank is a linear
  store, so the whole schedule is now solved as one linear program: heat
  delivered `k` steps early still contributes `(1 - UA·Δt/C)^k / C` degrees when
  it is needed, and minimising `Σ price·energy/COP` under the availability
  floors and the tank ceiling gives the genuinely cheapest feasible plan. That
  decay factor *is* the standby loss, so pre-heating is priced correctly by
  construction and the artificial lead-time cap has been removed entirely.
  Heating now lands in the cheap night block and holds, rather than running
  through the evening peak.

  The previous cheapest-first planner is still there, seeded with that solution,
  as a repair pass: it re-simulates with the true non-linear tank (temperature
  dependent COP, cold-water floor) and tops up any residual shortfall. If the
  solve is unavailable for any reason it takes over completely, so the
  integration cannot lose hot water to a solver failure.

### Added
- **The tank's standby loss is learned instead of assumed.** How far ahead
  pre-heating pays off depends entirely on how well the tank holds heat, so it
  is now measured. The parameter has been restated in terms you can actually
  check — **°C lost per hour at 45 °C tank temperature in a 20 °C room**,
  defaulting to 0.3 °C/h — and is converted to a heat loss coefficient using
  your tank volume. The previous fixed coefficient implied 0.36–0.65 °C/h
  depending on tank size, i.e. a leakier tank than most, which made the
  optimizer needlessly reluctant to store heat.

  Whenever the tank temperature is sampled across an interval in which the heat
  pump did not run, the decay itself gives the answer:
  `UA/C = -ln((T_end - T_ambient)/(T_start - T_ambient)) / Δt`. Water drawn
  during the interval can only make the tank look leakier than it is, never
  tighter, so readings are folded in as a lower envelope — the estimate moves
  quickly towards a quieter observation and only creeps upward. One unnoticed
  shower therefore cannot convince the model that the tank is badly insulated,
  while a genuinely deteriorating tank is still learned within days. Samples
  shorter than 15 minutes or longer than 6 hours, and tanks within 5 °C of room
  temperature, are ignored; the result is clamped to 0.05–3.0 °C/h and survives
  restarts.

- **Tank cooling rate is configurable.** It appears in the DHW step of both the
  setup and options flows, and as `dhw_cooling_rate` on the
  `set_thermal_parameters` service. Setting it explicitly resets the learned
  estimate to your value.

- **New attributes on the DHW sensors.** `dhw_cooling_rate`,
  `dhw_cooling_rate_learned`, `dhw_cooling_samples`, `dhw_hold_hours` and
  `dhw_preheat_hours` show what the model believes about your tank and how far
  ahead it is willing to plan.

### Upgrading
No action required. Existing installations pick up the 0.3 °C/h default and
start refining it from the next quiet period onwards; the value only affects
*when* hot water is heated, never whether it is available.

## v2.4.1

### Summary
A QA pass against a real Home Assistant instance found two ways an ordinary
weather forecast could quietly ruin a day's heating plan, plus a handful of
smaller defects. If your house has been running warmer and more expensively
than the savings figures suggested, this release is likely the reason why.

### Fixed
- **Wind speed is no longer guessed from its magnitude.** The forecast wind was
  assumed to be km/h whenever it exceeded 30, and m/s otherwise. Home Assistant
  hands the forecast over in whichever unit you have configured, so an ordinary
  20 km/h breeze fell under that threshold and was used as 20 m/s, a severe
  storm. For anyone whose units are km/h that inflated the predicted heat loss
  2.17x, the scheduled energy by 128% and the predicted cost by 211%. The
  correction applied above the threshold was the km/h factor, so it was wrong
  for mph as well. The unit is now read from the weather entity, and m/s, km/h,
  mph and knots all produce the same plan.

- **A single missing value in the forecast no longer disables the optimizer.**
  Weather integrations are allowed to report a field as empty. An empty wind
  speed raised an error that was caught and discarded, so the integration went
  on looking perfectly healthy while silently never producing a plan again. An
  empty temperature was worse: it spread through the prediction until most of
  the 24-hour trajectory was invalid, the solver gave up, and the savings
  sensors either disappeared at startup or froze at their last value while
  logging an error every cycle. Unusable values now fall back to a sane default.

- **Missing electricity prices are reported instead of invented.** When prices
  could not be fetched, a flat 0.5 SEK/kWh curve was substituted and the
  optimizer still published a savings figure that no price data supported. It
  now says so in the log and skips the run, leaving the cost sensors unknown.

- **The hot water slab thermal mass could not be set.** The `slab_thermal_mass`
  field of the `set_thermal_parameters` service was documented and accepted but
  silently did nothing.

- **The target temperature on the thermostat card is yours again.** It used to
  show the optimizer's own setpoint for the current 15-minute step, so the card
  drifted away from whatever you had just dialled in, and your change was lost
  on the next reload. The card now shows and remembers your target; the
  optimizer's current setpoint is available as the "Optimal Setpoint" sensor and
  as an `optimizer_setpoint` attribute.

- **The current price sensor records history again.** It declared itself a
  monetary sensor while reporting a continuous measurement, a combination Home
  Assistant rejects, so it warned on every startup and stored no statistics.

- **Turning the optimizer off no longer reports an unknown preset**, and the
  three platforms no longer disagree about the device's model and version. The
  device now reports the real version from the manifest.

## v2.4.0

### Summary
Two things: the options flow is now a proper menu where every setting,
including the sensor entities, can be changed after setup and every field is
explained in plain language. And the optimizer got substantially cheaper to
run, because the term that pulls the house toward the target temperature was
drowning out the electricity price.

### Changed
- **The comfort pull is now measured against the range you allow.** The
  pull-to-target penalty was a fixed quadratic, which at a typical winter
  setting was roughly 2.4x the entire electricity bill for the day. The
  optimizer therefore behaved like an ordinary thermostat and the minimum
  temperature you configured had almost no effect. It is now scaled by the gap
  between your target and your minimum, so widening that range genuinely buys
  cheaper operation and narrowing it holds the setpoint tighter. Winter savings
  went from ~35% to ~45% in a single-zone house and from ~15% to ~36% in a
  two-zone house.

  If you prefer the previous, warmer behaviour, raise "How strictly to hold the
  temperature". Around 5 lets the house use the full range you allow, 10 keeps
  it noticeably closer to target, and 20 or more behaves much like a thermostat.

- **Reconfiguration is now a menu.** Instead of one long form, the options flow
  opens on a menu with separate pages for sensors, comfort, hot water, the
  building, tuning and the heat curve. Editing one page leaves the others
  untouched.

### Added
- **Sensor entities can be changed after setup.** Indoor and outdoor
  temperature, solar radiance, wind, precipitation, power and energy meters and
  the Tibber token can all be re-pointed from the options flow. Previously they
  were fixed at initial setup. Clearing a field now genuinely clears it.
- **Every setting is explained.** All options pages and all setup steps have
  friendly labels and a per-field description, in English and Swedish, instead
  of raw parameter names.
- **A terminal cost on the planning horizon.** Nothing beyond the horizon was
  scored, so the optimizer reliably dumped the last couple of hours of every
  plan: it coasted the house down because the resulting cold never appeared in
  the objective. End-of-horizon shortfall is now priced using the same
  reference the savings settle-up uses, so the plan and the reported savings
  agree.

### Fixed
- **Two-zone houses were applying the comfort weight twice.** The penalty
  summed both zones, so a two-zone house behaved as if the setting were double
  what was configured. It hugged the setpoint and gave up most of the available
  savings, and used 22% of its energy in the most expensive quarter of the day
  against 3% now. The penalty is averaged across zones, so the setting means
  the same thing in both modes.
- **Savings could be reported as strongly negative in summer.** The settle-up
  charged the optimizer for ending *less* overheated than the baseline: in July
  both end up well above target from solar gain, and stored heat above what is
  actually useful was still being valued. Stored heat is now capped at what the
  comfort target and hot water requirement genuinely call for, and only real
  shortfalls are charged.
- **Two-zone end-of-horizon state was partly fabricated.** The end state was
  built from the room and slab only, so in two-zone mode the floor and buffer
  tank temperatures silently fell back to their defaults and were compared
  against the baseline's real values. The schedule is now replayed through the
  model to get a consistent end state.
- **"Suboptimal" was reported for perfectly good plans.** On a flat price curve
  the cost surface is genuinely degenerate, so the solver's line search aborts
  even though the result is fine. That is no longer surfaced as suboptimal
  unless the solver actually failed to improve on its starting point.

## v2.3.1

### Summary
Fixes the savings sensors, which routinely reported implausible numbers (often
above 90%). The reported figure is the gap between an optimized plan and a
"what a normal thermostat would have done" baseline, and the baseline was
burning far more energy than any real thermostat would.

### Fixed
- **The baseline no longer burns minimum power around the clock.** Baseline
  power was clipped to a *minimum* of the heat pump's minimum modulation power,
  so the reference schedule consumed at least `min_power x 24 h` every day even
  in weather that needs no heating at all. On a mild day that was a flat
  ~24 kWh against an optimized 0.16 kWh, which by itself produced the >90%
  readings. It also drove the baseline house to 25.3 °C, which no thermostat
  would do. Minimum modulation power is the lowest the pump can run *while
  running*; a pump that cannot go lower cycles instead, so 0 is now allowed.
- **The same floor applied to the optimizer itself.** With DHW disabled, space
  heating power was bounded below by the minimum modulation power, so the pump
  was forced on every single step. In warm weather this heated the house to
  25.3 °C and cost 40 SEK/day where the correct answer was to stay off.
- **The baseline is now a real thermostat.** It used a heuristic proportional
  term that over-delivered heat. It is now a cascade controller derived from
  the thermal model's own steady state, so the comparison is like-for-like. It
  holds the setpoint within 0.02–0.5 °C and its energy balance closes exactly.
- **End-of-horizon borrowed heat is no longer counted as savings.** Nothing
  past the optimization window is penalised, so the plan coasts the building
  and tank down as the window closes. That heat has to be bought back in the
  next window. The difference in stored thermal energy is now settled up at the
  25th-percentile price and charged against the reported savings. It is
  published separately as a `deferred_energy_cost` attribute on the savings
  percentage sensor, so `predicted_cost` remains the actual expected spend.
- **Savings percentage is clamped and guarded.** Baselines at or near zero no
  longer turn rounding noise into huge percentages.
- **Two-zone simulation lost the slab temperature every step.** The two-zone
  step function computed the new slab temperature and then dropped it when
  building the next state, so the slab was pinned at its default value forever
  and the lower floor could never be charged. Outdoor temperature and the
  anti-legionella timer were dropped the same way, which broke legionella
  tracking in two-zone mode.

### Effect on reported numbers
A control scenario with a completely flat electricity price, where there is
nothing to arbitrage and correct savings are therefore near zero, previously
reported 27%. It now reports 3.1%. Realistic scenarios with a 10x daily price
spread report 43–50% instead of up to 93%.

## v2.3.0

### Summary
This release reworks domestic hot water (DHW) optimization. Hot water is now
required only during time frames you configure, and it is produced with a
cheapest-first schedule instead of a target temperature the optimizer tried to
track regardless of price.

### Fixed
- **DHW no longer heats to high setpoints during price peaks.** The objective
  previously contained a "comfort" term that penalised any deviation from a
  ramped DHW target temperature. Its weight was orders of magnitude larger than
  the electricity cost term, so the solver effectively ignored price and heated
  the tank to setpoint whenever it drifted — including in the most expensive
  hours and while space heating was idle. DHW is now penalised only for
  *violating an availability requirement*, never rewarded for being hot, which
  leaves electricity cost as the only thing deciding when the pump runs.
- **DHW plans are now physically realizable.** The gradient solver used to smear
  DHW across many steps at 0.1–0.5 kW, below the level at which the heat pump is
  considered to be running. DHW is now scheduled as discrete on/off blocks.
- **The 45 °C floor no longer applies around the clock.** It applies inside the
  demand time frames; outside them the tank may cool to the idle minimum.
- **The options dialog no longer fails with a 500 error.** Reconfiguring an
  already-configured device returned *"Config flow could not be loaded: 500
  Internal Server Error"*. The options flow assigned to `self.config_entry`,
  which goes through a property setter Home Assistant deprecated in 2024.11 and
  removed in 2025.12. The flow now keeps its own reference to the entry.
- **Config entries from older releases now migrate.** The config flow declared
  schema version 6 without an `async_migrate_entry` handler, so Home Assistant
  refused to load entries written by earlier releases. Entries are now migrated
  forward; a newer entry is refused with a clear log message instead of failing
  obscurely.
- **Removed an invalid SciPy solver option** (`disp`) that produced an
  `OptimizeWarning` on every optimization run with recent SciPy versions.

### Added
- **Hot water demand time frames.** Configure when hot water must be available,
  e.g. `06:00-08:30, 17:00-22:00`. Frames may wrap past midnight and are
  editable from both the setup dialog and the options dialog.
  - Inside a frame the tank is guaranteed at or above the DHW minimum
    temperature.
  - At the start of a frame the tank is pre-heated only as far as that frame's
    expected draw requires, capped at the DHW setpoint — small consumers are no
    longer heated to full setpoint for no reason.
  - Outside the frames there is no availability requirement.
  - Leave the field empty to derive the frames from the learned usage profile,
    or switch the schedule off to require hot water around the clock.
- **Anti-legionella cycle**, enabled by default: the tank is heated to 60 °C
  every 7 days, scheduled at the cheapest hour before the deadline. The timer
  resets whenever the tank is observed at the disinfection temperature for any
  reason, so manual boosts and immersion heaters count. Temperature and interval
  are configurable, and the cycle can be turned off.
- **Idle minimum temperature** (default 20 °C) — the floor that applies outside
  the demand time frames.
- New DHW sensor attributes: `dhw_windows`, `dhw_in_demand_window`,
  `dhw_next_window_in_hours`, `dhw_required_temperature`,
  `dhw_idle_min_temperature`, `dhw_legionella_due_in_hours` and
  `dhw_planned_heating_hours`.

### Changed
- **Two-stage solve.** DHW is scheduled by a cheapest-first planner, then space
  heating is optimized around the fixed DHW blocks with the pump's remaining
  capacity as a hard per-step bound. This replaces the joint solve and its soft
  capacity penalty, so the capacity limit can no longer be violated.
- Slot ranking uses an *effective* price that includes the standby heat lost
  while water waits in the tank, so pre-heating many hours ahead is only chosen
  when it is genuinely cheaper.
- The tank is never planned above `min(70 °C, max(setpoint, legionella temp))`.
- The learned hourly draw pattern is masked by the configured time frames while
  preserving the total daily volume.
- Typical solve time with DHW enabled dropped from roughly 6 s to under 1 s, and
  the solver no longer hits its iteration limit.

### Changed limits
- Buffer tank volume now accepts up to **1500 L** (was 500 L), and is editable
  from the options dialog instead of setup only.
- DHW tank volume and daily hot water consumption now accept up to **1500 L**
  and **1500 L/day** (both were 500).

### Configuration options
| Option | Default |
|---|---|
| `dhw_schedule_enabled` | `true` |
| `dhw_windows` | `06:00-08:30, 17:00-22:00` |
| `dhw_idle_min_temperature` | `20` °C |
| `dhw_legionella_enabled` | `true` |
| `dhw_legionella_temperature` | `60` °C |
| `dhw_legionella_interval_days` | `7` |

### Upgrade notes
Existing installations pick up the default time frames on upgrade. If your
household draws hot water at other times, set `dhw_windows` in the integration
options. To keep the previous always-hot behaviour, turn off *Only guarantee hot
water during set time frames*.

## v2.2.0
**Release date:** 2026-04-27

### Summary
This minor release introduces a new, preferred ECL110 MQTT direct-write control path while keeping full backward compatibility with existing legacy JSON command workflows.

### Highlights
- **New ECL110 direct-write MQTT interface (preferred):**
  - Commands are now published as plain numeric payloads to a dedicated `/set` topic for cleaner, lower-overhead control.
  - Default direct-write topic: `ecl110/flow_temp_control/displace/set`.
- **Backward compatibility preserved:**
  - Legacy JSON command publishing remains supported on `ecl110/command`.
  - Existing ECL110 installations using the previous JSON interface continue to work without mandatory migration.
- **Broader state payload compatibility:**
  - State handling now supports both legacy JSON/dictionary payloads and scalar numeric payloads from hierarchical topic structures.
- **Improved configuration UX:**
  - Added a new configurable option: `ecl110_displace_set_topic`.
  - Existing `ecl110_command_topic` labeling has been clarified as the **legacy JSON path**.
  - Updated UI strings/translations for clearer topic purpose in both setup and options flows.

### Configuration options
The following MQTT topic settings are now available for ECL110 control:
- `ecl110_displace_set_topic` *(new, preferred direct-write path)*
  - Default: `ecl110/flow_temp_control/displace/set`
- `ecl110_command_topic` *(legacy JSON path, optional for compatibility)*
  - Default: `ecl110/command`
- `ecl110_state_topic` *(state feedback topic)*
  - Default: `ecl110/flow_temp_control/displace`

### User impact
- Recommended for users integrating with ECL110 hierarchical MQTT topics and direct numeric control.
- Existing users can safely upgrade without immediate topic migration.
- Integrators can run both paths in parallel during transition if needed.

### Notes
- This is a backward-compatible minor release.
- No required database/config migration for existing installations.

## v2.1.0
**Release date:** 2026-04-23

### Summary
This release improves Domestic Hot Water (DHW) optimization to prioritize cost savings while maintaining safe hot water availability.

### Highlights
- **Configured DHW minimum temperature is now actively enforced as the true floor** in optimization logic.
- **Predictive DHW pre-heating** now uses forecasted usage windows and estimated lead-time so the tank can coast near minimum between peaks.
- **Price-aware DHW control** reduces heating in expensive periods when no near-term hot water usage is predicted.
- **Learning usage patterns over time** from observed DHW temperature drops, persisted across restarts.
- **Post-install editability improvements** in the options flow for comfort/day-night schedule and DHW parameters.
- **Branding update**: added integration icon (`icon.png`) for HACS/repository branding.

## v2.0.1
**Release date:** 2026-04-21

### Summary
This patch release fixes a critical control logic issue that could prevent Domestic Hot Water (DHW) reheating when space heating demand was low or zero.

### Fixed bug
- **Critical ON/OFF control fix:**
  - The heat pump ON decision now correctly considers **both**:
    - space heating demand, and
    - DHW demand.
  - Previously, ON/OFF logic only evaluated space heating demand, which could keep the heat pump OFF even when DHW needed heating.

### Improvements and changes
- Updated ON/OFF schedule generation to use combined demand logic (`space OR dhw`) so the heat pump can activate for DHW-only demand periods.
- Added enhanced debug logging for optimizer decision-making, including:
  - per-step space heating power,
  - per-step DHW power,
  - threshold comparisons,
  - explicit decision reason tags (for example: `space_only`, `dhw_only`, `space_and_dhw`).
- Added clearer first-step decision summary logging to simplify troubleshooting during live operation.

### User impact and benefits
- Prevents missed DHW reheating cycles when there is no immediate space heating demand.
- Improves comfort and reliability by ensuring DHW demand can independently trigger heat pump operation.
- Makes behavior easier to diagnose with richer decision logs.
- Reduces risk of confusion where optimization output indicated DHW demand but physical heat pump stayed OFF.

### Upgrade instructions (HACS)
1. Open **HACS → Integrations**.
2. Find **Heat Pump Cost Optimizer**.
3. Click **Update** and install **v2.0.1**.
4. Restart Home Assistant (recommended after integration updates).
5. Verify operation:
   - Confirm integration version shows **2.0.1**.
   - Check logs at debug level if needed to validate combined ON/OFF decisions for space heating and DHW.

### Notes
- This is a backward-compatible patch release focused on control correctness and observability.
- No configuration migration is required.
