# Recurring bug classes across audit rounds 1–7

Source: `docs/audit-2026-09.md` (rounds 1, 2, 4, 6, 7), `tools/audit/round3/ledger/verdicts.tsv`
(round 3), GitHub issues #1293–#1340 (round 5). Only findings that **survived**
(verified or judge-weakened; refuted/withdrawn/unreproduced excluded) are counted.
One row per finding, classified by mechanism, is in `findings.tsv` (285 rows).

Findings classified per round: **R1 59, R2 75, R3 40, R4 37, R5 48, R6 31, R7 31**
(R7 includes the round-level instrument finding R7-INSTR-01). Total **285** — this
is a few short of the doc's own headline counts in a couple of rounds because a
handful of very-low-severity/duplicate rows (e.g. some `corroborates #N` rows
folded entirely into an already-counted issue, and R2's two panels not yet run
at time of writing for D0/D1/D4 were taken at their table status since nothing
in the tree later marks them refuted) were merged with their sibling row rather
than double counted. No round was unreadable; all seven were read in full.

Fifteen classes, ten **production** (custom_components/**, the card JS) and five
**instrument/process** (tests/, tools/, .claude/, .github/).

## Ranked list (by number of rounds the class recurs in, then total count)

| Rank | Class | Kind | Rounds present | Total | Sev mix (H/M/L, crit as H) |
|---|---|---|---|---|---|
| 1 | **I5** Docs/comments/compliance-checklist drift stale vs. code | instrument | 7/7 | 60 | mostly low, a few medium |
| 2 | **I1** Mutation-kill miscounted / vacuous test-gate coverage | instrument | 7/7 | 49 | mostly low/medium, some high |
| 3 | **P2** One fact decided twice by divergent/asymmetric predicates (sibling-seam guard gap) | production | 7/7 | 28 | high-heavy: 1 critical, several high |
| 4 | **P4** Optimizer seed set / stop-tolerance doesn't bracket the optimum | production | 7/7 | 14 | low/medium |
| 5 | **P5** sysid/adoption-gate metric keyed on the wrong quantity | production | 7/7 | 13 | medium/high |
| 6 | **P10** Solve on a GIL-holding thread starves the event loop | production | 7/7 | 10 | high-heavy |
| 7 | **P9** Card UI: clipping ancestor / missing token / unfloor'd hit-target | production | 6/7 | 19 | high-heavy in R1/R2/R7 |
| 8 | **P6** Producer/consumer key or field mismatch, silent fallback | production | 6/7 | 18 | high-heavy |
| 9 | **I3** Governance/CI required-check gap (skipped, stale ref, bypassable) | instrument | 6/7 | 18 | critical/high |
| 10 | **P1** Non-finite value crosses a persisted-store boundary, no guard | production | 6/7 | 12 | high-heavy: several critical/high |
| 11 | **P3** Fixed/mismatched capacity floor or divisor across sibling formulas | production | 5/7 | 13 | medium |
| 12 | **P8** Currency/unit resolved by divergent precedence on different surfaces | production | 5/7 | 7 | high in R1/R4/R7 |
| 13 | **I4** Two independent parsers/definitions of the same concept disagree | instrument | 4/7 | 14 | all medium (D13's own class) |
| 14 | **I2** Measured closure/scope diverges from the real dependency graph | instrument | 4/7 | 6 | low/medium |
| 15 | **P7** Naive wall-clock datetime arithmetic across DST | production | 3/7 | 4 | medium |

---

## Class detail

### P2 — One fact decided twice by divergent predicates (sibling-seam guard gap)
**What it is:** a freeze/availability/mode/staleness predicate is applied at one
code path and not at a sibling path that should share it, so two readers of "is
this frozen / is this stale / is this two-zone" disagree.

- Counts: R1 5, R2 7, R3 2, R4 3, R5 4, R6 3, R7 4 = **28**, severity 1 critical / 9
  high / rest medium-low.
- Examples: R1 D7-05 (`_accuracy.record()` gated on pump signals only), R2 D7-02
  (defrost flag freezes COP learner, not fabric learners), R5 D7-03/D7-04 (curve
  comfort tracker runs before pump-signal read; comfort quiet-period learner
  outside the shared freeze discipline), R7 D12-01 ("is this install two-zone"
  decided twice, divergently, by two different predicates), R7 D1-02
  (`_plan_is_stale` checked by one actuating write path, not the other).
- **Recurrence:** yes, repeatedly — this is the single most-recorded chain in the
  whole corpus. `#192` (round-1 D7-05) was corroborated again in R2 (D7-03), R5
  (D7-03), each time the panel found the fix narrower than the phenomenon. Round
  6→7's D8 chain (`#1398` → R7 D8-02) is the same shape on entity availability:
  the round-6 fix moved five DHW sensors to a dynamic `entity_registry_enabled_default`
  property; the sixth sensor was outside the mixin and the fix's own mechanism
  could not reach it.
- **Detector:** grep/AST for every call site of a named freeze/gate/staleness
  predicate function (`_learning_frozen`, `_plan_is_stale`, `pump_signals.freeze_reason`,
  `entity_registry_enabled_default`, `two_zone_enabled`) and diff the set of
  call sites against the set of sibling functions that structurally should share
  it (same class, same decorator, same dict of learners/entities/write-paths).
  Fully mechanical: build the call graph once, list every sibling that doesn't
  call the predicate. High feasibility, would need per-family policy (which
  siblings a predicate must reach) supplied once.

### P4 — Optimizer seed set / stop-tolerance doesn't bracket the optimum
**What it is:** the multi-start seed list, refine/discard rule, or `ftol`/`FACTR`
stop tolerance is fixed and doesn't reach the true optimum for a class of price
shapes or configurations it wasn't tuned against.

- Counts: R1 2, R2 3, R3 2 (weakened, low-actionable), R4 2, R5 3, R6 1, R7 1 = **14**.
- Examples: R1 D0-01/02, R2 D0-01..03 (top-k plateau, FACTR stop, buffer-clamp
  kink), R4 D0-01/02 (ftol halts short; iteration budget ungated), R5 D0-01/03/04
  (ftol tightening, fixed-seed gap, no MPC warm start), R7 D0-01 (multi-start
  anchored to `{0.35, 1.0}`, never brackets 0.20×).
- **Recurrence:** every round finds a new corner of the same knob — the panel
  named this explicitly (R6 dedup note): "a D0 fix must be priced in money and
  CPU beside the objective" because round-5's #1294/#1295 fix shipped a warm
  start and *dropped* the refine-cut change, and R6 D0-01 re-proposed exactly
  that dropped change, weakened for being priced only in the objective.
- **Detector:** property test — for every golden/fixture price×config cell, run
  production's multi-start with N seeds, then re-run with a much denser seed
  grid (or a global solver) on the identical objective/bounds/jac, and assert
  the gap is within tolerance; flag cells where it isn't. This is exactly the
  harness pattern every round already builds ad hoc (`race_grid.py`,
  `budget_race.py`); making it a permanent CI property test (not a one-off
  audit harness) is straightforward and would catch every future regression of
  this class. High feasibility, already half-built.

### P5 — sysid/adoption-gate metric keyed on the wrong quantity
**What it is:** the confidence/adoption gate that decides whether a system-
identification fit is trusted measures something other than the bias of the
parameter it is gating (excitation/SNR, self-consistency half-width, a fixed
excursion range) — so a biased fit can score well and an unbiased one can fail.

- Counts: R1 2, R2 2, R3 3, R4 1, R5 3, R6 1, R7 1 = **13**, medium/high.
- Examples: R1 D2-01 (adoption gate rewards drift), R2 D7-01/D2-04, R5 D7-01/02
  (0/360 combos pass; >2h settle routes to a biased one-state fit), R6 D7-01
  ("`_slab_confidence` has no term for the parameter of interest"), R7 D7-01
  (fixed-width `0.1 kW` pseudo-observation pins gains at the prior regardless of
  data, +7.44% bias passes at halfwidth ≈1e-4).
- **Recurrence:** the clearest chain in the corpus — round 2 D7-01 corroborates
  open #191 (round-1 D7-02); round 5 D7-01/02 corroborate #190/#191 again; round
  6 D7-01 corroborates #1394 narrower than the phenomenon; round 7 D7-01
  corroborates #1394 *again*, narrower still, driving the exact gate line #1437
  installed. Four successive "narrower than the phenomenon" verdicts on the same
  gate.
- **Detector:** a synthetic-bias sweep harness (already exists per-round as
  `sysid_bias.py`/`sysid_step_bias.py`): inject a known bias (sensor drift,
  noise, settle-gap) into the simulator, run `identify()`/`identify_slab()`,
  and assert the gate's admit/reject decision is monotone in the *true* bias,
  not merely in its own internal statistic. Promote to a permanent CI property
  test over the three shipped presets × a drift/noise grid. Medium-high
  feasibility — the harness exists, needs to become a first-class regression
  test with a tight pass bar instead of an audit one-off.

### P10 — Solve on a GIL-holding thread starves the event loop
**What it is:** the optimizer's heavy CPU work runs inside a `ThreadPoolExecutor`
under the real GIL with no yield bound, so the asyncio loop's heartbeat stalls
for the bulk of the solve's wall time; every fix (batching, yields) narrows but
does not remove the mechanism.

- Counts: R1 3 (D7-03, D9-01, D9-02/M1), R2 2 (D9-03, D9-05), R3 1 (D9-03), R5 1
  (D9-06), R6 1 (D9-01), R7 1 (D9-02) = **10**, high-heavy.
- **Recurrence:** M1 (round 1) → R2 D9-05 corroborates it and finds the
  190–300× headline doesn't reproduce but the ~75–97% starvation *share* does
  and is *understated* by the finder → R5 D9-06 corroborates again on the
  `#511` fallback route → R6 D9-01 corroborates `#1337`, measuring 0.97 after
  the batched-path fix, and shows adding yields moves the share only 0.97→0.98
  because the cap is the longest single L-BFGS-B run, not the between-run gaps.
  Four generations of the same mechanism.
- **Detector:** a real-loop heartbeat harness (exists every round as
  `h3_gil_hold.py`/`m3_gil_hold.py`) driven from CI: start a 1ms-period asyncio
  ticker, run a real solve in the production executor, assert p99 tick gap
  under a bound. High feasibility as a permanent perf-regression test (it is
  wall-clock sensitive, so needs a generous, machine-relative threshold rather
  than an absolute one — every round's finder already had to caveat this).

### P9 — Card UI: clipping ancestor / missing color token / unfloor'd hit-target
**What it is:** the Lovelace card has a size/contrast/hit-target floor rule that
covers most controls, and each round finds a control, container or language
variant the rule's own selector list doesn't reach.

- Counts: R1 4, R2 8, R4 1, R5 3, R6 1, R7 2 = **19** (no R3, D4 wasn't run there).
- **Recurrence:** R2 D4-01 is an explicit *regression* of R1's own 8px floor fix
  (only applies to renders that happen attached, not the dialog); R5 D4-02 →
  R6 D4-01 (the score pill, still missing from `htmlTargetFloor`'s selector
  list) → R7 D4-01/02 (a clipping *ancestor*, not a size floor, on the savings
  table and the Swedish tab label) — same "the floor doesn't cover container X"
  shape recurring across five rounds with a new container each time.
- **Detector:** the card already has the harness pattern
  (`card_geometry.mjs`/`sweep.mjs`) that enumerates every rendered DOM node's
  bounding box, contrast and clip state across arms (viewport × language ×
  pointer × theme). Turning that into a CI assertion — every clickable node ≥
  its floor, every text node's computed color passes contrast, every node's
  `scrollWidth` ≤ its clipping ancestor's `clientWidth` unless the ancestor
  scrolls — is mechanical and high-feasibility; it is already ~90% built as an
  audit tool, just not wired into the gate.

### P6 — Producer/consumer key or field mismatch, silent fallback
**What it is:** a reader (a sensor, a solve step, a log line) consumes a
key/field/side-channel that production never writes for it, or a code path
falls back to a stale/default value with no signal that it did.

- Counts: R1 5, R2 6, R3 2, R4 1, R6 1, R7 3 = **18**, high-heavy.
- Examples: R1 D8-01/D8-02, R2 D1-04/D1-05/D7-04/D8-01, R7 D8-01 (SensorGapAdvisor
  reads `house_power_series`/`heat_pump_power_series` — keys `_build_data_dict`
  never writes — publishes 0.00 SEK where the real series prices 30.0 SEK; the
  tests pass because they feed the advisor a fake coordinator with the series
  present), R7 D9-01 (36% of recorded bytes are values another entity already
  published or a class the plan sensors already exclude), R7 D1-01 (rate-limit
  slot only set on success, so every failing return re-triggers a fresh solve).
- **Recurrence:** same shape, new key each round — no single fix chain, but the
  mechanism (a test double or fake coordinator papers over a key production
  never populates) repeats.
- **Detector:** a static cross-reference — enumerate every `coordinator.data[...]`
  / `hass.data[...]` read across sensor/optimizer modules, and every key
  `_build_data_dict`/equivalent producers actually write, then flag reads with
  no matching write. Medium feasibility: needs to handle dynamic key
  construction (f-strings), but a first pass over literal keys would catch this
  class's exact shape (R7 D8-01) directly.

### I5 — Docs/comments/compliance-checklist drift stale vs. code
**What it is:** README/docs/`quality_scale.yaml`/code comments assert a fact
(a field list, a module count, a rule's status, a symbol name, a service
example) that the shipped tree no longer matches.

- Counts: R1 10, R2 15, R3 10, R4 7, R5 9, R6 6, R7 3 = **60**, overwhelmingly low.
- **Recurrence:** constant across every round; several rows are explicit
  successors of an earlier fix that corrected one instance and left a sibling
  (R6 D5-02 vs. R5 D5-03: same "orphan/unreachable doc" class, different
  measurement; R7 D5-01 vs. R2 D5-05: same "backticked symbol resolves to
  nothing" instrument, new instance).
- **Detector:** already mostly built per-round (`claims_check.py`,
  `docs_structure.py`, `comment_symbols.py`) — a claims table executed against
  the real platform/schema/constants, a link-graph walker, and a backticked-
  identifier resolver. High feasibility to run continuously; the gap is that it
  runs once per audit round rather than as a CI check on every docs-touching
  PR.

### I1 — Mutation-kill miscounted / vacuous test-gate coverage
**What it is:** a production guard, clamp or branch can be deleted (or its
condition forced) with the full gate green, because no assertion in the
measured closure exercises the changed behavior, or because the kill-detection
rule itself counts a non-assertion signal (an unrelated red, an exit code) as a
kill.

- Counts: R1 8, R2 11, R3 7, R4 4, R5 10, R6 6, R7 3 = **49**, the largest raw
  count in the corpus.
- **Recurrence:** the meta-version of this class recurs on its own kill rule:
  R6 D3-01 found `tests/entities.py` false-passes when `orjson` is importable;
  R7 D3-02 found `tests/mutation_table.py` counts `structure.py`'s exit code 2
  (an *improvement*, not a violation) as a kill, and that channel produced 2 of
  5 kills in the pre-screen — an instrument bug about the instrument's own
  scoring, one meta-level up from the ordinary vacuous-mutant finding, itself
  recurring (round 4 and round 6 both found different scoring artifacts).
- **Detector:** this *is* the detector already (mutation testing against the
  measured closure) — the gap is coverage density and kill-rule fidelity. Two
  concrete, mechanical fixes: (1) never count a non-zero/changed exit code as a
  kill unless the tool also reports ≥1 failing assertion; (2) periodically
  re-run the corpus of previously-survived mutants as a regression check that
  they now die. High feasibility, mostly a policy change to the existing
  harness rather than new tooling.

### I3 — Governance/CI required-check gap
**What it is:** a required GitHub check is skipped by a preceding step's
failure, checks out a stale ref instead of the PR head, or the ruleset/identity
boundary it depends on has a hole (no CODEOWNERS match, no pull_request rule,
a bypass-always identity).

- Counts: R3 4, R4 6, R5 2, R6 2, R7 3 = **18** (D11 didn't exist R1/R2),
  critical/high-heavy.
- **Recurrence:** R4 D11-01 (no pull_request rule at all) → R3's own D11-01
  (same mechanism, filed earlier chronologically in the repo's real numbering
  but read after R4 here) → R5 D11-01 (ruleset drift between committed fixture
  and live boundary) → R6 D11-01/02 (CODEOWNERS coverage gap; `policy-docs`
  checks out no `ref:`) → R7 D11-01 (the histogram's filer step skipped in
  39/40 runs) — five generations of "the enforcement surface has a hole the
  instrument doesn't see."
- **Detector:** drive the production ruleset-reading code (already exists per
  round as `check_rules.py`) against the *live* GitHub ruleset API rather than
  a committed fixture, and diff; also grep every `uses:`/`checkout` step in
  `.github/workflows/*.yml` for a missing or wrong `ref:` on a job whose name
  matches a branch-protection required-context. Medium feasibility — needs
  live API access, which the audit rounds already have.

### P1 — Non-finite value crosses a persisted-store boundary, no guard
**What it is:** a `NaN`/`Infinity`/malformed string reaches a persisted HA
Store's loader, survives `from_dict`, and either crashes every future update
cycle or is silently absorbed into learned state with no log/reset/repair.

- Counts: R1 2, R2 1, R3 1, R5 2 (excl. via D3 rows), R6 2 = **12** (missing R4,
  R7 — R7's nearest instance, D2-01, is a divisor mismatch classed P3 instead),
  several critical/high.
- **Recurrence:** R1 D1-01/D1-05 (ledger, snapshot) → round-1's own fix (A2,
  `#134`) hardened two stores → R2 D1-03 measured the other seven stores against
  2000 seeded mutants and found 152/2000 still fatal → R5 D1-05 found the same
  class on the DHW-profile store (4 more seams: `dhw_learning`, `dhw_draws`,
  `tariff.PeakTracker`, `curve_learning`) → R6 D1-01 found the fifth seam of
  that exact family, explicitly named as round-5's `#1296` guard covering four
  of five → R6 D1-02 found the same class on the *accuracy* store's
  `defrost.duty` field. This is the textbook "a fix for one instance later had
  a sibling found in a later round" pattern, repeated at least four times on
  four different stores.
- **Detector:** for every dataclass/`from_dict` that deserializes a persisted
  Store, an AST/reflection sweep listing every `float`-typed field and
  asserting each passes through an explicit `math.isfinite` check before use;
  a property-based fuzz test (seed every numeric field with `nan`/`inf`/a
  malformed string across every store class in one run, already built per-round
  as `nonfinite_drill.py`/`store_fuzz.py`) run permanently in CI over the full
  store roster rather than one store at a time. High feasibility, and the
  round-2/round-5 harnesses are most of the way there already.

### P3 — Fixed/mismatched capacity floor or divisor across sibling formulas
**What it is:** a capacity constant (`max(C, 0.01)`, a fixed temperature
ceiling, an inlet floor) is used inconsistently across formulas that should
agree, so the energy/mass balance silently manufactures or deletes heat, or a
solve stalls at the clamp's kink.

- Counts: R2 3, R4 4, R5 2, R6 3, R7 1 = **13**, medium-heavy.
- **Recurrence:** R7 D2-01 found `max(C_buf, 0.01)` disagreeing with the raw
  `C_buf` used by the availability bound and stiffness count at **four** seams
  in `thermal_model.py`; a fixer's own step-8 enumeration then found a fifth,
  sibling seam in `optimizer.py:_dhw_coil_wood_forecast` **after** the fix PR
  had already merged (GitHub issue #1487, filed against the still-open sibling
  divisor). This is a recurrence discovered *within* the same fix wave, not
  just across audit rounds — the clearest "sibling seam" example in the corpus.
- **Detector:** grep every `max(<capacity var>, <constant>)` in
  `thermal_model.py`/`optimizer.py` and cross-reference each capacity variable
  against every other formula that reads the same variable unclamped in the
  same function/file; flag disagreement. Mechanical and cheap — this is
  exactly what issue #1487 was found by (a fixer's own enumeration), so
  formalizing that enumeration as a repo-wide grep is high feasibility.

### P8 — Currency/unit resolved by divergent precedence on different surfaces
**What it is:** the same currency or physical unit is computed by two
different rules on two different UI/production surfaces (a sensor's declared
`unit_of_measurement` vs. a card's `config.currency || attrRaw || hass.config`
chain; an assumed-metric temperature input regardless of HA's real unit).

- Counts: R1 1, R2 1, R4 3, R5 1, R7 1 = **7**, high-heavy (R1, R4, R7).
- **Recurrence:** R1 D4-04 (hardcoded SEK) → closed by B3 → R4 D12-01
  (temperature unit always assumed °C) is the same *shape* on a different
  quantity → R7 D4-03 explicitly names R1's closed `#168` as "the origin of the
  card's currency: option" and finds the headline and the savings table
  resolving currency through two different precedence chains on the same card.
- **Detector:** for currency — grep every site that reads a currency/unit
  (`config.currency`, `attrRaw("currency")`, `hass.config`,
  `unit_of_measurement`) in the card JS and assert they all resolve through one
  shared function; for units — a property test that drives every guarded
  numeric input through both a metric and non-metric HA instance and asserts
  identical physical (not textual) results. Medium feasibility for the card
  (needs a shared resolver refactor to make it enforceable); the unit sweep
  already exists as a harness pattern from R4 D12-01.

### I4 — Two independent parsers/definitions of the same concept disagree
**What it is:** two separately-maintained pieces of code (a regex, a class
vocabulary, a metric formula) both claim to read/compute the same thing and
disagree, so one reader sees a signal the other cannot.

- Counts: R5 3, R6 3, R7 7 = **14** (D13 only exists from round 5 on), all
  medium.
- **Recurrence:** near-100% within D13's lifespan — every round D13 has run,
  it has found a new pair of readers disagreeing (R5: `--stats` vs. `VERDICT_RE`,
  friction-id grammar; R6: `head-moved` class defined but never emitted, verdict
  population denominator; R7: seven more — the histogram's regex vs. the wave's
  `VERDICT_RE` on four axes, class-vocabulary gap, CFR merge-keyed vs.
  head-keyed, the reviews endpoint never fetched, `stress.py`'s docstring vs.
  `SolverWork`'s literal definition disagreeing by 96×).
- **Detector:** for each pair of readers of the same corpus (a diff of two
  regex patterns' accepted-language, or two functions computing "the same"
  count from the same inputs), a property test that generates the boundary
  cases each pattern/definition disagrees on and asserts both readers give the
  same verdict. High feasibility once the pairs are enumerated — R7's own
  dedup notes already did this enumeration by hand for three pairs.

### I2 — Measured closure/scope diverges from the real dependency graph
**What it is:** `tests/closures.json` (or an equivalent scope recorder) records
a script's dependency set incorrectly — a warm `__pycache__` `exec_module` load
recorded as no file, a phantom entry pointing at a file that doesn't exist, or
an audit workflow's own dimension list omitting a whole dimension.

- Counts: R2 1, R5 3, R7 1 (R7-INSTR-01, the audit driver's own D13 omission)
  = **6**.
- **Recurrence:** R2 D3-09 (closures are the whole package import) → R5 D3-01/02
  (the recorder misses warm-cache loads; 199 phantom entries) — same underlying
  "the scope recorder and the real graph disagree" mechanism, worse in R5
  because it was measured directly rather than inferred.
- **Detector:** run the closure/dependency recorder twice — once cold, once
  warm (`__pycache__` populated) — and diff; separately, validate every entry
  in `closures.json` resolves to an existing file. Both are cheap, mechanical,
  and already what the R5 harnesses did (`warm_pyc_miss.py`, `phantoms.py`).
  High feasibility to run as a standing CI check.

### P7 — Naive wall-clock datetime arithmetic across DST
**What it is:** two clocks that should agree (a plan's UTC grid vs. a tariff's
local-time grid; an "age" computation naively subtracting two `ZoneInfo`
datetimes) diverge by exactly the DST offset on transition days.

- Counts: R2 1, R3 1, R5 1 = **4** (only in rounds where D1/D2 finders happened
  to drive a DST fixture), medium.
- **Recurrence:** R2 D2-03 (planning grid) and R3 D2-02 (`tariff.window_factors`)
  are the same mechanism on two different grids, both open at the time R5's
  D1-08 found a third instance (age seams) — three sibling instances, never
  consolidated into one fix.
- **Detector:** a property test that runs every datetime-difference/grid-
  construction call site (`_plan_age_minutes`, `weather_stale_hours`,
  `window_factors`, `_price_series`) across all six DST transition days
  2025–2027 and asserts the result matches a UTC-normalized reference. High
  feasibility — the harness (`h5_dst_age_seams.py`) already exists and is a
  pure function sweep with no solver cost.

---

## Notes on method

- "Weakened" verdicts are counted as survived per the task's instructions
  (only refuted/withdrawn/unreproduced are excluded); their final severity
  (post-judge) is what's recorded in `findings.tsv`.
- Round 4's `D3-S4` ("judged equivalent" — a mutant that provably cannot change
  behavior) and round 4's `D4-02` (3-0 refuted: the finder's premise, HA's stock
  dark-theme color, was false) are the only two rows excluded from an otherwise-
  reported table; both are noted in the register as refuted/equivalent.
- Round 2's D0/D1/D4 panels were noted in the doc as "still to run" at the point
  the register was written; nothing later in the tree marks any of those rows
  refuted, so they are counted at their table status (`reported`), consistent
  with every other round's finder-reported severity being carried through
  unless a later verdict overrides it.
