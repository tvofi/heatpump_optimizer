# The open-issues and alert-fix program

Written 2026-08-30 against `main` at `83b7ea0` (v5.5.0), covering every
open issue at that moment (#86–#101) and all eleven open CodeQL alerts.
This is the worklist for the releases that follow v5.5.0; each merge out
of this program gets its own version and its own `RELEASE_NOTES.md`
section, per the release workflow's contract.

Two design forks were settled before this file was written, and both are
decisions, not proposals:

- **#86 uses a threshold-gated re-anchor law.** The re-anchor applies
  only when the coefficient change exceeds the learner's own materiality
  threshold; sub-threshold edits keep today's behaviour, which measured
  better on the 30-hop walk (+2.5 % for today's behaviour against the
  ungated law's 18.2 %).
- **#101's renderer is wired up, not deleted.** `setup_qa_render.mjs`
  joins the visual-QA lane with a DOM stub shared with `card.mjs`
  instead of a drifting copy.

## Delivery status

Updated as the program lands; each item names the release that carried
it. Where this section and a wave body below disagree, this section is
the truth.

**Delivered:**

- **The eleven CodeQL alerts** — cleared in v5.6.2 (verified empty on
  the default branch after merge).
- **#87, the settlement cap's bound** — v5.7.0. Inert at every captured
  configuration; the mutation anchors are the schema-minimum case and a
  reachable 45 °C plant.
- **#89, the optimality gate's budget check** — v5.7.1. The gate now
  races the production-budget solve against a starved one; the cut it
  could not see cost 16.2 % on two-zone.
- **#86, the re-anchor** — v6.0.0. The threshold-gated law, the zone-
  total basis, clamp-means-reset, the gated write, and both collateral
  defects, mutation-proven three ways (the disabled-law mutation
  reproduces the issue's 1.937× headline number exactly).
- **#93, the crawl-space double count** — v6.0.1. No golden moves: the
  captured presets never pair a slab-bearing structure with a crawl
  space. With the re-anchor in place, a questionnaire re-answer now
  reaches an install that has already learned something.
- **#92, the comfort-band validation** — v6.0.2. The night-selector
  exemption, the joint satisfiability sweep, and the shared selector
  bounds in `const.py`.
- **#90, the loud closures gate** — v6.0.3. `derive_closures.sh
  --single` shipped with it and immediately proved itself by fixing the
  `frontend.py` closure under-scoping that main's gate had just caught.
- **The entities.py repair (#100's prerequisite)** — v6.0.4. The
  options-flow loops classify every page's outcome instead of skipping
  silently.
- **#91, the no-copies rule** — v6.0.5. `closure.py no-copies` fails on
  a test-defined symbol that matches production; runs in the closures
  job on main.
- **#88, the BLAS thread pin** — v6.0.6. `threadpoolctl` as a manifest
  requirement, scoped to each minimize call; plan fingerprints
  byte-identical.
- **#98, the GIL-yield bound** — closed by measurement, no code change:
  the longest contiguous GIL hold during a realistic cold solve is
  ~34 ms (median ~7 ms, the 5 ms switch interval plus scheduling),
  recorded on the issue with the Pi extrapolation stated.
- **#99, retention** — v6.0.8. The rolling-suite harness measured every
  audited collection bounded (the lead-error maps at their bucket count,
  the promise list under its 512 cap, the ring at its 672 maxlen), and
  `manual_override`/`dhw_windows` left the recorder.
- **#94, drift-cache warming** — v6.0.9. The push-to-main run stores the
  main-tree capture it already makes under the key the following PRs
  compute; the nightly keeps it fresh. Verified on its first
  beneficiary: PR #121's re-run restored the warmed entry.
- **#96, the browser lane** — v6.1.0. Real Chromium asserting real
  geometry for the three historically-shipped defect classes, with a
  vacuous-pass guard; its own workflow job.
- **#95, the card seams** — v6.1.1. `cardStyleBlock()` and
  `setupSvgHtml()` left the god class as top-level functions; the class
  shrank from ~7,600 to 4,895 lines behind same-named thin seams.
- **#101, the QA renderer** — v6.1.2. Wired into the card lane of every
  gate on one shared DOM stub (`tests/dom_stub.mjs`); the drifted copy
  is gone.
- **#97, the gradient** — v6.2.0. The `maxfun` cap was rejected by the
  drift gate (five scenarios moved: the default 15,000 evaluations is
  load-bearing, recorded on the issue). What shipped is the real fix:
  `simulate_trajectory_batch`, the bitwise-parity vectorized twin of the
  scalar step, plus a `jac=` that reproduces scipy's own 2-point
  estimate as one batched call. Measured **11.5 s → 1.0 s** per
  two-zone solve, plans byte-identical, with the batch serving uniform
  bounds only — the drift gate caught the capped-tariff scenarios moving
  on Linux and the guard is the record of that catch.
- **#100, the menu-return** — v6.2.1. Write-through with immediate
  reload, the choice stripped before persisting, advanced pages back to
  the advanced menu; the config_flow golden's 12 new leaves are the
  field itself, claimed.

**All sixteen issues and all eleven alerts are closed. The program is
complete.**

The final count: 19 releases (v5.6.0 through v6.2.1), every merge
stamped, tagged and released per the release workflow's contract. Two
unplanned items joined the program on the way and are part of the
record above: v5.6.0 (the test harness's file and network sinks — five
pre-existing security-scan findings that were blocking all commits) and
v6.0.3's closure fix for `frontend.py`. Two findings were closed by
measurement rather than code (#98, and #97's `maxfun` item) — the
issues' own measure-first discipline, honoured.

## Standing rules for every item

- One PR per issue (or one tightly themed group), squash-merged, closing
  its issue in the body.
- Tests **import** production symbols. A test that re-implements a
  production formula and asserts against its own copy pins nothing
  (#91's rule, written in `tests/README.md`).
- Every new runnable test script gets a `closures.json` entry, so the
  scoped gate keeps working (#90 makes forgetting this loud).
- Golden fixtures are re-recorded deliberately, with the drift explained
  in the PR, never as an accident of the run.
- `RELEASE_NOTES.md` gains the version's section and `VERSION` is bumped
  in the same PR; the tag follows the merge and the workflow quotes the
  notes onto the release page.

## Wave 0 — the eleven CodeQL alerts

One PR, no behaviour change:

1. `open_meteo.py:351-352` — stop logging the coordinates in the
   solar-fetch failure warning. Rounding is not a reliable silencer and
   four decimals is genuinely identifying; `diagnostics()` already
   publishes rounded coordinates where they are wanted.
2. `tests/setup_qa_render.mjs:269` — splice the style block after the
   opening `<svg>` tag with `indexOf(">")` + slice instead of a
   non-global `replace(/>/, …)`, which trips the incomplete-sanitization
   query while doing the same thing.
3. `tests/card.mjs:4910` — extract tooltip row labels with the file's
   existing DOM stub (`parseHtml(...).textContent`) instead of regex
   tag-stripping.
4. `permissions: contents: read` at the top of `hassfest.yml`,
   `validate.yml` and `tests.yml` — the convention `release.yml` already
   follows — clearing all five missing-permissions alerts.
5. Pin `home-assistant/actions/hassfest` and `hacs/action` to commit
   SHAs, with the upstream tag recorded in a trailing comment, clearing
   the two unpinned-tag alerts.

Alerts only clear on the default branch, so verification happens after
merge: CodeQL re-analyzes `main` and the eleven alerts close.

## Wave 1 — independent correctness fixes

**#87 — bound the slab settlement cap.** `optimizer.py`'s
`slab_settlement_cap` ends in an unbounded `q_demand /
slab_heat_transfer` that reaches ~195 °C at the derivation's own floor.
Bound it by a physical ceiling derived from existing configuration (the
emitter's maximum flow temperature, or the slab temperature the
configured maximum output can sustain) so it moves with future config
changes rather than a magic constant. Tested across the full
`slab_heat_transfer` span `presets.derive` can emit, including the
floor; mutation-proven by removing the bound.

**#92 — validate `comfort_temp_day/night` against the comfort band.**
Both traps recorded in the issue are load-bearing: the rule must be
*jointly satisfiable at every slider extreme* of all five fields (a
standing exhaustive test over the 0.5 °C grid — a first attempt
dead-ended initial setup at `min_temperature = 25.0` because the night
selector caps at 24.0), and a pre-existing contradictory entry is
exempted only for values its own selector can produce, never
unconditionally, or `apply_schedule` amplifies the contradiction. Both
the initial and options paths are tested; the config-flow golden moves.

**#93 — the crawl-space double count in `presets.derive()`.** Use the
subtract-the-slab form derived from `_STRUCTURE_MASS` itself —
`slow_per_m2 = max(slow − (TIMBER_SLAB_slow − TIMBER_CRAWLSPACE_slow),
TIMBER_CRAWLSPACE_slow)` — not the rejected `min(slow, 0.010)` cap,
which over-corrected honest masonry-over-crawlspace answers. The test
must prove the uplift reaches an install that has already learned
something; until #86 lands, the re-anchoring gap absorbs exactly that
event, so this item's full effect is only observable after Wave 2.

## Wave 2 — #86, the flagship

The learned heat-loss scale re-anchor, fourth attempt, this time by the
recorded decisions rather than against them:

1. `_thermal_learning_payload` records the coefficient the scale was
   fitted against (the anchor).
2. `_async_load_thermal_learning` re-anchors on load with the law
   `U_eff' = (1 − φ)·nameplate_new + φ·measured_UA`, written in absolute
   UA on the zone-total basis — the two properties round one got wrong —
   and **gated by the learner's own materiality threshold**: below it,
   today's behaviour stands (the settled fork above).
3. If the re-anchored scale falls outside `[0.3, 3.0]`, reset explicitly
   and log it. Clipping onto a bound lets the next edit read the bound
   as the learner's own signal.
4. Persistence is gated in the loader by `if reanchored or not
   anchored` — one extra write per install; unconditional writes are
   defeated by `updated_at` moving every call.
5. Both collateral defects go with it: the service path
   (`async_update_thermal_params`) must not leave a reset scale paired
   with an in-memory-only coefficient across restarts, and
   `_apply_learner_payloads` must not re-install a pre-edit scale from a
   weekly snapshot after an options edit.
6. The tests are rewritten, not iterated: they import the confidence
   curve and materiality guard from the coordinator, their mutation
   proofs delete constants in `coordinator.py`, and the 26-scenario grid
   and the 30-hop sub-threshold walk run against `main` as the
   reference.

## Wave 3 — test infrastructure the rest depends on

- **#90 — the scoped gate fails loud.** The `closures` job on `main`
  fails when a selectable script has no recorded closure, instead of PRs
  silently degrading to full runs; `derive_closures.sh` learns to record
  a single script instead of re-deriving everything (~25 min today —
  the friction that causes the skips); `tests/README.md` documents the
  step.
- **#91 — stop tests re-implementing production formulas.** An AST check
  in the closures job comparing the production symbols a test file
  mentions in assertions against the set it imports, plus a cheap
  name-collision flag. Not airtight against renamed copies; it raises
  the cost of the accident.
- **#89 — make `optimality.py` budget-sensitive.** Measure first whether
  a 3-iteration solve is materially worse than a 300-iteration one —
  SLSQP multi-start may genuinely converge early, in which case the
  issue closes with the measurement. If the gap is real, bind achieved
  objective to the iteration budget with an assertion mutation-proven
  against the exact 300 → 3 cut, never against a hardcoded objective.
- **#100's prerequisite — repair `tests/entities.py`.** The options-flow
  loop skips any page that does not return `create_entry`; fix the skip
  and the `["data"]` index sites before the menu-return feature lands,
  or it ships untested by construction.

## Wave 4 — performance and latency, measure-first

The issues demand measurement before change, and closing an item with
"measured, already adequate" is a valid outcome.

- **#88 — BLAS oversubscription.** Scope thread counts around the solve
  (`threadpoolctl` if the environment has it; environment variables
  before the first numpy import only as the coarse fallback), never
  process-wide — other HA components share the interpreter. Verified by
  plan-fingerprint identity across the golden scenarios plus a CPU-time
  factor drop in `tests/stress.py`; CI's relaxed `STRESS_SOLVE_BUDGET_MS`
  is not a signal.
- **#97 — the finite-difference gradient cost.** Instrument the actual
  evaluation count and time share on realistic inputs before touching
  anything. Then cheapest first: a `maxfun` cap, a coarser `eps` (1e-4
  may be finer than the objective's own noise floor), a vectorized
  finite-difference batch. An analytic gradient only if all three fall
  short. Plans stay byte-identical across the goldens or the drift is
  claimed explicitly.
- **#98 — the GIL-yield bound.** Measure the longest contiguous
  GIL-holding interval on a realistic cold solve. Already short → close
  with the measurement. Seconds → a periodic yield inside the iteration
  loop via scipy's `callback=` hook, not more seams.
- **#99 — memory instrumentation.** A retention harness in
  `tests/rolling.py` (SLOW-gated) snapshotting `SystemIdentification`
  samples, the COP baseline and capacity envelopes, `AccuracyTracker`'s
  float-keyed lead maps, and `ThermalModel.last_buffer_trajectory` after
  long simulated runs, asserting bounds where they should exist. Also
  decide whether `manual_override` and `dhw_windows` join
  `_unrecorded_attributes` — recorder volume is a real cost on
  SD-card-class hardware.

## Wave 5 — browser lane, QA renderer, card seams, options UX

Strictly ordered; each item is riskier without the one before it.

1. **#96 — a real-browser layout lane.** Playwright against the
   pre-installed Chromium (`PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`),
   SLOW-gated or its own job, with a `closures.json` entry. It asserts
   real positions, sizes and visibility for the three historically
   shipped defect classes (the zoom-limited editing trap, tooltip
   overflow, the legend chips that read as one). The stub's constant
   900×400 geometry catches none of these.
2. **#101 — wire up `setup_qa_render.mjs`.** Extract the DOM stub into
   one module shared with `card.mjs`, run the renderer in the visual-QA
   lane, register it in `closures.json`, and remove the exclusion
   references in `run.sh` and `closure.py`'s `NOT_A_TEST`.
3. **#95 — extract the card's clean seams.** `_styleBlock` (a
   self-contained CSS string) and the setup-page rendering path leave
   the 7,900-line class without reaching back into it. Every pinned
   contract stays literal-tested: `data-edge="a>b"` with the class order
   `setup-pipe[ layout-match| invalid]`, one `rect.setup-hit` with
   `data-key` per slot, the `apply_topology {layout, positions}`
   payload, the `0 0 720 H` viewBox, four editor ports per node at
   bounding-box side midpoints.
4. **#100 — options flow returns to the section menu.** A schema field
   expresses the two outcomes from one submit (a form renders exactly
   one button; that is the only mechanism), the submit label is
   overridable per step via translation keys, and saving writes through
   with an immediate reload — never a flow-liveness deferral, whose
   leaked flow ids would suppress reloads permanently. The
   `suggested_value` safety invariant is pinned by a real test, not the
   golden, which does not record it.

## Delivery order

Waves land in order; within a wave the items are independent except
where marked (#93 completes after #86; #95 after #96; #100 after its
Wave 3 prerequisite). Every merge is released as its own version, and
each PR closes its issue.
